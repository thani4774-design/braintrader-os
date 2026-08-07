import yfinance as yf

print("Downloading TCS data...")

tcs = yf.download(
    "TCS.NS",
    start="2015-01-01",
    end="2025-01-01"
)

tcs.to_csv(r"C:\BrainTrader\Data\TCS.csv")

print("Data saved successfully!")