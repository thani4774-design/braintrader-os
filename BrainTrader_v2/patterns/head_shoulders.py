"""
BrainTrader V2
------------------------
Pattern: Head & Shoulders

Purpose:
    Detect bearish Head & Shoulders
    using Swing High points.
"""


def detect_head_shoulders(swings, tolerance=0.05):
    """
    Detect Head & Shoulders pattern.

    Structure:

          Head
           ▲
          / \
     ▲   /   \   ▲
 Left           Right

    Parameters
    ----------
    swings : list[SwingPoint]

    tolerance : float
        Allowed shoulder height difference.

    Returns
    -------
    list
    """

    patterns = []


    highs = [
        swing for swing in swings
        if swing.type == "HIGH"
    ]


    if len(highs) < 3:
        return patterns


    for i in range(len(highs) - 2):

        left = highs[i]
        head = highs[i + 1]
        right = highs[i + 2]


        # Head must be higher than shoulders

        if (
            head.price > left.price
            and
            head.price > right.price
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


            # Shoulders should be similar

            if shoulder_variation <= tolerance:


                confidence = (
                    1 - shoulder_variation
                ) * 100


                patterns.append({

                    "pattern":
                        "HEAD_SHOULDERS",

                    "direction":
                        "BEARISH",

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