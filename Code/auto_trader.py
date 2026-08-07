"""
BrainTrader - EOD Master Auto-Scanner with Auto-Grader
------------------------------------------------------
"""

import json
import os
import time
import sqlite3
import yfinance as yf
from datetime import datetime
from scanner import analyze_stock
from watchlists import NIFTY50, BANKNIFTY, NIFTY_MIDCAP, NIFTY_SMALLCAP

MASTER_UNIVERSE = sorted(list(set(NIFTY50 + BANKNIFTY + NIFTY_MIDCAP + NIFTY_SMALLCAP)))
DB_PATH = r"C:\BrainTrader\trade_history.db"

def init_db():
    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()
    c.execute('''
        CREATE TABLE IF NOT EXISTS trades (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            date TEXT,
            symbol TEXT,
            entry REAL,
            target_1 REAL,
            stop_loss REAL,
            status TEXT
        )
    ''')
    conn.commit()
    conn.close()

def log_trade(date, symbol, entry, target, sl):
    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()
    c.execute("SELECT * FROM trades WHERE date=? AND symbol=?", (date, symbol))
    if not c.fetchone():
        c.execute("INSERT INTO trades (date, symbol, entry, target_1, stop_loss, status) VALUES (?, ?, ?, ?, ?, ?)",
                  (date, symbol, entry, target, sl, "ACTIVE"))
        conn.commit()
    conn.close()

def grade_active_trades():
    print("=" * 60)
    print("RUNNING AUTO-GRADER ON PAST ACTIVE TRADES...")
    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()
    
    # NEW FIX: Only grade trades that were NOT logged today (T+1 Grading)
    today_str = datetime.now().strftime("%Y-%m-%d")
    c.execute("SELECT id, symbol, target_1, stop_loss, date FROM trades WHERE status='ACTIVE' AND date != ?", (today_str,))
    active_trades = c.fetchall()
    
    updated_count = 0
    for trade in active_trades:
        trade_id, symbol, target_1, sl, trade_date = trade
        try:
            ticker = yf.Ticker(symbol)
            df = ticker.history(start=trade_date)
            
            if df.empty:
                continue
                
            recent_high = df['High'].max()
            recent_low = df['Low'].min()
            
            new_status = 'ACTIVE'
            if recent_high >= target_1:
                new_status = 'WON'
            elif recent_low <= sl:
                new_status = 'LOST'
                
            if new_status != 'ACTIVE':
                c.execute("UPDATE trades SET status=? WHERE id=?", (new_status, trade_id))
                conn.commit()
                updated_count += 1
                print(f"[GRADER] {symbol} resolved as {new_status}!")
        except Exception as e:
            pass
            
    conn.close()
    print(f"Auto-Grader finished. {updated_count} trades resolved.")
    print("=" * 60)

def run_eod_scan():
    init_db()
    grade_active_trades()
    
    print(f"STARTING EOD MASTER SCAN: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print("=" * 60)
    
    top_setups = []
    today_str = datetime.now().strftime("%Y-%m-%d")
    
    for count, symbol in enumerate(MASTER_UNIVERSE, 1):
        try:
            res = analyze_stock(symbol, timeframe="short")
            if res and res.get("Decision") == "STRONG_BUY":
                top_setups.append(res)
                print(f"[✓] FOUND SETUP: {symbol} @ ₹{res['Price']}")
        except Exception as e:
            pass
            
        if count % 20 == 0:
            print(f"[*] Processed {count}/{len(MASTER_UNIVERSE)} stocks...")
        time.sleep(0.3)
        
    top_setups = sorted(top_setups, key=lambda x: x.get("Score", 0), reverse=True)
    
    for setup in top_setups:
        sym = setup["Stock"]
        entry = setup["TradeSetup"]["entry"]
        t1 = setup["TradeSetup"]["target_1"]
        sl = setup["TradeSetup"]["stop_loss"]
        log_trade(today_str, sym, entry, t1, sl)
    
    output_data = {
        "last_updated": datetime.now().strftime("%d %b %Y, %I:%M %p"),
        "total_scanned": len(MASTER_UNIVERSE),
        "setups": top_setups
    }
    
    save_path = r"C:\BrainTrader\daily_setups.json"
    with open(save_path, "w", encoding="utf-8") as f:
        json.dump(output_data, f, indent=4)
        
    print("=" * 60)
    print(f"EOD SCAN COMPLETE! Found {len(top_setups)} total setups.")
    print("=" * 60)

if __name__ == "__main__":
    run_eod_scan()