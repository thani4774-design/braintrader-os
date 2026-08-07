import pandas as pd

# Read CSV
df = pd.read_csv(r"C:\BrainTrader\Data\TCS.csv", skiprows=[1])

# Rename first column
df.rename(columns={"Price": "Date"}, inplace=True)

# Convert Close column to number
df["Close"] = pd.to_numeric(df["Close"], errors="coerce")

# Calculate EMAs
df["EMA20"] = df["Close"].ewm(span=20, adjust=False).mean()
df["EMA50"] = df["Close"].ewm(span=50, adjust=False).mean()
df["EMA100"] = df["Close"].ewm(span=100, adjust=False).mean()
df["EMA200"] = df["Close"].ewm(span=200, adjust=False).mean()

# Display last 10 rows
print(
    df[
        [
            "Date",
            "Close",
            "EMA20",
            "EMA50",
            "EMA100",
            "EMA200",
        ]
    ].tail(10)
)
# Calculate RSI
delta = df["Close"].diff()

gain = delta.clip(lower=0)
loss = -delta.clip(upper=0)

avg_gain = gain.rolling(14).mean()
avg_loss = loss.rolling(14).mean()

rs = avg_gain / avg_loss

df["RSI"] = 100 - (100 / (1 + rs))