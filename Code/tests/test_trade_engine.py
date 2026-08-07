"""
BrainTrader
------------------------
Trade Engine Test
"""

import pandas as pd
import yfinance as yf

from indicators import calculate_indicators

from trade_engine import generate_trade_setup



STOCK = "HDFCBANK.NS"



df = yf.download(
    STOCK,
    period="1y",
    interval="1d",
    auto_adjust=True,
    progress=False
)



if df.empty:

    print("No data found")

    raise SystemExit



# Fix yfinance MultiIndex columns

if isinstance(df.columns, pd.MultiIndex):

    df.columns = df.columns.get_level_values(0)



df = df.reset_index()



df = calculate_indicators(
    df
)



current_price = float(
    df.iloc[-1]["Close"]
)



# Test support/resistance levels

levels = {

    "nearest_support":

    720,


    "nearest_resistance":

    760

}



setup = generate_trade_setup(

    df,

    current_price,

    levels,

    score=45,

    confidence=60

)



print()

print("=" * 60)

print("TRADE ENGINE TEST")

print(STOCK)

print("=" * 60)


print()

print("Current Price :", round(current_price,2))


print()


for key, value in setup.items():

    print(
        key,
        ":",
        value
    )