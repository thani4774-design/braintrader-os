import urllib.request
import csv
import ssl
import os

def update_watchlist():
    print("==================================================")
    print(" DOWNLOADING LIVE NIFTY 500 LIST FROM NSE")
    print("==================================================")
    
    url = "https://www.niftyindices.com/IndexConstituent/ind_nifty500list.csv"
    
    # Bypass SSL and set headers to prevent NSE from blocking the request
    ctx = ssl.create_default_context()
    ctx.check_hostname = False
    ctx.verify_mode = ssl.CERT_NONE
    req = urllib.request.Request(url, headers={'User-Agent': 'Mozilla/5.0'})

    try:
        with urllib.request.urlopen(req, context=ctx) as response:
            lines = [line.decode('utf-8') for line in response.readlines()]
            
        reader = csv.DictReader(lines)
        symbols = []
        
        for row in reader:
            if 'Symbol' in row:
                sym = row['Symbol'].strip()
                # Auto-correct LTIM to LTM for Yahoo Finance
                if sym == "LTIM":
                    sym = "LTM"
                symbols.append(f"'{sym}.NS'")
                
        if not symbols:
            print("Error: Could not parse symbols from NSE data.")
            return

        # Write directly to your BrainTrader folder
        file_path = r"C:\BrainTrader\Code\watchlists.py"
        with open(file_path, "w", encoding="utf-8") as f:
            f.write("# AUTO-GENERATED NIFTY WATCHLIST\n\n")
            
            # Write Nifty 500
            f.write("NIFTY500 = [\n")
            for sym in symbols:
                f.write(f"    {sym},\n")
            f.write("]\n\n")
            
            # Write a Nifty 50 approximation using the top 50 by market cap
            f.write("NIFTY50 = NIFTY500[:50]\n")
            
        print(f"SUCCESS! {len(symbols)} stocks saved to watchlists.py")
        print("Your BrainTrader SMC Engine is now fully loaded.")
        
    except Exception as e:
        print(f"Failed to fetch data: {e}")

if __name__ == "__main__":
    update_watchlist()
    input("\nPress Enter to exit...")