import pandas as pd
import yfinance as yf

from indicators import calculate_indicators
from market_structure.swing_points import detect_swings
from market_structure.swing_strength import calculate_swing_strength
from market_structure.swing_classifier import classify_swings
from market_structure.swing_analysis import analyze_swings


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

analysis = analyze_swings(swings)


print("\n========== SWING ANALYSIS ==========\n")


for swing in analysis[:25]:

    print(
        f"{str(swing['date'])[:10]} | "
        f"{swing['type']:4} | "
        f"{swing.get('label','-'):10} | "
        f"{round(swing['price'],2):8} | "
        f"{swing['strength']}% | "
        f"{swing['importance']}"
    )