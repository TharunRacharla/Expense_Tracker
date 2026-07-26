from pathlib import Path
from db_models.database import get_connection, get_db_path

SQL_FILES = [
    "accounts.sql",
    "transactions.sql",
    "holdings.sql",
]

def initialize_database():
    db_path = get_db_path()
    if db_path.exists():
        print(f"Database already exists at: {db_path}")
        print("Skipping initialization to avoid modifying an existing database file.")
        return

    conn = get_connection(create_if_missing=True)
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