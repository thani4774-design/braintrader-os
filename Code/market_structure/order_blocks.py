"""
BrainTrader
------------------------
Order Block Engine V1 (Institutional SMC)

Identifies institutional Order Blocks by tracing backward from a 
confirmed Break of Structure (BOS) or Change of Character (CHoCH) 
to find the origin candle of the impulse move.
"""

import pandas as pd

def detect_order_blocks(df: pd.DataFrame, bos_events: list, max_lookback: int = 15):
    """
    Detects unmitigated Order Blocks (OB).
    
    Parameters
    ----------
    df : pd.DataFrame
        OHLCV price data.
    bos_events : list
        List of validated BOS events from the BOS Engine.
    max_lookback : int
        How many candles to look backward from the BOS to find the origin.
        
    Returns
    -------
    dict
        {"bullish_obs": [], "bearish_obs": []}
    """
    bullish_obs = []
    bearish_obs = []

    if not bos_events or df.empty:
        return {"bullish_obs": bullish_obs, "bearish_obs": bearish_obs}

    # Add a color column for fast vectorized checking
    df = df.copy()
    df['is_bullish'] = df['Close'] > df['Open']
    df['is_bearish'] = df['Close'] < df['Open']

    for bos in bos_events:
        bos_date = bos["date"]
        bos_direction = bos["direction"] # "BULLISH" or "BEARISH"

        # Find the index of the candle that broke structure
        try:
            bos_idx = df[df["Date"] == bos_date].index[0]
        except IndexError:
            continue

        # Look backward to find the origin of the move
        start_idx = max(0, bos_idx - max_lookback)
        lookback_df = df.iloc[start_idx:bos_idx]

        if lookback_df.empty:
            continue

        # -------------------------
        # Bullish Order Block
        # -------------------------
        # The last bearish candle before the bullish impulse that broke structure
        if bos_direction == "BULLISH":
            bearish_candles = lookback_df[lookback_df['is_bearish']]
            if not bearish_candles.empty:
                # The most recent bearish candle in the lookback window
                ob_candle = bearish_candles.iloc[-1]
                
                bullish_obs.append({
                    "date": ob_candle["Date"],
                    "top": float(ob_candle["High"]),
                    "bottom": float(ob_candle["Low"]),
                    "bos_date": bos_date,
                    "status": "UNMITIGATED" # Will be updated to MITIGATED once price touches it
                })

        # -------------------------
        # Bearish Order Block
        # -------------------------
        # The last bullish candle before the bearish impulse that broke structure
        elif bos_direction == "BEARISH":
            bullish_candles = lookback_df[lookback_df['is_bullish']]
            if not bullish_candles.empty:
                # The most recent bullish candle in the lookback window
                ob_candle = bullish_candles.iloc[-1]
                
                bearish_obs.append({
                    "date": ob_candle["Date"],
                    "top": float(ob_candle["High"]),
                    "bottom": float(ob_candle["Low"]),
                    "bos_date": bos_date,
                    "status": "UNMITIGATED"
                })

    return {
        "bullish_obs": bullish_obs,
        "bearish_obs": bearish_obs
    }