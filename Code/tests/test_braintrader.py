import pandas as pd
import yfinance as yf

from indicators import calculate_indicators
from indicator_confirmation import indicator_confirmation
from multi_timeframe_structure import analyze_timeframe
from mtf_score_engine import calculate_mtf_score
from market_structure.mtf_decision_engine import calculate_alignment, generate_reason
from recommendation_engine import create_recommendation


TEST_STOCKS = [
    "RELIANCE.NS",
    "HDFCBANK.NS",
    "ICICIBANK.NS",
    "SBIN.NS",
    "LT.NS",
    "BHARTIARTL.NS",
    "SUNPHARMA.NS",
    "TATAMOTORS.NS",
    "TRENT.NS",
    "INFY.NS",
]


TIMEFRAMES = {
    "MACRO_15Y": ("15y", "1mo"),
    "MAJOR_5Y": ("5y", "1wk"),
    "CURRENT_2Y": ("2y", "1d"),
    "ENTRY_6M": ("6mo", "1d"),
}


def download_indicator_data(stock):
    """Download and prepare the daily data required by the indicator engine."""
    try:
        df = yf.download(
            stock,
            period="2y",
            auto_adjust=True,
            progress=False,
        )
    except Exception:
        return None

    if df is None or df.empty:
        return None

    if isinstance(df.columns, pd.MultiIndex):
        df.columns = df.columns.get_level_values(0)

    return df.reset_index()


for stock in TEST_STOCKS:
    print()
    print("=" * 70)
    print(stock)
    print("=" * 70)

    results = {}

    for name, (period, interval) in TIMEFRAMES.items():
        results[name] = analyze_timeframe(stock, period, interval)

    if not all(results.values()):
        print("No complete multi-timeframe data available. Skipping.")
        continue

    df = download_indicator_data(stock)

    if df is None:
        print("No indicator data available. Skipping.")
        continue

    mtf_score = calculate_mtf_score(results)
    alignment = calculate_alignment(results)

    df = calculate_indicators(df)
    indicator = indicator_confirmation(df)

    latest = df.iloc[-1]
    recommendation = create_recommendation(
        stock=stock,
        price=float(latest["Close"]),
        mtf_score=mtf_score,
        alignment=alignment["alignment"],
        indicator_score=indicator["score"],
        atr=float(latest["ATR"]),
        reasons=generate_reason(results),
    )

    print()
    print("MTF Score       :", recommendation["MTF Score"])
    print("Indicator Score :", recommendation["Indicator Score"])
    print("Final Score     :", recommendation["Final Score"])
    print("Alignment       :", recommendation["Alignment"], "%")
    print("Decision        :", recommendation["Decision"])

    if recommendation["Stop Loss"] is not None:
        print("Entry           :", recommendation["Entry"])
        print("Stop Loss       :", recommendation["Stop Loss"])
        print("Target          :", recommendation["Target"])

    print("\nReasons")
    for reason in recommendation["Reasons"]:
        print("-", reason)

    print("\nIndicator Details")
    for name, status in indicator["details"].items():
        label = "PASS" if status else "FAIL"
        print(f"- {name}: {label}")
