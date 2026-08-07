"""
BrainTrader
------------------------
Candlestick Pattern Engine

Detects major bullish and bearish
candlestick patterns.
"""


def detect_patterns(df):
    """
    Detect candlestick patterns.

    Parameters
    ----------
    df : DataFrame

    Returns
    -------
    dict
    """

    if len(df) < 3:

        return {

            "patterns": [],

            "bullish": False,

            "bearish": False

        }

    latest = df.iloc[-1]

    previous = df.iloc[-2]

    third = df.iloc[-3]

    patterns = []

    bullish = False

    bearish = False

    # ---------------------------------
    # Candle Body
    # ---------------------------------

    body = abs(
        latest["Close"] -
        latest["Open"]
    )

    upper_shadow = (

        latest["High"] -

        max(
            latest["Open"],
            latest["Close"]
        )

    )

    lower_shadow = (

        min(
            latest["Open"],
            latest["Close"]
        )

        -

        latest["Low"]

    )

    # ---------------------------------
    # Hammer
    # ---------------------------------

    if (

        lower_shadow > body * 2

        and

        upper_shadow < body

    ):

        patterns.append("HAMMER")

        bullish = True

    # ---------------------------------
    # Inverted Hammer
    # ---------------------------------

    if (

        upper_shadow > body * 2

        and

        lower_shadow < body

    ):

        patterns.append(
            "INVERTED_HAMMER"
        )

    # ---------------------------------
    # Doji
    # ---------------------------------

    if body <= (

        latest["High"] -

        latest["Low"]

    ) * 0.1:

        patterns.append("DOJI")

    # ---------------------------------
    # Bullish Engulfing
    # ---------------------------------

    if (

        previous["Close"] <
        previous["Open"]

        and

        latest["Close"] >
        latest["Open"]

        and

        latest["Close"] >
        previous["Open"]

        and

        latest["Open"] <
        previous["Close"]

    ):

        patterns.append(
            "BULLISH_ENGULFING"
        )

        bullish = True

    # ---------------------------------
    # Bearish Engulfing
    # ---------------------------------

    if (

        previous["Close"] >
        previous["Open"]

        and

        latest["Close"] <
        latest["Open"]

        and

        latest["Open"] >
        previous["Close"]

        and

        latest["Close"] <
        previous["Open"]

    ):

        patterns.append(
            "BEARISH_ENGULFING"
        )

        bearish = True

    # ---------------------------------
    # Morning Star
    # ---------------------------------

    if (

        third["Close"] <
        third["Open"]

        and

        abs(
            previous["Close"] -
            previous["Open"]
        )

        <

        abs(
            third["Close"] -
            third["Open"]
        ) * 0.5

        and

        latest["Close"] >
        latest["Open"]

    ):

        patterns.append(
            "MORNING_STAR"
        )

        bullish = True

    # ---------------------------------
    # Evening Star
    # ---------------------------------

    if (

        third["Close"] >
        third["Open"]

        and

        abs(
            previous["Close"] -
            previous["Open"]
        )

        <

        abs(
            third["Close"] -
            third["Open"]
        ) * 0.5

        and

        latest["Close"] <
        latest["Open"]

    ):

        patterns.append(
            "EVENING_STAR"
        )

        bearish = True

    # ---------------------------------
    # Shooting Star
    # ---------------------------------

    if (

        upper_shadow > body * 2

        and

        lower_shadow < body

        and

        latest["Close"] <
        latest["Open"]

    ):

        patterns.append(
            "SHOOTING_STAR"
        )

        bearish = True

    return {

        "patterns": patterns,

        "bullish": bullish,

        "bearish": bearish

    }