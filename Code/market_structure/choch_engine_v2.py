"""
BrainTrader
------------------------
CHoCH Engine V2

Detects Change of Character
using HH/HL/LH/LL structure.
"""


def detect_choch(df, swings):

    events = []

    last_LH = None
    last_HL = None


    for swing in swings:


        label = swing.get("label")


        # Store bearish structure resistance

        if label == "LH":

            last_LH = swing


        # Store bullish structure support

        if label == "HL":

            last_HL = swing



        # -------------------------
        # Bullish CHoCH
        # Break above LH
        # -------------------------

        if (
            swing["type"] == "HIGH"
            and
            last_LH
            and
            swing["price"] > last_LH["price"]
            and
            swing["date"] != last_LH["date"]
        ):

            events.append({

                "date": swing["date"],

                "type": "BULLISH_CHOCH",

                "level": last_LH["price"],

                "strength": swing.get(
                    "strength",
                    0
                )

            })

            last_LH = None



        # -------------------------
        # Bearish CHoCH
        # Break below HL
        # -------------------------

        if (
            swing["type"] == "LOW"
            and
            last_HL
            and
            swing["price"] < last_HL["price"]
            and
            swing["date"] != last_HL["date"]
        ):

            events.append({

                "date": swing["date"],

                "type": "BEARISH_CHOCH",

                "level": last_HL["price"],

                "strength": swing.get(
                    "strength",
                    0
                )

            })

            last_HL = None


    return events