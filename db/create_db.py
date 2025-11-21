import os
import sqlite3
from dotenv import load_dotenv

load_dotenv()

def create_db():
    connection = sqlite3.connect(os.getenv("DB_PATH"))

    cursor = connection.cursor()

    # stock table
    cursor.execute(
        '''
        CREATE TABLE IF NOT EXISTS stock (
            id INTEGER PRIMARY KEY,
            symbol TEXT NOT NULL,
            name TEXT NOT NULL,
            exchange TEXT NOT NULL
        )
        '''
    )

    # stock prices table
    cursor.execute(
        '''
        CREATE TABLE IF NOT EXISTS stock_price (
            id INTEGER PRIMARY KEY,
            stock_id INTEGER,
            date NOT NULL,
            open NOT NULL,
            high NOT NULL,
            low NOT NULL,
            close NOT NULL,
            volume NOT NULL,
            FOREIGN KEY (stock_id) REFERENCES stock (id)
        )
        '''
    )

    cursor.execute(
        '''
        CREATE TABLE IF NOT EXISTS strategy (
            id INTEGER PRIMARY KEY,
            name NOT NULL
        )
        '''
    )

    strategies = ['Buy and Hold', 'Opening Range Breakout', 'Bollinger Band', 'SMA Crossover']

    for strategy in strategies:
        cursor.execute(
            '''
            INSERT INTO strategy (name) VALUES (?)
            ''', (strategy,)
        )

    connection.commit()
    connection.close()  