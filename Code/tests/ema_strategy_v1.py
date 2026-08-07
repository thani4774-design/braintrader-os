def get_signal(df):
    """
    Returns BUY or WAIT based on EMA alignment.
    """

    latest = df.iloc[-1]

    if (
        latest["EMA20"] > latest["EMA50"] >
        latest["EMA100"] > latest["EMA200"]
    ):
        return "BUY"

    return "WAIT"