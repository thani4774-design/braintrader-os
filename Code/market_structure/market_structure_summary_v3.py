"""
BrainTrader
------------------------
Market Structure Summary V3

Improved interpretation engine.

Uses:
- Recent swing priority
- HH HL LH LL structure
- BOS
- CHoCH
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
    # Recent swings weighted
    # ---------------------------------

    recent_swings = swings[-5:]

    weights = [1, 1, 2, 2, 3]


    for swing, weight in zip(
        recent_swings,
        weights
    ):

        label = swing.get("label")

        importance = swing.get(
            "importance",
            "NORMAL"
        )


        base = 5


        if importance == "MAJOR":
            base = 10

        elif importance == "WEAK":
            base = 3


        value = base * weight


        if label == "HH":

            score += value
            reasons.append(
                "Higher High detected"
            )


        elif label == "HL":

            score += value
            reasons.append(
                "Higher Low detected"
            )


        elif label == "LH":

            score -= value
            reasons.append(
                "Lower High detected"
            )


        elif label == "LL":

            score -= value
            reasons.append(
                "Lower Low detected"
            )


    # ---------------------------------
    # BOS influence
    # ---------------------------------

    last_bos = None


    if bos_events:

        last_bos = bos_events[-1]


        if last_bos["type"] == "BULLISH":

            score += 15

            reasons.append(
                "Latest Bullish BOS"
            )


        else:

            score -= 15

            reasons.append(
                "Latest Bearish BOS"
            )


    # ---------------------------------
    # CHoCH influence
    # ---------------------------------

    last_choch = None


    if choch_events:

        last_choch = choch_events[-1]


        if "BULLISH" in last_choch["type"]:

            score += 20

            reasons.append(
                "Bullish CHoCH reversal"
            )


        else:

            score -= 20

            reasons.append(
                "Bearish CHoCH reversal"
            )


    # ---------------------------------
    # Trend classification
    # ---------------------------------

    if score >= 50:

        trend = "BULLISH"


    elif score >= 20:

        trend = "BULLISH_TRANSITION"


    elif score <= -50:

        trend = "BEARISH"


    elif score <= -20:

        trend = "BEARISH_TRANSITION"


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