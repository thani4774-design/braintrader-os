def score_report(df):

    latest = df.iloc[-1]

    report = []

    if latest["EMA20"] > latest["EMA50"]:
        report.append("EMA20 above EMA50 +20")

    if latest["EMA50"] > latest["EMA100"]:
        report.append("EMA50 above EMA100 +20")

    if latest["EMA100"] > latest["EMA200"]:
        report.append("EMA100 above EMA200 +20")


    rsi = latest["RSI"]

    if 40 <= rsi <= 70:
        report.append("RSI healthy +20")

    elif 30 <= rsi < 40:
        report.append("RSI recovery zone +10")

    elif 20 <= rsi < 30:
        report.append("RSI oversold zone +5")


    if latest["MACD"] > latest["MACD_Signal"]:
        report.append("MACD bullish +20")

    else:
        report.append("MACD not confirmed")


    if latest["Volume"] > latest["Volume_Avg"]:
        report.append("Volume confirmation +10")

    else:
        report.append("Volume not confirmed")
    return report