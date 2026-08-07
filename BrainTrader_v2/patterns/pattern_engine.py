"""
BrainTrader V2
------------------------
Module: Pattern Engine

Purpose:
    Central controller for all chart pattern detection.
"""


from patterns.double_top import detect_double_top
from patterns.double_bottom import detect_double_bottom
from patterns.head_shoulders import detect_head_shoulders
from patterns.inverse_head_shoulders import detect_inverse_head_shoulders
from patterns.triangles import detect_triangles
from patterns.wedges import detect_wedges
from patterns.flags import detect_flags



def detect_patterns(swings):
    """
    Run all available pattern detectors.

    Parameters
    ----------
    swings : list[SwingPoint]

    Returns
    -------
    list
        Detected patterns
    """

    patterns = []


    # =========================
    # Reversal Patterns
    # =========================

    patterns.extend(
        detect_double_top(swings)
    )

    patterns.extend(
        detect_double_bottom(swings)
    )

    patterns.extend(
        detect_head_shoulders(swings)
    )

    patterns.extend(
        detect_inverse_head_shoulders(swings)
    )


    # =========================
    # Continuation Patterns
    # =========================

    patterns.extend(
        detect_triangles(swings)
    )

    patterns.extend(
        detect_wedges(swings)
    )

    patterns.extend(
        detect_flags(swings)
    )


    return patterns