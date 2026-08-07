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

print("\n========== SWING QUALITY REPORT ==========\n")

print("Total Swings:", len(swings))

highs = sum(1 for s in swings if s["type"] == "HIGH")
lows = sum(1 for s in swings if s["type"] == "LOW")

print("Swing Highs :", highs)
print("Swing Lows  :", lows)

consecutive_highs = 0
consecutive_lows = 0

for i in range(1, len(swings)):

    if (
        swings[i]["type"] == "HIGH"
        and
        swings[i-1]["type"] == "HIGH"
    ):
        consecutive_highs += 1

    if (
        swings[i]["type"] == "LOW"
        and
        swings[i-1]["type"] == "LOW"
    ):
        consecutive_lows += 1

print("\nConsecutive HIGHs :", consecutive_highs)
print("Consecutive LOWs  :", consecutive_lows)

print("\nFirst 20 Swings:\n")

for swing in swings[:20]:
    print(
        f"{str(swing['date'])[:10]} | "
        f"{swing['type']:4} | "
        f"{round(swing['price'],2)}"
    )