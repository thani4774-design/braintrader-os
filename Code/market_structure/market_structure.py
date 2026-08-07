"""
BrainTrader
------------------------
Market Structure Detection
"""


def detect_market_structure(swings):
    """
    Detect overall market structure
    from swing points.
    """

    if len(swings) < 4:
        return {
            "trend": "SIDEWAYS",
            "higher_highs": 0,
            "higher_lows": 0,
            "lower_highs": 0,
            "lower_lows": 0
        }

    higher_highs = 0
    higher_lows = 0
    lower_highs = 0
    lower_lows = 0

    previous_high = None
    previous_low = None

    for swing in swings:

        if swing["type"] == "HIGH":

            if previous_high is not None:

                if swing["price"] > previous_high:
                    higher_highs += 1
                else:
                    lower_highs += 1

            previous_high = swing["price"]

        elif swing["type"] == "LOW":

            if previous_low is not None:

                if swing["price"] > previous_low:
                    higher_lows += 1
                else:
                    lower_lows += 1

            previous_low = swing["price"]

    score = (higher_highs + higher_lows) - (lower_highs + lower_lows)

    if score >= 8:
        trend = "STRONG_BULLISH"
    elif score >= 3:
        trend = "BULLISH"
    elif score <= -8:
        trend = "STRONG_BEARISH"
    elif score <= -3:
        trend = "BEARISH"
    else:
        trend = "SIDEWAYS"

    return {
        "trend": trend,
        "higher_highs": higher_highs,
        "higher_lows": higher_lows,
        "lower_highs": lower_highs,
        "lower_lows": lower_lows
    }