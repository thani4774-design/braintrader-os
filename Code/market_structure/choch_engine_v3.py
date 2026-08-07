"""
BrainTrader
------------------------
CHoCH Engine V3

Filters weak structure changes.
"""


def detect_choch(df, swings):

    events = []

    last_LH = None
    last_HL = None


    for swing in swings:


        label = swing.get("label")

        importance = swing.get(
            "importance",
            "WEAK"
        )

        strength = swing.get(
            "strength",
            0
        )


        # ignore weak swings

        if importance == "WEAK":
            continue


        # store resistance

        if label == "LH":

            last_LH = swing



        # store support

        if label == "HL":

            last_HL = swing



        # -------------------------
        # Bullish CHoCH
        # -------------------------

        if (
            swing["type"] == "HIGH"
            and
            last_LH
            and
            swing["price"] > last_LH["price"]
            and
            strength >= 5
        ):

            events.append({

                "date": swing["date"],

                "type": "BULLISH_CHOCH",

                "level": last_LH["price"],

                "strength": strength,

                "confidence":
                    round(
                        70 + strength,
                        2
                    )

            })

            last_LH = None



        # -------------------------
        # Bearish CHoCH
        # -------------------------

        if (
            swing["type"] == "LOW"
            and
            last_HL
            and
            swing["price"] < last_HL["price"]
            and
            strength >= 5
        ):

            events.append({

                "date": swing["date"],

                "type": "BEARISH_CHOCH",

                "level": last_HL["price"],

                "strength": strength,

                "confidence":
                    round(
                        70 + strength,
                        2
                    )

            })

            last_HL = None



    return events