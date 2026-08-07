"""
BrainTrader
------------------------
Market Structure Summary V5

Uses:
- Recent swing sequence
- BOS confirmation
- CHoCH reversal
- Trend maturity
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


    # -------------------------------
    # Count structure
    # -------------------------------

    hh = labels.count("HH")
    hl = labels.count("HL")

    lh = labels.count("LH")
    ll = labels.count("LL")



    score = 0
    reasons = []



    # -------------------------------
    # Structure scoring
    # -------------------------------

    if hh:
        score += hh * 15
        reasons.append("Higher High")


    if hl:
        score += hl * 12
        reasons.append("Higher Low")


    if lh:
        score -= lh * 12
        reasons.append("Lower High")


    if ll:
        score -= ll * 15
        reasons.append("Lower Low")



    # -------------------------------
    # BOS confirmation
    # -------------------------------

    bullish_bos = False
    bearish_bos = False


    if last_bos:

        if last_bos["type"] == "BULLISH":

            bullish_bos = True
            score += 20
            reasons.append(
                "Bullish BOS"
            )


        else:

            bearish_bos = True
            score -= 20
            reasons.append(
                "Bearish BOS"
            )



    # -------------------------------
    # CHoCH detection
    # -------------------------------

    bullish_choch = False
    bearish_choch = False


    if last_choch:

        if "BULLISH" in last_choch["type"]:

            bullish_choch = True
            score += 25
            reasons.append(
                "Bullish CHoCH"
            )


        elif "BEARISH" in last_choch["type"]:

            bearish_choch = True
            score -= 25
            reasons.append(
                "Bearish CHoCH"
            )



    # -------------------------------
    # Final classification
    # -------------------------------

    if (
        hh >= 1
        and hl >= 1
        and bullish_bos
    ):

        trend = "BULLISH"



    elif (
        ll >= 1
        and lh >= 1
        and bearish_bos
    ):

        trend = "BEARISH"



    elif (
        bullish_choch
        and (hh or hl)
    ):

        trend = "BULLISH_TRANSITION"



    elif (
        bearish_choch
        and (ll or lh)
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