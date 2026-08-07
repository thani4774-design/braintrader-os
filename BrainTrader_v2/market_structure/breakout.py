"""
BrainTrader V2
------------------------
Module: Breakout Detection

Purpose:
    Detect Support Breakdowns and
    Resistance Breakouts.
"""


def detect_breakouts(df, support_levels, resistance_levels):
    """
    Detect simple support and resistance breakouts.

    Parameters
    ----------
    df : pandas.DataFrame
    support_levels : list
    resistance_levels : list

    Returns
    -------
    list
    """

    breakouts = []

    latest_close = float(df["Close"].iloc[-1])
    latest_date = str(df["Date"].iloc[-1])[:10]

    # ===========================
    # Resistance Breakout
    # ===========================

    for level in resistance_levels:

        if latest_close > level["price"]:

            breakouts.append({
                "date": latest_date,
                "type": "RESISTANCE_BREAKOUT",
                "level": level["price"],
                "close": latest_close
            })

    # ===========================
    # Support Breakdown
    # ===========================

    for level in support_levels:

        if latest_close < level["price"]:

            breakouts.append({
                "date": latest_date,
                "type": "SUPPORT_BREAKDOWN",
                "level": level["price"],
                "close": latest_close
            })

    return breakouts