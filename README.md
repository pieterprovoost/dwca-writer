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
    "occurrenceID": [1, 2, 3],
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

core_table = Table(spec="https://rs.gbif.org/core/dwc_occurrence_2022-02-02.xml", data=df_core, id_index=0, only_mapped_columns=True)
archive.core = core_table

extension_table = Table(spec="https://rs.gbif.org/extension/dwc/measurements_or_facts_2022-02-02.xml", data=df_extension, id_index=0)
archive.extensions.append(extension_table)

print(archive)
```

```
Archive with 1 core tables and 1 extension tables
Table of type http://rs.tdwg.org/dwc/terms/Occurrence with 3 rows and 4 columns
  occurrenceID: http://rs.tdwg.org/dwc/terms/occurrenceID (column 1)
  scientificName: http://rs.tdwg.org/dwc/terms/scientificName (column 2)
  notes
  year: http://rs.tdwg.org/dwc/terms/year (column 3)
Table of type http://rs.tdwg.org/dwc/terms/MeasurementOrFact with 3 rows and 3 columns
  id (column 1)
  measurementType: http://rs.tdwg.org/dwc/terms/measurementType (column 2)
  measurementValue: http://rs.tdwg.org/dwc/terms/measurementValue (column 3)
```

```python
archive.export("dummy.zip")
```
