import os
from datetime import datetime
from lumibot.backtesting import YahooDataBacktesting
from lumibot.strategies import Strategy
from lumibot.entities import Asset 

class DailyRangeBreakout(Strategy):

    def initialize(self, ticker="AAPL", risk_fraction=0.1):
        self.ticker = ticker
        self.asset = Asset(symbol=ticker) # Define Asset entity
        self.risk_fraction = risk_fraction

        self.prev_day_high = None
        self.prev_day_low = None
        self.entered_today = False
        
        # We need minute data to track intraday price movement, 
        # so we set the sleeptime to 1 minute
        self.sleeptime = "1M" 
        self.log_message(f"Strategy initialized for {self.ticker}")

    def before_market_opens(self):
        """
        Lumibot method that runs once per day before the market opens.
        This is the ideal place to reset daily flags and calculate the previous day's range.
        """
        # --- 1. Reset daily flags ---
        self.entered_today = False
        self.log_message("Daily flags reset.")

        # --- 2. Close any open position from the previous day ---
        pos = self.get_position(self.asset)
        if pos:
            self.log_message(f"Closing previous day's position: {pos.quantity} shares.")
            self.sell_all() # sell_all handles both long and short positions
        
        # --- 3. Calculate the Previous Day's Range (The ORB) ---
        # Fetch 2 daily bars: the last completed day (index 0) and the day before.
        # This can sometimes be tricky depending on the backtesting library's data cut-off.
        # Let's fetch the last two completed daily bars (2 days ago and 1 day ago).
        
        bars = self.get_historical_prices(self.asset, 2, "day")
        
        if bars is not None and len(bars.df) >= 2:
            # The second-to-last bar (index -2) is the *most recently completed* day.
            prev_day_bar = bars.df.iloc[-2]
            self.prev_day_high = prev_day_bar["high"]
            self.prev_day_low = prev_day_bar["low"]
            self.log_message(f"Previous Day's Range: High={self.prev_day_high:.2f}, Low={self.prev_day_low:.2f}")
        else:
            self.log_message("Could not retrieve enough historical data to set previous day's range.")
            self.prev_day_high = None
            self.prev_day_low = None

    def on_trading_iteration(self):
        """
        Lumibot method that runs on every minute bar (because self.sleeptime = "1M").
        This is where the live breakout is checked against the previous day's range.
        """
        current_dt = self.get_datetime()
        
        # --- 1. Pre-checks ---
        if self.prev_day_high is None or self.entered_today:
            return # Wait for range to be set or if trade already taken

        # --- 2. Check for Breakout ---
        # Get the current price (close of the latest minute bar)
        current_close = self.get_last_price(self.asset)

        if current_close is None:
            return

        # Breakout UP (Close above previous day's high)
        if current_close > self.prev_day_high:
            self.log_message(f"Long Breakout: Current Close {current_close:.2f} > Previous High {self.prev_day_high:.2f}")
            
            qty = self.calculate_order_quantity(current_close)
            
            # Use the previous day's low as the initial stop-loss
            stop_loss = self.prev_day_low
            
            if qty > 0:
                order = self.create_order(
                    self.asset, 
                    qty, 
                    'buy',
                    stop_loss_price=stop_loss
                )
                self.submit_order(order)
                self.entered_today = True

        # Breakout DOWN (Close below previous day's low)
        elif current_close < self.prev_day_low:
            self.log_message(f"Short Breakout: Current Close {current_close:.2f} < Previous Low {self.prev_day_low:.2f}")
            
            qty = self.calculate_order_quantity(current_close)
            
            # Use the previous day's high as the initial stop-loss
            stop_loss = self.prev_day_high
            
            # For a short trade, quantity must be negative
            if qty > 0:
                order = self.create_order(
                    self.asset, 
                    -qty, # Submit a negative quantity for a short order
                    'sell',
                    stop_loss_price=stop_loss
                )
                self.submit_order(order)
                self.entered_today = True

    # Position sizing helper (Uses the risk_fraction)
    def calculate_order_quantity(self, price):
        # A simple position sizing model: risk a fraction of the portfolio value
        portfolio_value = self.get_portfolio_value()
        risk_amount = portfolio_value * self.risk_fraction
        
        # Calculate maximum number of shares we can buy/sell
        qty = int(risk_amount // price) 
        
        return qty

# === BACKTEST ===
if __name__ == "__main__":
    dir = "logs"
    for filename in os.listdir(dir):
        file_path = os.path.join(dir, filename)
        if os.path.isfile(file_path):
            os.remove(file_path)
            
    # Backtest dates are kept. NOTE: Ensure ticker 'BBAI' has Yahoo data for this period.
    backtesting_start = datetime(2025, 8, 1)
    backtesting_end = datetime(2025, 10, 1)

    result = DailyRangeBreakout.backtest(
        datasource_class=YahooDataBacktesting,
        backtesting_start=backtesting_start,
        backtesting_end=backtesting_end,
        name="Daily Range Breakout",
        show_plot=True,
        show_tearsheet=True,
        parameters={
            "ticker": "TSLA",
            "risk_fraction": 0.8 # Using 10% risk, 1 is too high for margin/leverage safety
        }
    )