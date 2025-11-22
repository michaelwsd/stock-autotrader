# Stock Analytica

## Overview
Stock Analytica is a web-based application designed to help users analyze stock data, apply trading strategies, and backtest their performance.

## Features
- **Stock List**: Browse and search for stocks with filtering options.
- **Stock Details**: View detailed information about a stock, including historical price data and charts.
- **Trading Strategies**: Apply predefined trading strategies such as Buy and Hold, SMA Crossover, and Opening Range Breakout.
- **Backtesting**: Run backtests on selected strategies and view performance metrics.

## Project Structure
```
app.db                     # SQLite database file
cron.log                   # Log file for cron jobs
main.py                    # Main application file
run_backtest.py            # Script to execute backtests
strategy/                  # Folder containing trading strategies
    buy_and_hold.py        # Buy and Hold strategy
    opening_range_breakout.py # Opening Range Breakout strategy
    sma_crossover.py       # SMA Crossover strategy
templates/                 # HTML templates for the web interface
    index.html             # Homepage template
    stock.html             # Stock details template
db/                        # Database setup and management scripts
logs/                      # Folder for storing backtest logs
```

## Installation
1. Clone the repository:
   ```bash
   git clone <repository-url>
   cd stock-analytica
   ```

2. Set up a Python virtual environment:
   ```bash
   python3 -m venv venv
   source venv/bin/activate
   ```

3. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```

4. Set up the database:
   ```bash
   python db/setup_db.py
   ```

6. Run the application:
   ```bash
   fastapi dev main.py
   ```

7. Open the app in your browser at [http://127.0.0.1:8000](http://127.0.0.1:8000).

## Usage
1. **Browse Stocks**: Navigate to the homepage to view a list of stocks. Use the search bar and filters to refine the list.
2. **View Stock Details**: Click on a stock to view its details, including historical price data and charts.
3. **Apply Strategies**: Select a strategy, choose a backtest period, and execute the strategy.
4. **Analyze Results**: View the backtest results, including performance metrics and trade details.

## Trading Strategies
- **Buy and Hold**: A simple strategy that buys a stock and holds it for the entire backtest period.
- **SMA Crossover**: A strategy based on the crossover of short-term and long-term simple moving averages.
- **Opening Range Breakout**: A strategy that trades based on the breakout of the opening range.

## Logs
Backtest logs and results are stored in the `logs/` directory. These include:
- Tearsheet HTML files
- Trade CSV files
- Performance metrics

## Preview
<img width="1148" height="899" alt="image" src="https://github.com/user-attachments/assets/e0715c68-6901-456c-b8d9-2d59b49ce992" />
<img width="1184" height="821" alt="image" src="https://github.com/user-attachments/assets/eb090238-58cd-42c4-8a3d-157327dcfecd" />
<img width="1060" height="902" alt="image" src="https://github.com/user-attachments/assets/f4aea4b4-d4f7-470c-9f83-88126b17bbe1" />

## Acknowledgments
- [Lumibot](https://github.com/Lumiwealth/lumibot): Used for backtesting and strategy implementation.
- [FastAPI](https://fastapi.tiangolo.com): Framework for building the web application.
- [SQLite](https://www.sqlite.org): Database for storing stock and price data.
