"""
BrainTrader
------------------------
Indicator Confirmation Engine

Confirms whether technical
indicators support the
market structure.

Version 1
"""

def indicator_confirmation(df):

    latest = df.iloc[-1]

    score = 0

    details = {}

    # ==========================
    # EMA
    # ==========================

    ema = (
        latest["EMA20"] >
        latest["EMA50"] >
        latest["EMA100"] >
        latest["EMA200"]
    )

    details["EMA"] = ema

    if ema:
        score += 20

    # ==========================
    # RSI
    # ==========================

    rsi = latest["RSI"]

    rsi_ok = 45 <= rsi <= 70

    details["RSI"] = rsi_ok

    if rsi_ok:
        score += 15

    # ==========================
    # MACD
    # ==========================

    macd = latest["MACD"] > latest["MACD_Signal"]

    details["MACD"] = macd

    if macd:
        score += 20

    # ==========================
    # Volume
    # ==========================

    volume = latest["Volume"] > latest["Volume_Avg"]

    details["Volume"] = volume

    if volume:
        score += 10

    # ==========================
    # ADX
    # ==========================

    if "ADX" in df.columns:

        adx = latest["ADX"] >= 25

    else:

        adx = False

    details["ADX"] = adx

    if adx:
        score += 20

    # ==========================
    # Ichimoku
    # ==========================

    if (
        "Ichimoku_Conversion" in df.columns and
        "Ichimoku_Base" in df.columns
    ):

        ichi = (
            latest["Ichimoku_Conversion"] >
            latest["Ichimoku_Base"]
        )

    else:

        ichi = False

    details["ICHIMOKU"] = ichi

    if ichi:
        score += 15

    return {

        "score": score,

        "details": details

    }