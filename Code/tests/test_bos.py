import pandas as pd
import yfinance as yf

from indicators import calculate_indicators
from market_structure.swing_points import detect_swings
from market_structure.swing_classifier import classify_swings
from market_structure.bos import detect_bos

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

bos_events = detect_bos(classified)

print("\n========== BOS EVENTS ==========\n")

print(f"Total BOS Events: {len(bos_events)}\n")

for bos in bos_events[:20]:
    print(
        f"{str(bos['date'])[:10]} | "
        f"{bos['direction']:8} | "
        f"{round(bos['price'],2)}"
    )