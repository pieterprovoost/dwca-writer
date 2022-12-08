from typing import List
import xml.etree.ElementTree as ET
import tempfile
import os
from zipfile import ZipFile
from dwcawriter.table import Table
import pandas as pd


def xml_to_string(root: ET.Element, encoding: str = "UTF-8") -> str:
    """Dump an XML element to string."""

    tree = ET.ElementTree(root)
    ET.indent(tree, space="\t", level=0)
    return ET.tostring(tree.getroot()).decode(encoding)


class Archive:

    def __init__(self, eml: ET.Element = None, eml_text=None, core: Table = None, extensions: List[Table] = None):
        self.eml = eml
        self.eml_text = eml_text
        self.core = core
        self.extensions = extensions if extensions is not None else []

    def get_meta_xml(self) -> ET.Element:
        """Return XML element for meta.xml."""

        root = ET.Element("archive", attrib={"xmlns": "http://rs.tdwg.org/dwc/text/", "metadata": "eml.xml"})
        root.append(self.core.get_table_xml(True))

        if self.extensions:
            for extension in self.extensions:
                root.append(extension.get_table_xml(False))

        return root

    def merge(self, other: "Archive"):

        if self.core.spec != other.core.spec:
            raise Exception("Core types do not match")
        self.core.data = pd.concat([self.core.data, other.core.data])

        for extension in other.extensions:
            merged = False
            for existing_extension in self.extensions:
                if extension.spec == existing_extension.spec:
                    existing_extension.data = pd.concat([existing_extension.data, extension.data])
                    merged = True
                    break
            if not merged:
                self.extensions.append(extension)

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
