"""
BrainTrader
------------------------
Phase 10: Headless Automation Engine (Rate-Limited for 500 Stocks)
"""

import logging
import os
import time
from datetime import datetime
from concurrent.futures import ThreadPoolExecutor, as_completed
from scanner import analyze_stock
from risk_manager import RiskManager
from execution.broker_adapter import PaperTradingBroker
from watchlists import NIFTY50, BANKNIFTY, NIFTY_MIDCAP, NIFTY_SMALLCAP, NIFTY_MICROCAP

logging.basicConfig(level=logging.INFO, format="%(asctime)s - %(message)s")

# Combine all watchlists into a massive master universe
MASTER_UNIVERSE = list(set(NIFTY50 + BANKNIFTY + NIFTY_MIDCAP + NIFTY_SMALLCAP + NIFTY_MICROCAP))

def run_daily_automation():
    print("=" * 60)
    print(f"BRAINTRADER AUTOMATION INITIATED: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print("=" * 60)
    
    initial_capital = 1000000
    broker = PaperTradingBroker(initial_balance=initial_capital)
    risk_manager = RiskManager(max_risk_per_trade_pct=0.02, max_portfolio_exposure_pct=0.60)
    
    buys_executed = []
    
    print(f"[*] Scanning {len(MASTER_UNIVERSE)} symbols. Rate-limiting engaged to prevent API bans...")
    
    # Throttle workers to 2 to protect the local IP address
    with ThreadPoolExecutor(max_workers=2) as executor:
        future_to_symbol = {executor.submit(analyze_stock, sym): sym for sym in MASTER_UNIVERSE}
        
        for count, future in enumerate(as_completed(future_to_symbol), 1):
            symbol = future_to_symbol[future]
            try:
                res = future.result()
                if res and res["Decision"] == "STRONG_BUY":
                    setup = res["TradeSetup"]
                    current_deployed = sum(pos["quantity"] * pos["entry_price"] for pos in broker.positions.values())
                    
                    qty, risk_details = risk_manager.calculate_position_size(
                        account_balance=initial_capital,
                        current_deployed_capital=current_deployed,
                        entry_price=res['Price'],
                        stop_loss=setup.get("stop_loss")
                    )
                    
                    if qty > 0:
                        logging.info(f"STRONG BUY Triggered: {symbol} at ₹{res['Price']}")
                        broker.place_order(symbol, "MARKET", qty, res['Price'], setup.get("stop_loss"), setup.get("target1"))
                        buys_executed.append({"stock": symbol, "price": res['Price'], "qty": qty, "risk": risk_details['portfolio_risk_pct']})
                        
            except Exception as e:
                logging.error(f"Failed to process {symbol}: {e}")
                
            # Print progress cleanly
            if count % 25 == 0:
                print(f"[*] Processed {count}/{len(MASTER_UNIVERSE)} stocks...")
            
            # Rate Limiter: Pause for 1 second between processing to respect API limits
            time.sleep(1)

    # --- Generate Daily Report ---
    report_path = r"C:\BrainTrader\daily_trade_report.txt"
    with open(report_path, "w", encoding="utf-8") as f:
        f.write(f"[{datetime.now().strftime('%Y-%m-%d %H:%M:%S')}] SCAN COMPLETE.\n")
        f.write(f"Universe Scanned: {len(MASTER_UNIVERSE)} stocks.\n\n")
        if buys_executed:
            f.write("EXECUTED TRADES:\n")
            for b in buys_executed:
                f.write(f" -> BOUGHT {b['qty']} shares of {b['stock']} @ ₹{b['price']} (Risk: {b['risk']}%)\n")
        else:
            f.write(" -> No STRONG_BUY setups detected in today's scan. Capital preserved.\n")
            
    print(f"\n[*] Scan complete. Feed updated. Reload your web browser.")

if __name__ == "__main__":
    run_daily_automation()