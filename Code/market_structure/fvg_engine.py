"""
BrainTrader
------------------------
Fair Value Gap (FVG) Engine V1 (Institutional SMC)

Detects structural price imbalances (FVGs).
A Bullish FVG occurs when Candle 1 High < Candle 3 Low.
A Bearish FVG occurs when Candle 1 Low > Candle 3 High.
"""

import pandas as pd

def detect_fvgs(df: pd.DataFrame, min_gap_percent: float = 0.1):
    """
    Detects unmitigated Fair Value Gaps.
    
    Parameters
    ----------
    df : pd.DataFrame
        OHLCV price data.
    min_gap_percent : float
        The minimum size of the gap as a percentage of the price to filter out micro-gaps.
        
    Returns
    -------
    dict
        {"bullish_fvgs": [], "bearish_fvgs": []}
    """
    bullish_fvgs = []
    bearish_fvgs = []

    if len(df) < 3:
        return {"bullish_fvgs": bullish_fvgs, "bearish_fvgs": bearish_fvgs}

    # Vectorized FVG detection using Pandas shift()
    # Candle 1 (2 periods ago), Candle 2 (1 period ago), Candle 3 (Current)
    
    c1_high = df['High'].shift(2)
    c1_low = df['Low'].shift(2)
    
    c3_high = df['High']
    c3_low = df['Low']

    # Bullish FVG: Candle 1 High is strictly less than Candle 3 Low
    bullish_mask = c1_high < c3_low
    
    # Bearish FVG: Candle 1 Low is strictly greater than Candle 3 High
    bearish_mask = c1_low > c3_high

    # Extract Bullish FVGs
    for idx in df[bullish_mask].index:
        top = float(df.loc[idx, 'Low'])          # Candle 3 Low
        bottom = float(df.loc[idx - 2, 'High'])  # Candle 1 High
        
        gap_size = ((top - bottom) / bottom) * 100
        if gap_size >= min_gap_percent:
            bullish_fvgs.append({
                "date": df.loc[idx - 1, 'Date'], # Date of the actual imbalance candle (Candle 2)
                "top": top,
                "bottom": bottom,
                "status": "UNMITIGATED"
            })

    # Extract Bearish FVGs
    for idx in df[bearish_mask].index:
        top = float(df.loc[idx - 2, 'Low'])      # Candle 1 Low
        bottom = float(df.loc[idx, 'High'])      # Candle 3 High
        
        gap_size = ((top - bottom) / bottom) * 100
        if gap_size >= min_gap_percent:
            bearish_fvgs.append({
                "date": df.loc[idx - 1, 'Date'], # Date of the actual imbalance candle (Candle 2)
                "top": top,
                "bottom": bottom,
                "status": "UNMITIGATED"
            })

    # Optional: Filter out mitigated FVGs (where future price has already traded through the gap)
    # For a high-performance scanner, we only keep FVGs that haven't been filled yet.
    
    active_bullish = []
    for fvg in bullish_fvgs:
        future_df = df[df['Date'] > fvg['date']]
        if future_df.empty or future_df['Low'].min() > fvg['bottom']:
            active_bullish.append(fvg)

    active_bearish = []
    for fvg in bearish_fvgs:
        future_df = df[df['Date'] > fvg['date']]
        if future_df.empty or future_df['High'].max() < fvg['top']:
            active_bearish.append(fvg)

    return {
        "bullish_fvgs": active_bullish,
        "bearish_fvgs": active_bearish
    }