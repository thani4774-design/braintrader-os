"""Run the complete historical MTF BrainTrader backtest for one stock."""

import pandas as pd
import yfinance as yf

from historical_mtf_backtest import run_historical_mtf_backtest


def main():
    stock = input("Stock symbol [SUNPHARMA.NS]: ").strip().upper() or "SUNPHARMA.NS"

    try:
        df = yf.download(stock, period="max", auto_adjust=True, progress=False)
    except Exception:
        print("Could not download price data.")
        return

    if df is None or df.empty:
        print("No price data available for", stock)
        return

    if isinstance(df.columns, pd.MultiIndex):
        df.columns = df.columns.get_level_values(0)

    trade_log_path = f"Historical_MTF_Trades_{stock.replace('.', '_')}.csv"
    result = run_historical_mtf_backtest(
        df.reset_index(),
        trade_log_path=trade_log_path,
    )

    print("\n" + "=" * 64)
    print("BRAINTRADER HISTORICAL MTF BACKTEST")
    print(stock)
    print("=" * 64)

    for name, value in result.items():
        if name != "Equity Curve":
            print(f"{name:<22}: {value}")

    print("\nTrade log saved:", trade_log_path)


if __name__ == "__main__":
    main()
