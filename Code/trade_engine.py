"""
BrainTrader
------------------------
Trade Setup Engine V3 (Trailing Stops & Exact Ranges)

Generates:
- Exact Entry Zone (Low/High)
- Hard Stop Loss
- Trailing Stop Logic (Breakeven & Target tracking)
- Targets (Target 1 & Target 2)
- Risk Reward Ratio
- Setup Quality Rating
"""

def calculate_atr(df, period=14):
    if len(df) < period + 1:
        return float(df["Close"].iloc[-1] * 0.02) 

    high = df["High"]
    low = df["Low"]
    close = df["Close"]

    tr1 = high - low
    tr2 = abs(high - close.shift())
    tr3 = abs(low - close.shift())

    tr = tr1.combine(tr2, max).combine(tr3, max)
    atr = tr.rolling(period).mean()

    return float(atr.iloc[-1])

def calculate_quality(score, confidence, rr):
    if rr >= 2.0 and score >= 75 and confidence >= 70:
        return "A+"
    if rr >= 1.5 and score >= 50 and confidence >= 50:
        return "A"
    if rr >= 1.5 and score >= 35:
        return "B"
    if rr < 1.5:
        return "POOR_RR"
    return "C"

def generate_trade_setup(df, price, levels, score, confidence, direction="LONG"):
    atr = calculate_atr(df)
    support = levels.get("nearest_support")
    resistance = levels.get("nearest_resistance")

    warnings = []
    
    if direction == "LONG":
        # Exact Entry Zone (0.5 ATR spread around current price)
        entry_low = round(price - (atr * 0.3), 2)
        entry_high = round(price + (atr * 0.3), 2)

        # Stop Loss
        if support and support < price:
            stop_loss = support - (atr * 0.5)
        else:
            stop_loss = price - (atr * 1.5)

        risk = price - stop_loss

        # Targets
        if resistance and resistance > price:
            target1 = resistance
        else:
            target1 = price + (risk * 2)

        target2 = price + (risk * 3)
        reward = target1 - price
        
        # Trailing Stop Strategy: Move stop-loss to Breakeven once price moves 1R in favor,
        # or trail by 1 ATR behind current price structure.
        trailing_stop_stage1 = round(price, 2) # Breakeven at entry
        trailing_stop_stage2 = round(target1 - atr, 2) # Trail behind target 1

    elif direction == "SHORT":
        entry_low = round(price - (atr * 0.3), 2)
        entry_high = round(price + (atr * 0.3), 2)

        if resistance and resistance > price:
            stop_loss = resistance + (atr * 0.5)
        else:
            stop_loss = price + (atr * 1.5)

        risk = stop_loss - price

        if support and support < price:
            target1 = support
        else:
            target1 = price - (risk * 2)

        target2 = price - (risk * 3)
        reward = price - target1
        
        trailing_stop_stage1 = round(price, 2)
        trailing_stop_stage2 = round(target1 + atr, 2)

    rr = reward / risk if risk > 0 else 0

    if rr < 1.5:
        warnings.append(f"Hard Reject: R:R is {round(rr,2)}. Minimum required is 1.5.")
        return None 

    if confidence < 40:
        warnings.append("Low confidence.")
        
    quality = calculate_quality(score, confidence, rr)

    return {
        "setup": "BUY" if direction == "LONG" else "SELL",
        "entry_zone": f"₹{entry_low} - ₹{entry_high}",
        "stop_loss": round(stop_loss, 2),
        "target1": round(target1, 2),
        "target2": round(target2, 2),
        "risk_reward": round(rr, 2),
        "quality": quality,
        "trailing_plan": {
            "move_to_breakeven_at": round(price + (risk * 1.0), 2) if direction == "LONG" else round(price - (risk * 1.0), 2),
            "trail_stop_at_target1": trailing_stop_stage2
        },
        "warnings": warnings
    }