"""
BrainTrader
------------------------
Market Structure Summary V2

Creates overall market structure interpretation
using:

- Swing labels (HH, HL, LH, LL)
- BOS events
- CHoCH events
- Swing importance
"""


def create_structure_summary(
        swings,
        bos_events,
        choch_events
):

    score = 0
    reasons = []


    # ---------------------------------
    # Recent swing structure
    # ---------------------------------

    recent_swings = swings[-5:]


    for swing in recent_swings:

        label = swing.get("label")
        importance = swing.get("importance")


        weight = 5

        if importance == "MAJOR":
            weight = 15

        elif importance == "NORMAL":
            weight = 10


        if label == "HH":

            score += weight
            reasons.append(
                "Higher High formed"
            )


        elif label == "HL":

            score += weight
            reasons.append(
                "Higher Low formed"
            )


        elif label == "LH":

            score -= weight
            reasons.append(
                "Lower High formed"
            )


        elif label == "LL":

            score -= weight
            reasons.append(
                "Lower Low formed"
            )


    # ---------------------------------
    # Latest BOS
    # ---------------------------------

    last_bos = None

    if bos_events:

        last_bos = bos_events[-1]


        if last_bos["type"] == "BULLISH":

            score += 15

            reasons.append(
                "Bullish BOS"
            )


        elif last_bos["type"] == "BEARISH":

            score -= 15

            reasons.append(
                "Bearish BOS"
            )



    # ---------------------------------
    # Latest CHoCH
    # ---------------------------------

    last_choch = None

    if choch_events:

        last_choch = choch_events[-1]


        if "BULLISH" in last_choch["type"]:

            score += 20

            reasons.append(
                "Bullish CHoCH"
            )


        elif "BEARISH" in last_choch["type"]:

            score -= 20

            reasons.append(
                "Bearish CHoCH"
            )



    # ---------------------------------
    # Final trend
    # ---------------------------------

    if score >= 30:

        trend = "BULLISH"

    elif score <= -30:

        trend = "BEARISH"

    else:

        trend = "SIDEWAYS"



    # ---------------------------------
    # Confidence
    # ---------------------------------

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