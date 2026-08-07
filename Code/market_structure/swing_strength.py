"""
BrainTrader
------------------------
Swing Strength Calculator

Calculates the significance of each swing
based on the percentage move from the previous
opposite swing point.
"""


def calculate_swing_strength(swings):
    """
    Add strength value to swing points.

    Parameters
    ----------
    swings : list
        Filtered swing points.

    Returns
    -------
    list
        Swing points with strength added.
    """

    if len(swings) == 0:
        return []


    enhanced = []

    previous_opposite = None


    for swing in swings:

        new_swing = swing.copy()


        if previous_opposite is None:

            new_swing["strength"] = 0


        else:

            move = abs(
                swing["price"]
                -
                previous_opposite["price"]
            )


            strength = (
                move
                /
                previous_opposite["price"]
            ) * 100


            new_swing["strength"] = round(
                strength,
                2
            )


        enhanced.append(new_swing)


        # Store only opposite swing
        if (
            previous_opposite is None
            or
            swing["type"] != previous_opposite["type"]
        ):

            previous_opposite = swing


    return enhanced