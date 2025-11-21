import os
import sqlite3
from dotenv import load_dotenv
from datetime import datetime, timedelta
from alpaca.data.historical import StockHistoricalDataClient
from alpaca.data.requests import StockBarsRequest
from alpaca.data.timeframe import TimeFrame

load_dotenv()

def populate_prices():
    # set up db connection
    connection = sqlite3.connect(os.getenv("DB_PATH"))

    # set up data client
    client = StockHistoricalDataClient(os.getenv("ALPACA_API_KEY"), os.getenv("ALPACA_API_SECRET"))

    # make each row an object
    connection.row_factory = sqlite3.Row 
    cursor = connection.cursor()

    # get all current stocks
    cursor.execute(
        '''
        SELECT id, symbol, name FROM stock
        '''
    )

    rows = cursor.fetchall()

    # process rows
    symbols = []
    stock_dict = {}
    for row in rows:
        symbol = row['symbol']
        symbols.append(symbol)
        stock_dict[symbol] = row['id'] # map symbol to id

    # insert time data
    chunk_size = 200
    for i in range(0, len(symbols), chunk_size):
        symbol_chunk = symbols[i:i+chunk_size]

        # calculate dates for past 2 months
        end_date = datetime.now()
        start_date = end_date - timedelta(days=60)
        start_date = start_date.replace(hour=0, minute=0, second=0, microsecond=0)
        end_date = end_date.replace(hour=0, minute=0, second=0, microsecond=0)

        request_params = StockBarsRequest(
            symbol_or_symbols=symbol_chunk,
            timeframe=TimeFrame.Day,
            start=start_date, 
            end=end_date,
            feed="iex"      
        )

        bars = client.get_stock_bars(request_params).data

        for symbol in bars:
            print(f'processing {symbol}')

            for bar in bars[symbol]:
                stock_id = stock_dict[symbol]
                cursor.execute(
                    '''
                    INSERT INTO stock_price (stock_id, date, open, high, low, close, volume)
                    VALUES (?, ?, ?, ?, ?, ?, ?)
                    ''', (stock_id, bar.timestamp.date(), bar.open, bar.high, bar.low, bar.close, bar.volume)
                ) 

    connection.commit()
    connection.close()