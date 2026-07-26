from pathlib import Path
from db_models.database import get_connection

SQL_FILES = [
    "accounts.sql",
    "transactions.sql",
    "holdings.sql",
]

def initialize_database():
    conn = get_connection()
    cur = conn.cursor()

    sql_dir = Path(__file__).parent

    print(f"Loading SQL from: {sql_dir}")

    for file in SQL_FILES:
        path = sql_dir / file
        print(f"Executing {path}")

        with open(path, encoding="utf-8") as f:
            cur.executescript(f.read())

    conn.commit()

    cur.execute("""
        SELECT name
        FROM sqlite_master
        WHERE type='table'
    """)

    print(cur.fetchall())

    conn.close()