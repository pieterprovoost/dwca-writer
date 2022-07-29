from dwcawriter import Archive, Table
import os
import psycopg2
import psycopg2.extras
from dotenv.main import load_dotenv
import pandas as pd


d = {
    "scientificName": ["Abra alba", "Lanice conchilega", "Nereis diversicolor"],
    "notes": ["white", "brown", "green"],
    "year": [2008, 2009, 2010]
}
df = pd.DataFrame(data=d)
df.insert(0, "id", range(1, 1 + len(df)))

archive = Archive()
table = Table(row_type="http://rs.tdwg.org/dwc/terms/Occurrence", data=df, id_index=0)
archive.core = table
archive.eml_text = ""

archive.export(os.path.expanduser(f"~/Desktop/temp/dummy.zip"), only_mapped_columns=True)
