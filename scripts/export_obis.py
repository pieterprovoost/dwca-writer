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

    # fetch metadata

    cur.execute(f"select eml_content from datasets where id = '{dataset_id}';")
    eml_text = cur.fetchone()[0]

    # create archive

    archive = Archive()
    table = Table(row_type="http://rs.tdwg.org/dwc/terms/Occurrence", data=df)
    archive.core = table
    archive.eml_text = eml_text

    # export

    archive.export(os.path.expanduser(f"~/Desktop/temp/export_{dataset_id}.zip"))

    # teardown

    cur.close()
    con.close()


export_dataset("afb23951-7a91-44f5-9c70-1c569bc7f996")
