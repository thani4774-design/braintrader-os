"""Walk-forward validation for the historical BrainTrader MTF strategy."""

import pandas as pd
import yfinance as yf

from historical_mtf_backtest import run_historical_mtf_backtest


TRAIN_SHARE = 0.60


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
    split_index = int(len(df) * TRAIN_SHARE)
    split_date = df["Date"].iloc[split_index]

    print("\nRunning training-period MTF backtest...")
    training = run_historical_mtf_backtest(
        df,
        end_date=split_date,
        trade_log_path=None,
    )

    test_log_path = f"Historical_MTF_Test_Trades_{stock.replace('.', '_')}.csv"
    print("Running unseen-period MTF backtest...")
    testing = run_historical_mtf_backtest(
        df,
        start_date=split_date,
        trade_log_path=test_log_path,
    )

    comparison = pd.DataFrame(
        [
            {
                "Period": "Training (first 60%)",
                "Start": training["Evaluation Start"],
                "End": training["Evaluation End"],
                "Trades": training["Total Trades"],
                "Net Profit %": training["Net Profit %"],
                "CAGR %": training["CAGR %"],
                "Profit Factor": training["Profit Factor"],
                "Max Drawdown %": training["Max Drawdown %"],
            },
            {
                "Period": "Unseen test (final 40%)",
                "Start": testing["Evaluation Start"],
                "End": testing["Evaluation End"],
                "Trades": testing["Total Trades"],
                "Net Profit %": testing["Net Profit %"],
                "CAGR %": testing["CAGR %"],
                "Profit Factor": testing["Profit Factor"],
                "Max Drawdown %": testing["Max Drawdown %"],
            },
        ]
    )

    print("\n" + "=" * 90)
    print("BRAINTRADER HISTORICAL MTF WALK-FORWARD VALIDATION")
    print(stock)
    print("=" * 90)
    print(comparison.to_string(index=False))

    comparison.to_csv("Historical_MTF_WalkForward_Summary.csv", index=False)
    print("\nSaved: Historical_MTF_WalkForward_Summary.csv")
    print("Saved:", test_log_path)


if __name__ == "__main__":
    main()
