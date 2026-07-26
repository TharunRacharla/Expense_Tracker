from pathlib import Path
import sqlite3

DB_PATH = Path(__file__).resolve().parents[1] / "expense_tracker.db"

def get_db_path():
    return DB_PATH

def get_connection(create_if_missing=True):
    mode = "rwc" if create_if_missing else "rw"
    uri = f"file:{DB_PATH}?mode={mode}"
    return sqlite3.connect(uri, uri=True)

