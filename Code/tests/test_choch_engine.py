import pandas as pd
import yfinance as yf

from indicators import calculate_indicators

from market_structure.swing_points import detect_swings
from market_structure.swing_classifier import classify_swings
from market_structure.swing_strength import calculate_swing_strength
from market_structure.swing_analysis import analyze_swings

from market_structure.choch_engine import detect_choch


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

swings = classify_swings(swings)

swings = calculate_swing_strength(swings)

swings = analyze_swings(swings)



choch = detect_choch(
    df,
    swings
)



print("\n========== CHoCH EVENTS ==========\n")

print(
    "Total CHoCH:",
    len(choch)
)


for event in choch:

    print(
        f"{str(event['date'])[:10]} | "
        f"{event['type']} | "
        f"Level: {round(event['level'],2)}"
    )