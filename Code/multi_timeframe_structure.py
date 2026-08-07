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


def analyze_timeframe_data(df):
    """Analyze market structure from an already available OHLCV dataframe.

    This function makes it possible to analyze a historical data slice during
    a backtest without downloading today's data or exposing future candles.
    """
    if df is None or df.empty:
        return None

    df = df.copy()

    # Handle yfinance multi-index columns.
    if isinstance(df.columns, pd.MultiIndex):
        df.columns = df.columns.get_level_values(0)

    if "Date" not in df.columns:
        df = df.reset_index()
    else:
        df = df.reset_index(drop=True)

    df = calculate_indicators(df)

    # Swing Detection
    swings = detect_swings(df)
    swings = classify_swings(swings)
    swings = calculate_swing_strength(swings)
    swings = analyze_swings(swings)

    # Market Structure Events
    bos_events = detect_bos(df, swings)
    choch_events = detect_choch(df, swings)

    summary = create_structure_summary(
        swings,
        bos_events,
        choch_events,
    )

    return summary


def analyze_timeframe(stock, period, interval):
    """Download and analyze market structure for one stock and timeframe.

    Returns the structure summary, or ``None`` when price data is unavailable.
    """
    try:
        df = yf.download(
            stock,
            period=period,
            interval=interval,
            auto_adjust=True,
            progress=False,
        )
    except Exception:
        return None

    return analyze_timeframe_data(df)
