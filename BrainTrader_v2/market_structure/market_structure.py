"""
BrainTrader V2
------------------------
Module: Market Structure

Purpose:
    Classify swing points into:
    - Higher High (HH)
    - Higher Low (HL)
    - Lower High (LH)
    - Lower Low (LL)
"""

from market_structure.models import SwingPoint


def detect_market_structure(swings):
    """
    Classify swing points into HH, HL, LH and LL.

    Parameters
    ----------
    swings : list[SwingPoint]

    Returns
    -------
    list[dict]
    """

    structure = []

    previous_high = None
    previous_low = None

    for swing in swings:

        label = None

        if swing.type == "HIGH":

            if previous_high is None:
                label = "SH"      # First Swing High
            elif swing.price > previous_high.price:
                label = "HH"
            else:
                label = "LH"

            previous_high = swing

        elif swing.type == "LOW":

            if previous_low is None:
                label = "SL"      # First Swing Low
            elif swing.price > previous_low.price:
                label = "HL"
            else:
                label = "LL"

            previous_low = swing

        structure.append({
            "date": swing.date,
            "type": swing.type,
            "price": swing.price,
            "structure": label
        })

    return structure