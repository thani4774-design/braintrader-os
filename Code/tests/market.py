import yfinance as yf
import pandas as pd


def market_condition():

    df = yf.download(
    "^NSEI",
    period="1y",
    interval="1d",
    progress=False,
    auto_adjust=True
)

    if df.empty:
        return "UNKNOWN"


    if isinstance(df.columns, pd.MultiIndex):
        df.columns = df.columns.get_level_values(0)


    close = df["Close"]


    ema200 = close.ewm(
        span=200,
        adjust=False
    ).mean()


    if float(close.iloc[-1]) > float(ema200.iloc[-1]):
        return "BULLISH"

    else:
        return "BEARISH"