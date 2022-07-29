from dwcawriter import Archive, Table
import os
import psycopg2
import psycopg2.extras
from dotenv.main import load_dotenv
import pandas as pd


load_dotenv()


def export_dataset(dataset_id: str) -> None:

    con = psycopg2.connect(
        "host='%s' dbname='%s' user='%s' password='%s' options='-c statement_timeout=%s'" %
        (os.getenv("DB_HOST"), os.getenv("DB_DB"), os.getenv("DB_USER"), os.getenv("DB_PASSWORD"), os.getenv("DB_TIMEOUT")))
    cur = con.cursor(cursor_factory=psycopg2.extras.DictCursor)

    # fetch occurrences

    cur.execute(f"select flat from occurrence where dataset_id = '{dataset_id}';")
    rows = [row[0] for row in cur.fetchall()]
    df = pd.DataFrame(rows)
    df.insert(0, "id", range(1, 1 + len(df)))

    # fetch metadata

    cur.execute(f"select eml_content from datasets where id = '{dataset_id}';")
    eml_text = cur.fetchone()[0]

    # create archive

    archive = Archive()
    table = Table(row_type="http://rs.tdwg.org/dwc/terms/Occurrence", data=df, id_index=0)
    archive.core = table
    archive.eml_text = eml_text

    # export

    archive.export(os.path.expanduser(f"~/Desktop/temp/{dataset_id}.zip"), only_mapped_columns=False)

    # teardown

    cur.close()
    con.close()


for dataset_id in [
    "4c3e6e4d-4c4c-4071-8057-1196d52c48c1"
]:
    print(dataset_id)
    export_dataset(dataset_id)
