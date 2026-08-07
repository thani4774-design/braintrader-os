"""
BrainTrader
------------------------
MTF Score Engine

Combines multiple timeframe market structure into one score.
"""


def trend_score(trend):
    """Convert a market-structure trend label into a base score."""
    scores = {
        "BULLISH": 100,
        "BULLISH_TRANSITION": 65,
        "SIDEWAYS": 50,
        "BEARISH_TRANSITION": 35,
        "BEARISH": 0,
    }

    return scores.get(trend, 50)


def calculate_mtf_score(results):
    """Return the confidence-adjusted multi-timeframe structure score."""
    weights = {
        "MACRO_15Y": 0.30,
        "MAJOR_5Y": 0.35,
        "CURRENT_2Y": 0.20,
        "ENTRY_6M": 0.15,
    }

    total = 0

    for timeframe, result in results.items():
        if result:
            score = trend_score(result["trend"])
            confidence = result["confidence"] / 100
            adjusted = score * (0.5 + confidence / 2)
            total += adjusted * weights[timeframe]

    return round(total, 2)
