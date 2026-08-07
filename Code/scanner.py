"""
BrainTrader - Production-Hardened Scanner V3.5
Includes Order Blocks, FVGs, Premium/Discount Zones, Paper Trading, and Risk Management.
"""

import logging
import pandas as pd
import yfinance as yf
from concurrent.futures import ThreadPoolExecutor, as_completed

from indicators import calculate_indicators
from indicator_confirmation import indicator_confirmation
from multi_timeframe_structure import analyze_timeframe
from market_structure.mtf_decision_engine import calculate_alignment
from market_structure.swing_points import detect_swings
from market_structure.swing_classifier import classify_swings
from market_structure.swing_strength import calculate_swing_strength
from market_structure.swing_analysis import analyze_swings
from market_structure.support_resistance import find_support_resistance, nearest_levels
from market_structure.liquidity_sweep import detect_liquidity_sweeps
from market_structure.order_blocks import detect_order_blocks
from market_structure.fvg_engine import detect_fvgs
from market_structure.premium_discount import calculate_pd_zones  # --- NEW: Phase 3 PD Zones ---
from confluence_engine import calculate_confluence
from trade_engine import generate_trade_setup
from watchlists import NIFTY50, BANKNIFTY, MY_WATCHLIST

# --- Execution & Risk Imports ---
from execution.broker_adapter import PaperTradingBroker
from risk_manager import RiskManager

