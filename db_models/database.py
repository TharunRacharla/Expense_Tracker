from config import DB_CONFIG

import mysql.connector

def get_connection():
    return mysql.connector.connect(**DB_CONFIG)