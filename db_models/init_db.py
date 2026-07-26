from database import get_connection
from pathlib import Path

SQL_FILES = [
    'accounts.sql',
    'transactions.sql',
    'holdings.sql',
]

def initialize_database():
    conn = get_connection()
    cur = conn.cursor()

    sql_dir = Path(__file__).parent

    for file in SQL_FILES:
        with open(sql_dir/file, "r", encoding="utf-8") as f:
            cur.executescript(f.read())

    cur.close()
    conn.close()



