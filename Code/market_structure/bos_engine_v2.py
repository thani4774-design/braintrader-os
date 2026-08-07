"""
BrainTrader
------------------------
BOS Engine V2

Detects confirmed Break of Structure
using major swing points.

Features:
- Major swing filtering
- Duplicate BOS protection
- Price zone tolerance
- Confidence scoring
"""


def detect_bos(df, swings, tolerance=0.02):
    """
    Detect bullish and bearish BOS events.

    Parameters
    ----------
    df : pandas.DataFrame
        OHLCV data.

    swings : list
        Analyzed swing points.

    tolerance : float
        Price zone tolerance.

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


    broken_levels = []


    def already_detected(price):

        for level in broken_levels:

            difference = abs(
                price - level
            ) / level

            if difference <= tolerance:
                return True

        return False



    # -------------------------
    # Scan candles
    # -------------------------

    for i in range(len(df)):

        current_date = df["Date"].iloc[i]
        close = df["Close"].iloc[i]



        # -------------------------
        # Bullish BOS
        # -------------------------

        for high in major_highs:

            if (
                current_date > high["date"]
                and
                close > high["price"]
                and
                not already_detected(high["price"])
            ):

                confidence = min(
                    round(
                        70 +
                        high["strength"],
                        2
                    ),
                    99
                )


                events.append({

                    "date": current_date,

                    "type": "BULLISH",

                    "level":
                        high["price"],

                    "strength":
                        high["strength"],

                    "confidence":
                        confidence

                })


                broken_levels.append(
                    high["price"]
                )


                break



        # -------------------------
        # Bearish BOS
        # -------------------------

        for low in major_lows:

            if (
                current_date > low["date"]
                and
                close < low["price"]
                and
                not already_detected(low["price"])
            ):

                confidence = min(
                    round(
                        70 +
                        low["strength"],
                        2
                    ),
                    99
                )


                events.append({

                    "date": current_date,

                    "type": "BEARISH",

                    "level":
                        low["price"],

                    "strength":
                        low["strength"],

                    "confidence":
                        confidence

                })


                broken_levels.append(
                    low["price"]
                )


                break


    return events