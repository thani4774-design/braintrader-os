"""Run the daily indicator backtest across a standard BrainTrader stock basket."""

import pandas as pd
import yfinance as yf

from backtest import run_backtest


TEST_STOCKS = [
    "TCS.NS",
    "INFY.NS",
    "RELIANCE.NS",
    "HDFCBANK.NS",
    "ICICIBANK.NS",
    "SBIN.NS",
    "LT.NS",
    "BHARTIARTL.NS",
    "SUNPHARMA.NS",
    "TRENT.NS",
]


def download_data(symbol):
    """Download five years of daily data for one symbol."""
    try:
        df = yf.download(symbol, period="5y", auto_adjust=True, progress=False)
    except Exception:
        return None

    if df is None or df.empty:
        return None

    if isinstance(df.columns, pd.MultiIndex):
        df.columns = df.columns.get_level_values(0)

    return df.reset_index()


def main():
    summary = []

    for symbol in TEST_STOCKS:
        print(f"\nBacktesting {symbol}...")
        df = download_data(symbol)

        if df is None:
            print("No data available. Skipping.")
            continue

        trade_log_path = f"Backtest_Trades_{symbol.replace('.', '_')}.csv"
        result = run_backtest(df, trade_log_path=trade_log_path)

        summary.append(
            {
                "Stock": symbol,
                "Total Trades": result["Total Trades"],
                "Win Rate %": result["Win Rate"],
                "Net Profit %": result["Net Profit %"],
                "CAGR %": result["CAGR %"],
                "Profit Factor": result["Profit Factor"],
                "Max Drawdown %": result["Max Drawdown %"],
            }
        )

    if not summary:
        print("\nNo backtest results were produced.")
        return

    summary_df = pd.DataFrame(summary).sort_values(
        by="Net Profit %",
        ascending=False,
    )

    print("\n" + "=" * 72)
    print("BRAINTRADER BATCH BACKTEST SUMMARY")
    print("=" * 72)
    print(summary_df.to_string(index=False))

    summary_df.to_csv("Backtest_Summary.csv", index=False)
    print("\nSummary saved: Backtest_Summary.csv")


if __name__ == "__main__":
    main()
