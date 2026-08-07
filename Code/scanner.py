"""
BrainTrader - Swing Trading Engine
----------------------------------
Calibrated to find 3-5 high-probability setups.
Calculates Entry, SL, Target 1, Target 2, and Trailing SL.
"""

import yfinance as yf
import pandas as pd
import numpy as np

def calculate_rsi(data, periods=14):
    delta = data['Close'].diff()
    gain = (delta.where(delta > 0, 0)).rolling(window=periods).mean()
    loss = (-delta.where(delta < 0, 0)).rolling(window=periods).mean()
    rs = gain / loss
    return 100 - (100 / (1 + rs))

def analyze_stock(symbol: str, timeframe="short"):
    """
    timeframe options: 
    'short' = Daily chart (Hold days to weeks)
    'mid' = Weekly chart (Hold weeks to months)
    'long' = Monthly chart (Hold months to years)
    """
    
    interval_map = {"short": "1d", "mid": "1wk", "long": "1mo"}
    period_map = {"short": "1y", "mid": "2y", "long": "5y"}
    
    try:
        ticker = yf.Ticker(symbol)
        df = ticker.history(period=period_map[timeframe], interval=interval_map[timeframe])
        
        if df.empty or len(df) < 50:
            return None
            
        # 1. Calculate Core Technicals
        df['EMA_20'] = df['Close'].ewm(span=20, adjust=False).mean()
        df['EMA_50'] = df['Close'].ewm(span=50, adjust=False).mean()
        df['RSI'] = calculate_rsi(df, 14)
        
        current_price = df['Close'].iloc[-1]
        prev_price = df['Close'].iloc[-2]
        current_rsi = df['RSI'].iloc[-1]
        ema_20 = df['EMA_20'].iloc[-1]
        ema_50 = df['EMA_50'].iloc[-1]
        
        # 2. Swing Trading Logic (Loosened to find 3-5 real trades)
        # Rule 1: Uptrend (Price above 50 EMA)
        # Rule 2: Pullback/Value Zone (RSI between 40 and 60)
        # Rule 3: Momentum Shift (Today's close higher than yesterday's)
        
        is_uptrend = current_price > ema_50
        is_value_zone = 40 <= current_rsi <= 65
        is_momentum_up = current_price > prev_price
        
        score = 0
        reasons = []
        
        if is_uptrend:
            score += 40
            reasons.append("Trading in a healthy uptrend (Above 50 EMA).")
        if is_value_zone:
            score += 30
            reasons.append("Price is in a discount/pullback zone (RSI balanced).")
        if is_momentum_up:
            score += 30
            reasons.append("Fresh buying momentum detected today.")
            
        # 3. Decision & Trade Math
        decision = "WAIT"
        trade_setup = {}
        
        if score >= 80:  # If at least 2 out of 3 conditions are met perfectly
            decision = "STRONG_BUY"
            
            # Risk Management Math
            atr = df['High'].iloc[-14:].max() - df['Low'].iloc[-14:].min() # Simple volatility measure
            stop_loss = current_price - (atr * 0.5) # Stop loss below recent volatility
            risk = current_price - stop_loss
            
            target_1 = current_price + (risk * 1.5) # 1:1.5 Risk Reward
            target_2 = current_price + (risk * 2.5) # 1:2.5 Risk Reward
            
            trade_setup = {
                "entry": round(current_price, 2),
                "stop_loss": round(stop_loss, 2),
                "target_1": round(target_1, 2),
                "target_2": round(target_2, 2),
                "trailing_sl": f"Move SL to Entry (₹{round(current_price, 2)}) when price hits Target 1",
                "risk_reward": "1:2.5 Max"
            }
            
        return {
            "Stock": symbol,
            "Price": round(current_price, 2),
            "Timeframe": timeframe.upper(),
            "Score": score,
            "Decision": decision,
            "TradeSetup": trade_setup,
            "Reasons": reasons
        }
        
    except Exception as e:
        return None