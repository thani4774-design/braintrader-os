"""
BrainTrader
------------------------
Recommendation Engine

Combines multi-timeframe structure, trend alignment, and indicator
confirmation into one final trading recommendation.
"""

from risk_manager import calculate_stop_loss, calculate_target


def calculate_final_score(mtf_score, indicator_score):
    """Combine structure and indicator scores into a score out of 100."""
    return round((mtf_score * 0.70) + (indicator_score * 0.30), 2)


def make_recommendation(final_score, alignment, indicator_score):
    """Return a final recommendation from the combined analysis."""
    if final_score >= 75 and alignment >= 75 and indicator_score >= 60:
        return "STRONG_BUY"

    if final_score >= 60 and alignment >= 60 and indicator_score >= 45:
        return "BUY_WATCH"

    if final_score >= 40:
        return "WAIT"

    return "AVOID"


def create_recommendation(
    stock,
    price,
    mtf_score,
    alignment,
    indicator_score,
    atr,
    reasons=None,
):
    """Create a complete BrainTrader recommendation dictionary.

    Risk levels are included only for actionable recommendations. ``reasons``
    can be the list returned by ``generate_reason()`` from the MTF decision
    engine.
    """
    final_score = calculate_final_score(mtf_score, indicator_score)
    decision = make_recommendation(final_score, alignment, indicator_score)

    recommendation = {
        "Stock": stock,
        "Entry": round(price, 2),
        "MTF Score": mtf_score,
        "Indicator Score": indicator_score,
        "Final Score": final_score,
        "Alignment": alignment,
        "Decision": decision,
        "Reasons": reasons or [],
        "Stop Loss": None,
        "Target": None,
    }

    if decision in {"STRONG_BUY", "BUY_WATCH"}:
        recommendation["Stop Loss"] = calculate_stop_loss(price, atr)
        recommendation["Target"] = calculate_target(price, atr)

    return recommendation
