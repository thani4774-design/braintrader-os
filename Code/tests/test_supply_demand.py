"""
BrainTrader
------------------------
Supply & Demand Test
"""

import pandas as pd
import yfinance as yf

from indicators import calculate_indicators
from market_structure.supply_demand import detect_supply_demand


STOCK = "RELIANCE.NS"


df = yf.download(
    STOCK,
    period="2y",
    interval="1d",
    auto_adjust=True,
    progress=False,
)

if df.empty:
    print("No data.")
    raise SystemExit

if isinstance(df.columns, pd.MultiIndex):
    df.columns = df.columns.get_level_values(0)

df = df.reset_index()

df = calculate_indicators(df)

zones = detect_supply_demand(df)

print()
print("=" * 60)
print("SUPPLY & DEMAND TEST")
print(STOCK)
print("=" * 60)

print()
print("Demand Zones :", len(zones["demand"]))
print("Supply Zones :", len(zones["supply"]))

print()

print("=" * 30)
print("LATEST DEMAND ZONES")
print("=" * 30)

if zones["demand"]:

    for zone in zones["demand"][-5:]:

        print(
            zone["date"].date(),
            "|",
            round(zone["low"], 2),
            "-",
            round(zone["high"], 2),
            "| Strength:",
            zone["strength"]
        )

else:

    print("No Demand Zones")


print()

print("=" * 30)
print("LATEST SUPPLY ZONES")
print("=" * 30)

if zones["supply"]:

    for zone in zones["supply"][-5:]:

        print(
            zone["date"].date(),
            "|",
            round(zone["low"], 2),
            "-",
            round(zone["high"], 2),
            "| Strength:",
            zone["strength"]
        )

else:

    print("No Supply Zones")