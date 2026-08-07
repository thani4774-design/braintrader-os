"""
BrainTrader V2
------------------------
Pattern: Inverse Head & Shoulders

Purpose:
    Detect bullish Inverse Head & Shoulders
    using Swing Low points.
"""


def detect_inverse_head_shoulders(swings, tolerance=0.05):
    """
    Detect Inverse Head & Shoulders pattern.

    Structure:

          ▼       ▼       ▼
       Left    Head    Right

    Head should be the deepest low.

    Parameters
    ----------
    swings : list[SwingPoint]

    tolerance : float
        Allowed difference between shoulders.

    Returns
    -------
    list
    """

    patterns = []


    lows = [
        swing for swing in swings
        if swing.type == "LOW"
    ]


    if len(lows) < 3:
        return patterns


    for i in range(len(lows) - 2):

        left = lows[i]
        head = lows[i + 1]
        right = lows[i + 2]


        # Head must be lower than shoulders

        if (
            head.price < left.price
            and
            head.price < right.price
        ):

            shoulder_difference = abs(
                left.price -
                right.price
            )


            average_shoulders = (
                left.price +
                right.price
            ) / 2


            shoulder_variation = (
                shoulder_difference /
                average_shoulders
            )


            if shoulder_variation <= tolerance:


                confidence = (
                    1 - shoulder_variation
                ) * 100


                patterns.append({

                    "pattern":
                        "INVERSE_HEAD_SHOULDERS",

                    "direction":
                        "BULLISH",

                    "left_shoulder":
                        left.price,

                    "head":
                        head.price,

                    "right_shoulder":
                        right.price,

                    "left_date":
                        left.date,

                    "head_date":
                        head.date,

                    "right_date":
                        right.date,

                    "confidence":
                        round(
                            confidence,
                            2
                        )

                })


    return patterns