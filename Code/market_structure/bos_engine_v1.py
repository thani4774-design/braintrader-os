"""
BrainTrader
------------------------
BOS Engine

Detects Break of Structure (BOS)
using important swing points.
"""


def detect_bos(df, swings):
    """
    Detect bullish and bearish BOS events.

    Parameters
    ----------
    df : pandas.DataFrame
        OHLCV data.

    swings : list
        Analyzed swings containing:
        label, strength, importance.

    Returns
    -------
    list
        BOS events.
    """

    events = []


    major_highs = [
        swing for swing in swings
        if (
            swing["type"] == "HIGH"
            and
            swing.get("importance") == "MAJOR"
        )
    ]


    major_lows = [
        swing for swing in swings
        if (
            swing["type"] == "LOW"
            and
            swing.get("importance") == "MAJOR"
        )
    ]


    for i in range(len(df)):

        current_date = df["Date"].iloc[i]
        current_close = df["Close"].iloc[i]


        # -------------------------
        # Bullish BOS
        # -------------------------

        for high in major_highs:

            if (
                current_close > high["price"]
                and
                current_date > high["date"]
            ):

                events.append({

                    "date": current_date,

                    "type": "BULLISH",

                    "broken_level":
                        high["price"],

                    "swing_date":
                        high["date"],

                    "strength":
                        high["strength"]

                })

                major_highs.remove(high)

                break



        # -------------------------
        # Bearish BOS
        # -------------------------

        for low in major_lows:

            if (
                current_close < low["price"]
                and
                current_date > low["date"]
            ):

                events.append({

                    "date": current_date,

                    "type": "BEARISH",

                    "broken_level":
                        low["price"],

                    "swing_date":
                        low["date"],

                    "strength":
                        low["strength"]

                })

                major_lows.remove(low)

                break


    return events