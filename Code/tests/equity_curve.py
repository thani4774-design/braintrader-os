import matplotlib.pyplot as plt


def plot_equity_curve(equity_curve):

    plt.figure(figsize=(10,5))

    plt.plot(equity_curve)

    plt.title("BrainTrader Equity Curve")
    plt.xlabel("Trades")
    plt.ylabel("Account Value")

    plt.grid(True)

    plt.show()