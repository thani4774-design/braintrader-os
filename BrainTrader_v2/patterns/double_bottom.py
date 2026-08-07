"""
BrainTrader V2
------------------------
Pattern: Double Bottom

Purpose:
    Detect potential bullish Double Bottom patterns
    using Swing Low points.
"""


def detect_double_bottom(swings, tolerance=0.03):
    """
    Detect Double Bottom pattern.

    Parameters
    ----------
    swings : list[SwingPoint]

    tolerance : float
        Allowed difference between two bottoms.

    Returns
    -------
    list
        Detected patterns
    """

    patterns = []

    lows = [
        swing for swing in swings
        if swing.type == "LOW"
    ]

    if len(lows) < 2:
        return patterns


    for i in range(len(lows) - 1):

        first_low = lows[i]
        second_low = lows[i + 1]


        difference = abs(
            first_low.price -
            second_low.price
        )


        average_price = (
            first_low.price +
            second_low.price
        ) / 2


        percentage_difference = (
            difference /
            average_price
        )


        # Similar depth bottoms
        if percentage_difference <= tolerance:


            patterns.append({

                "pattern": "DOUBLE_BOTTOM",

                "direction": "BULLISH",

                "first_bottom_date":
                    first_low.date,

                "second_bottom_date":
                    second_low.date,

                "first_bottom":
                    first_low.price,

                "second_bottom":
                    second_low.price,

                "confidence":
                    round(
                        (1 - percentage_difference)
                        * 100,
                        2
                    )

            })


    return patterns