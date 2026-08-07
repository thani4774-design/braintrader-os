"""
BrainTrader
------------------------
Swing Analysis

Combines swing classification and strength
to identify important market structure points.
"""


def analyze_swings(swings, major_threshold=8):
    """
    Analyze swing importance.

    Parameters
    ----------
    swings : list
        Swing points with classification and strength.

    major_threshold : float
        Strength percentage above which a swing
        is considered major.

    Returns
    -------
    list
        Enhanced swing analysis.
    """

    analyzed = []


    for swing in swings:

        result = swing.copy()


        strength = result.get(
            "strength",
            0
        )


        if strength >= major_threshold:

            result["importance"] = "MAJOR"

        elif strength >= 4:

            result["importance"] = "NORMAL"

        else:

            result["importance"] = "WEAK"


        analyzed.append(result)


    return analyzed