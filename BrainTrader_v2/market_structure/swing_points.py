from market_structure.models import SwingPoint
"""
BrainTrader V2
------------------------
Module: Swing Point Detection

Purpose:
    Detect significant Swing Highs and Swing Lows
    from OHLCV price data.
"""


def detect_swings(df, strength=3):
    """
    Detect Swing Highs and Swing Lows.

    Parameters
    ----------
    df : pandas.DataFrame

    strength : int
        Number of candles on each side
        used for comparison.

    Returns
    -------
    list
        Swing point dictionaries
    """

    swings = []


    for i in range(strength, len(df) - strength):

        current_high = df["High"].iloc[i]
        current_low = df["Low"].iloc[i]


        # ==========================
        # Swing High
        # ==========================

        previous_highs = (
            df["High"]
            .iloc[i-strength:i]
        )

        next_highs = (
            df["High"]
            .iloc[i+1:i+strength+1]
        )


        if (
            current_high > previous_highs.max()
            and
            current_high > next_highs.max()
        ):

            swings.append({

                "date":
                    df["Date"].iloc[i],

                "type":
                    "HIGH",

                "price":
                    float(current_high)

            })


        # ==========================
        # Swing Low
        # ==========================

        previous_lows = (
            df["Low"]
            .iloc[i-strength:i]
        )

        next_lows = (
            df["Low"]
            .iloc[i+1:i+strength+1]
        )


        if (
            current_low < previous_lows.min()
            and
            current_low < next_lows.min()
        ):

            swings.append({

                "date":
                    df["Date"].iloc[i],

                "type":
                    "LOW",

                "price":
                    float(current_low)

            })


    return swings