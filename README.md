# dwca-writer

Python package for writing Darwin Core Archives (DwC-A).

## Installation

```
pip install dwca-writer
```

## Quick start

```python
from dwcawriter import Archive, Table
import os
import pandas as pd

df_core = pd.DataFrame(data={
    "id": [1, 2, 3],
    "scientificName": ["Abra alba", "Lanice conchilega", "Nereis diversicolor"],
    "notes": ["white", "brown", "green"],
    "year": [2008, 2009, 2010]
})

df_extension = pd.DataFrame(data={
    "id": [1, 2, 3],
    "measurementType": ["temperature", "temperature", "temperature"],
    "measurementValue": [12, 13, 14]
})

archive = Archive()
archive.eml_text = ""

core_table = Table(spec="https://rs.gbif.org/core/dwc_occurrence_2022-02-02.xml", data=df_core, id_index=0)
archive.core = core_table

extension_table = Table(spec="https://rs.gbif.org/extension/dwc/measurements_or_facts_2022-02-02.xml", data=df_extension, id_index=0)
archive.extensions.append(extension_table)

archive.export("dummy.zip", only_mapped_columns=True)
```
