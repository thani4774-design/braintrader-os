"""
BrainTrader V2
------------------------
Test:
    Pattern Recognition Engine
"""

import yfinance as yf
import pandas as pd


from indicators.indicators import calculate_indicators
from market_structure.swing_points import detect_swings
from patterns.pattern_engine import detect_patterns



# =====================================
# Download Stock Data
# =====================================

symbol = "INFY.NS"

print("\nDownloading data:", symbol)


df = yf.download(
    symbol,
    period="5y",
    auto_adjust=True,
    progress=False
)


if isinstance(df.columns, pd.MultiIndex):
    df.columns = df.columns.get_level_values(0)


df = df.reset_index()



# =====================================
# Indicators
# =====================================

df = calculate_indicators(df)



# =====================================
# Swing Detection
# =====================================

swings = detect_swings(df)
print(type(swings))
print(type(swings[0]))
print(swings[0])


print("\nSwing Points Detected:")
print(len(swings))



# =====================================
# Pattern Detection
# =====================================

patterns = detect_patterns(swings)



print("\n==============================")
print("Pattern Detection Report")
print("==============================")



if len(patterns) == 0:

    print("No patterns detected")


else:

    for pattern in patterns:

        print("\nPattern:",
              pattern["pattern"])

        print("Direction:",
              pattern["direction"])

        print("Confidence:",
              pattern["confidence"])



print("\nTotal Patterns Found:",
      len(patterns))