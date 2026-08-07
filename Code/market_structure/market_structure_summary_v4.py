"""
BrainTrader
------------------------
Market Structure Summary V4

Trend maturity engine.

Classifies:

BULLISH
BULLISH_TRANSITION
BEARISH
BEARISH_TRANSITION
SIDEWAYS
"""


def create_structure_summary(
        swings,
        bos_events,
        choch_events
):

    score = 0
    reasons = []


    recent = swings[-5:]


    labels = [
        s.get("label")
        for s in recent
    ]


    # ---------------------------------
    # Recent structure
    # ---------------------------------

    for label in labels:


        if label == "HH":

            score += 15
            reasons.append(
                "Higher High"
            )


        elif label == "HL":

            score += 12
            reasons.append(
                "Higher Low"
            )


        elif label == "LH":

            score -= 12
            reasons.append(
                "Lower High"
            )


        elif label == "LL":

            score -= 15
            reasons.append(
                "Lower Low"
            )



    # ---------------------------------
    # BOS
    # ---------------------------------

    last_bos = None


    if bos_events:

        last_bos = bos_events[-1]


        if last_bos["type"] == "BULLISH":

            score += 25

            reasons.append(
                "Bullish BOS confirmation"
            )


        else:

            score -= 25

            reasons.append(
                "Bearish BOS confirmation"
            )



    # ---------------------------------
    # CHoCH
    # ---------------------------------

    last_choch = None


    if choch_events:

        last_choch = choch_events[-1]


        if "BULLISH" in last_choch["type"]:

            score += 20

            reasons.append(
                "Bullish CHoCH"
            )


        else:

            score -= 20

            reasons.append(
                "Bearish CHoCH"
            )



    # ---------------------------------
    # Detect maturity
    # ---------------------------------

    has_hh = "HH" in labels
    has_hl = "HL" in labels
    has_lh = "LH" in labels
    has_ll = "LL" in labels


    bullish_bos = (
        last_bos
        and last_bos["type"] == "BULLISH"
    )


    bearish_bos = (
        last_bos
        and last_bos["type"] == "BEARISH"
    )



    if (
        has_hh
        and has_hl
        and bullish_bos
    ):

        trend = "BULLISH"



    elif (
        has_ll
        and has_lh
        and bearish_bos
    ):

        trend = "BEARISH"



    elif (
        "BULLISH" in str(last_choch)
        and (has_hh or has_hl)
    ):

        trend = "BULLISH_TRANSITION"



    elif (
        "BEARISH" in str(last_choch)
        and (has_ll or has_lh)
    ):

        trend = "BEARISH_TRANSITION"



    else:

        trend = "SIDEWAYS"



    confidence = abs(score)

    if confidence > 95:

        confidence = 95



    return {

        "trend": trend,

        "confidence": confidence,

        "score": score,

        "reasons": reasons,

        "last_bos": last_bos,

        "last_choch": last_choch

    }