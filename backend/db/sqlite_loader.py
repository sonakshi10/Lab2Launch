import pandas as pd
import sqlalchemy
from app.config import SQLITE_DB_PATH

def load_sheets_to_sqlite(google_sheets_url):
    spreadsheet_id = google_sheets_url.split("/d/")[1].split("/")[0]
    export_url = f"https://docs.google.com/spreadsheets/d/{spreadsheet_id}/export?format=xlsx"

    all_sheets = pd.read_excel(export_url, sheet_name=None)

    engine = sqlalchemy.create_engine(f"sqlite:///{SQLITE_DB_PATH}")

    for sheet_name, df in all_sheets.items():
        if sheet_name != "Rules":
            df.to_sql(sheet_name, engine, index=False, if_exists="replace")

    return list(all_sheets.keys())