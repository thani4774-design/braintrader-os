"""Batch out-of-sample validation using one fixed indicator-score threshold."""

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

FIXED_MINIMUM_SCORE = 70
TRAIN_SHARE = 0.60


def download_data(symbol):
    """Download five years of daily price data for one symbol."""
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
    results = []

    for symbol in TEST_STOCKS:
        print(f"\nValidating {symbol}...")
        df = download_data(symbol)

        if df is None:
            print("No data available. Skipping.")
            continue

        split_index = int(len(df) * TRAIN_SHARE)
        test_df = df.iloc[split_index:].copy()

        if len(test_df) < 300:
            print("Not enough unseen data. Skipping.")
            continue

        trade_log_path = f"WalkForward_Test_Trades_{symbol.replace('.', '_')}.csv"
        result = run_backtest(
            test_df,
            minimum_indicator_score=FIXED_MINIMUM_SCORE,
            trade_log_path=trade_log_path,
        )

        results.append(
            {
                "Stock": symbol,
                "Minimum Score": FIXED_MINIMUM_SCORE,
                "Trades": result["Total Trades"],
                "Win Rate %": result["Win Rate"],
                "Net Profit %": result["Net Profit %"],
                "CAGR %": result["CAGR %"],
                "Profit Factor": result["Profit Factor"],
                "Max Drawdown %": result["Max Drawdown %"],
            }
        )

    if not results:
        print("\nNo out-of-sample results were produced.")
        return

    results_df = pd.DataFrame(results).sort_values(
        by="Net Profit %",
        ascending=False,
    )

    print("\n" + "=" * 84)
    print("BRAINTRADER FIXED-RULE OUT-OF-SAMPLE SUMMARY")
    print(f"Minimum indicator score: {FIXED_MINIMUM_SCORE}")
    print("=" * 84)
    print(results_df.to_string(index=False))

    profitable = (results_df["Net Profit %"] > 0).sum()
    total = len(results_df)
    print(f"\nPositive out-of-sample results: {profitable} of {total}")

    results_df.to_csv("WalkForward_Batch_Summary.csv", index=False)
    print("Saved: WalkForward_Batch_Summary.csv")


if __name__ == "__main__":
    main()
