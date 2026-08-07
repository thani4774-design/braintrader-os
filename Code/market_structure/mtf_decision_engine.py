"""
BrainTrader
------------------------
MTF Decision Engine (Hardened Hierarchical Version)

Uses Timeframe Hierarchy rather than equal-weight counting.
Macro (15Y) and Major (5Y) dictate allowed trade direction.
Current (2Y) and Entry (6M) dictate timing and setup validity.
"""

def calculate_alignment(results):
    """
    Calculate hierarchical multi-timeframe trend alignment.
    Returns alignment score (-100 to +100) and allowed trade direction.
    """
    alignment_score = 0
    
    # Weightings: Higher timeframes carry more structural gravity
    weights = {
        "MACRO": 40,   # 15y
        "MAJOR": 30,   # 5y
        "CURRENT": 20, # 2y
        "ENTRY": 10    # 6m
    }

    total_available_weight = 0

    for tf_name, tf_data in results.items():
        if not tf_data:
            continue
            
        weight = weights.get(tf_name, 0)
        total_available_weight += weight
        trend = tf_data.get("trend", "SIDEWAYS")

        if trend in ["BULLISH", "BULLISH_TRANSITION"]:
            alignment_score += weight
        elif trend in ["BEARISH", "BEARISH_TRANSITION"]:
            alignment_score -= weight
            
    # Normalize the score to a percentage (-100% to 100%)
    # Positive = Bullish Alignment, Negative = Bearish Alignment
    if total_available_weight == 0:
        normalized_alignment = 0
    else:
        normalized_alignment = (alignment_score / total_available_weight) * 100

    # Determine permitted trade direction based on Macro/Major dominance
    macro_trend = results.get("MACRO", {}).get("trend", "SIDEWAYS") if results.get("MACRO") else "SIDEWAYS"
    
    if normalized_alignment >= 50 and "BULLISH" in macro_trend:
        overall_alignment = "BULLISH_ALIGNED"
    elif normalized_alignment <= -50 and "BEARISH" in macro_trend:
        overall_alignment = "BEARISH_ALIGNED"
    else:
        overall_alignment = "CONFLICTED"

    return {
        "alignment_score": round(normalized_alignment),
        "alignment": overall_alignment,
    }

def make_decision(confluence_score, alignment_data):
    """
    Generate final decision requiring both local setup quality (confluence) 
    and macro timeframe permission (alignment).
    """
    align_status = alignment_data["alignment"]
    
    if confluence_score >= 75 and align_status == "BULLISH_ALIGNED":
        return "STRONG_BUY"
    elif confluence_score >= 75 and align_status == "BEARISH_ALIGNED":
        return "STRONG_SHORT"
        
    if confluence_score >= 60 and align_status != "CONFLICTED":
        return "WATCHLIST"
        
    return "AVOID"

def generate_reason(results):
    reasons = []
    for tf_name, tf in results.items():
        if not tf:
            continue
        trend = tf.get("trend", "UNKNOWN").replace("_", " ").title()
        reasons.append(f"{tf_name} Structure: {trend}")
    return reasons