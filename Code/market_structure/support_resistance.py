"""
BrainTrader
------------------------
Support & Resistance Engine

Works with the BrainTrader swing pipeline.

Input
-----
List of analyzed swing dictionaries.

Output
------
Support levels
Resistance levels
Level strengths
Nearest levels
Strongest levels
"""


def merge_levels(levels, tolerance=0.01):

    if not levels:
        return []

    levels = sorted(levels)

    merged = []

    group = [levels[0]]

    for level in levels[1:]:

        average = sum(group) / len(group)

        if abs(level - average) / average <= tolerance:

            group.append(level)

        else:

            merged.append(
                round(sum(group) / len(group), 2)
            )

            group = [level]

    merged.append(
        round(sum(group) / len(group), 2)
    )

    return merged


def calculate_strength(
        original_levels,
        merged_levels,
        tolerance=0.01):

    strength = {}

    for merged in merged_levels:

        count = 0

        for level in original_levels:

            if abs(level - merged) / merged <= tolerance:

                count += 1

        strength[merged] = count

    return strength


def find_support_resistance(
        swings,
        tolerance=0.01):

    if not swings:

        return {

            "supports": [],

            "resistances": [],

            "support_strength": {},

            "resistance_strength": {},

            "nearest_support": None,

            "nearest_resistance": None

        }

    support_levels = []

    resistance_levels = []

    for swing in swings:

        if swing["type"] == "LOW":

            support_levels.append(
                float(swing["price"])
            )

        elif swing["type"] == "HIGH":

            resistance_levels.append(
                float(swing["price"])
            )

    supports = merge_levels(
        support_levels,
        tolerance
    )

    resistances = merge_levels(
        resistance_levels,
        tolerance
    )

    return {

        "supports": supports,

        "resistances": resistances,

        "support_strength": calculate_strength(
            support_levels,
            supports,
            tolerance
        ),

        "resistance_strength": calculate_strength(
            resistance_levels,
            resistances,
            tolerance
        ),

        "nearest_support": None,

        "nearest_resistance": None

    }


def nearest_levels(
        levels,
        current_price):

    supports = [

        level

        for level in levels["supports"]

        if level <= current_price

    ]

    resistances = [

        level

        for level in levels["resistances"]

        if level >= current_price

    ]

    levels["nearest_support"] = (

        max(supports)

        if supports

        else None

    )

    levels["nearest_resistance"] = (

        min(resistances)

        if resistances

        else None

    )

    return levels


def strongest_support(levels):

    strengths = levels["support_strength"]

    if not strengths:

        return None

    return max(
        strengths,
        key=strengths.get
    )


def strongest_resistance(levels):

    strengths = levels["resistance_strength"]

    if not strengths:

        return None

    return max(
        strengths,
        key=strengths.get
    )