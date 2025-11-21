import os
import sqlite3
from typing import List
from dotenv import load_dotenv
from alpaca.trading.client import TradingClient
from alpaca.trading.requests import GetAssetsRequest
from alpaca.trading.enums import AssetClass
from alpaca.trading.models import Asset

load_dotenv()

def populate_stocks():
    # set up db connection
    connection = sqlite3.connect(os.getenv("DB_PATH"))

    # set up trading client
    trading_client = TradingClient(os.getenv("ALPACA_API_KEY"), os.getenv("ALPACA_API_SECRET"), paper=True)
    search_params = GetAssetsRequest(asset_class=AssetClass.US_EQUITY)
    assets = trading_client.get_all_assets(search_params)

    # make each row an object
    connection.row_factory = sqlite3.Row 
    cursor = connection.cursor()

    def fetch_symbols(cursor: sqlite3.Cursor):
        # add only stocks that are new 
        cursor.execute(
            '''
            SELECT symbol, name FROM stock
            '''
        )

        # fetch all existing symbols
        rows = cursor.fetchall()
        existing_symbols = set([row['symbol'] for row in rows])

        return existing_symbols

    # add items to db
    def add_stocks(assets: List[Asset], cursor: sqlite3.Cursor):
        existing_symbols = fetch_symbols(cursor)

        for asset in assets:
            try:
                if asset.symbol not in existing_symbols:        
                    if asset.status == 'active' and asset.tradable:
                        print(f'New stock added: {asset.symbol}, {asset.name}, {asset.exchange}')
                        cursor.execute("INSERT INTO stock (symbol, name, exchange) VALUES (?, ?, ?)", (asset.symbol, asset.name, asset.exchange))
            except Exception as e:
                print(e)

    add_stocks(assets, cursor)

    connection.commit()
    connection.close()