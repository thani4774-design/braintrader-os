import pandas as pd


def calculate_indicators(df):

    # =========================
    # EMA
    # =========================

    df["EMA20"] = df["Close"].ewm(
        span=20,
        adjust=False
    ).mean()

    df["EMA50"] = df["Close"].ewm(
        span=50,
        adjust=False
    ).mean()

    df["EMA100"] = df["Close"].ewm(
        span=100,
        adjust=False
    ).mean()

    df["EMA200"] = df["Close"].ewm(
        span=200,
        adjust=False
    ).mean()



    # =========================
    # RSI
    # =========================

    delta = df["Close"].diff()

    gain = delta.where(delta > 0, 0)

    loss = -delta.where(delta < 0, 0)


    avg_gain = gain.rolling(14).mean()

    avg_loss = loss.rolling(14).mean()


    rs = avg_gain / avg_loss


    df["RSI"] = (
        100 -
        (100 / (1 + rs))
    )



    # =========================
    # ATR
    # =========================

    high_low = (
        df["High"]
        -
        df["Low"]
    )


    high_close = abs(
        df["High"]
        -
        df["Close"].shift()
    )


    low_close = abs(
        df["Low"]
        -
        df["Close"].shift()
    )


    ranges = pd.concat(
        [
            high_low,
            high_close,
            low_close
        ],
        axis=1
    )


    true_range = ranges.max(axis=1)


    df["ATR"] = (
        true_range
        .rolling(14)
        .mean()
    )



    # =========================
    # MACD
    # =========================

    ema12 = df["Close"].ewm(
        span=12,
        adjust=False
    ).mean()


    ema26 = df["Close"].ewm(
        span=26,
        adjust=False
    ).mean()


    df["MACD"] = ema12 - ema26


    df["MACD_Signal"] = (
        df["MACD"]
        .ewm(
            span=9,
            adjust=False
        )
        .mean()
    )



    # =========================
    # Volume Average
    # =========================

    df["Volume_Avg"] = (
        df["Volume"]
        .rolling(20)
        .mean()
    )



    # =========================
    # ADX
    # =========================

    period = 14


    up_move = (
        df["High"]
        -
        df["High"].shift(1)
    )


    down_move = (
        df["Low"].shift(1)
        -
        df["Low"]
    )


    plus_dm = pd.Series(
        0.0,
        index=df.index
    )


    minus_dm = pd.Series(
        0.0,
        index=df.index
    )


    plus_dm[
        (up_move > down_move)
        &
        (up_move > 0)
    ] = up_move


    minus_dm[
        (down_move > up_move)
        &
        (down_move > 0)
    ] = down_move



    tr14 = (
        true_range
        .rolling(period)
        .sum()
    )


    plus_di = (
        100 *
        plus_dm
        .rolling(period)
        .sum()
        /
        tr14
    )


    minus_di = (
        100 *
        minus_dm
        .rolling(period)
        .sum()
        /
        tr14
    )


    dx = (
        abs(
            plus_di -
            minus_di
        )
        /
        (
            plus_di +
            minus_di
        )
    ) * 100


    df["ADX"] = (
        dx
        .rolling(period)
        .mean()
    )
        # =========================
    # Ichimoku Cloud
    # =========================

    # Tenkan-sen (Conversion Line)
    period9_high = df["High"].rolling(9).max()
    period9_low = df["Low"].rolling(9).min()

    df["Ichimoku_Conversion"] = (
        period9_high + period9_low
    ) / 2


    # Kijun-sen (Base Line)
    period26_high = df["High"].rolling(26).max()
    period26_low = df["Low"].rolling(26).min()

    df["Ichimoku_Base"] = (
        period26_high + period26_low
    ) / 2


    # Senkou Span A
    df["Ichimoku_Span_A"] = (
        (
            df["Ichimoku_Conversion"]
            +
            df["Ichimoku_Base"]
        ) / 2
    ).shift(26)


    # Senkou Span B
    period52_high = df["High"].rolling(52).max()
    period52_low = df["Low"].rolling(52).min()

    df["Ichimoku_Span_B"] = (
        (
            period52_high
            +
            period52_low
        ) / 2
    ).shift(26)


    # Chikou Span
    df["Ichimoku_Chikou"] = (
        df["Close"]
        .shift(-26)
    )



    return df