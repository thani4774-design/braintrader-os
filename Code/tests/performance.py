def print_performance(result):

    print("\n" + "=" * 50)
    print("      BrainTrader Performance Report")
    print("=" * 50)

    print(f"Total Trades      : {result['Total Trades']}")
    print(f"Wins              : {result['Wins']}")
    print(f"Losses            : {result['Losses']}")
    print(f"Win Rate          : {result['Win Rate']}%")
    print(f"Net Profit        : {result['Net Profit %']}%")
    print(f"CAGR              : {result['CAGR %']}%")
    print(f"Average Trade     : {result['Average Profit %']}%")
    print(f"Profit Factor     : {result['Profit Factor']}")
    print(f"Max Drawdown      : {result['Max Drawdown %']}%")

    if result["Win Rate"] >= 60:
        rating = "★★★★★ Excellent"

    elif result["Win Rate"] >= 55:
        rating = "★★★★☆ Good"

    elif result["Win Rate"] >= 50:
        rating = "★★★☆☆ Average"

    else:
        rating = "★★☆☆☆ Needs Improvement"

    print("\nStrategy Rating :", rating)
    print("=" * 50)