watchlist = [
    {"stock": "TCS", "current": 3490, "buy": 3500},
    {"stock": "INFY", "current": 1715, "buy": 1700},
    {"stock": "RELIANCE", "current": 1498, "buy": 1500},
    {"stock": "ITC", "current": 420, "buy": 415},
    {"stock": "SBIN", "current": 805, "buy": 810}
]

print("\n========== BrainTrader Recommendations ==========\n")

for stock in watchlist:

    if stock["current"] <= stock["buy"]:
        signal = "BUY ✅"
    else:
        signal = "WAIT ⏳"

    print(f"Stock : {stock['stock']}")
    print(f"Current Price : {stock['current']}")
    print(f"Buy Price : {stock['buy']}")
    print(f"Signal : {signal}")
    print("--------------------------------")