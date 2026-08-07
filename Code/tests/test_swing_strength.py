import pandas as pd
import yfinance as yf

from indicators import calculate_indicators
from market_structure.swing_points import detect_swings
from market_structure.swing_strength import calculate_swing_strength


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


strength_swings = calculate_swing_strength(swings)


print("\n========== SWING STRENGTH ==========\n")


print("Total Swings:", len(strength_swings))


print("\nFirst 20 Swings:\n")


for swing in strength_swings[:20]:

    print(
        f"{str(swing['date'])[:10]} | "
        f"{swing['type']:4} | "
        f"{round(swing['price'],2):8} | "
        f"Strength: {swing['strength']}%"
    )