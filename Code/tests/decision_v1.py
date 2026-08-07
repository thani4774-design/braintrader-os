stock_name = input("Enter Stock Name: ")
current_price = float(input("Enter Current Price: "))
buy_price = float(input("Enter Buy Price: "))

if current_price <= buy_price:
    print("\n✅ BUY SIGNAL")
    print("Stock:", stock_name)
else:
    print("\n⏳ WAIT")
    print("Current price is above the buy price.")