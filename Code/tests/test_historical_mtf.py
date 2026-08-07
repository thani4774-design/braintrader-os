"""Test historical multi-timeframe analysis at the latest available date."""

import pandas as pd
import yfinance as yf

from historical_mtf_engine import analyze_historical_mtf


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

    df = df.reset_index()
    result = analyze_historical_mtf(df, df["Date"].iloc[-1])

    if result is None:
        print("Not enough history for complete MTF analysis.")
        return

    print("\n" + "=" * 60)
    print("HISTORICAL MTF ANALYSIS")
    print(stock)
    print("=" * 60)

    for name, timeframe in result["results"].items():
        print(f"{name:<12}: {timeframe['trend']}")

    print("\nMTF Score :", result["mtf_score"])
    print("Alignment :", result["alignment"]["alignment"], "%")


if __name__ == "__main__":
    main()
