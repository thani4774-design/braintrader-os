import yfinance as yf
import pandas as pd


def get_market_condition():

    nifty = yf.download(
        "^NSEI",
        period="max",
        auto_adjust=True,
        progress=False
    )


    if isinstance(nifty.columns, pd.MultiIndex):
        nifty.columns = nifty.columns.get_level_values(0)


    nifty = nifty.reset_index()


    nifty["EMA200"] = (
        nifty["Close"]
        .ewm(span=200)
        .mean()
    )


    latest_close = float(
        nifty["Close"].iloc[-1]
    )

    latest_ema200 = float(
        nifty["EMA200"].iloc[-1]
    )


    if latest_close > latest_ema200:

        return True

    else:

        return False