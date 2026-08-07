import yfinance as yf
import pandas as pd

from indicators import calculate_indicators
from market_structure.swing_points import detect_swings
from market_structure.market_structure import detect_market_structure

# ============================================
# Download Data
# ============================================

symbol = "INFY.NS"

df = yf.download(
    symbol,
    period="5y",
    auto_adjust=True,
    progress=False
)

if isinstance(df.columns, pd.MultiIndex):
    df.columns = df.columns.get_level_values(0)

df = df.reset_index()

# ============================================
# Calculate Indicators
# ============================================

df = calculate_indicators(df)

# ============================================
# Detect Swing Points
# ============================================

swings = detect_swings(df)

print("\nDetected Swings:", len(swings))

# ============================================
# Detect Market Structure
# ============================================

structure = detect_market_structure(swings)

print("\nMarket Structure\n")
print("-" * 70)

for item in structure:
    print(
        f"{item['date']}   "
        f"{item['type']:<5}   "
        f"{item['price']:>10.2f}   "
        f"{item['structure']}"
    )