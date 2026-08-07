import pandas as pd
import yfinance as yf

from indicators import calculate_indicators
from market_structure.swing_points import detect_swings
from market_structure.swing_classifier import classify_swings

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

classified = classify_swings(swings)

print("\n========== CLASSIFIED SWINGS ==========\n")

for swing in classified[:20]:

    print(
        f"{str(swing['date'])[:10]} | "
        f"{swing['type']:4} | "
        f"{swing['label']:11} | "
        f"{round(swing['price'],2)}"
    )