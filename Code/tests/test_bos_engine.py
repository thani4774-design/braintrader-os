import pandas as pd
import yfinance as yf

from indicators import calculate_indicators

from market_structure.swing_points import detect_swings
from market_structure.swing_classifier import classify_swings
from market_structure.swing_strength import calculate_swing_strength
from market_structure.swing_analysis import analyze_swings

from market_structure.bos_engine import detect_bos


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


# -------------------------
# Swing Pipeline
# -------------------------

swings = detect_swings(df)

swings = classify_swings(swings)

swings = calculate_swing_strength(swings)

swings = analyze_swings(swings)



# -------------------------
# BOS Detection
# -------------------------

bos_events = detect_bos(
    df,
    swings
)



print("\n========== BOS ENGINE ==========\n")


print(
    "Total BOS Events:",
    len(bos_events)
)


print("\n")


for event in bos_events[:30]:

    print(
        f"{str(event['date'])[:10]} | "
        f"{event['type']:8} | "
        f"Level: {round(event['level'],2)} | "
        f"Swing Strength: {event['strength']}% | "
        f"Confidence: {event['confidence']}%"
    )