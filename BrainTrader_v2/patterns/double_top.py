"""
BrainTrader V2
------------------------
Pattern: Double Top

Purpose:
    Detect potential bearish Double Top patterns
    using Swing High points.
"""


def detect_double_top(swings, tolerance=0.03):
    """
    Detect Double Top pattern.

    Parameters
    ----------
    swings : list

    tolerance : float
        Allowed difference between two peaks.

    Returns
    -------
    list
        Detected patterns
    """

    patterns = []

    highs = [
        swing for swing in swings
        if swing["type"] == "HIGH"
    ]

    if len(highs) < 2:
        return patterns

    for i in range(len(highs) - 1):

        first_high = highs[i]
        second_high = highs[i + 1]

        difference = abs(
            first_high["price"] -
            second_high["price"]
        )

        average_price = (
            first_high["price"] +
            second_high["price"]
        ) / 2

        percentage_difference = (
            difference /
            average_price
        )

        if percentage_difference <= tolerance:

            patterns.append({

                "pattern": "DOUBLE_TOP",

                "direction": "BEARISH",

                "first_peak_date":
                    first_high["date"],

                "second_peak_date":
                    second_high["date"],

                "first_peak":
                    first_high["price"],

                "second_peak":
                    second_high["price"],

                "confidence":
                    round(
                        (1 - percentage_difference)
                        * 100,
                        2
                    )

            })

    return patterns