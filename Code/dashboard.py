"""
BrainTrader OS
------------------------
Visual Dashboard (Phase 11)

A professional web interface for the BrainTrader quantitative engine.
To run: python -m streamlit run Code/dashboard.py
"""

import streamlit as st
import pandas as pd
import time
from scanner import analyze_stock
# --- NEW: Added Midcap and Smallcap imports ---
from watchlists import NIFTY50, BANKNIFTY, NIFTY_MIDCAP, NIFTY_SMALLCAP

# --- UI CONFIGURATION ---
st.set_page_config(
    page_title="BrainTrader OS",
    page_icon="🧠",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Custom CSS for Institutional Look
st.markdown("""
    <style>
    .stApp { background-color: #0E1117; color: #FAFAFA; }
    .card { background-color: #1E2127; padding: 20px; border-radius: 10px; border-left: 5px solid #00C853; margin-bottom: 20px; }
    .card-wait { border-left: 5px solid #FFC107; }
    .card-short { border-left: 5px solid #FF5252; }
    .metric-value { font-size: 24px; font-weight: bold; }
    </style>
""", unsafe_allow_html=True)

# --- SIDEBAR & ROUTING ---
st.sidebar.title("🧠 BrainTrader OS")
st.sidebar.markdown("Institutional Swing Trading Engine")

# --- LIVE PORTFOLIO METRICS ---
st.sidebar.markdown("---")
st.sidebar.subheader("💼 Paper Portfolio")
st.sidebar.metric(label="Available Capital", value="₹10,00,000.00")
st.sidebar.metric(label="Active Positions", value="0")
st.sidebar.metric(label="Current Drawdown", value="0.00%")

st.sidebar.markdown("---")
# --- NEW: Updated Dropdown Menu ---
market_choice = st.sidebar.selectbox(
    "Select Market to Scan",
    ("Nifty 50", "Bank Nifty", "Nifty Midcap", "Nifty Smallcap")
)

# --- NEW: Map selection to all 4 watchlists ---
if market_choice == "Nifty 50":
    watchlist = NIFTY50
elif market_choice == "Bank Nifty":
    watchlist = BANKNIFTY
elif market_choice == "Nifty Midcap":
    watchlist = NIFTY_MIDCAP
elif market_choice == "Nifty Smallcap":
    watchlist = NIFTY_SMALLCAP

st.sidebar.markdown("---")
st.sidebar.write("**Risk Settings (Active)**")
st.sidebar.write("Max Risk Per Trade: 2.0%")
st.sidebar.write("Max Portfolio Exposure: 60%")

# --- MAIN DASHBOARD ---
st.title("Daily Market Recommendations")
st.write("Scanning multi-timeframe structural alignment, liquidity sweeps, and order blocks.")

if st.button("Run Quantitative Scan", type="primary"):
    
    progress_text = f"Scanning {market_choice}... Please wait."
    my_bar = st.progress(0, text=progress_text)
    
    results = []
    total_symbols = len(watchlist)
    
    # Run the scan (Sequential for Streamlit safety)
    with st.spinner("Analyzing Institutional Footprints..."):
        for i, symbol in enumerate(watchlist):
            res = analyze_stock(symbol)
            if res:
                results.append(res)
            my_bar.progress((i + 1) / total_symbols, text=f"Analyzing {symbol}...")
            
    my_bar.empty()
    
    # Sort results so best scores are at the top
    results.sort(key=lambda x: x["Score"], reverse=True)
    
    # --- DISPLAY RESULTS ---
    st.markdown("### 🎯 Trade Setups")
    
    buys = [r for r in results if r["Decision"] in ["STRONG_BUY", "BUY_WATCH"]]
    waits = [r for r in results if r["Decision"] not in ["STRONG_BUY", "BUY_WATCH"]]
    
    if not buys:
        st.warning(f"No HIGH-PROBABILITY trade setups detected in {market_choice} today. Capital preserved.")
    
    for item in buys:
        st.markdown(f"""
        <div class="card">
            <h3>🟢 {item['Stock']} (Score: {item['Score']})</h3>
            <p><b>Current Price:</b> ₹{item['Price']:.2f} | <b>Confidence:</b> {item['Confidence']}% | <b>Alignment:</b> {item['Alignment']}</p>
        </div>
        """, unsafe_allow_html=True)
        
        setup = item.get("TradeSetup")
        if setup:
            col1, col2, col3, col4 = st.columns(4)
            col1.metric("Entry Zone", setup.get("entry_zone", "N/A"))
            col2.metric("Stop Loss", f"₹{setup.get('stop_loss', 0)}")
            col3.metric("Target 1", f"₹{setup.get('target1', 0)}")
            col4.metric("Risk:Reward", setup.get("risk_reward", 0))
            
            with st.expander("View Logic & Trade Plan"):
                st.write("**Trailing Stop Plan:** Move to Breakeven at ₹" + str(setup.get("trailing_plan", {}).get("move_to_breakeven_at", "N/A")))
                st.write("**Algorithm Reasons:**")
                for r in item["Reasons"]:
                    st.write(f"- {r}")
                if item["Warnings"]:
                    st.write("**Warnings:**")
                    for w in item["Warnings"]:
                        st.write(f"⚠️ {w}")
    
    st.markdown("---")
    st.markdown("### 🛡️ Defensive Holds (WAIT)")
    with st.expander(f"View {len(waits)} stocks rejected by the Risk Engine"):
        for item in waits:
            st.write(f"**{item['Stock']}** | Price: ₹{item['Price']:.2f} | Score: {item['Score']}")
            if item["Warnings"]:
                st.write(f"Reason for rejection: {item['Warnings'][0]}")
            st.markdown("---")