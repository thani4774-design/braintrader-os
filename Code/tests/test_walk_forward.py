"""Walk-forward validation for the daily BrainTrader indicator strategy."""

import pandas as pd
import yfinance as yf

from backtest import run_backtest


CANDIDATE_SCORES = [60, 70, 80]
TRAIN_SHARE = 0.60


def download_data(symbol):
    """Download five years of daily price data."""
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
    stock = input("Stock symbol [SUNPHARMA.NS]: ").strip().upper() or "SUNPHARMA.NS"
    df = download_data(stock)

    if df is None:
        print("No price data available for", stock)
        return

    split_index = int(len(df) * TRAIN_SHARE)
    train_df = df.iloc[:split_index].copy()
    test_df = df.iloc[split_index:].copy()

    if len(train_df) < 300 or len(test_df) < 300:
        print("Not enough historical data for walk-forward validation.")
        return

    training_results = []

    for score in CANDIDATE_SCORES:
        result = run_backtest(
            train_df,
            minimum_indicator_score=score,
            trade_log_path=None,
        )
        training_results.append({"Minimum Score": score, **result})

    eligible_results = [
        result
        for result in training_results
        if result["Total Trades"] >= 10
    ]

    if not eligible_results:
        print("No training configuration produced enough trades.")
        return

    selected = max(
        eligible_results,
        key=lambda result: (result["Net Profit %"], result["Profit Factor"]),
    )

    selected_score = selected["Minimum Score"]
    test_trade_log = f"WalkForward_Test_Trades_{stock.replace('.', '_')}.csv"
    test_result = run_backtest(
        test_df,
        minimum_indicator_score=selected_score,
        trade_log_path=test_trade_log,
    )

    training_table = pd.DataFrame(
        [
            {
                "Minimum Score": result["Minimum Score"],
                "Trades": result["Total Trades"],
                "Net Profit %": result["Net Profit %"],
                "Profit Factor": result["Profit Factor"],
                "Max Drawdown %": result["Max Drawdown %"],
            }
            for result in training_results
        ]
    )

    print("\n" + "=" * 72)
    print("BRAINTRADER WALK-FORWARD VALIDATION")
    print(stock)
    print("=" * 72)
    print("\nTraining period: first 60% of downloaded history")
    print(training_table.to_string(index=False))

    print("\nSelected minimum indicator score:", selected_score)
    print("\nOut-of-sample test period: final 40% of downloaded history")
    print("Total Trades      :", test_result["Total Trades"])
    print("Win Rate          :", test_result["Win Rate"], "%")
    print("Net Profit        :", test_result["Net Profit %"], "%")
    print("CAGR              :", test_result["CAGR %"], "%")
    print("Profit Factor     :", test_result["Profit Factor"])
    print("Max Drawdown      :", test_result["Max Drawdown %"], "%")

    summary = pd.DataFrame(
        [
            {
                "Stock": stock,
                "Selected Minimum Score": selected_score,
                "Training Net Profit %": selected["Net Profit %"],
                "Test Net Profit %": test_result["Net Profit %"],
                "Test Profit Factor": test_result["Profit Factor"],
                "Test Max Drawdown %": test_result["Max Drawdown %"],
            }
        ]
    )
    summary.to_csv("WalkForward_Summary.csv", index=False)

    print("\nSaved: WalkForward_Summary.csv")
    print("Saved:", test_trade_log)


if __name__ == "__main__":
    main()
