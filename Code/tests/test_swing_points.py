import pandas as pd
import yfinance as yf

from indicators import calculate_indicators
from market_structure.swing_points import detect_swings


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

print("\nSwing Points Found:", len(swings))

print("\nFirst 10 Swing Points:\n")

for swing in swings[:10]:
    print(swing)