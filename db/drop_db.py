import os
import sqlite3
from dotenv import load_dotenv

load_dotenv()

def drop_db():
    connection = sqlite3.connect(os.getenv("DB_PATH"))
    cursor = connection.cursor()

    cursor.execute("DROP TABLE IF EXISTS stock;")
    cursor.execute("DROP TABLE IF EXISTS stock_price;")
    cursor.execute("DROP TABLE IF EXISTS strategy;")

    connection.commit()
    connection.close()