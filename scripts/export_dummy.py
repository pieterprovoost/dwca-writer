from dwcawriter import Archive, Table
import os
import pandas as pd


data_core = {
    "occurrenceID": [1, 2, 3],
    "scientificName": ["Abra alba", "Lanice conchilega", "Nereis diversicolor"],
    "notes": ["white", "brown", "green"],
    "year": [2008, 2009, 2010]
}
df_core = pd.DataFrame(data=data_core)

data_extension = {
    "id": [1, 2, 3],
    "measurementType": ["temperature", "temperature", "temperature"],
    "measurementValue": [12, 13, 14]
}
df_extension = pd.DataFrame(data=data_extension)

archive = Archive()
core_table = Table(spec="https://rs.gbif.org/core/dwc_occurrence_2022-02-02.xml", data=df_core, id_index=0, only_mapped_columns=True)
core_table.add_id()
archive.core = core_table
extension_table = Table(spec="https://rs.gbif.org/extension/dwc/measurements_or_facts_2022-02-02.xml", data=df_extension, id_index=0)
archive.extensions.append(extension_table)

print(archive)

archive.eml_text = """<?xml version="1.0" encoding="UTF-8"?>
<ns0:eml xmlns:ns0="eml://ecoinformatics.org/eml-2.1.1" packageId="http://ipt.vliz.be/kmfri/resource?id=vegetation_gazi_bay_kenya_1987/v1.0" scope="system" system="http://gbif.org" xml:lang="eng">
  <dataset>
    <alternateIdentifier>http://ipt.vliz.be/kmfri/resource?id=vegetation_gazi_bay_kenya_1987/v1.0</alternateIdentifier>
    <title>Test dataset</title>
    <ns0:creator>
      <individualName>
        <ns0:givenName>John</ns0:givenName>
        <ns0:surName>Doe</ns0:surName>
      </individualName>
    </ns0:creator>
    <abstract>
      <para>Suspendisse imperdiet imperdiet leo, at eleifend nisi rutrum eget. Donec aliquam mollis risus, feugiat laoreet nulla facilisis vel. Fusce viverra magna ante, ut lobortis sapien convallis ut. Nulla facilisi. Cras at tellus leo. Suspendisse eget blandit tellus. Duis auctor turpis eros. Nullam convallis ligula eleifend volutpat aliquam. Donec cursus mattis viverra. Nunc ac lorem vel lectus malesuada bibendum. Vestibulum non dolor quis enim auctor consectetur in a augue. Maecenas sodales ullamcorper quam.</para>
    </abstract>
    <keywordSet>
      <ns0:keyword>test keyword</ns0:keyword>
    </keywordSet>
    <intellectualRights>
      <para>This work is licensed under a <ns0:ulink url="http://creativecommons.org/licenses/by/4.0/legalcode">Creative Commons Attribution (CC-BY) 4.0 License</ns0:ulink>.</para>
    </intellectualRights>
  </dataset>
</ns0:eml>"""

archive.export(os.path.expanduser(f"~/Desktop/temp/dummy.zip"))
