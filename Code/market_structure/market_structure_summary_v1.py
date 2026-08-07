"""
BrainTrader
------------------------
Market Structure Summary

Combines:
- Swing classification
- BOS
- CHoCH
- Strength
"""


def create_structure_summary(
        swings,
        bos_events,
        choch_events
):


    summary = {}


    # -------------------------
    # Current swing structure
    # -------------------------

    recent = swings[-10:]


    hh = 0
    hl = 0
    lh = 0
    ll = 0


    for swing in recent:

        label = swing.get(
            "label"
        )

        if label == "HH":
            hh += 1

        elif label == "HL":
            hl += 1

        elif label == "LH":
            lh += 1

        elif label == "LL":
            ll += 1



    if hh > lh and hl > ll:

        trend = "BULLISH"


    elif lh > hh and ll > hl:

        trend = "BEARISH"


    else:

        trend = "SIDEWAYS"



    summary["trend"] = trend



    # -------------------------
    # Latest BOS
    # -------------------------

    if bos_events:

        summary["last_bos"] = (
            bos_events[-1]
        )

    else:

        summary["last_bos"] = None



    # -------------------------
    # Latest CHoCH
    # -------------------------

    if choch_events:

        summary["last_choch"] = (
            choch_events[-1]
        )

    else:

        summary["last_choch"] = None



    # -------------------------
    # Confidence
    # -------------------------

    confidence = 50


    if trend == "BULLISH":

        confidence += 15


    elif trend == "BEARISH":

        confidence += 15



    if bos_events:

        confidence += 10


    if choch_events:

        confidence += 10



    summary["confidence"] = min(
        confidence,
        95
    )


    return summary