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

    archive.export(os.path.expanduser(f"~/Desktop/temp/{dataset_id}.zip"))

    # teardown

    cur.close()
    con.close()


for dataset_id in [
    "88e48126-685b-4322-abe8-325104362095",
    "4f2c5765-273b-4ac3-b046-dceeb3fe1a2b",
    "6cb505c3-d66d-4aa5-8feb-9e1d43d1ea69",
    "ed8963c7-f420-470a-b1ac-0358a1decc3e",
    "8632d5e1-8cba-45f5-a9b6-f40a43978b07",
    "e236b3f0-ea8c-42a9-b699-9ea9466e598c",
    "0393c368-5ef8-4dc2-8cf9-2d49e9117381",
    "cbf2f660-7224-4c6f-b889-716bb34dd86a",
    "afb23951-7a91-44f5-9c70-1c569bc7f996",
    "0766c909-9cd6-40da-9163-e3e6178ff983",
    "19311ebc-25a9-48fd-9146-f8bd4fceb3ed",
    "8f3521d1-1426-42a3-890f-420238cb3343",
    "a4f822c7-b89b-4fa7-b726-d9193728f85e",
    "5eadec64-9271-4b48-9595-f63bc2a228cf",
    "b981b947-e3bf-4369-b84b-ace7279427fd",
    "a159d264-575a-47fa-886d-46d69d47d0b2",
    "cbed8acb-c59f-428a-b25e-932b1a48af55",
    "4c4c6f67-9922-449d-9ee9-4a4daf166bfe",
    "865b16a2-ac9d-4919-95d1-c062ae84823a",
    "8fb2c5cc-d5cd-4c48-8248-75539f33116a",
    "fa68d11f-fc9d-4002-8caa-c9e62dd12f4f",
    "7096cbf5-0449-4981-bfac-4b670735af61",
    "777d9e3d-276c-4cc8-8d69-cc7cb2c782d1",
    "7dbfd861-f435-4089-9a4b-327fa1e5c1a9",
    "cf2ac646-ed51-493d-a254-993c11b97baf",
    "f7a69ece-9e1b-4203-b90a-ebcdf2bbde30",
    "deb2ab69-667a-4107-9c09-3456f91b2dc1",
    "7813e8a9-ff1e-4c1f-95ed-96e1411f4dd3",
    "222d85fd-d6fb-454b-baaf-2ab60906dab1",
    "dfeee5b2-a48e-4156-969f-669e87f3fb8b",
    "0b7e9ae4-6983-46c1-8f3f-16c0b3b56fc2",
    "b62013ef-2619-41ce-8471-f7551003226e",
    "2f225f89-ec58-4118-9389-589f1263436e",
    "af30b9a6-4b63-468d-be9d-c72fee8e9243",
    "9310a22d-a9bd-4183-b2a1-299e2e727c36",
    "b2e5b9e9-d668-486f-b909-fb5d621d0c61",
    "c7dc832f-8083-4622-b94b-2c12b9a1d1f7",
    "eeb6cbe0-b300-4394-b3ca-82b15649b69f",
    "b43f52af-ad41-4fe9-af3d-c1289d3d0372",
    "d60a4110-b7ee-4bee-855e-b0d1c070fd99",
    "c6e7b1fb-6fb6-43dc-b65a-357aa6ed3d3f",
    "763f35db-6944-46f4-8f47-1341a00e9796"
]:
    print(dataset_id)
    try:
        export_dataset(dataset_id)
    except:
        pass
