"""
BrainTrader
------------------------
Trendline Engine

Version 3

Features
--------
- Ascending Trendline
- Descending Trendline
- Multi Swing Validation
- Touch Count
- Strength
- Confidence
"""


LOOKBACK = 6


def confidence_score(touches, total):

    if total == 0:
        return 0

    return round((touches / total) * 100, 2)


def build_uptrend(lows):

    if len(lows) < 3:
        return None

    recent = lows[-LOOKBACK:]

    # Overall trend must rise
    if recent[-1]["price"] <= recent[0]["price"]:
        return None

    touches = 1

    for i in range(1, len(recent)):

        if recent[i]["price"] > recent[i - 1]["price"]:
            touches += 1

    if touches < 3:
        return None

    return {

        "direction": "ASCENDING",

        "start": recent[0],

        "end": recent[-1],

        "touches": touches,

        "strength": round(
            touches / len(recent),
            2
        ),

        "confidence": confidence_score(
            touches,
            len(recent)
        )

    }


def build_downtrend(highs):

    if len(highs) < 3:
        return None

    recent = highs[-LOOKBACK:]

    # Overall trend must fall
    if recent[-1]["price"] >= recent[0]["price"]:
        return None

    touches = 1

    for i in range(1, len(recent)):

        if recent[i]["price"] < recent[i - 1]["price"]:
            touches += 1

    if touches < 3:
        return None

    return {

        "direction": "DESCENDING",

        "start": recent[0],

        "end": recent[-1],

        "touches": touches,

        "strength": round(
            touches / len(recent),
            2
        ),

        "confidence": confidence_score(
            touches,
            len(recent)
        )

    }


def detect_trendlines(swings):

    if not swings:

        return {

            "uptrend": None,

            "downtrend": None

        }

    lows = [

        swing

        for swing in swings

        if swing["type"] == "LOW"

    ]

    highs = [

        swing

        for swing in swings

        if swing["type"] == "HIGH"

    ]

    return {

        "uptrend": build_uptrend(
            lows
        ),

        "downtrend": build_downtrend(
            highs
        )

    }