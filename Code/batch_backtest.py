"""
BrainTrader
------------------------
Batch Historical Backtest Engine (Phase 6)

Runs historical walk-forward tests across multiple stocks simultaneously,
aggregating trade logs, win rates, and portfolio returns to measure 
strategy expectancy.
"""

import pandas as pd
import yfinance as yf
from datetime import timedelta
import logging

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
from watchlists import NIFTY50

logging.basicConfig(level=logging.WARNING)

def run_stock_backtest(symbol, start_date="2024-01-01", end_date="2026-01-01", initial_capital=200000):
    print(f"[*] Backtesting {symbol}...")
    fetch_start = pd.to_datetime(start_date) - timedelta(days=400)
    
    try:
        df = yf.download(symbol, start=fetch_start, end=end_date, progress=False)
        if df.empty or len(df) < 200:
            return None
            
        if isinstance(df.columns, pd.MultiIndex):
            df.columns = df.columns.get_level_values(0)
            
        df = df.reset_index()
        if 'Date' not in df.columns and 'Datetime' in df.columns:
            df.rename(columns={'Datetime': 'Date'}, inplace=True)
            
        df = calculate_indicators(df)
    except Exception as e:
        print(f"[!] Error loading {symbol}: {e}")
        return None

    start_idx = df[df['Date'] >= start_date].index
    if start_idx.empty:
        return None
    start_idx = start_idx[0]

    balance = initial_capital
    trades = []
    position = None

    # Walk-forward simulation
    for i in range(start_idx, len(df)):
        current_df = df.iloc[:i+1].copy()
        candle = current_df.iloc[-1]
        price = float(candle['Close'])
        date = candle['Date']

        # If we are holding a position, check for stop loss or target hit
        if position:
            if price <= position['stop_loss']:
                # Stopped out
                pnl = (position['stop_loss'] - position['entry']) * position['qty']
                balance += (position['qty'] * position['stop_loss'])
                trades.append({"symbol": symbol, "exit_date": date, "type": "STOP_LOSS", "pnl": pnl})
                position = None
            elif price >= position['target1']:
                # Target hit
                pnl = (position['target1'] - position['entry']) * position['qty']
                balance += (position['qty'] * position['target1'])
                trades.append({"symbol": symbol, "exit_date": date, "type": "TARGET_1", "pnl": pnl})
                position = None

        # Look for new entries if flat
        if not position:
            swings = detect_swings(current_df)
            swings = classify_swings(swings)
            swings = calculate_swing_strength(swings)
            swings = analyze_swings(swings)
            
            levels = find_support_resistance(swings)
            levels = nearest_levels(levels, price)
            liquidity = detect_liquidity_sweeps(current_df, swings)
            order_blocks = detect_order_blocks(current_df, [])
            fvgs = detect_fvgs(current_df)
            indicator_conf = indicator_confirmation(current_df)
            
            confluence = calculate_confluence(
                structure=None, bos=None, choch=None,
                liquidity=liquidity, support_resistance=levels,
                indicator=indicator_conf, price=price,
                order_blocks=order_blocks, fvgs=fvgs
            )
            
            # Relaxed threshold slightly for backtesting discovery
            if confluence.get("score", 0) >= 45:
                setup = generate_trade_setup(current_df, price, levels, confluence["score"], confluence["confidence"], "LONG")
                if setup:
                    risk_amt = balance * 0.10
                    qty = int(risk_amt / price)
                    if qty > 0:
                        position = {
                            "entry": price,
                            "qty": qty,
                            "stop_loss": setup["stop_loss"],
                            "target1": setup["target1"]
                        }
                        balance -= (qty * price)

    return {
        "symbol": symbol,
        "final_balance": balance,
        "net_profit": balance - initial_capital,
        "total_trades": len(trades),
        "trades": trades
    }

if __name__ == "__main__":
    print("=" * 50)
    print("BrainTrader Batch Backtest Engine (Phase 6)")
    print("=" * 50)
    
    # Test top 5 index stocks
    test_symbols = NIFTY50[:5] 
    results = []

    for sym in test_symbols:
        res = run_stock_backtest(sym)
        if res:
            results.append(res)

    print("\n" + "=" * 50)
    print("BATCH BACKTEST RESULTS SUMMARY")
    print("=" * 50)
    for r in results:
        print(f"Stock: {r['symbol']} | Trades: {r['total_trades']} | Net PnL: ₹{r['net_profit']:.2f}")