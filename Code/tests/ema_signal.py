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

# Get latest row
latest = df.iloc[-1]

print("\n====== BrainTrader EMA Signal ======\n")
print(f"Close  : {latest['Close']:.2f}")
print(f"EMA20  : {latest['EMA20']:.2f}")
print(f"EMA50  : {latest['EMA50']:.2f}")
print(f"EMA100 : {latest['EMA100']:.2f}")
print(f"EMA200 : {latest['EMA200']:.2f}")

if (
    latest["EMA20"] > latest["EMA50"] >
    latest["EMA100"] > latest["EMA200"]
):
    print("\n✅ Signal : BUY")
else:
    print("\n⏳ Signal : WAIT")