def calculate_score(df):

    score = 0

    latest = df.iloc[-1]


    # EMA Trend score

    if latest["EMA20"] > latest["EMA50"]:
        score += 20

    if latest["EMA50"] > latest["EMA100"]:
        score += 20

    if latest["EMA100"] > latest["EMA200"]:
        score += 20


    # RSI score

    rsi = latest["RSI"]

    if 40 <= rsi <= 70:
        score += 20

    elif 30 <= rsi < 40:
        score += 10

    elif 20 <= rsi < 30:
        score += 5


    # MACD score

    if latest["MACD"] > latest["MACD_Signal"]:
        score += 20


    # Volume score

    if latest["Volume"] > latest["Volume_Avg"]:
        score += 10
    return score