logging.basicConfig(level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s")

TIMEFRAMES = {
    "MACRO": ("15y", "1mo"),
    "MAJOR": ("5y", "1wk"),
    "CURRENT": ("2y", "1d")
}

def select_watchlist():
    print("=" * 50)
    print("BrainTrader Scanner V3.5 (Risk-Managed & PD Zones)")
    print("=" * 50)
    print("1. Nifty 50\n2. Bank Nifty\n3. My Watchlist")
    choice = input("Enter choice (default 1): ").strip()
    if choice == "2":
        return BANKNIFTY
    elif choice == "3":
        return MY_WATCHLIST
    return NIFTY50

def download_data(symbol: str, period: str, interval: str) -> pd.DataFrame:
    try:
        df = yf.download(symbol, period=period, interval=interval, auto_adjust=True, progress=False)
        if df is None or df.empty:
            return None

        if isinstance(df.columns, pd.MultiIndex):
            if 'Close' in df.columns.get_level_values(0):
                df.columns = df.columns.get_level_values(0)
            elif 'Close' in df.columns.get_level_values(1):
                df.columns = df.columns.get_level_values(1)

        df = df.reset_index()
        
        if 'Date' not in df.columns and 'Datetime' in df.columns:
            df.rename(columns={'Datetime': 'Date'}, inplace=True)
            
        return df
    except Exception as e:
        logging.error(f"Failed to download {symbol} [{period}/{interval}]: {e}")
        return None

def analyze_stock(symbol: str):
    try:
        timeframe_data = {}
        for name, (period, interval) in TIMEFRAMES.items():
            df = download_data(symbol, period, interval)
            if df is None or len(df) < 50:
                logging.warning(f"Insufficient data for {symbol} on {name} timeframe.")
                return None
            timeframe_data[name] = calculate_indicators(df)

        current_df = timeframe_data["CURRENT"]
        latest_live_price = float(current_df.iloc[-1]["Close"])
        closed_df = current_df.iloc[:-1].copy() if len(current_df) > 1 else current_df

        indicator_conf = indicator_confirmation(closed_df)

        mtf_structure = {}
        for name, df in timeframe_data.items():
            res = analyze_timeframe(symbol, name, df)
            mtf_structure[name] = res if res is not None else {}

        alignment = calculate_alignment(mtf_structure)

        swings = detect_swings(closed_df)
        swings = classify_swings(swings)
        swings = calculate_swing_strength(swings)
        swings = analyze_swings(swings)

        current_structure = mtf_structure.get("CURRENT", {})
        levels = find_support_resistance(swings)
        levels = nearest_levels(levels, latest_live_price)
        liquidity = detect_liquidity_sweeps(closed_df, swings)
        
        recent_bos = current_structure.get("last_bos")
        bos_list = [recent_bos] if recent_bos else []
        order_blocks = detect_order_blocks(closed_df, bos_list)
        fvgs = detect_fvgs(closed_df)

        # --- NEW: Calculate Premium & Discount Zones ---
        pd_zones = calculate_pd_zones(swings, latest_live_price)

        confluence = calculate_confluence(
            structure=current_structure,
            bos=current_structure.get("last_bos"),
            choch=current_structure.get("last_choch"),
            liquidity=liquidity,
            support_resistance=levels,
            indicator=indicator_conf,
            price=latest_live_price,
            order_blocks=order_blocks,
            fvgs=fvgs,
            pd_zones=pd_zones # Passed successfully to the decision engine
        )

        decision = confluence.get("decision", "WAIT")
        direction = "LONG"
        
        trade_setup = generate_trade_setup(
            closed_df,
            latest_live_price,
            levels,
            confluence.get("score", 0),
            confluence.get("confidence", 0),
            direction=direction
        )

        return {
            "Stock": symbol,
            "Price": latest_live_price,
            "Score": confluence.get("score", 0),
            "Decision": decision,
            "Confidence": confluence.get("confidence", 0),
            "Alignment": alignment.get("alignment", "NEUTRAL"),
            "Reasons": confluence.get("reasons", []),
            "Warnings": confluence.get("warnings", []),
            "TradeSetup": trade_setup or {}
        }

    except Exception as e:
        logging.error(f"Error processing stock {symbol}: {e}", exc_info=True)
        return None

def main():
    watchlist = select_watchlist()
    print(f"\nScanning {len(watchlist)} symbols...\n")

    initial_capital = 1000000
    broker = PaperTradingBroker(initial_balance=initial_capital)
    
    risk_manager = RiskManager(max_risk_per_trade_pct=0.02, max_portfolio_exposure_pct=0.60)

    results = []
    with ThreadPoolExecutor(max_workers=8) as executor:
        future_to_symbol = {executor.submit(analyze_stock, sym): sym for sym in watchlist}
        for future in as_completed(future_to_symbol):
            res = future.result()
            if res:
                results.append(res)

    results.sort(key=lambda x: x["Score"], reverse=True)

    print("\n" + "=" * 70)
    print("BRAINTRADER SCANNER RESULTS")
    print("=" * 70)

    for item in results:
        print("\n" + "=" * 60)
        print(f"{item['Stock']} | Price: {item['Price']:.2f} | Score: {item['Score']} | Decision: {item['Decision']}")
        print("=" * 60)
        print(f"Confidence: {item['Confidence']}% | Alignment: {item['Alignment']}")

        if item["Reasons"]:
            print("\nReasons:")
            for r in item["Reasons"]:
                print("  -", r)

        if item["Warnings"]:
            print("\nWarnings:")
            for w in item["Warnings"]:
                print("  !", w)

        print("\nTrade Setup:")
        setup = item["TradeSetup"]
        if setup:
            for k, v in setup.items():
                print(f"  {k}: {v}")
                
            if item["Decision"] in ["STRONG_BUY"]:
                print("\n>>> INITIATING PAPER TRADE EXECUTOR <<<")
                
                current_deployed = sum(pos["quantity"] * pos["entry_price"] for pos in broker.positions.values())
                
                qty, risk_details = risk_manager.calculate_position_size(
                    account_balance=initial_capital,
                    current_deployed_capital=current_deployed,
                    entry_price=item['Price'],
                    stop_loss=setup.get("stop_loss")
                )
                
                if qty > 0:
                    print(f"[*] Risk Manager Approved: Buying {qty} shares.")
                    print(f"    -> Max Portfolio Risk on this trade: {risk_details['portfolio_risk_pct']}% (₹{risk_details['max_loss_if_stopped']})")
                    
                    broker.place_order(
                        symbol=item['Stock'],
                        order_type="MARKET",
                        quantity=qty,
                        price=item['Price'],
                        stop_loss=setup.get("stop_loss"),
                        target=setup.get("target1")
                    )
                else:
                    print(f"[!] Risk Manager Rejected Trade: {risk_details}")
        else:
            print("  No valid trade setup generated (Failed quality/risk rules).")

if __name__ == "__main__":
    main()