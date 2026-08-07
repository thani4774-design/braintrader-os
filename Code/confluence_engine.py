"""
BrainTrader
------------------------
Confluence Engine V4 (Premium/Discount Integration)
Scores variables to output an unemotional, institutional-grade decision.
"""

import logging

logging.basicConfig(level=logging.INFO)

def calculate_confluence(structure, bos, choch, liquidity, support_resistance, indicator, price, order_blocks, fvgs, pd_zones=None):
    score = 0
    confidence = 0
    reasons = []
    warnings = []
    
    # 1. Market Structure & Trend
    if structure and structure.get("trend") == "BULLISH":
        score += 20
        confidence += 15
        reasons.append("Macro Trend is BULLISH")
    elif structure and structure.get("trend") == "BEARISH":
        score -= 20
        warnings.append("Macro Trend is BEARISH")
        
    # 2. Premium / Discount (The Institutional Shield)
    if pd_zones:
        zone = pd_zones.get("zone")
        if zone == "DISCOUNT":
            score += 25
            confidence += 20
            reasons.append(f"Price is in DISCOUNT zone (< ₹{pd_zones.get('equilibrium')})")
        elif zone == "PREMIUM":
            score -= 30
            warnings.append(f"Price is in PREMIUM zone (> ₹{pd_zones.get('equilibrium')}). Refusing to buy high.")

    # 3. Order Blocks & FVGs
    if order_blocks and order_blocks.get("bullish"):
        score += 20
        confidence += 10
        reasons.append("Unmitigated Bullish Order Block detected")
        
    if fvgs and fvgs.get("bullish"):
        score += 15
        confidence += 10
        reasons.append("Bullish Fair Value Gap (Imbalance) present")

    # 4. Liquidity
    if liquidity == "BULLISH":
        score += 15
        confidence += 10
        reasons.append("Sell-side liquidity swept (Bullish trap)")
    elif liquidity == "BEARISH":
        score -= 20
        warnings.append("Buy-side liquidity swept (Bearish trap)")

    # 5. Support & Resistance
    if support_resistance:
        support = support_resistance.get("nearest_support")
        resistance = support_resistance.get("nearest_resistance")
        
        if support and (price - support) / price < 0.02:
            score += 10
            reasons.append("Price is very close to structural support")
        
        if resistance and (resistance - price) / price < 0.02:
            score -= 20
            warnings.append("Price is hitting overhead resistance")

    # 6. Indicator Alignment
    if indicator:
        if indicator.get("ema_trend") == "BULLISH":
            score += 10
            reasons.append("EMAs are aligned bullishly")
        if indicator.get("rsi_status") == "OVERSOLD":
            score += 10
            reasons.append("RSI indicates oversold conditions")
        elif indicator.get("rsi_status") == "OVERBOUGHT":
            score -= 10
            warnings.append("RSI is overbought")
            
    # Final Decision Thresholds
    decision = "WAIT"
    
    # Hard risk block: Never allow a STRONG_BUY in a Premium Zone
    is_premium = any("PREMIUM zone" in w for w in warnings)
    
    if score >= 60 and not is_premium:
        decision = "STRONG_BUY"
    elif score >= 40 and not is_premium:
        decision = "BUY_WATCH"
    elif score <= -40:
        decision = "STRONG_SHORT"

    return {
        "score": score,
        "confidence": min(confidence, 100),
        "reasons": reasons,
        "warnings": warnings,
        "decision": decision
    }