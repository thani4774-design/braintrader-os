"""
BrainTrader
------------------------
Historical Multi-Timeframe Engine

Builds date-aware MTF analysis from historical daily OHLCV data. It is intended
for backtests, where each analysis must use only information available then.
"""

import pandas as pd

from market_structure.mtf_decision_engine import calculate_alignment, generate_reason
from mtf_score_engine import calculate_mtf_score
from multi_timeframe_structure import analyze_timeframe_data


TIMEFRAME_CONFIG = {
    "MACRO_15Y": {"rule": "ME", "bars": 180},
    "MAJOR_5Y": {"rule": "W-FRI", "bars": 260},
    "CURRENT_2Y": {"rule": None, "bars": 504},
    "ENTRY_6M": {"rule": None, "bars": 126},
}


def _resample_ohlcv(df, rule):
    """Resample daily OHLCV data while preserving standard candle fields."""
    indexed = df.set_index("Date").sort_index()
    aggregation = {
        "Open": "first",
        "High": "max",
        "Low": "min",
        "Close": "last",
        "Volume": "sum",
    }

    try:
        sampled = indexed.resample(rule).agg(aggregation)
    except ValueError:
        # Older pandas versions use M instead of ME for month-end resampling.
        if rule == "ME":
            sampled = indexed.resample("M").agg(aggregation)
        else:
            raise

    return sampled.dropna(subset=["Open", "High", "Low", "Close"]).reset_index()


def analyze_historical_mtf(df, as_of_date):
    """Return MTF analysis using data available on or before ``as_of_date``.

    Parameters
    ----------
    df : pandas.DataFrame
        Daily OHLCV history containing a ``Date`` column.
    as_of_date : date-like
        The historical point at which the analysis is performed.

    Returns
    -------
    dict or None
        Timeframe results, score, alignment, and reasons. Returns ``None`` if
        any required timeframe lacks enough historical data.
    """
    required_columns = {"Date", "Open", "High", "Low", "Close", "Volume"}
    missing_columns = required_columns.difference(df.columns)
    if missing_columns:
        raise ValueError(f"Missing required columns: {sorted(missing_columns)}")

    history = df.copy()
    history["Date"] = pd.to_datetime(history["Date"])
    history = history[history["Date"] <= pd.Timestamp(as_of_date)].copy()

    if history.empty:
        return None

    results = {}

    for name, config in TIMEFRAME_CONFIG.items():
        timeframe_df = history

        if config["rule"]:
            timeframe_df = _resample_ohlcv(timeframe_df, config["rule"])

        if len(timeframe_df) < config["bars"]:
            return None

        timeframe_df = timeframe_df.tail(config["bars"]).copy()
        results[name] = analyze_timeframe_data(timeframe_df)

        if not results[name]:
            return None

    alignment = calculate_alignment(results)
    mtf_score = calculate_mtf_score(results)

    return {
        "results": results,
        "mtf_score": mtf_score,
        "alignment": alignment,
        "reasons": generate_reason(results),
    }
