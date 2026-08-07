"""
BrainTrader
------------------------
Swing Classifier (Hardened)

Classifies swing points into:
HH = Higher High
LH = Lower High
EH = Equal High (Liquidity Pool)
HL = Higher Low
LL = Lower Low
EL = Equal Low (Liquidity Pool)
"""

def classify_swings(swings: list) -> list:
    """
    Classify swing highs and lows, specifically separating out 
    Equal Highs and Equal Lows for downstream liquidity detection.
    """
    previous_high = None
    previous_low = None
    classified = []

    for swing in swings:
        # Create a shallow copy to avoid mutating the upstream dictionaries
        new_swing = swing.copy()

        if swing["type"] == "HIGH":
            if previous_high is None:
                new_swing["label"] = "FIRST_HIGH"
            elif swing["price"] > previous_high:
                new_swing["label"] = "HH"
            elif swing["price"] < previous_high:
                new_swing["label"] = "LH"
            else:
                # Critical for SMC: Identifies built-up buy-side liquidity
                new_swing["label"] = "EH"  
            
            previous_high = swing["price"]

        elif swing["type"] == "LOW":
            if previous_low is None:
                new_swing["label"] = "FIRST_LOW"
            elif swing["price"] > previous_low:
                new_swing["label"] = "HL"
            elif swing["price"] < previous_low:
                new_swing["label"] = "LL"
            else:
                # Critical for SMC: Identifies built-up sell-side liquidity
                new_swing["label"] = "EL"
                
            previous_low = swing["price"]

        classified.append(new_swing)

    return classified