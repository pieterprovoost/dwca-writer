from typing import Dict, List
import pandas as pd
import xml.etree.ElementTree as ET
import xmltodict
import tempfile
import os
from zipfile import ZipFile
import csv
import pkg_resources
import re
import warnings


def xml_to_string(root: ET.Element, encoding: str="UTF-8") -> str:
    """Dump an XML element to string."""

    tree = ET.ElementTree(root)
    ET.indent(tree, space="\t", level=0)
    return ET.tostring(tree.getroot()).decode(encoding)


def escape_character(input: str) -> str:
    """Escape a character for use in the table element attribute values."""

    return repr(input).replace("'", "") if input is not None else ""


class Table:

    def __init__(self, data: pd.DataFrame=None, spec: str=None, id_index: int=None, encoding: str="UTF-8", fields_terminated_by: str="\t", lines_terminated_by: str="\n", fields_enclosed_by: str=None, ignore_header_lines: int=1, only_mapped_columns: bool=False):
        self.spec = spec
        self.id_index = id_index
        self.data = data
        self.encoding = encoding
        self.fields_terminated_by = fields_terminated_by
        self.lines_terminated_by = lines_terminated_by
        self.fields_enclosed_by = fields_enclosed_by
        self.ignore_header_lines = ignore_header_lines
        self.dwc_fields = None
        self.row_type = None
        self.only_mapped_columns = only_mapped_columns

    def get_filename(self) -> str:
        """Generate a filename for this table."""

        return self.row_type.split("/")[-1].lower() + ".txt"

    def update_spec(self) -> Dict:
        """Populate row type and a dictionary with all associated Darwin Core field names and URIs."""

        if self.spec is not None and self.spec.startswith("https://rs.gbif.org/"):
            spec_location = re.search("https://rs.gbif.org/(.+xml)", self.spec).group(1)
            parts = spec_location.split("/")
            spec_path = pkg_resources.resource_filename(__name__, os.path.join("data", *parts))

            with open(spec_path) as spec_file:
                spec_json = xmltodict.parse(spec_file.read())
                self.row_type = spec_json["extension"]["@rowType"]
                self.dwc_fields = { prop["@name"]: prop["@qualName"] for prop in spec_json["extension"]["property"] }

        else:
            raise Exception(f"Specification {self.spec} not supported")

    def get_fields(self) -> List[Dict]:
        """Return a data structure listing all table fields, their mapping, and their index in the output file."""

        if self.dwc_fields is None:
            self.update_spec()

        result = []
        index_output = 0

        for index, column in enumerate(self.data.columns):
            entry = {
                "name": column,
                "index_output": None,
                "uri": None
            }
            if column in self.dwc_fields or index == self.id_index or self.only_mapped_columns == False:
                entry["index_output"] = index_output
                index_output = index_output + 1
            if column in self.dwc_fields:
                entry["uri"] = self.dwc_fields[column]
            result.append(entry)

        return result

    def get_table_xml(self, is_core=False) -> ET.Element:
        """Generate the XML element for this table's entry in meta.xml."""

        self.update_spec()
        fields = self.get_fields()

        root = ET.Element("core" if is_core else "extension", attrib=self.get_attributes())
        
        # files

        files = ET.SubElement(root, "files")
        location = ET.SubElement(files, "location")
        location.text = self.get_filename()

        # id / coreid

        if self.id_index is not None:
            if is_core:
                ET.SubElement(root, "id", attrib={"index": str(self.id_index)})
            else:
                ET.SubElement(root, "coreid", attrib={"index": str(self.id_index)})

        # field

        for field in fields:
            if field["index_output"] is not None and field["uri"] is not None:
                ET.SubElement(root, "field", attrib={"index": str(field["index_output"]), "term": field["uri"]})

        return root

    def get_attributes(self) -> Dict:
        """Generate the attributes for this table's XML element."""

        return {
            "encoding": self.encoding,
            "fieldsTerminatedBy": escape_character(self.fields_terminated_by),
            "linesTerminatedBy": escape_character(self.lines_terminated_by),
            "fieldsEnclosedBy": escape_character(self.fields_enclosed_by),
            "ignoreHeaderLines": str(self.ignore_header_lines),
            "rowType": self.row_type
        }

    def has_column(self, name:str) -> bool:
        """Table has a column with the specified name."""

        return name in [field["name"] for field in self.get_fields()]

    def add_id(self, name: str="id") -> None:
        """Add a sequential id column, copy the column if id_index is already set."""

        if self.has_column(name):
            warnings.warn(f"Column {name} already exists")
        elif self.id_index is not None:
            self.data.insert(0, name, self.data.iloc[:, self.id_index])
            self.id_index = 0
        else:
            self.data.insert(0, name, range(1, 1 + len(self.data)))
            self.id_index = 0

    def write_tsv(self, file) -> None:
        """Write the table to tsv."""

        fields = self.get_fields()
        exported_fields = [field["name"] for field in fields if field["index_output"] is not None]
        self.data.loc[:, exported_fields].to_csv(file, sep=self.fields_terminated_by, index=False, escapechar="\\", encoding=self.encoding, quoting=csv.QUOTE_MINIMAL if self.fields_enclosed_by is not None else csv.QUOTE_NONE, quotechar=self.fields_enclosed_by, line_terminator=self.lines_terminated_by)

    def __str__(self):
        if self.row_type is None:
            self.update_spec()
        result = f"Table of type {self.row_type} with {len(self.data)} rows and {len(self.data.columns)} columns"
        for field in self.get_fields():
            result = result + f"\n  {field['name']}{': ' + field['uri'] if field['uri'] is not None else ''}{' (column ' + str(field['index_output'] + 1) + ')' if field['index_output'] is not None else ''}"
        return result


class Archive:

    def __init__(self, eml: ET.Element=None, eml_text=None, core: Table=None, extensions: List[Table]=[]):
        self.eml = eml
        self.eml_text = eml_text
        self.core = core
        self.extensions = extensions

    def get_meta_xml(self) -> ET.Element:
        """Return XML element for meta.xml."""

        root = ET.Element("archive", attrib={"xmlns": "http://rs.tdwg.org/dwc/text/", "metadata" : "eml.xml"})
        root.append(self.core.get_table_xml(True))
        
        if self.extensions:
            for extension in self.extensions:
                root.append(extension.get_table_xml(False))

        return root

    def export(self, path: str) -> None:
        """Export Darwin Core Archive."""

        with tempfile.TemporaryDirectory() as tmpdir:

            with open(os.path.join(tmpdir, "meta.xml"), "w") as f:
                f.write(xml_to_string(self.get_meta_xml()))

            with open(os.path.join(tmpdir, "eml.xml"), "w") as f:
                if self.eml_text is not None:
                    f.write(self.eml_text)
                else:
                    f.write(xml_to_string(self.eml))

            core_filename = self.core.get_filename()
            with open(os.path.join(tmpdir, core_filename), "w") as f:
                self.core.write_tsv(f)

            for extension in self.extensions:
                extension_filename = extension.get_filename()
                with open(os.path.join(tmpdir, extension_filename), "w") as f:
                    extension.write_tsv(f)

            zip_file = ZipFile(path, "w")
            for root, dirs, files in os.walk(tmpdir):
                for file in files:
                    zip_file.write(os.path.join(root, file), arcname=file)

    def __str__(self):
        result = f"Archive with {'1' if self.core is not None else '0'} core tables and {len(self.extensions)} extension tables"
        if self.core is not None:
            result = result + "\n" + str(self.core)
        for extension in self.extensions:
            result = result + "\n" + str(extension)
        return result
