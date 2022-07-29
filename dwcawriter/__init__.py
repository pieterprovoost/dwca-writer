from typing import Dict, List
import pandas as pd
import xml.etree.ElementTree as ET
import requests
import xmltodict
import io
import tempfile
import os
from zipfile import ZipFile
import csv


def xml_to_string(root: ET.Element, encoding:str="UTF-8") -> str:
    """Dump an XML element to string."""

    tree = ET.ElementTree(root)
    ET.indent(tree, space="\t", level=0)
    return ET.tostring(tree.getroot()).decode(encoding)


def escape_character(input: str) -> str:
    """Escape a character for use in the table element attribute values."""

    return repr(input).replace("'", "") if input is not None else ""


class Table:

    def __init__(self, data: pd.DataFrame=None, is_core = True, row_type: str=None, id_index=None, encoding="UTF-8", fields_terminated_by="\t", lines_terminated_by="\n", fields_enclosed_by=None, ignore_header_lines=1):
        self.is_core = is_core
        self.row_type = row_type
        self.id_index = id_index
        self.data = data
        self.encoding = encoding
        self.fields_terminated_by = fields_terminated_by
        self.lines_terminated_by = lines_terminated_by
        self.fields_enclosed_by = fields_enclosed_by
        self.ignore_header_lines = ignore_header_lines
        self.dwc_fields = None

    def get_filename(self) -> str:
        """Generate a filename for this table."""

        return self.row_type.split("/")[-1].lower() + ".txt"

    def fetch_dwc_fields(self) -> Dict:
        """Populate a dictionary with all Darwin Core field names and URIs for this table."""

        if self.row_type == "http://rs.tdwg.org/dwc/terms/Occurrence":
            spec_url = "https://rs.gbif.org/core/dwc_occurrence_2022-02-02.xml"
        if spec_url is not None:
            res = requests.get(spec_url, timeout=30, verify=False)
            content = io.BytesIO(res.content)
            spec_json = xmltodict.parse(content)
            properties = { prop["@name"]: prop["@qualName"] for prop in spec_json["extension"]["property"] }
            self.dwc_fields = properties
        else:
            raise Exception(f"Row type {self.row_type} not supported")

    def get_dwc_fields(self) -> Dict:
        """Return a dictionary with all Darwin Core field names and URIs for this table, fetch if non populated."""

        if self.dwc_fields is None:
            self.fetch_dwc_fields()
        return self.dwc_fields

    def get_fields(self, only_mapped_columns: bool=False) -> List[Dict]:
        """Return a data structure listing all table fields, their mapping, and their index in the output file."""

        result = []
        index_output = 0

        for index, column in enumerate(self.data.columns):
            entry = {
                "name": column,
                "index_output": None,
                "uri": None
            }
            if column in self.get_dwc_fields() or index == self.id_index or only_mapped_columns == False:
                entry["index_output"] = index_output
                index_output = index_output + 1
            if column in self.get_dwc_fields():
                entry["uri"] = self.get_dwc_fields()[column]
            result.append(entry)

        return result

    def get_table_xml(self, only_mapped_columns: bool=False) -> ET.Element:
        """Generate the XML element for this table's entry in meta.xml."""

        root = ET.Element("core" if self.is_core else "extension", attrib=self.get_attributes())
        
        # files

        files = ET.SubElement(root, "files")
        location = ET.SubElement(files, "location")
        location.text = self.get_filename()

        # id / coreid

        if self.id_index is not None:
            if self.is_core:
                ET.SubElement(root, "id", attrib={"index": str(self.id_index)})
            else:
                ET.SubElement(root, "coreid", attrib={"index": str(self.id_index)})

        # field

        for field in self.get_fields(only_mapped_columns):
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

    def write_tsv(self, file, only_mapped_columns: bool=False) -> None:
        """Write the table to tsv."""

        exported_fields = [field["name"] for field in self.get_fields(only_mapped_columns) if field["index_output"] is not None]
        self.data.loc[:, exported_fields].to_csv(file, sep=self.fields_terminated_by, index=False, escapechar="\\", encoding=self.encoding, quoting=csv.QUOTE_MINIMAL if self.fields_enclosed_by is not None else csv.QUOTE_NONE, quotechar=self.fields_enclosed_by, line_terminator=self.lines_terminated_by)


class Archive:

    def __init__(self, eml: ET.Element=None, eml_text=None, core: Table=None, extensions: List[Table]=None):
        self.eml = eml
        self.eml_text = eml_text
        self.core = core
        self.extensions = extensions

    def get_meta_xml(self, only_mapped_columns: bool=False) -> ET.Element:
        """Return XML element for meta.xml."""

        root = ET.Element("archive", attrib={"xmlns": "http://rs.tdwg.org/dwc/text/", "metadata" : "eml.xml"})
        root.append(self.core.get_table_xml(only_mapped_columns))
        
        if self.extensions:
            for extension in self.extensions:
                root.append(extension.get_table_xml(only_mapped_columns))

        return root

    def export(self, path: str, only_mapped_columns: bool=False) -> None:
        """Export Darwin Core Archive."""

        with tempfile.TemporaryDirectory() as tmpdir:

            with open(os.path.join(tmpdir, "meta.xml"), "w") as f:
                f.write(xml_to_string(self.get_meta_xml(only_mapped_columns)))

            with open(os.path.join(tmpdir, "eml.xml"), "w") as f:
                if self.eml_text is not None:
                    f.write(self.eml_text)
                else:
                    f.write(xml_to_string(self.eml))

            core_filename = self.core.get_filename()
            with open(os.path.join(tmpdir, core_filename), "w") as f:
                self.core.write_tsv(f, only_mapped_columns)

            zip_file = ZipFile(path, "w")
            for root, dirs, files in os.walk(tmpdir):
                for file in files:
                    zip_file.write(os.path.join(root, file), arcname=file)
