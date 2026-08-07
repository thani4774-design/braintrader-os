import pandas as pd
import yfinance as yf

from indicators import calculate_indicators
from market_structure.swing_points import detect_swings
from market_structure.market_structure import detect_market_structure

print("Downloading data...")

df = yf.download(
    "INFY.NS",
    period="2y",
    auto_adjust=True,
    progress=False
)

if isinstance(df.columns, pd.MultiIndex):
    df.columns = df.columns.get_level_values(0)

df = df.reset_index()

df = calculate_indicators(df)

swings = detect_swings(df)

structure = detect_market_structure(swings)

print("\n========== MARKET STRUCTURE ==========")
print("Trend         :", structure["trend"])
print("Higher Highs  :", structure["higher_highs"])
print("Higher Lows   :", structure["higher_lows"])
print("Lower Highs   :", structure["lower_highs"])
print("Lower Lows    :", structure["lower_lows"])