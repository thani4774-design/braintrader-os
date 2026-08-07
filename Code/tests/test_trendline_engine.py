"""
BrainTrader
------------------------
Trendline Engine Test
"""

import pandas as pd
import yfinance as yf

from indicators import calculate_indicators

from market_structure.swing_points import detect_swings
from market_structure.swing_classifier import classify_swings
from market_structure.swing_strength import calculate_swing_strength
from market_structure.swing_analysis import analyze_swings

from market_structure.trendline_engine import detect_trendlines


STOCK = "RELIANCE.NS"


df = yf.download(
    STOCK,
    period="2y",
    interval="1d",
    auto_adjust=True,
    progress=False,
)

if df.empty:
    print("No data.")
    raise SystemExit

if isinstance(df.columns, pd.MultiIndex):
    df.columns = df.columns.get_level_values(0)

df = df.reset_index()

df = calculate_indicators(df)

swings = detect_swings(df)
swings = classify_swings(swings)
swings = calculate_swing_strength(swings)
swings = analyze_swings(swings)

trendlines = detect_trendlines(swings)

print()
print("=" * 60)
print("TRENDLINE ENGINE TEST")
print(STOCK)
print("=" * 60)


def print_trendline(title, trendline):

    print()

    if trendline is None:
        print(f"No {title}")
        return

    print(title)

    print(
        "Direction  :",
        trendline["direction"]
    )

    print(
        "Start      :",
        round(
            trendline["start"]["price"],
            2
        )
    )

    print(
        "End        :",
        round(
            trendline["end"]["price"],
            2
        )
    )

    print(
        "Touches    :",
        trendline["touches"]
    )

    print(
        "Strength   :",
        trendline["strength"]
    )

    print(
        "Confidence :",
        trendline["confidence"],
        "%"
    )


print_trendline(
    "Ascending Trendline",
    trendlines["uptrend"]
)

print_trendline(
    "Descending Trendline",
    trendlines["downtrend"]
)