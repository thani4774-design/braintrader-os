import pandas as pd
import yfinance as yf

from indicators import calculate_indicators
from indicator_confirmation import indicator_confirmation


stock = "INFY.NS"

print("=" * 60)
print("INDICATOR CONFIRMATION TEST")
print(stock)
print("=" * 60)


df = yf.download(
    stock,
    period="2y",
    auto_adjust=True,
    progress=False
)


if isinstance(df.columns, pd.MultiIndex):
    df.columns = df.columns.get_level_values(0)

df = df.reset_index()


df = calculate_indicators(df)


result = indicator_confirmation(df)


print("\nIndicator Score:", result["score"], "/100")

print("\nIndicator Details\n")

for name, status in result["details"].items():

    print(
        f"{name:<12}:",
        "PASS ✅" if status else "FAIL ❌"
    )