"""
BrainTrader
------------------------
Liquidity Sweep Engine (Hardened & Vectorized)

Detects institutional liquidity sweeps instantly using Pandas masking.
Merges nearby levels into high-probability liquidity zones.
"""
import pandas as pd

LEVEL_TOLERANCE = 0.01

def merge_zones(items):
    """Merges overlapping sweep levels into a single liquidity zone."""
    if not items:
        return []

    items = sorted(items, key=lambda x: x["level"])
    zones = []
    current = [items[0]]

    for item in items[1:]:
        previous = current[-1]
        
        # If the level is within tolerance, it's the same liquidity pool
        if abs(item["level"] - previous["level"]) / previous["level"] <= LEVEL_TOLERANCE:
            current.append(item)
        else:
            zones.append(create_zone(current))
            current = [item]

    zones.append(create_zone(current))
    return zones

def create_zone(items):
    levels = [x["level"] for x in items]
    quality = max(x["quality"] for x in items)
    latest_date = max(x["date"] for x in items)
    
    return {
        "level": round(sum(levels) / len(levels), 2),
        "touches": len(items),
        "quality": quality,
        "last_seen": latest_date,
        "status": "ACTIVE"
    }

def calculate_quality(distance, importance, is_equal_level=False):
    """
    Scores the liquidity sweep.
    Equal Highs/Lows (EH/EL) get a massive quality boost because 
    they represent obvious retail liquidity pools.
    """
    score = 50
    if distance >= 1:
        score += 20
        
    if importance == "MAJOR":
        score += 30
    elif importance == "NORMAL":
        score += 15
        
    # SMC Boost: Sweeping an Equal High/Low is a prime institutional setup
    if is_equal_level:
        score += 25

    return min(score, 100)

def detect_liquidity_sweeps(df: pd.DataFrame, swings: list):
    """Vectorized detection of Bullish and Bearish Liquidity Sweeps."""
    bullish = []
    bearish = []

    if not swings or df.empty:
        return {"bullish": [], "bearish": []}

    important = [s for s in swings if s.get("importance") in ["MAJOR", "NORMAL"]]

    # -------------------------
    # Vectorized Bullish Sweeps
    # -------------------------
    lows = [s for s in important if s["type"] == "LOW"]
    
    for low in lows:
        level = low["price"]
        swing_date = low["date"]
        
        # Fast masking: Get all future rows simultaneously
        mask = df["Date"] > swing_date
        future_df = df[mask]
        
        if future_df.empty:
            continue
            
        # Vectorized check: Low goes below the level, but Close stays above it
        sweep_mask = (future_df["Low"] < level) & (future_df["Close"] > level)
        sweeps = future_df[sweep_mask]
        
        if not sweeps.empty:
            # Get the first occurrence of the sweep
            first_sweep = sweeps.iloc[0]
            distance = ((level - first_sweep["Low"]) / level) * 100
            
            # Did we sweep an Equal Low?
            is_el = low.get("label") == "EL"
            
            bullish.append({
                "date": first_sweep["Date"],
                "level": level,
                "quality": calculate_quality(distance, low.get("importance", "WEAK"), is_el)
            })

    # -------------------------
    # Vectorized Bearish Sweeps
    # -------------------------
    highs = [s for s in important if s["type"] == "HIGH"]
    
    for high in highs:
        level = high["price"]
        swing_date = high["date"]
        
        # Fast masking
        mask = df["Date"] > swing_date
        future_df = df[mask]
        
        if future_df.empty:
            continue
            
        # Vectorized check: High goes above the level, but Close stays below it
        sweep_mask = (future_df["High"] > level) & (future_df["Close"] < level)
        sweeps = future_df[sweep_mask]
        
        if not sweeps.empty:
            # Get the first occurrence of the sweep
            first_sweep = sweeps.iloc[0]
            distance = ((first_sweep["High"] - level) / level) * 100
            
            # Did we sweep an Equal High?
            is_eh = high.get("label") == "EH"
            
            bearish.append({
                "date": first_sweep["Date"],
                "level": level,
                "quality": calculate_quality(distance, high.get("importance", "WEAK"), is_eh)
            })

    return {
        "bullish": merge_zones(bullish),
        "bearish": merge_zones(bearish)
    }