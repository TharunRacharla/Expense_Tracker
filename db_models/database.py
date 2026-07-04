# from pathlib import Path
# import sys

# PROJECT_ROOT = Path(__file__).resolve().parents[1]
# if str(PROJECT_ROOT) not in sys.path:
#     sys.path.insert(0, str(PROJECT_ROOT))

# from config import DB_CONFIG

# import mysql.connector

# def get_connection():
#     return mysql.connector.connect(**DB_CONFIG)

import sqlite3

def get_connection():
    return sqlite3.connect("expense_tracker.db")