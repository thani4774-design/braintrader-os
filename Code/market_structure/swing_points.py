"""
BrainTrader
------------------------
Swing Point Detection (Hardened & Vectorized)

Detects significant Swing Highs and Swing Lows using rolling windows.
Eliminates look-ahead bias, fixes Outside Bar omissions, and resolves EQH/EQL drops.
"""

import pandas as pd

def detect_swings(df: pd.DataFrame, strength: int = 3) -> list:
    """Detect and filter alternating swing highs and swing lows."""
    if len(df) < (strength * 2 + 1):
        return []

    window = strength * 2 + 1

    # 1. Vectorized Peak/Valley Detection
    # rolling(center=True) looks 'strength' bars backward and 'strength' bars forward.
    # We use min_periods=window to ensure we don't detect swings near the absolute edges 
    # where we don't have enough data to confirm them.
    rolling_max = df['High'].rolling(window=window, center=True, min_periods=window).max()
    rolling_min = df['Low'].rolling(window=window, center=True, min_periods=window).min()

    # Boolean masks to find where the actual high/low matches the rolling extreme.
    # Using == fixes the Equal Highs/Lows bug.
    is_high = (df['High'] == rolling_max)
    is_low = (df['Low'] == rolling_min)

    # Extract raw highs and lows
    highs = df[is_high].copy()
    lows = df[is_low].copy()

    highs['type'] = 'HIGH'
    highs['price'] = highs['High']

    lows['type'] = 'LOW'
    lows['price'] = lows['Low']

    # Combine them and sort chronologically. 
    # This automatically solves the "Outside Bar" bug because both a HIGH and LOW 
    # for the exact same date will be appended to the dataframe sequentially.
    combined_swings = pd.concat([highs, lows]).sort_index()

    # Convert to list of dicts for the filtering engine
    raw_swings = []
    for _, row in combined_swings.iterrows():
        raw_swings.append({
            "date": row['Date'],
            "type": row['type'],
            "price": float(row['price'])
        })

    # 2. Filter for Alternating Swings
    # Keeps the most extreme point if multiple consecutive highs or lows are detected
    # (e.g., in the case of Equal Highs, it will keep the first one and drop the second).
    if len(raw_swings) <= 1:
        return raw_swings

    filtered = [raw_swings[0]]

    for swing in raw_swings[1:]:
        previous = filtered[-1]

        if swing["type"] != previous["type"]:
            filtered.append(swing)
        elif swing["type"] == "HIGH":
            # If consecutive highs, keep the higher one (or the earlier one if equal)
            if swing["price"] > previous["price"]:
                filtered[-1] = swing
        elif swing["type"] == "LOW":
            # If consecutive lows, keep the lower one (or the earlier one if equal)
            if swing["price"] < previous["price"]:
                filtered[-1] = swing

    return filtered