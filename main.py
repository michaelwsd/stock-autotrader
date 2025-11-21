import os, subprocess, json, tempfile
import sqlite3
from datetime import date, timedelta
from dotenv import load_dotenv
from typing import Annotated
from fastapi import FastAPI, Request, Form
from fastapi.responses import HTMLResponse
from fastapi.templating import Jinja2Templates

load_dotenv()

BACKTEST_RESULTS = {}

app = FastAPI()
templates = Jinja2Templates(directory="templates")

@app.get("/")
def index(request: Request, page: int = 1, per_page: int = 20):
    stock_filter = request.query_params.get("filter", "all")
    search_term = request.query_params.get("search", "").strip().upper()   
    stock_to_search = '%' + search_term + '%' if search_term else '%'

    connection = sqlite3.connect(os.getenv("DB_PATH"))
    connection.row_factory = sqlite3.Row
    cursor = connection.cursor()

    offset = (page - 1) * per_page
    yesterday = (date.today() - timedelta(days=2)).isoformat()

    # --- (1) Build BASE query ---
    if stock_filter == "new_closing_highs":
        base_query = f"""
            SELECT symbol, name, stock_id, max_close, date FROM (
                SELECT 
                    stock.symbol AS symbol,
                    stock.name AS name,
                    stock.id AS stock_id,
                    MAX(stock_price.close) AS max_close,
                    stock_price.date AS date
                FROM stock
                JOIN stock_price ON stock.id = stock_price.stock_id
                GROUP BY stock_id
            )
            WHERE date = ? AND symbol LIKE ?
        """
        params = (yesterday, stock_to_search)

    elif stock_filter == "new_closing_lows":
        base_query = f"""
            SELECT symbol, name, stock_id, min_close, date FROM (   
                SELECT 
                    stock.symbol AS symbol,
                    stock.name AS name,
                    stock.id AS stock_id,
                    MIN(stock_price.close) AS min_close,
                    stock_price.date AS date
                FROM stock
                JOIN stock_price ON stock.id = stock_price.stock_id
                GROUP BY stock_id
            )
            WHERE date = ? AND symbol LIKE ?
        """
        params = (yesterday, stock_to_search)
    
    else:
        # normal list
        base_query = "SELECT symbol, name FROM stock WHERE symbol LIKE ?"
        params = (stock_to_search,)

    # --- (2) Get total count based on filter ---
    count_query = f"SELECT COUNT(*) AS count FROM ({base_query})"
    cursor.execute(count_query, params)
    total_count = cursor.fetchone()["count"]

    # --- (3) Add pagination ---
    paginated_query = base_query + " ORDER BY symbol LIMIT ? OFFSET ?"
    paginated_params = params + (per_page, offset)

    cursor.execute(paginated_query, paginated_params)
    stocks = cursor.fetchall()

    connection.close()

    total_pages = (total_count + per_page - 1) // per_page

    return templates.TemplateResponse(
        "index.html",
        {
            "request": request,
            "stocks": stocks,
            "page": page,
            "per_page": per_page,
            "total_pages": total_pages
        }
    )

@app.get("/stock/{symbol}")
def get_stock_detail(request: Request, symbol):
    connection = sqlite3.connect(os.getenv("DB_PATH"))
    connection.row_factory = sqlite3.Row 
    cursor = connection.cursor()

    cursor.execute(
        '''
        SELECT * FROM strategy
        '''
    )

    strategies = cursor.fetchall()

    cursor.execute(
        '''
        SELECT id, symbol, name, exchange FROM stock where symbol = ?
        ''', (symbol,)
    )

    stock = cursor.fetchone()

    cursor.execute(
        '''
        SELECT * from stock_price where stock_id = ?
        ''', (stock['id'],)
    )

    prices = cursor.fetchall()

    connection.commit()
    connection.close()

    return templates.TemplateResponse( 
        request=request, 
        name="stock.html", 
        context={
                "request": request, 
                "stock": stock, 
                "prices": prices,
                "strategies": strategies
            }
    )

@app.post("/strategy")
def insert_strategy(strategy_id: Annotated[str, Form()], stock_id: Annotated[str, Form()], backtest_period: Annotated[str, Form()]):
    connection = sqlite3.connect(os.getenv("DB_PATH"))
    connection.row_factory = sqlite3.Row
    cursor = connection.cursor()

    # get stock symbol
    cursor.execute("SELECT symbol FROM stock WHERE id = ?", (stock_id,))
    symbol = cursor.fetchone()["symbol"]
    connection.close()

    # parse backtest period
    if backtest_period == "1m":
        backtest_period = '1'
    elif backtest_period == "3m":
        backtest_period = '3'
    elif backtest_period == "6m":
        backtest_period = '6'
    elif backtest_period == "1y":
        backtest_period = '12'

    # create temp file to store result
    tmp = tempfile.NamedTemporaryFile(delete=False, suffix=".html")
    tmp_path = tmp.name
    tmp.close()

    # run backtest in a SEPARATE PYTHON PROCESS
    subprocess.run([
        "python", "run_backtest.py", symbol, tmp_path, backtest_period, strategy_id
    ], check=True)

    with open(tmp_path) as f:
        html = f.read()

    return HTMLResponse(html)
