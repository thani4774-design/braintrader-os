import pandas as pd
import yfinance as yf

from indicators import calculate_indicators
from backtest import run_backtest
from performance import print_performance
from equity_curve import plot_equity_curve


symbol = "INFY.NS"


print("=" * 50)
print("      BrainTrader Backtest")
print("=" * 50)


print("""
Select Backtest Period:

1. Maximum History
2. Last 20 Years
3. Last 15 Years
4. Last 10 Years
5. Last 5 Years
""")


choice = input("Enter choice: ")


if choice == "1":
    start_date = None

elif choice == "2":
    start_date = "2006-01-01"

elif choice == "3":
    start_date = "2011-01-01"

elif choice == "4":
    start_date = "2016-01-01"

elif choice == "5":
    start_date = "2021-01-01"

else:
    print("Invalid choice. Using maximum history.")
    start_date = None



df = yf.download(
    symbol,
    start=start_date,
    period="max" if start_date is None else None,
    auto_adjust=True,
    progress=False
)


print("Stock:", symbol)
print("Years of data:", round(len(df) / 252, 1))
print("Trading days:", len(df))



if isinstance(df.columns, pd.MultiIndex):
    df.columns = df.columns.get_level_values(0)



df = df.reset_index()


df = calculate_indicators(df)


result = run_backtest(df)


print_performance(result)


plot_equity_curve(result["Equity Curve"])