def stock_recommendation(stock_name, current_price, buy_price):

    if current_price <= buy_price:
        print("\n========== BrainTrader ==========")
        print("Stock :", stock_name)
        print("Signal: BUY ✅")
    else:
        print("\n========== BrainTrader ==========")
        print("Stock :", stock_name)
        print("Signal: WAIT ⏳")


stock_recommendation("TCS", 3490, 3500)
stock_recommendation("INFY", 1715, 1700)
stock_recommendation("RELIANCE", 1498, 1500)