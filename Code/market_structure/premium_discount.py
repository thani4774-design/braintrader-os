"""
BrainTrader
------------------------
Premium & Discount Zone Engine (Phase 3)

Calculates the Equilibrium (50% mark) of the current structural swing range.
Categorizes current price action to prevent buying in Premium zones 
and selling in Discount zones.
"""

import logging
import pandas as pd

logging.basicConfig(level=logging.INFO)

def calculate_pd_zones(swings, current_price):
    """
    Identifies the active swing range and calculates if the current price
    is in Premium (>50%), Discount (<50%), or Equilibrium (50%).
    """
    if not swings or len(swings) < 2:
        return {"zone": "UNKNOWN", "equilibrium": None, "warning": "Insufficient swing data"}

    # Filter out unconfirmed minor swings to find the true structural range
    major_swings = [s for s in swings if s.get('type') in ['HH', 'HL', 'LH', 'LL']]
    
    if len(major_swings) < 2:
        # Fallback to recent raw swings if structure isn't fully developed
        recent_highs = [s for s in swings if s['type'] in ['High', 'HH', 'LH']]
        recent_lows = [s for s in swings if s['type'] in ['Low', 'HL', 'LL']]
        
        if not recent_highs or not recent_lows:
             return {"zone": "UNKNOWN", "equilibrium": None, "warning": "No clear range"}
             
        active_high = recent_highs[-1]['price']
        active_low = recent_lows[-1]['price']
    else:
        # Grab the two most recent major structural points to define the range
        p1 = major_swings[-1]['price']
        p2 = major_swings[-2]['price']
        active_high = max(p1, p2)
        active_low = min(p1, p2)

    equilibrium = (active_high + active_low) / 2

    # Define strict zones
    if current_price > equilibrium:
        zone = "PREMIUM"
    elif current_price < equilibrium:
        zone = "DISCOUNT"
    else:
        zone = "EQUILIBRIUM"
        
    return {
        "zone": zone,
        "active_high": round(active_high, 2),
        "active_low": round(active_low, 2),
        "equilibrium": round(equilibrium, 2),
        "premium_range": f"₹{round(equilibrium, 2)} - ₹{round(active_high, 2)}",
        "discount_range": f"₹{round(active_low, 2)} - ₹{round(equilibrium, 2)}"
    }