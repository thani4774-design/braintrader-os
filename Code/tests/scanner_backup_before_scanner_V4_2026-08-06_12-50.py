"""
BrainTrader
------------------------
Scanner V3

Full Pipeline:

Multiple Timeframes
        |
Market Structure
        |
Liquidity
        |
Support Resistance
        |
Confluence Engine
        |
Trade Engine
        |
Final Decision
"""

import pandas as pd
import yfinance as yf


from indicators import calculate_indicators
from indicator_confirmation import indicator_confirmation


from multi_timeframe_structure import analyze_timeframe

from market_structure.mtf_decision_engine import calculate_alignment

from market_structure.swing_points import detect_swings
from market_structure.swing_classifier import classify_swings
from market_structure.swing_strength import calculate_swing_strength
from market_structure.swing_analysis import analyze_swings


from market_structure.support_resistance import (
    find_support_resistance,
    nearest_levels
)


from market_structure.liquidity_sweep import (
    detect_liquidity_sweeps
)


from confluence_engine import calculate_confluence

from trade_engine import generate_trade_setup


from watchlists import (
    NIFTY50,
    BANKNIFTY,
    MY_WATCHLIST
)



TIMEFRAMES = {

    "MACRO": ("15y", "1mo"),

    "MAJOR": ("5y", "1wk"),

    "CURRENT": ("2y", "1d")

}





def select_watchlist():

    print("=" * 50)
    print("BrainTrader Scanner")
    print("=" * 50)

    print("1. Nifty 50")
    print("2. Bank Nifty")
    print("3. My Watchlist")


    choice = input(
        "Enter choice: "
    )


    if choice == "2":

        return BANKNIFTY


    elif choice == "3":

        return MY_WATCHLIST


    return NIFTY50





def download_data(symbol, period, interval):


    df = yf.download(

        symbol,

        period=period,

        interval=interval,

        auto_adjust=True,

        progress=False

    )


    if df.empty:

        return None



    if isinstance(
        df.columns,
        pd.MultiIndex
    ):

        df.columns = df.columns.get_level_values(0)



    df = df.reset_index()


    return df





def analyze_stock(symbol):


    print(
        "Analyzing",
        symbol
    )



    timeframe_data = {}



    for name, settings in TIMEFRAMES.items():

        period, interval = settings


        df = download_data(

            symbol,

            period,

            interval

        )


        if df is None:

            return None



        df = calculate_indicators(
            df
        )


        timeframe_data[name] = df





    current_df = timeframe_data["CURRENT"]



    price = float(

        current_df.iloc[-1]["Close"]

    )



    indicator = indicator_confirmation(

        current_df

    )





    mtf_structure = {}



    for name, df in timeframe_data.items():


        mtf_structure[name] = analyze_timeframe(

            symbol,

            name,

            df

        )





    alignment = calculate_alignment(

        mtf_structure

    )





    swings = detect_swings(

        current_df

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





    levels = find_support_resistance(

        swings

    )



    levels = nearest_levels(

        levels,

        price

    )





    liquidity = detect_liquidity_sweeps(

        current_df,

        swings

    )





    confluence = calculate_confluence(

        structure=mtf_structure["CURRENT"],

        bos=mtf_structure["CURRENT"].get(
            "last_bos"
        ),

        choch=mtf_structure["CURRENT"].get(
            "last_choch"
        ),

        liquidity=liquidity,

        support_resistance=levels,

        indicator=indicator,

        price=price

    )





    trade_setup = generate_trade_setup(

        current_df,

        price,

        levels,

        confluence["score"],

        confluence["confidence"]

    )





    return {


        "Stock": symbol,


        "Price": price,


        "Score": confluence["score"],


        "Decision": confluence["decision"],


        "Confidence": confluence["confidence"],


        "Alignment": alignment["alignment"],


        "Reasons": confluence["reasons"],


        "Warnings": confluence["warnings"],


        "TradeSetup": trade_setup


    }





def main():


    watchlist = select_watchlist()


    results = []



    for symbol in watchlist:


        result = analyze_stock(

            symbol

        )


        if result:

            results.append(

                result

            )





    results.sort(

        key=lambda x:x["Score"],

        reverse=True

    )





    print()

    print("=" * 70)

    print("BRAINTRADER RESULTS")

    print("=" * 70)





    for item in results:


        print()

        print("=" * 60)

        print(item["Stock"])

        print("=" * 60)



        print(
            "Price:",
            round(item["Price"],2)
        )


        print(
            "Score:",
            item["Score"]
        )


        print(
            "Decision:",
            item["Decision"]
        )


        print(
            "Confidence:",
            item["Confidence"],
            "%"
        )


        print(
            "Alignment:",
            item["Alignment"]
        )



        print()

        print("Reasons")

        print("-"*30)


        for r in item["Reasons"]:

            print("-", r)




        print()

        print("Trade Setup")

        print("-"*30)


        for k,v in item["TradeSetup"].items():

            print(
                k,
                ":",
                v
            )





if __name__ == "__main__":

    main()