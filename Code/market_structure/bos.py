"""
BrainTrader
------------------------
Break of Structure (BOS) Engine (Hardened SMC Version)

Detects true structural breaks. 
Enforces the Institutional rule that a BOS requires a body close 
beyond the previous structural extreme, not just a wick (liquidity sweep).
"""

def detect_bos(df, classified_swings):
    """
    Detect true Break of Structure (BOS) requiring a body close.

    Parameters
    ----------
    df : pd.DataFrame
        The OHLCV price data.
    classified_swings : list
        List of classified swing dictionaries (HH, HL, LH, LL, EH, EL).

    Returns
    -------
    list
        List of validated BOS events.
    """
    bos_events = []
    
    last_high = None
    last_low = None

    for swing in classified_swings:
        # Match the swing date to the exact row in the DataFrame to get the Close price
        swing_row = df[df["Date"] == swing["date"]]
        if swing_row.empty:
            continue
            
        close_price = float(swing_row.iloc[0]["Close"])

        if swing["type"] == "HIGH":
            # If it's a Higher High, check if the BODY closed above the last structural high
            if swing["label"] == "HH" and last_high is not None:
                if close_price > last_high["price"]:
                    bos_events.append({
                        "date": swing["date"],
                        "direction": "BULLISH",
                        "price": swing["price"],
                        "break_type": "BODY_CLOSE"
                    })
                else:
                    # It just wicked above the old high. This is a Liquidity Sweep, NOT a BOS.
                    pass 
            
            # Update the last structural high tracker
            last_high = swing

        elif swing["type"] == "LOW":
            # If it's a Lower Low, check if the BODY closed below the last structural low
            if swing["label"] == "LL" and last_low is not None:
                if close_price < last_low["price"]:
                    bos_events.append({
                        "date": swing["date"],
                        "direction": "BEARISH",
                        "price": swing["price"],
                        "break_type": "BODY_CLOSE"
                    })
                else:
                    # It just wicked below the old low. This is a Liquidity Sweep, NOT a BOS.
                    pass
            
            # Update the last structural low tracker
            last_low = swing

    return bos_events