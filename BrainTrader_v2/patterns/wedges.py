"""
BrainTrader V2
------------------------
Pattern: Wedge Patterns

Detects:
- Rising Wedge
- Falling Wedge
"""


def detect_wedges(swings):
    """
    Detect wedge patterns using swing points.

    Parameters
    ----------
    swings : list[SwingPoint]

    Returns
    -------
    list
    """

    patterns = []


    highs = [
        swing for swing in swings
        if swing.type == "HIGH"
    ]

    lows = [
        swing for swing in swings
        if swing.type == "LOW"
    ]


    if len(highs) < 3 or len(lows) < 3:
        return patterns


    recent_highs = highs[-3:]
    recent_lows = lows[-3:]


    # Price movement comparison

    high_direction = (
        recent_highs[-1].price -
        recent_highs[0].price
    )


    low_direction = (
        recent_lows[-1].price -
        recent_lows[0].price
    )


    # ==================================
    # Rising Wedge
    #
    # Higher highs
    # Higher lows
    # But narrowing
    # ==================================

    if (
        high_direction > 0
        and
        low_direction > 0
        and
        recent_highs[-1].price <
        recent_lows[-1].price * 1.20
    ):

        patterns.append({

            "pattern":
                "RISING_WEDGE",

            "direction":
                "BEARISH",

            "confidence":
                70

        })


    # ==================================
    # Falling Wedge
    #
    # Lower highs
    # Lower lows
    # ==================================

    if (
        high_direction < 0
        and
        low_direction < 0
    ):

        patterns.append({

            "pattern":
                "FALLING_WEDGE",

            "direction":
                "BULLISH",

            "confidence":
                70

        })


    return patterns