import os
import sys
import pytz
from datetime import datetime, timedelta
from dateutil.relativedelta import relativedelta
from lumibot.backtesting import YahooDataBacktesting
from strategy.buy_and_hold import buy_and_hold

symbol = sys.argv[1]
output_path = sys.argv[2]
duration = sys.argv[3]
strategy = sys.argv[4]

log_dir = "logs"

# clean up log folder
for filename in os.listdir(log_dir):
    file_path = os.path.join(log_dir, filename)
    if os.path.isfile(file_path):
        os.remove(file_path)

# run backtest
ny_tz = pytz.timezone("America/New_York")
# Current time in NY
now_ny = datetime.now(ny_tz)

# Use yesterday as the safe backtest end date
yesterday_ny = now_ny.date() - timedelta(days=1)
end = ny_tz.localize(datetime(yesterday_ny.year, yesterday_ny.month, yesterday_ny.day))
start = end - relativedelta(months=int(duration)) if duration != 'ytd' else datetime(end.year, 1, 1) 

if strategy == '1':
    buy_and_hold.backtest(
            datasource_class=YahooDataBacktesting,
            backtesting_start=start,
            backtesting_end=end,
            name=f"Buy and Hold {symbol}",
            show_plot=False,
            show_tearsheet=False,
            parameters={
                "ticker": symbol
            },
            save_logfile=False,
            save_stats_file=False,
            save_tearsheet=True
        )

# find the generated tearsheet file
html_files = [
    os.path.join(log_dir, f)
    for f in os.listdir(log_dir)
    if f.endswith(".html")
]

# write to temp file
with open(html_files[0], "r") as src:
    html_content = src.read()

with open(output_path, "w") as f:
    f.write(html_content)
