"""
BrainTrader V2
------------------------
Pattern: Triangle Patterns

Detects:
- Ascending Triangle
- Descending Triangle
- Symmetrical Triangle
"""


def detect_triangles(swings, tolerance=0.03):
    """
    Detect triangle patterns using swing points.

    Parameters
    ----------
    swings : list[SwingPoint]

    tolerance : float
        Allowed price variation.

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


    if len(highs) < 2 or len(lows) < 2:
        return patterns


    recent_highs = highs[-2:]
    recent_lows = lows[-2:]


    high_difference = abs(
        recent_highs[0].price -
        recent_highs[1].price
    )


    low_difference = abs(
        recent_lows[0].price -
        recent_lows[1].price
    )


    high_average = (
        recent_highs[0].price +
        recent_highs[1].price
    ) / 2


    low_average = (
        recent_lows[0].price +
        recent_lows[1].price
    ) / 2


    high_variation = (
        high_difference /
        high_average
    )


    low_variation = (
        low_difference /
        low_average
    )


    # =================================
    # Ascending Triangle
    # Flat resistance
    # Higher lows
    # =================================

    if (
        high_variation <= tolerance
        and
        recent_lows[1].price > recent_lows[0].price
    ):

        patterns.append({

            "pattern":
                "ASCENDING_TRIANGLE",

            "direction":
                "BULLISH",

            "confidence":
                round(
                    (1-high_variation)
                    *100,
                    2
                )
        })


    # =================================
    # Descending Triangle
    # Lower highs
    # Flat support
    # =================================

    if (
        low_variation <= tolerance
        and
        recent_highs[1].price < recent_highs[0].price
    ):

        patterns.append({

            "pattern":
                "DESCENDING_TRIANGLE",

            "direction":
                "BEARISH",

            "confidence":
                round(
                    (1-low_variation)
                    *100,
                    2
                )
        })


    # =================================
    # Symmetrical Triangle
    # Lower highs
    # Higher lows
    # =================================

    if (
        recent_highs[1].price < recent_highs[0].price
        and
        recent_lows[1].price > recent_lows[0].price
    ):

        patterns.append({

            "pattern":
                "SYMMETRICAL_TRIANGLE",

            "direction":
                "NEUTRAL",

            "confidence":
                70
        })


    return patterns