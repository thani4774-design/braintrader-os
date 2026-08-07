"""
BrainTrader
------------------------
Multi Timeframe Structure Engine

Timeframes:

15Y Monthly  -> Macro Trend
5Y Weekly    -> Major Trend
2Y Daily     -> Current Structure
6M Daily     -> Entry Structure
"""


import pandas as pd
import yfinance as yf


from indicators import calculate_indicators


from market_structure.swing_points import detect_swings
from market_structure.swing_classifier import classify_swings
from market_structure.swing_strength import calculate_swing_strength
from market_structure.swing_analysis import analyze_swings


from market_structure.bos_engine import detect_bos
from market_structure.choch_engine import detect_choch


from market_structure.market_structure_summary import create_structure_summary



def analyze_timeframe(
        stock,
        period,
        interval
):


    df = yf.download(

        stock,

        period=period,

        interval=interval,

        auto_adjust=True,

        progress=False

    )



    if df.empty:

        print("No data for", stock)

        return None



    # Handle yfinance multi-index

    if isinstance(
        df.columns,
        pd.MultiIndex
    ):

        df.columns = (
            df.columns
            .get_level_values(0)
        )



    df = df.reset_index()



    df = calculate_indicators(
        df
    )



    # -------------------------
    # Swing Detection
    # -------------------------

    swings = detect_swings(
        df
    )


    swings = classify_swings(
        swings
    )


    swings = calculate_swing_strength(
        swings
    )


    swings = analyze_swings(
        swings
    )



    # -------------------------
    # Market Structure Events
    # -------------------------

    bos_events = detect_bos(

        df,

        swings

    )


    choch_events = detect_choch(

        df,

        swings

    )



    summary = create_structure_summary(

        swings,

        bos_events,

        choch_events

    )



    return summary





# ==================================
# TEST
# ==================================


stock = "INFY.NS"



timeframes = {


    "MACRO_15Y":

    (
        "15y",
        "1mo"
    ),



    "MAJOR_5Y":

    (
        "5y",
        "1wk"
    ),



    "CURRENT_2Y":

    (
        "2y",
        "1d"
    ),



    "ENTRY_6M":

    (
        "6mo",
        "1d"
    )



}



print("\n")
print("=" * 60)
print("MULTI TIMEFRAME STRUCTURE")
print(stock)
print("=" * 60)




for name, (period, interval) in timeframes.items():


    print("\n------------------------")

    print(name)



    result = analyze_timeframe(

        stock,

        period,

        interval

    )



    if result is None:

        continue



    print(

        "Trend:",

        result["trend"]

    )



    print(

        "Confidence:",

        result["confidence"],

        "%"

    )



    if result["last_bos"]:


        print(

            "BOS:",

            result["last_bos"]["type"],

            "| Level:",

            round(
                result["last_bos"]["level"],
                2
            )

        )



    if result["last_choch"]:


        print(

            "CHoCH:",

            result["last_choch"]["type"],

            "| Level:",

            round(
                result["last_choch"]["level"],
                2
            )

        )