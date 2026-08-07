"""
BrainTrader V2
------------------------
Module: Support & Resistance

Purpose:
    Detect major Support and Resistance levels
    using confirmed Swing Points.
"""

from market_structure.models import SwingPoint


def detect_support_resistance(swings):
    """
    Detect Support and Resistance levels.

    Parameters
    ----------
    swings : list[SwingPoint]

    Returns
    -------
    dict
    {
        "support": [...],
        "resistance": [...]
    }
    """

    support = []
    resistance = []

    for swing in swings:

        if swing.type == "LOW":
            support.append({
                "date": swing.date,
                "price": swing.price
            })

        elif swing.type == "HIGH":
            resistance.append({
                "date": swing.date,
                "price": swing.price
            })

    return {
        "support": support,
        "resistance": resistance
    }