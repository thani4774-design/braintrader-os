"""
BrainTrader
------------------------
Candlestick Pattern Test
"""

import pandas as pd
import yfinance as yf

from market_structure.candlestick_patterns import detect_patterns


STOCK = "RELIANCE.NS"


df = yf.download(
    STOCK,
    period="6mo",
    interval="1d",
    auto_adjust=True,
    progress=False,
)

if df.empty:
    print("No data downloaded.")
    raise SystemExit

if isinstance(df.columns, pd.MultiIndex):
    df.columns = df.columns.get_level_values(0)

df = df.reset_index()

result = detect_patterns(df)

print()
print("=" * 60)
print("CANDLESTICK PATTERN TEST")
print(STOCK)
print("=" * 60)

print("\nDetected Patterns")

if result["patterns"]:
    for pattern in result["patterns"]:
        print("-", pattern)
else:
    print("No major candlestick patterns detected.")

print("\nBullish Signal :", result["bullish"])
print("Bearish Signal :", result["bearish"])