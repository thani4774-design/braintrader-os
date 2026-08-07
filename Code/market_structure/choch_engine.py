"""
BrainTrader
------------------------
CHoCH Engine V3 (Hardened SMC Version)

Filters weak structure changes and enforces body-close validation 
to avoid trading into liquidity sweeps.
"""

def detect_choch(df, swings):
    events = []
    
    last_LH = None
    last_HL = None

    for swing in swings:
        label = swing.get("label")
        importance = swing.get("importance", "WEAK")
        strength = swing.get("strength", 0)

        # Store major structural points. We only care about STRONG structure for CHoCH.
        if importance != "WEAK":
            if label == "LH":
                last_LH = swing
            elif label == "HL":
                last_HL = swing

        # Extract the closing price of the current swing's candle
        swing_row = df[df["Date"] == swing["date"]]
        if swing_row.empty:
            continue
            
        close_price = float(swing_row.iloc[0]["Close"])

        # -------------------------
        # Bullish CHoCH
        # -------------------------
        # Price must BODY CLOSE above the last major Lower High
        if swing["type"] == "HIGH" and last_LH is not None:
            if close_price > last_LH["price"] and strength >= 5:
                events.append({
                    "date": swing["date"],
                    "type": "BULLISH_CHOCH",
                    "level": last_LH["price"],
                    "strength": strength,
                    "confidence": round(70 + strength, 2),
                    "break_type": "BODY_CLOSE"
                })
                # Reset to avoid duplicate triggers on the same level
                last_LH = None

        # -------------------------
        # Bearish CHoCH
        # -------------------------
        # Price must BODY CLOSE below the last major Higher Low
        if swing["type"] == "LOW" and last_HL is not None:
            if close_price < last_HL["price"] and strength >= 5:
                events.append({
                    "date": swing["date"],
                    "type": "BEARISH_CHOCH",
                    "level": last_HL["price"],
                    "strength": strength,
                    "confidence": round(70 + strength, 2),
                    "break_type": "BODY_CLOSE"
                })
                # Reset to avoid duplicate triggers on the same level
                last_HL = None

    return events