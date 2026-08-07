"""
BrainTrader
------------------------
Support & Resistance Test
"""

import pandas as pd
import yfinance as yf

from indicators import calculate_indicators

from market_structure.swing_points import detect_swings
from market_structure.swing_classifier import classify_swings
from market_structure.swing_strength import calculate_swing_strength
from market_structure.swing_analysis import analyze_swings

from market_structure.support_resistance import (
    find_support_resistance,
    nearest_levels,
    strongest_support,
    strongest_resistance,
)


STOCK = "RELIANCE.NS"


df = yf.download(
    STOCK,
    period="2y",
    interval="1d",
    auto_adjust=True,
    progress=False,
)

if isinstance(df.columns, pd.MultiIndex):
    df.columns = df.columns.get_level_values(0)

df = df.reset_index()

df = calculate_indicators(df)

swings = detect_swings(df)
swings = classify_swings(swings)
swings = calculate_swing_strength(swings)
swings = analyze_swings(swings)

levels = find_support_resistance(swings)

current_price = float(df.iloc[-1]["Close"])

levels = nearest_levels(
    levels,
    current_price,
)

print()
print("=" * 60)
print("SUPPORT / RESISTANCE TEST")
print(STOCK)
print("=" * 60)

print("\nCurrent Price :", round(current_price, 2))

print("\nNearest Support    :", levels["nearest_support"])
print("Nearest Resistance :", levels["nearest_resistance"])

print("\nStrongest Support    :", strongest_support(levels))
print("Strongest Resistance :", strongest_resistance(levels))

print("\n==============================")
print("SUPPORT LEVELS")
print("==============================")

for level in levels["supports"]:

    strength = levels["support_strength"][level]

    print(
        f"{level:<10} Strength : {strength}"
    )

print("\n==============================")
print("RESISTANCE LEVELS")
print("==============================")

for level in levels["resistances"]:

    strength = levels["resistance_strength"][level]

    print(
        f"{level:<10} Strength : {strength}"
    )