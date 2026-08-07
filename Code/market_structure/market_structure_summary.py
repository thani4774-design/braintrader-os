"""
BrainTrader
------------------------
Market Structure Summary V6

Priority:
1. Recent CHoCH
2. Recent swing structure
3. BOS confirmation
"""


def create_structure_summary(
        swings,
        bos_events,
        choch_events
):


    last_bos = None
    last_choch = None


    if bos_events:
        last_bos = bos_events[-1]


    if choch_events:
        last_choch = choch_events[-1]



    recent = swings[-5:]


    labels = [
        s.get("label")
        for s in recent
    ]



    score = 0
    reasons = []



    # -----------------------------
    # Recent swing condition
    # -----------------------------

    last_labels = labels[-3:]



    bullish_structure = (

        "HH" in last_labels

        and

        "HL" in last_labels

    )


    bearish_structure = (

        "LL" in last_labels

        and

        "LH" in last_labels

    )



    # -----------------------------
    # CHoCH priority
    # -----------------------------

    bullish_choch = False
    bearish_choch = False


    if last_choch:


        if last_choch["type"] == "BULLISH_CHOCH":

            bullish_choch = True

            score += 30

            reasons.append(
                "Bullish CHoCH"
            )


        elif last_choch["type"] == "BEARISH_CHOCH":

            bearish_choch = True

            score -= 30

            reasons.append(
                "Bearish CHoCH"
            )



    # -----------------------------
    # Recent structure scoring
    # -----------------------------

    for label in last_labels:


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

            score -= 10
            reasons.append(
                "Lower High"
            )


        elif label == "LL":

            score -= 15
            reasons.append(
                "Lower Low"
            )



    # -----------------------------
    # BOS confirmation
    # -----------------------------

    bullish_bos = False
    bearish_bos = False


    if last_bos:


        if last_bos["type"] == "BULLISH":

            bullish_bos = True

            score += 15


            reasons.append(
                "Bullish BOS"
            )


        else:

            bearish_bos = True

            score -= 15


            reasons.append(
                "Bearish BOS"
            )



    # -----------------------------
    # Final decision
    # -----------------------------


    # Confirmed trends

    if (
        bullish_structure
        and bullish_bos
        and not bearish_choch
    ):

        trend = "BULLISH"



    elif (
        bearish_structure
        and bearish_bos
        and not bullish_choch
    ):

        trend = "BEARISH"



    # Transition states

    elif bullish_choch:

        trend = "BULLISH_TRANSITION"



    elif bearish_choch:

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