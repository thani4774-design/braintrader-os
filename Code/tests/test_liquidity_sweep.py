"""
BrainTrader
------------------------
Liquidity Zone Test V3
"""


import pandas as pd
import yfinance as yf


from indicators import calculate_indicators

from market_structure.swing_points import detect_swings
from market_structure.swing_classifier import classify_swings
from market_structure.swing_strength import calculate_swing_strength
from market_structure.swing_analysis import analyze_swings

from market_structure.liquidity_sweep import detect_liquidity_sweeps



STOCK = "RELIANCE.NS"



df = yf.download(
    STOCK,
    period="2y",
    interval="1d",
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



zones = detect_liquidity_sweeps(
    df,
    swings
)



print()

print("="*60)

print("LIQUIDITY ZONE TEST V3")

print(STOCK)

print("="*60)



print()

print(
    "Bullish Zones :",
    len(zones["bullish"])
)


print(
    "Bearish Zones :",
    len(zones["bearish"])
)



print()

print("="*60)

print("BULLISH LIQUIDITY ZONES")

print("="*60)



if not zones["bullish"]:

    print("No bullish zones")


else:

    for zone in zones["bullish"]:

        print(
            "Level:",
            zone["level"],
            "| Touches:",
            zone["touches"],
            "| Quality:",
            zone["quality"],
            "%",
            "| Last Seen:",
            zone["last_seen"]
        )



print()

print("="*60)

print("BEARISH LIQUIDITY ZONES")

print("="*60)



if not zones["bearish"]:

    print("No bearish zones")


else:

    for zone in zones["bearish"]:

        print(
            "Level:",
            zone["level"],
            "| Touches:",
            zone["touches"],
            "| Quality:",
            zone["quality"],
            "%",
            "| Last Seen:",
            zone["last_seen"]
        )