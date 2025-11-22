import os
from datetime import datetime
from lumibot.backtesting import YahooDataBacktesting
from lumibot.strategies import Strategy
from lumibot.entities import Asset

class SMACrossover(Strategy):

    def initialize(self, ticker="AAPL", fast_period=50, slow_period=200):
        # Initialize parameters
        self.ticker = ticker
        self.asset = Asset(symbol=ticker)
        self.fast_period = fast_period
        self.slow_period = slow_period
        
        # Set sleeptime to "1D" since we are using daily moving averages
        self.sleeptime = "1D" 
        
        self.log_message(f"SMA Crossover initialized for {self.ticker} with Fast Period={self.fast_period} and Slow Period={self.slow_period}.")

    def on_trading_iteration(self):
        current_dt = self.get_datetime()
        self.log_message(f"Current time: {current_dt}")

        # --- 1. Get Historical Data ---
        # We need enough days to calculate both SMAs (max period + 1 for the current bar)
        # We fetch the close price for the total required length.
        try:
            bars = self.get_historical_prices(self.asset, self.slow_period + 1, "day")
            
            if bars is None or len(bars.df) < self.slow_period:
                self.log_message("Not enough data to calculate SMAs.", "warning")
                return
            
            close_prices = bars.df["close"]

        except Exception as e:
            self.log_message(f"Error fetching data: {e}", "error")
            return

        # --- 2. Calculate SMAs ---
        # Calculate the Simple Moving Averages
        fast_sma = close_prices.iloc[-(self.fast_period):].mean()
        slow_sma = close_prices.iloc[-(self.slow_period):].mean()

        # Check if we have valid SMA values
        if not fast_sma or not slow_sma:
            return

        self.log_message(f"Fast SMA ({self.fast_period} days): {fast_sma:.2f}")
        self.log_message(f"Slow SMA ({self.slow_period} days): {slow_sma:.2f}")

        # --- 3. Check for Position and Signal ---
        
        # Get current position
        pos = self.get_position(self.asset)
        
        # Determine the signal from the most recent closing price
        # To check for a *crossover*, we should compare the current relationship
        # with the previous one. However, for simplicity and robustness in backtesting,
        # we often use the current position relative to the crossover as the entry/exit trigger.
        
        # Strategy: Go long if fast SMA > slow SMA; Exit/Go flat if fast SMA < slow SMA.

        # --- Buy Signal (Fast SMA > Slow SMA) ---
        if fast_sma > slow_sma:
            if pos is None:
                # Entry: If we don't have a position, buy!
                quantity = self.get_target_quantity(close_prices.iloc[-1])
                if quantity > 0:
                    self.log_message(f"BUY signal: Fast SMA > Slow SMA. Purchasing {quantity} shares.")
                    order = self.create_order(self.asset, quantity, 'buy')
                    self.submit_order(order)
            elif pos.quantity < 0:
                # Exit Short/Reverse: We are short but should be long. Close short position.
                self.log_message("Closing short position on BUY signal.")
                self.sell_all()

        # --- Sell Signal (Fast SMA < Slow SMA) ---
        elif fast_sma < slow_sma:
            if pos is not None and pos.quantity > 0:
                # Exit: If we are long, sell to exit the position (go flat).
                self.log_message("SELL signal: Fast SMA < Slow SMA. Selling all long shares.")
                self.sell_all()
            elif pos is None:
                # Optional: Uncomment the following lines if you want to short the asset on a death cross.
                # quantity = self.get_target_quantity(close_prices.iloc[-1])
                # if quantity > 0:
                #     self.log_message(f"SHORT signal: Fast SMA < Slow SMA. Shorting {quantity} shares.")
                #     self.sell(self.asset, quantity)
                pass # Default: Just stay flat if not long

    def get_target_quantity(self, price):
        """Calculates a simple quantity based on a fixed percentage of portfolio value."""
        # Risk 10% of portfolio value per trade for simplicity
        allocation_fraction = 0.8
        portfolio_value = self.get_portfolio_value()
        target_allocation = portfolio_value * allocation_fraction
        
        if price > 0:
            qty = int(target_allocation // price)
            return max(qty, 1) # Ensure at least 1 share is bought
        return 0

# --- BACKTEST EXECUTION ---
if __name__ == "__main__":
    dir = "logs"
    for filename in os.listdir(dir):
        file_path = os.path.join(dir, filename)
        if os.path.isfile(file_path):
            os.remove(file_path)

    backtesting_start = datetime(2023, 1, 1)
    backtesting_end = datetime(2025, 11, 1)

    result = SMACrossover.backtest(
        datasource_class=YahooDataBacktesting,
        backtesting_start=backtesting_start,
        backtesting_end=backtesting_end,
        name="SMA Crossover (50/200)",
        show_plot=True,
        show_tearsheet=True,
        save_logfile=True,
        parameters={
            "ticker": "TSLA", # Using a highly liquid ETF for a long-term strategy
            "fast_period": 50,
            "slow_period": 200,
        }
    )

    print(result)