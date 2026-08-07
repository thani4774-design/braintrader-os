"""Run the daily indicator strategy backtest for one Yahoo Finance symbol."""

import pandas as pd
import yfinance as yf

from backtest import run_backtest


def main():
    stock = input("Stock symbol [SUNPHARMA.NS]: ").strip().upper() or "SUNPHARMA.NS"

    try:
        df = yf.download(stock, period="5y", auto_adjust=True, progress=False)
    except Exception:
        print("Could not download price data.")
        return

    if df is None or df.empty:
        print("No price data available for", stock)
        return

    if isinstance(df.columns, pd.MultiIndex):
        df.columns = df.columns.get_level_values(0)

    result = run_backtest(df.reset_index())

    print("\n" + "=" * 60)
    print("BRAINTRADER DAILY INDICATOR BACKTEST")
    print(stock)
    print("=" * 60)

    for name, value in result.items():
        if name != "Equity Curve":
            print(f"{name:<22}: {value}")

    print("\nTrade log saved: Backtest_Trades.csv")


if __name__ == "__main__":
    main()
