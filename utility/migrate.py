import sqlite3
from decimal import Decimal
from datetime import date, datetime

from db_models.database import get_connection

# --------------------------
# Connect to MySQL
# --------------------------

mysql_conn = get_connection()
mysql_cur = mysql_conn.cursor(dictionary=True)

# --------------------------
# Connect to SQLite
# --------------------------

sqlite_conn = sqlite3.connect("expense_tracker.db")
sqlite_conn.execute("PRAGMA foreign_keys = ON")
sqlite_cur = sqlite_conn.cursor()


def convert_value(value):
    """Convert MySQL types into SQLite compatible types."""

    if isinstance(value, Decimal):
        return float(value)
    
    if isinstance(value, datetime):
        return value.strftime("%Y-%m-%d %H:%M:%S")

    if isinstance(value, date):
        return value.strftime("%Y-%m-%d")

    return value


def migrate_table(table):

    print(f"\nMigrating {table}...")

    mysql_cur.execute(f"SELECT * FROM {table}")
    rows = mysql_cur.fetchall()

    if not rows:
        print("No data found.")
        return

    columns = list(rows[0].keys())

    column_names = ",".join(columns)
    placeholders = ",".join(["?"] * len(columns))

    query = f"""
        INSERT INTO {table}
        ({column_names})
        VALUES ({placeholders})
    """

    copied = 0

    for row in rows:

        values = [convert_value(v) for v in row.values()]

        try:
            sqlite_cur.execute(query, values)
            copied += 1

        except Exception as e:
            print(f"\nFailed while inserting into {table}")
            print(row)
            print(e)
            raise

    sqlite_conn.commit()

    print(f"{copied} rows copied.")


# --------------------------
# Run Migration
# --------------------------

try:

    # Order matters because of foreign keys

    # migrate_table("accounts")
    # migrate_table("transactions")
    # migrate_table("holdings")

    print("\nMigration completed successfully!")

finally:

    mysql_cur.close()
    mysql_conn.close()

    sqlite_cur.close()
    sqlite_conn.close()