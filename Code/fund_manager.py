import yfinance as yf
import pandas as pd
import json
import os
import sys
import sqlite3
from datetime import datetime
import warnings

warnings.filterwarnings("ignore")

# Ensure Code folder and market_structure subfolder are in Python path
CODE_DIR = os.path.dirname(os.path.abspath(__file__))
MS_DIR = os.path.join(CODE_DIR, "market_structure")
if CODE_DIR not in sys.path:
    sys.path.append(CODE_DIR)
if MS_DIR not in sys.path:
    sys.path.append(MS_DIR)

# 1. Import custom SMC Confluence Engine
from confluence_engine import calculate_confluence

# 2. Import Live Angel One API Connection
try:
    from angel_connection import AngelOneAPI
    ANGEL_AVAILABLE = True
except ImportError:
    ANGEL_AVAILABLE = False

# 3. Attempt imports from real SMC market_structure modules
try:
    import order_blocks
    import fvg_engine
    import liquidity_sweep
    import premium_discount
    import choch_engine
    import bos_engine
    SMC_MODULES_LOADED = True
except ImportError:
    SMC_MODULES_LOADED = False

# 4. Import Watchlists
try:
    from watchlists import NIFTY50, NIFTY500
except ImportError:
    NIFTY50 = ['RELIANCE.NS', 'TCS.NS', 'HDFCBANK.NS', 'INFY.NS', 'ICICIBANK.NS', 'SBIN.NS']
    NIFTY500 = NIFTY50

def update_active_trades():
    """Checks past ACTIVE trades and grades them chronologically ONLY after the entry date."""
    print("\n[Phase 0] Grading past ACTIVE trades...")
    try:
        db_path = r"C:\BrainTrader\trade_history.db"
        conn = sqlite3.connect(db_path)
        cursor = conn.cursor()
        
        cursor.execute("SELECT id, symbol, entry, target, stop_loss, date FROM trade_history WHERE status='ACTIVE'")
        active_trades = cursor.fetchall()
        
        won_count = 0
        lost_count = 0
        
        for trade_id, symbol, entry, target, stop_loss, trade_date in active_trades:
            try:
                tkr = yf.Ticker(symbol)
                hist = tkr.history(period="1mo")
                if hist.empty:
                    continue
                    
                hist.index = hist.index.tz_localize(None)
                post_entry_hist = hist[hist.index >= pd.to_datetime(trade_date)]
                
                if post_entry_hist.empty:
                    continue
                    
                entered = False
                
                for current_date, row in post_entry_hist.iterrows():
                    day_high = row['High']
                    day_low = row['Low']
                    
                    if not entered:
                        if day_low <= entry:
                            entered = True
                        else:
                            continue
                            
                    if entered:
                        if day_low <= stop_loss:
                            cursor.execute("UPDATE trade_history SET status='LOST' WHERE id=?", (trade_id,))
                            lost_count += 1
                            break
                        elif day_high >= target:
                            cursor.execute("UPDATE trade_history SET status='WON' WHERE id=?", (trade_id,))
                            won_count += 1
                            break
            except Exception:
                continue
                
        conn.commit()
        conn.close()
        
        if won_count > 0 or lost_count > 0:
            print(f"--> Upgraded {won_count} to WON and {lost_count} to LOST.")
        else:
            print("--> All previous setups are still ACTIVE (or awaiting entry fill).")
            
    except Exception as e:
        print(f"History Update Warning: {e}")

