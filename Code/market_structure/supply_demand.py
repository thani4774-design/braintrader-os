"""
BrainTrader
------------------------
Supply & Demand Engine

Version 2

Detects

• Rally Base Rally (RBR)
• Drop Base Drop (DBD)

The remaining patterns (DBR/RBD)
will be added in the next version.
"""


BASE_THRESHOLD = 1.0
IMPULSE_THRESHOLD = 3.0
MAX_BASE_CANDLES = 5


def body_percent(candle):

    return (
        abs(candle["Close"] - candle["Open"])
        / candle["Open"]
    ) * 100


def bullish(candle):

    return candle["Close"] > candle["Open"]


def bearish(candle):

    return candle["Close"] < candle["Open"]


def detect_supply_demand(df):

    demand = []
    supply = []

    if len(df) < 10:

        return {

            "demand": demand,

            "supply": supply

        }

    i = 1

    while i < len(df) - 1:

        first = df.iloc[i]

        # -------------------------
        # Rally
        # -------------------------

        if (

            bullish(first)

            and

            body_percent(first) >= IMPULSE_THRESHOLD

        ):

            base = []

            j = i + 1

            while (

                j < len(df)

                and

                len(base) < MAX_BASE_CANDLES

            ):

                candle = df.iloc[j]

                if body_percent(candle) <= BASE_THRESHOLD:

                    base.append(candle)

                    j += 1

                else:

                    break

            if (

                len(base) >= 1

                and

                j < len(df)

            ):

                last = df.iloc[j]

                if (

                    bullish(last)

                    and

                    body_percent(last) >= IMPULSE_THRESHOLD

                ):

                    demand.append(

                        {

                            "pattern": "RBR",

                            "date": base[0]["Date"],

                            "low": min(
                                x["Low"]
                                for x in base
                            ),

                            "high": max(
                                x["High"]
                                for x in base
                            ),

                            "base_candles": len(base)

                        }

                    )

                    i = j

        # -------------------------
        # Drop
        # -------------------------

        elif (

            bearish(first)

            and

            body_percent(first) >= IMPULSE_THRESHOLD

        ):

            base = []

            j = i + 1

            while (

                j < len(df)

                and

                len(base) < MAX_BASE_CANDLES

            ):

                candle = df.iloc[j]

                if body_percent(candle) <= BASE_THRESHOLD:

                    base.append(candle)

                    j += 1

                else:

                    break

            if (

                len(base) >= 1

                and

                j < len(df)

            ):

                last = df.iloc[j]

                if (

                    bearish(last)

                    and

                    body_percent(last) >= IMPULSE_THRESHOLD

                ):

                    supply.append(

                        {

                            "pattern": "DBD",

                            "date": base[0]["Date"],

                            "low": min(
                                x["Low"]
                                for x in base
                            ),

                            "high": max(
                                x["High"]
                                for x in base
                            ),

                            "base_candles": len(base)

                        }

                    )

                    i = j

        i += 1

    return {

        "demand": demand,

        "supply": supply

    }