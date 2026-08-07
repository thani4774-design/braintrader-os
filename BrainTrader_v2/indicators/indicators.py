"""
BrainTrader V2
------------------------
Module: Indicators

Calculates technical indicators used throughout
BrainTrader.

Current Indicators
------------------
✓ EMA20
✓ EMA50
✓ EMA100
✓ EMA200
✓ RSI
✓ ATR
✓ MACD
✓ MACD Signal
✓ Volume Average
✓ ADX
"""

import pandas as pd


def calculate_indicators(df):
    """
    Calculate all technical indicators.

    Parameters
    ----------
    df : pandas.DataFrame

    Returns
    -------
    pandas.DataFrame
    """

    required_columns = [
        "Open",
        "High",
        "Low",
        "Close",
        "Volume"
    ]

    for column in required_columns:
        if column not in df.columns:
            raise ValueError(f"Missing required column: {column}")

    # ==========================================
    # EMA
    # ==========================================

    df["EMA20"] = df["Close"].ewm(span=20, adjust=False).mean()
    df["EMA50"] = df["Close"].ewm(span=50, adjust=False).mean()
    df["EMA100"] = df["Close"].ewm(span=100, adjust=False).mean()
    df["EMA200"] = df["Close"].ewm(span=200, adjust=False).mean()

    # ==========================================
    # RSI
    # ==========================================

    delta = df["Close"].diff()

    gain = delta.where(delta > 0, 0)
    loss = -delta.where(delta < 0, 0)

    avg_gain = gain.rolling(14).mean()
    avg_loss = loss.rolling(14).mean()

    rs = avg_gain / avg_loss

    df["RSI"] = 100 - (100 / (1 + rs))

    # ==========================================
    # ATR
    # ==========================================

    high_low = df["High"] - df["Low"]
    high_close = (df["High"] - df["Close"].shift()).abs()
    low_close = (df["Low"] - df["Close"].shift()).abs()

    true_range = pd.concat(
        [high_low, high_close, low_close],
        axis=1
    ).max(axis=1)

    df["ATR"] = true_range.rolling(14).mean()

    # ==========================================
    # MACD
    # ==========================================

    ema12 = df["Close"].ewm(span=12, adjust=False).mean()
    ema26 = df["Close"].ewm(span=26, adjust=False).mean()

    df["MACD"] = ema12 - ema26

    df["MACD_Signal"] = (
        df["MACD"]
        .ewm(span=9, adjust=False)
        .mean()
    )

    # ==========================================
    # Volume Average
    # ==========================================

    df["Volume_Avg"] = (
        df["Volume"]
        .rolling(20)
        .mean()
    )

    # ==========================================
    # ADX
    # ==========================================

    period = 14

    up_move = df["High"] - df["High"].shift(1)
    down_move = df["Low"].shift(1) - df["Low"]

    plus_dm = pd.Series(0.0, index=df.index)
    minus_dm = pd.Series(0.0, index=df.index)

    plus_dm[(up_move > down_move) & (up_move > 0)] = up_move
    minus_dm[(down_move > up_move) & (down_move > 0)] = down_move

    tr14 = true_range.rolling(period).sum()

    plus_di = (
        plus_dm.rolling(period).sum() / tr14
    ) * 100

    minus_di = (
        minus_dm.rolling(period).sum() / tr14
    ) * 100

    dx = (
        (plus_di - minus_di).abs()
        /
        (plus_di + minus_di)
    ) * 100

    df["ADX"] = dx.rolling(period).mean()

    return df