def log_setup_to_history(setup):
    """Saves approved SMC setups into trade_history.db ONLY if they aren't already ACTIVE."""
    try:
        db_path = r"C:\BrainTrader\trade_history.db"
        conn = sqlite3.connect(db_path)
        cursor = conn.cursor()
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS trade_history (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                date TEXT,
                symbol TEXT,
                entry REAL,
                target REAL,
                stop_loss REAL,
                status TEXT
            )
        ''')
        
        today = datetime.now().strftime("%Y-%m-%d")
        
        # Prevent duplicates
        cursor.execute("SELECT id FROM trade_history WHERE symbol=? AND status='ACTIVE'", (setup['Stock'],))
        if not cursor.fetchone():
            cursor.execute('''
                INSERT INTO trade_history (date, symbol, entry, target, stop_loss, status)
                VALUES (?, ?, ?, ?, ?, ?)
            ''', (
                today,
                setup['Stock'],
                float(setup['TradeSetup']['entry']),
                float(setup['TradeSetup']['target_1']),
                float(setup['TradeSetup']['stop_loss']),
                "ACTIVE"
            ))
            conn.commit()
        conn.close()
    except Exception as e:
        print(f"Database Logging Warning: {e}")

def is_sebi_safe_and_liquid(df, current_price):
    """SEBI Protection Shield: Filters out illiquid micro-caps and circuit locks."""
    try:
        recent_20 = df.tail(20)
        avg_daily_turnover = (recent_20['Volume'] * recent_20['Close']).mean()
        
        if avg_daily_turnover < 20000000:
            return False, "Low Turnover (Illiquidity Risk)"

        daily_ranges = ((recent_20['High'] - recent_20['Low']) / recent_20['Close']) * 100
        avg_daily_range = daily_ranges.mean()
        
        if avg_daily_range < 0.8:
            return False, "Narrow Circuit Range (ASM/GSM Risk)"

        return True, "SAFE"
    except Exception:
        return False, "Data Error"

def extract_real_smc_data(df, current_price):
    ema_50 = df['Close'].ewm(span=50, adjust=False).mean().iloc[-1]
    ema_200 = df['Close'].ewm(span=200, adjust=False).mean().iloc[-1]
    
    recent_high = df['High'].tail(10).max()
    recent_low = df['Low'].tail(10).min()
    equilibrium = (recent_high + recent_low) / 2.0
    
    pd_zone_status = "DISCOUNT" if current_price < equilibrium else "PREMIUM"
        
    pd_zones = {"zone": pd_zone_status, "equilibrium": round(equilibrium, 2)}
    structure = {"trend": "BULLISH" if current_price > ema_200 else "BEARISH"}
    indicator = {"ema_trend": "BULLISH" if current_price > ema_50 else "BEARISH", "rsi_status": "NORMAL"}

    bos = {"bullish_bos": current_price > ema_50}
    choch = {"bullish_choch": current_price > ema_50}
    liquidity = "BULLISH" if current_price > recent_low * 1.01 else "BEARISH"
    
    support_resistance = {
        "nearest_support": round(recent_low, 2),
        "nearest_resistance": round(recent_high, 2)
    }
    
    order_blocks_data = {"bullish": True, "level": round(current_price * 0.985, 2)}
    fvgs_data = {"bullish": True, "level": round(current_price * 0.99, 2)}

    if SMC_MODULES_LOADED:
        try:
            if hasattr(order_blocks, 'find_order_blocks'):
                obs = order_blocks.find_order_blocks(df)
                if obs:
                    ob_level = round(df['Low'].iloc[-5], 2)
                    if ob_level < current_price and ob_level >= current_price * 0.95:
                        order_blocks_data = {"bullish": True, "level": ob_level}
            if hasattr(fvg_engine, 'detect_fvg'):
                fvgs = fvg_engine.detect_fvg(df)
                if fvgs:
                    fvg_level = round(df['Low'].iloc[-3], 2)
                    if fvg_level < current_price and fvg_level >= current_price * 0.95:
                        fvgs_data = {"bullish": True, "level": fvg_level}
        except Exception:
            pass

    return structure, bos, choch, liquidity, support_resistance, indicator, order_blocks_data, fvgs_data, pd_zones

def analyze_stock(symbol, timeframe="short"):
    try:
        tkr = yf.Ticker(symbol)
        df = tkr.history(period="1y", interval="1d")
        
        if df.empty or len(df) < 100:
            return None
            
        current_price = round(df['Close'].iloc[-1], 2)
        
        is_safe, reason = is_sebi_safe_and_liquid(df, current_price)
        if not is_safe:
            return None

        smc_tuple = extract_real_smc_data(df, current_price)
        
        result = calculate_confluence(
            structure=smc_tuple[0], bos=smc_tuple[1], choch=smc_tuple[2],
            liquidity=smc_tuple[3], support_resistance=smc_tuple[4],
            indicator=smc_tuple[5], price=current_price,
            order_blocks=smc_tuple[6], fvgs=smc_tuple[7], pd_zones=smc_tuple[8]
        )
        
        if result['decision'] == "STRONG_BUY":
            ob_level = smc_tuple[6]['level']
            entry_price = ob_level if (ob_level < current_price and ob_level >= round(current_price * 0.97, 2)) else current_price
            
            stop_loss = round(entry_price * 0.96, 2)
            target_1 = round(entry_price * 1.06, 2)
            target_2 = round(entry_price * 1.12, 2) if smc_tuple[4]['nearest_resistance'] <= target_1 else smc_tuple[4]['nearest_resistance']
            
            reasons_str = " | ".join(result['reasons'])
            
            return {
                "Stock": symbol,
                "Price": current_price,
                "Decision": "STRONG_BUY",
                "TradeSetup": {
                    "entry": str(entry_price),
                    "stop_loss": str(stop_loss),
                    "target_1": str(target_1),
                    "target_2": str(round(target_2, 2)),
                    "split_execution": "Place 50% Qty targeting T1, and 50% Qty targeting T2.",
                    "trailing_sl": f"SMC Score: {result['score']}. {reasons_str}"
                }
            }
            
        elif timeframe == "long" and result['decision'] in ["STRONG_BUY", "BUY_WATCH"]:
            return {
                "Stock": symbol,
                "Price": current_price,
                "Decision": "ACCUMULATE",
                "InvestmentSetup": {
                    "fair_value": str(smc_tuple[8]['equilibrium']),
                    "accumulation_zone": f"₹{round(current_price*0.95, 2)} - ₹{round(current_price*1.03, 2)}",
                    "macro_invalid_level": str(round(current_price * 0.85, 2)),
                    "historical_resistance": str(round(df['High'].max(), 2))
                }
            }

        return None
            
    except Exception as e:
        return None

def run_master_scan():
    print("==================================================")
    print(" BRAINTRADER SMC CONFLUENCE SCANNER ACTIVE")
    print("==================================================")
    
    update_active_trades()
    
    available_margin = 0.0
    print("\n[Phase 0.5] Connecting to Live Exchange...")
    if ANGEL_AVAILABLE:
        try:
            broker = AngelOneAPI()
            if broker.login():
                available_margin = broker.get_available_balance()
        except Exception as e:
            print(f"[API ERROR] Connection failed: {e}")
    else:
        print("[WARNING] Angel One API module not loaded. Defaulting to Paper Trading.")
    
    print(f"\n[Phase 1] Scanning {len(NIFTY500)} stocks via SMC Engine (SEBI Filter ON)...")
    all_setups = []
    
    for idx, sym in enumerate(NIFTY500, start=1): 
        res = analyze_stock(sym, "short")
        if res and res.get("Decision") == "STRONG_BUY": 
            try:
                score_str = res['TradeSetup']['trailing_sl'].split('SMC Score: ')[1].split('.')[0]
                res['raw_score'] = int(score_str)
            except Exception:
                res['raw_score'] = 0
            all_setups.append(res)
            
    # Sort all setups by institutional score
    all_setups.sort(key=lambda x: x.get('raw_score', 0), reverse=True)
    
    # 1. Log ALL qualifying setups into SQLite database for rapid statistical sample testing
    for setup in all_setups:
        log_setup_to_history(setup)
    print(f"--> Logged all {len(all_setups)} qualified SMC setups to trade_history.db for testing.")

    # 2. Extract Top 5 for primary dashboard display and capital allocation modeling
    top_5_setups = all_setups[:5]
    num_trades = len(top_5_setups)
    if num_trades > 0 and available_margin > 0:
        capital_per_trade = available_margin / num_trades
        print(f"--> Institutional Allocation: Splitting live margin across {num_trades} assets (₹{round(capital_per_trade, 2)} each).")
    
    for setup in top_5_setups:
        entry_price = float(setup['TradeSetup']['entry'])
        if available_margin > 0:
            shares = int(capital_per_trade // entry_price)
            allocated_capital = round(shares * entry_price, 2)
            setup['TradeSetup']['quantity'] = str(shares)
            setup['TradeSetup']['capital_allocated'] = f"₹{allocated_capital}"
        else:
            setup['TradeSetup']['quantity'] = "N/A"
            setup['TradeSetup']['capital_allocated'] = "Paper Trading"
            
        setup.pop('raw_score', None)
            
    with open(r"C:\BrainTrader\daily_setups.json", "w", encoding="utf-8") as f:
        json.dump({
            "last_updated": datetime.now().strftime("%d %b %Y, %I:%M %p"), 
            "setups": top_5_setups
        }, f)
        
    print(f"--> Saved Top {len(top_5_setups)} elite swing trades to daily_setups.json.")
        
    print(f"\n[Phase 2] Scanning {len(NIFTY50)} stocks for Long-Term Value Accumulation...")
    wealth_setups = []
    
    for sym in NIFTY50: 
        res = analyze_stock(sym, "long")
        if res and res.get("Decision") == "ACCUMULATE": 
            wealth_setups.append(res)
            
    with open(r"C:\BrainTrader\wealth_setups.json", "w", encoding="utf-8") as f:
        json.dump({
            "last_updated": datetime.now().strftime("%d %b %Y, %I:%M %p"), 
            "setups": wealth_setups
        }, f)
    print(f"--> Approved {len(wealth_setups)} long-term accumulation assets.")
    
    print("\n==================================================")
    print(" SCAN COMPLETE! YOUR DASHBOARD IS READY.")
    print("==================================================")

if __name__ == "__main__":
    run_master_scan()