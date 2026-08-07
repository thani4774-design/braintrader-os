"""
BrainTrader
------------------------
Historical Backtest Engine (Phase 6)

Simulates live market conditions by walking forward through historical data
candle by candle. Strictly prevents look-ahead bias and logs trades using 
our existing PaperTradingBroker interface.
"""

import logging
import pandas as pd
import yfinance as yf
from datetime import timedelta

# Import our production modules
from execution.broker_adapter import PaperTradingBroker
from indicators import calculate_indicators
from indicator_confirmation import indicator_confirmation
from market_structure.swing_points import detect_swings
from market_structure.swing_classifier import classify_swings
from market_structure.swing_strength import calculate_swing_strength
from market_structure.swing_analysis import analyze_swings
from market_structure.support_resistance import find_support_resistance, nearest_levels
from market_structure.liquidity_sweep import detect_liquidity_sweeps
from market_structure.order_blocks import detect_order_blocks
from market_structure.fvg_engine import detect_fvgs
from confluence_engine import calculate_confluence
from trade_engine import generate_trade_setup

logging.basicConfig(level=logging.WARNING) # Suppress info logs for speed

class BacktestEngine:
    def __init__(self, symbol, start_date, end_date, initial_capital=1000000):
        self.symbol = symbol
        self.start_date = start_date
        self.end_date = end_date
        self.broker = PaperTradingBroker(initial_balance=initial_capital)
        self.trade_log = []
        self.historical_data = None

    def fetch_data(self):
        print(f"[*] Fetching historical data for {self.symbol}...")
        # Fetch extra data before start_date to allow indicators (like 200 EMA) to calculate
        fetch_start = pd.to_datetime(self.start_date) - timedelta(days=400)
        df = yf.download(self.symbol, start=fetch_start, end=self.end_date, progress=False)
        
        if df.empty:
            raise ValueError("No data fetched. Check symbol and dates.")
            
        if isinstance(df.columns, pd.MultiIndex):
            df.columns = df.columns.get_level_values(0)
            
        df = df.reset_index()
        if 'Date' not in df.columns and 'Datetime' in df.columns:
            df.rename(columns={'Datetime': 'Date'}, inplace=True)
            
        self.historical_data = calculate_indicators(df)
        print(f"[+] Data loaded. Total candles: {len(self.historical_data)}")

    def run(self):
        self.fetch_data()
        
        # Find the starting index that matches our requested start_date
        start_idx = self.historical_data[self.historical_data['Date'] >= self.start_date].index
        if start_idx.empty:
            print("[!] Start date not found in data.")
            return
            
        start_idx = start_idx[0]
        total_steps = len(self.historical_data) - start_idx
        
        print(f"[*] Starting Walk-Forward Analysis ({total_steps} trading days)...")
        print("-" * 60)

        # Walk forward day by day
        for i in range(start_idx, len(self.historical_data)):
            # Create a "blind" dataframe containing only data up to the current day
            current_df = self.historical_data.iloc[:i+1].copy()
            latest_candle = current_df.iloc[-1]
            current_price = float(latest_candle['Close'])
            current_date = latest_candle['Date']
            
            # 1. Market Structure Pipeline
            swings = detect_swings(current_df)
            swings = classify_swings(swings)
            swings = calculate_swing_strength(swings)
            swings = analyze_swings(swings)
            
            # 2. SMC Zones
            levels = find_support_resistance(swings)
            levels = nearest_levels(levels, current_price)
            liquidity = detect_liquidity_sweeps(current_df, swings)
            order_blocks = detect_order_blocks(current_df, []) # Simplified OB for BT
            fvgs = detect_fvgs(current_df)
            indicator_conf = indicator_confirmation(current_df)
            
            # 3. Decision Engine
            confluence = calculate_confluence(
                structure=None, # Simplified for Single Timeframe backtest first
                bos=None,
                choch=None,
                liquidity=liquidity,
                support_resistance=levels,
                indicator=indicator_conf,
                price=current_price,
                order_blocks=order_blocks,
                fvgs=fvgs
            )
            
            decision = confluence.get("decision", "WAIT")
            
            # 4. Execution Logic
            if decision in ["STRONG_BUY"]:
                direction = "LONG"
                setup = generate_trade_setup(current_df, current_price, levels, confluence["score"], confluence["confidence"], direction)
                
                if setup:
                    # Risk 10% of current balance
                    risk_capital = self.broker.get_account_balance() * 0.10
                    qty = int(risk_capital / current_price)
                    
                    if qty > 0:
                        print(f"[{current_date.strftime('%Y-%m-%d')}] SIGNAL: {decision} | Score: {confluence['score']}")
                        success = self.broker.place_order(self.symbol, "MARKET", qty, current_price, setup.get("stop_loss"), setup.get("target1"))
                        if success:
                            self.trade_log.append({
                                "date": current_date,
                                "type": "BUY",
                                "price": current_price,
                                "qty": qty,
                                "score": confluence['score']
                            })

        print("-" * 60)
        print(f"[*] Backtest Complete. Final Balance: ₹{self.broker.get_account_balance():.2f}")
        print(f"[*] Total Trades Taken: {len(self.trade_log)}")

if __name__ == "__main__":
    # Test on Reliance over the last 2 years
    tester = BacktestEngine(symbol="RELIANCE.NS", start_date="2024-01-01", end_date="2026-08-01")
    tester.run()