"""
BrainTrader - Auto Nifty 500 Universe Updater
"""
import pandas as pd
import requests
import io

print("Connecting to NSE Servers to fetch Nifty 500...")
url = "https://archives.nseindia.com/content/indices/ind_nifty500list.csv"
headers = {'User-Agent': 'Mozilla/5.0'}

try:
    response = requests.get(url, headers=headers)
    df = pd.read_csv(io.StringIO(response.text))
    
    # Extract symbols and format them for Yahoo Finance (.NS)
    symbols = [f"'{sym}.NS'" for sym in df['Symbol'].tolist()]
    
    # Overwrite the watchlists.py file dynamically
    with open(r"C:\BrainTrader\Code\watchlists.py", "w", encoding="utf-8") as f:
        f.write(f"NIFTY50 = [{', '.join(symbols)}]\n")
        f.write("BANKNIFTY = []\n")
        f.write("NIFTY_MIDCAP = []\n")
        f.write("NIFTY_SMALLCAP = []\n")
        
    print(f"Success! Your scanner is now locked and loaded with {len(symbols)} stocks.")

except Exception as e:
    print(f"Failed to connect to NSE: {e}")