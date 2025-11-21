from datetime import datetime
from lumibot.backtesting import YahooDataBacktesting
from lumibot.strategies import Strategy

from datetime import datetime
from lumibot.backtesting import YahooDataBacktesting
from lumibot.strategies import Strategy

class buy_and_hold(Strategy):

    def initialize(self, ticker='AAPL'):
        self.ticker = ticker

    def on_trading_iteration(self):
        if self.first_iteration:
            price = self.get_last_price(self.ticker)
            quantity = self.get_portfolio_value() // price
            order = self.create_order(self.ticker, quantity, "buy")
            self.submit_order(order)

if __name__ == "__main__":
    backtesting_start = datetime(2020, 11, 1)
    backtesting_end = datetime(2020, 11, 5)

    result = buy_and_hold.backtest(
        datasource_class=YahooDataBacktesting,
        backtesting_start=backtesting_start,
        backtesting_end=backtesting_end,
        name="Buy and Hold",
        show_plot=False,
        show_tearsheet=False,
        parameters={
            "ticker": "MSFT"
        },
        save_logfile=False,
        save_stats_file=False,
        save_tearsheet=True
    )

    print(result)