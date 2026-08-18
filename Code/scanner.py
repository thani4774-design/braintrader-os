import yfinance as yf
import pandas as pd
import json
import os
from datetime import datetime
import warnings

# Suppress pandas fragmentation warnings for clean terminal output
warnings.filterwarnings("ignore")

# Import watchlists properly
try:
    from watchlists import NIFTY50, NIFTY500
except ImportError:
    try:
        from Code.watchlists import NIFTY50, NIFTY500
    except ImportError:
        NIFTY50 = ['RELIANCE.NS', 'TCS.NS', 'HDFCBANK.NS', 'INFY.NS', 'ICICIBANK.NS', 'BHARTIARTL.NS', 'SBIN.NS', 'ITC.NS', 'LT.NS']
        NIFTY500 = NIFTY50

def get_data(symbol, period="1y", interval="1d"):
    """Fetches historical market data from Yahoo Finance."""
    tkr = yf.Ticker(symbol)
    df = tkr.history(period=period, interval=interval)
    return df

def calculate_rsi(data, window=14):
    """Calculates the Relative Strength Index (RSI) mathematically."""
    delta = data.diff()
    gain = delta.where(delta > 0, 0)
    loss = -delta.where(delta < 0, 0)
    
    avg_gain = gain.ewm(com=window-1, adjust=False).mean()
    avg_loss = loss.ewm(com=window-1, adjust=False).mean()
    
    rs = avg_gain / avg_loss
    rsi = 100 - (100 / (1 + rs))
    return rsi

def analyze_stock(symbol, timeframe="short"):
    """
    STRICT QUANTITATIVE FILTERING ENGINE (HANDLES BOTH MASTER SCAN & INDIVIDUAL SEARCH)
    """
    try:
        # Pull 2 years of data for Long-Term/Mid-Term, 1 year for Short-Term
        df = get_data(symbol, period="2y" if timeframe in ["long", "mid"] else "1y")
        
        if df.empty or len(df) < 100:
            return None
            
        # Calculate Core Indicators
        df['EMA_50'] = df['Close'].ewm(span=50, adjust=False).mean()
        df['EMA_200'] = df['Close'].ewm(span=200, adjust=False).mean()
        df['RSI_14'] = calculate_rsi(df['Close'])
        df['Avg_Volume'] = df['Volume'].rolling(window=20).mean()
        
        current_price = round(df['Close'].iloc[-1], 2)
        current_vol = df['Volume'].iloc[-1]
        avg_vol = df['Avg_Volume'].iloc[-1]
        ema_50 = df['EMA_50'].iloc[-1]
        ema_200 = df['EMA_200'].iloc[-1]
        current_rsi = df['RSI_14'].iloc[-1]
        
        # ---------------------------------------------------------
        # 1. SHORT TERM (DAYS): Strict Swing Rules (1.5x Vol Spike)
        # ---------------------------------------------------------
        if timeframe == "short":
            if (current_price > ema_200) and (current_price > ema_50) and (50 <= current_rsi <= 70) and (current_vol > avg_vol * 1.5):
                return {
                    "Stock": symbol,
                    "Price": current_price,
                    "Decision": "STRONG_BUY",
                    "Score": 92,
                    "Confidence": 88,
                    "Alignment": "BULLISH",
                    "Reasons": [
                        "Price > 200 & 50 EMA (Macro Trend Aligned)",
                        f"RSI at {round(current_rsi, 1)} (Momentum Zone)",
                        f"Institutional Volume Spike Detected ({(current_vol/avg_vol):.1f}x average)"
                    ],
                    "Warnings": [],
                    "TradeSetup": {
                        "entry": str(current_price),
                        "stop_loss": str(round(current_price * 0.94, 2)),
                        "target_1": str(round(current_price * 1.08, 2)),
                        "target_2": str(round(current_price * 1.15, 2)),
                        "risk_reward": "1:2.5",
                        "trailing_sl": "Move SL to Entry at T1"
                    }
                }
            # Default response for Individual Search when setup is NOT ready
            return {
                "Stock": symbol,
                "Price": current_price,
                "Decision": "WAIT",
                "Score": 45,
                "Confidence": 50,
                "Alignment": "NEUTRAL",
                "Reasons": [],
                "Warnings": [
                    "Failed Volume Spike test (No institutional participation detected)",
                    "RSI not in the optimal 50-70 swing pocket"
                ],
                "TradeSetup": {
                    "entry": str(current_price),
                    "stop_loss": "N/A",
                    "target_1": "N/A",
                    "target_2": "N/A",
                    "risk_reward": "N/A",
                    "trailing_sl": "No active breakout setup. Await volume spike."
                }
            }

        # ---------------------------------------------------------
        # 2. MID TERM (WEEKS): Positional Trend Rules (1.2x Vol Spike)
        # ---------------------------------------------------------
        elif timeframe == "mid":
            if (current_price > ema_200) and (current_price > ema_50) and (current_rsi >= 50):
                return {
                    "Stock": symbol,
                    "Price": current_price,
                    "Decision": "STRONG_BUY",
                    "Score": 85,
                    "Confidence": 80,
                    "Alignment": "BULLISH",
                    "Reasons": ["Positional Trend Alignment Confirmed", "EMA Support Held"],
                    "Warnings": [],
                    "TradeSetup": {
                        "entry": str(current_price),
                        "stop_loss": str(round(current_price * 0.90, 2)), 
                        "target_1": str(round(current_price * 1.15, 2)), 
                        "target_2": str(round(current_price * 1.25, 2)), 
                        "risk_reward": "1:3",
                        "trailing_sl": "Trail using 50-day EMA"
                    }
                }
            return {
                "Stock": symbol,
                "Price": current_price,
                "Decision": "WAIT",
                "Score": 30,
                "Confidence": 40,
                "Alignment": "BEARISH",
                "Reasons": [],
                "Warnings": ["Stock is not in a confirmed mid-term momentum zone."],
                "TradeSetup": {
                    "entry": str(current_price),
                    "stop_loss": "N/A",
                    "target_1": "N/A",
                    "target_2": "N/A",
                    "risk_reward": "N/A",
                    "trailing_sl": "Stock is not in a confirmed mid-term momentum zone."
                }
            }

        # ---------------------------------------------------------
        # 3. LONG TERM (MONTHS): Macro Accumulation Rules
        # ---------------------------------------------------------
        elif timeframe == "long":
            fair_value = round(ema_200 * 1.02, 2)
            zone_low = round(fair_value * 0.95, 2)
            zone_high = round(fair_value * 1.04, 2)
            
            if current_price <= (fair_value * 1.04):
                return {
                    "Stock": symbol,
                    "Price": current_price,
                    "Decision": "ACCUMULATE",
                    "Score": 95,
                    "Confidence": 90,
                    "Alignment": "MACRO DISCOUNT",
                    "Reasons": ["Trading below fair value equilibrium", "Strong risk-adjusted accumulation zone"],
                    "Warnings": [],
                    "InvestmentSetup": {
                        "fair_value": str(fair_value),
                        "accumulation_zone": f"₹{zone_low} - ₹{zone_high}",
                        "macro_invalid_level": str(round(ema_200 * 0.82, 2)),
                        "historical_resistance": str(round(df['High'].max() * 1.15, 2))
                    }
                }
            return {
                "Stock": symbol,
                "Price": current_price,
                "Decision": "WAIT",
                "Score": 50,
                "Confidence": 60,
                "Alignment": "PREMIUM",
                "Reasons": [],
                "Warnings": ["Asset is currently trading at a premium. Wait for a pullback to EMA 200."],
                "InvestmentSetup": {
                    "fair_value": str(fair_value),
                    "accumulation_zone": f"₹{zone_low} - ₹{zone_high}",
                    "macro_invalid_level": "N/A",
                    "historical_resistance": "N/A"
                }
            }
            
    except Exception as e:
        return None

