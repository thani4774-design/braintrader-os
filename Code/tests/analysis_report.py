def analysis_report(stock, score, signal, df):

    latest = df.iloc[-1]

    print("\n----------------------------")
    print("Stock:", stock)
    print("Signal:", signal)
    print("Score:", score, "/100")

    print("RSI:", round(latest["RSI"], 2))
    print("MACD:", round(latest["MACD"], 2))
    print("MACD Signal:", round(latest["MACD_Signal"], 2))
    print("ATR:", round(latest["ATR"], 2))

    if score >= 80:
     print("Status: 🔥 STRONG BUY")

    elif score >= 70:
     print("Status: ✅ BUY ZONE")

    elif score >= 50:
     print("Status: ⏳ WAIT")

    else:
     print("Status: ❌ AVOID")