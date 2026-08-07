"""
BrainTrader V2
------------------------
Pattern: Flags & Pennants

Detects:
- Bull Flag
- Bear Flag
- Bull Pennant
- Bear Pennant
"""


def detect_flags(swings):
    """
    Detect flag and pennant patterns.

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


    high_move = (
        recent_highs[-1].price -
        recent_highs[0].price
    )


    low_move = (
        recent_lows[-1].price -
        recent_lows[0].price
    )


    # ==================================
    # Bull Flag
    #
    # Strong upward move
    # Small downward consolidation
    # ==================================

    if (
        high_move > 0
        and
        low_move < 0
    ):

        patterns.append({

            "pattern":
                "BULL_FLAG",

            "direction":
                "BULLISH",

            "confidence":
                70

        })


    # ==================================
    # Bear Flag
    #
    # Strong downward move
    # Small upward consolidation
    # ==================================

    if (
        high_move < 0
        and
        low_move > 0
    ):

        patterns.append({

            "pattern":
                "BEAR_FLAG",

            "direction":
                "BEARISH",

            "confidence":
                70

        })


    # ==================================
    # Pennant
    #
    # Contracting price movement
    # ==================================

    if (
        abs(high_move) <
        abs(recent_highs[0].price * 0.05)
    ):

        patterns.append({

            "pattern":
                "PENNANT",

            "direction":
                "NEUTRAL",

            "confidence":
                65

        })


    return patterns