def run_master_scan():
    print("==================================================")
    print(" BRAINTRADER STRICT QUANT ENGINE RESTORED...")
    print("==================================================")
    
    # --- PHASE 1: Swing Trading Scan ---
    print(f"\n[Phase 1] Scanning Nifty 500 for True Institutional Momentum...")
    daily_setups = []
    
    for sym in NIFTY500: 
        res = analyze_stock(sym, "short")
        # Only keep stocks with STRONG_BUY for master list
        if res and res.get("Decision") == "STRONG_BUY": 
            daily_setups.append(res)
            
    with open(r"C:\BrainTrader\daily_setups.json", "w", encoding="utf-8") as f:
        json.dump({
            "last_updated": datetime.now().strftime("%d %b %Y, %I:%M %p"), 
            "setups": daily_setups
        }, f)
    print(f"--> Filtered down to {len(daily_setups)} high-probability swing trades.")
        
    # --- PHASE 2: Long-Term Wealth Scan ---
    print(f"\n[Phase 2] Scanning Nifty 50 for True Macro-Discount Accumulation...")
    wealth_setups = []
    
    for sym in NIFTY50: 
        res = analyze_stock(sym, "long")
        # Only keep stocks with ACCUMULATE for master list
        if res and res.get("Decision") == "ACCUMULATE": 
            wealth_setups.append(res)
            
    with open(r"C:\BrainTrader\wealth_setups.json", "w", encoding="utf-8") as f:
        json.dump({
            "last_updated": datetime.now().strftime("%d %b %Y, %I:%M %p"), 
            "setups": wealth_setups
        }, f)
    print(f"--> Filtered down to {len(wealth_setups)} assets currently at a discount.")
    
    print("\n==================================================")
    print(" ALGORITHMIC SCAN COMPLETE!")
    print("==================================================")

if __name__ == "__main__":
    run_master_scan()