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



TEST_STOCKS = [

    "INFY.NS",
    "RELIANCE.NS",
    "HDFCBANK.NS"

]



for stock in TEST_STOCKS:


    print("\n")
    print("=" * 50)
    print("Testing:", stock)
    print("=" * 50)



    df = yf.download(

        stock,

        period="2y",

        auto_adjust=True,

        progress=False

    )



    if df.empty:

        print("No data")
        continue



    if isinstance(df.columns, pd.MultiIndex):

        df.columns = (
            df.columns
            .get_level_values(0)
        )



    df = df.reset_index()



    # =========================
    # Indicators
    # =========================

    df = calculate_indicators(df)



    # =========================
    # Swing Structure
    # =========================

    swings = detect_swings(df)


    swings = classify_swings(
        swings
    )


    swings = calculate_swing_strength(
        swings
    )


    swings = analyze_swings(
        swings
    )



    # =========================
    # BOS
    # =========================

    bos_events = detect_bos(
        df,
        swings
    )



    # =========================
    # CHoCH
    # =========================

    choch_events = detect_choch(
        df,
        swings
    )



    # =========================
    # Summary
    # =========================

    summary = create_structure_summary(

        swings,

        bos_events,

        choch_events

    )



    print(
        "Swing Points:",
        len(swings)
    )


    print(
        "BOS Events:",
        len(bos_events)
    )


    print(
        "CHoCH Events:",
        len(choch_events)
    )



    print(
        "\n========== STRUCTURE SUMMARY =========="
    )


    print(
        "Trend:",
        summary["trend"]
    )


    print(
        "Confidence:",
        summary["confidence"],
        "%"
    )



    if summary["last_bos"]:

        print(

            "Last BOS:",

            summary["last_bos"]["type"],

            "| Level:",

            round(
                summary["last_bos"]["level"],
                2
            )

        )



    if summary["last_choch"]:

        print(

            "Last CHoCH:",

            summary["last_choch"]["type"],

            "| Level:",

            round(
                summary["last_choch"]["level"],
                2
            )

        )



    print(
        "\nLatest Structure:"
    )


    for swing in swings[-5:]:

        print(

            str(swing["date"])[:10],

            "|",

            swing["type"],

            "|",

            swing.get("label"),

            "|",

            round(
                swing["price"],
                2
            ),

            "|",

            swing.get("importance"),

            "| Strength:",

            swing.get("strength")

        )