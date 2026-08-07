from fastapi import FastAPI
from fastapi.responses import HTMLResponse
from fastapi.middleware.cors import CORSMiddleware
from scanner import analyze_stock
import uvicorn
import json
import os
import sqlite3

app = FastAPI(title="BrainTrader OS Pro")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

DB_PATH = r"C:\BrainTrader\trade_history.db"

HTML_LAYOUT = """
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>BrainTrader App</title>
    <link href="https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700;800&display=swap" rel="stylesheet">
    <style>
        * { box-sizing: border-box; margin: 0; padding: 0; font-family: 'Inter', sans-serif; }
        body { background-color: #0b0e14; color: #f1f5f9; padding: 20px; }
        .container { max-width: 850px; margin: 0 auto; }
        
        .header { display: flex; justify-content: space-between; align-items: center; margin-bottom: 24px; }
        .logo { font-size: 24px; font-weight: 800; color: #fff; }
        .logo span { color: #00e676; }
        
        /* Navigation Tabs */
        .main-nav { display: flex; gap: 15px; margin-bottom: 24px; border-bottom: 1px solid #1e293b; padding-bottom: 10px; }
        .nav-btn { background: transparent; border: none; color: #64748b; font-size: 16px; font-weight: 700; cursor: pointer; padding: 8px 12px; }
        .nav-btn.active { color: #00e676; border-bottom: 2px solid #00e676; }
        
        .view-section { display: none; }
        .view-section.active { display: block; }

        /* Capital Allocator */
        .capital-box { background: #0f172a; padding: 20px; border-radius: 10px; border: 1px solid #1e293b; margin-bottom: 20px; display: flex; align-items: center; gap: 15px; flex-wrap: wrap; }
        .capital-label { color: #94a3b8; font-weight: 700; font-size: 14px; text-transform: uppercase; }
        .capital-input { background: #0b0e14; border: 1px solid #1e293b; color: #fff; padding: 10px 16px; border-radius: 6px; font-size: 18px; font-weight: 700; width: 150px; outline: none; }
        .capital-input:focus { border-color: #00e676; }
        .capital-summary { color: #38bdf8; font-weight: 600; font-size: 14px; }

        /* Today's Feed */
        .section-header { font-size: 14px; font-weight: 700; color: #64748b; text-transform: uppercase; margin-bottom: 14px; display: flex; justify-content: space-between; align-items: center; }
        .recom-card { background: #0f172a; border: 1px solid #1e293b; border-left: 4px solid #00e676; border-radius: 10px; padding: 18px; margin-bottom: 12px; display: flex; justify-content: space-between; align-items: center; }
        .recom-sym { font-size: 20px; font-weight: 800; color: #fff; display: flex; align-items: center; gap: 10px; }
        .recom-details { font-size: 13px; color: #94a3b8; margin-top: 8px; display: flex; gap: 16px; }
        .qty-badge { background: rgba(56,189,248,0.15); color: #38bdf8; padding: 4px 10px; border-radius: 6px; font-size: 14px; font-weight: 800; border: 1px solid rgba(56,189,248,0.3); }
        .recom-btn { background: #1e293b; color: #00e676; border: 1px solid #00e676; padding: 8px 16px; border-radius: 6px; font-weight: 700; cursor: pointer; }
        .recom-btn:hover { background: #00e676; color: #000; }
        
        /* Search */
        .search-box { display: flex; gap: 10px; margin-bottom: 24px; }
        input.search-input { flex: 1; padding: 16px; border-radius: 8px; border: 1px solid #1e293b; background: #0f172a; color: #fff; font-size: 16px; outline: none; }
        input.search-input:focus { border-color: #00e676; }
        button.btn-search { background: #00e676; color: #000; font-weight: 700; border: none; padding: 0 24px; border-radius: 8px; cursor: pointer; font-size: 16px; }
        
        /* Timeframe Tabs */
        .tabs { display: flex; gap: 10px; margin-bottom: 20px; background: #0f172a; padding: 8px; border-radius: 10px; }
        .tab { flex: 1; text-align: center; padding: 12px; border-radius: 6px; cursor: pointer; font-weight: 600; color: #64748b; transition: 0.2s; }
        .tab.active { background: #1e293b; color: #00e676; }
        
        /* Clean Trade Card */
        .trade-card { background: #0f172a; border: 1px solid #1e293b; border-radius: 12px; padding: 24px; display: none; margin-bottom: 20px;}
        .tc-header { display: flex; justify-content: space-between; border-bottom: 1px solid #1e293b; padding-bottom: 16px; margin-bottom: 16px; }
        .tc-symbol { font-size: 28px; font-weight: 800; }
        .tc-price { font-size: 18px; color: #94a3b8; }
        .badge { padding: 8px 16px; border-radius: 8px; font-weight: 700; font-size: 14px; }
        .badge.buy { background: rgba(0, 230, 118, 0.15); color: #00e676; border: 1px solid #00e676; }
        .badge.wait { background: rgba(239, 68, 68, 0.15); color: #ef4444; border: 1px solid #ef4444; }

        .tc-grid { display: grid; grid-template-columns: 1fr 1fr; gap: 16px; margin-bottom: 20px; }
        .tc-box { background: #0b0e14; padding: 16px; border-radius: 8px; border: 1px solid #1e293b; }
        .tc-label { font-size: 12px; color: #64748b; text-transform: uppercase; font-weight: 700; margin-bottom: 4px; }
        .tc-value { font-size: 20px; font-weight: 700; color: #fff; }
        .tc-value.green { color: #00e676; }
        .tc-value.red { color: #ef4444; }
        .tc-subtext { font-size: 12px; font-weight: 600; margin-top: 4px; }

        .trailing-sl-box { background: rgba(56, 189, 248, 0.1); border: 1px solid rgba(56, 189, 248, 0.3); padding: 16px; border-radius: 8px; color: #38bdf8; font-weight: 600; font-size: 14px; }
        .loader { display: none; text-align: center; color: #00e676; font-weight: 600; margin: 40px 0; }
        
        /* History Table & Badges */
        .history-table { width: 100%; border-collapse: collapse; background: #0f172a; border-radius: 10px; overflow: hidden; }
        .history-table th, .history-table td { padding: 14px; text-align: left; border-bottom: 1px solid #1e293b; font-size: 14px; }
        .history-table th { background: #162032; color: #64748b; font-weight: 700; text-transform: uppercase; font-size: 12px; }
        .status-badge { padding: 4px 8px; border-radius: 4px; font-weight: 700; font-size: 12px; }
        .status-badge.ACTIVE { color: #38bdf8; background: rgba(56,189,248,0.1); }
        .status-badge.WON { color: #00e676; background: rgba(0,230,118,0.1); }
        .status-badge.LOST { color: #ef4444; background: rgba(239,68,68,0.1); }
        .win-rate-box { background: #1e293b; padding: 8px 16px; border-radius: 8px; color: #fff; font-size: 16px; font-weight: 700; }
        .win-rate-box span { color: #00e676; font-size: 18px; }
    </style>
</head>
<body>
    <div class="container">
        <div class="header">
            <div class="logo">BrainTrader<span>.</span></div>
            <div style="color: #64748b; font-weight: 600; font-size: 14px;">End-of-Day Screening App</div>
        </div>

        <div class="main-nav">
            <button class="nav-btn active" onclick="switchView('live')">Live Scanner</button>
            <button class="nav-btn" onclick="switchView('history'); loadHistory();">Past Performance</button>
        </div>

        <!-- Live Scanner View -->
        <div id="view-live" class="view-section active">
            <div class="capital-box">
                <div class="capital-label">Investable Capital (₹) :</div>
                <input type="number" id="capitalInput" class="capital-input" placeholder="e.g. 20000" oninput="renderFeed()">
                <div id="allocSummary" class="capital-summary">Enter amount to auto-calculate share quantities.</div>
            </div>

            <div class="section-header">
                <span>Today's Top Recommendations</span>
                <span id="lastUpdated" style="color: #00e676;">--</span>
            </div>
            
            <div id="recomFeed" style="margin-bottom: 30px;">Loading recommendations...</div>

            <div class="section-header"><span>Individual Stock Search</span></div>
            <div class="tabs">
                <div class="tab active" id="tab-short" onclick="setTimeframe('short')">Short Term (Days)</div>
                <div class="tab" id="tab-mid" onclick="setTimeframe('mid')">Mid Term (Weeks)</div>
                <div class="tab" id="tab-long" onclick="setTimeframe('long')">Long Term (Months)</div>
            </div>

            <div class="search-box">
                <input type="text" id="symbolInput" class="search-input" placeholder="Enter Stock Symbol (e.g. RELIANCE, ZOMATO)" onkeypress="if(event.key==='Enter') analyze()">
                <button class="btn-search" onclick="analyze()">Scan Stock</button>
            </div>

            <div id="loader" class="loader">Scanning Stock Data...</div>

            <div class="trade-card" id="tradeCard">
                <div class="tc-header">
                    <div>
                        <div class="tc-symbol" id="c-sym">--</div>
                        <div class="tc-price" id="c-price">₹0.00</div>
                    </div>
                    <div class="badge wait" id="c-badge">WAIT</div>
                </div>

                <div class="tc-grid">
                    <div class="tc-box">
                        <div class="tc-label">Entry Price</div>
                        <div class="tc-value" id="c-entry">--</div>
                        <div class="tc-subtext" id="c-alloc-shares" style="color:#38bdf8;">Allocated: -- shares</div>
                    </div>
                    <div class="tc-box">
                        <div class="tc-label">Stop Loss (Risk)</div>
                        <div class="tc-value red" id="c-sl">--</div>
                        <div class="tc-subtext red" id="c-risk-amt">Total Risk: --</div>
                    </div>
                    <div class="tc-box">
                        <div class="tc-label">Target 1 Profit</div>
                        <div class="tc-value green" id="c-t1">--</div>
                        <div class="tc-subtext green" id="c-t1-profit">Est. Profit: --</div>
                    </div>
                    <div class="tc-box">
                        <div class="tc-label">Target 2 Profit</div>
                        <div class="tc-value green" id="c-t2">--</div>
                        <div class="tc-subtext green" id="c-t2-profit">Est. Profit: --</div>
                    </div>
                </div>
                <div class="trailing-sl-box" id="c-trail">Trailing SL Strategy: --</div>
            </div>
        </div>

        <!-- History View -->
        <div id="view-history" class="view-section">
            <div class="section-header">
                <span>All Logged Trades</span>
                <div class="win-rate-box">Win Rate: <span id="winRateDisplay">--%</span></div>
            </div>
            <table class="history-table">
                <thead>
                    <tr>
                        <th>Date</th>
                        <th>Symbol</th>
                        <th>Entry</th>
                        <th>Target</th>
                        <th>Stop Loss</th>
                        <th>Status</th>
                    </tr>
                </thead>
                <tbody id="historyBody">
                    <tr><td colspan="6" style="text-align:center;">Loading history...</td></tr>
                </tbody>
            </table>
        </div>
    </div>

    <script>
        let currentTimeframe = 'short';
        let currentSetups = [];

        function switchView(viewId) {
            document.querySelectorAll('.nav-btn').forEach(btn => btn.classList.remove('active'));
            document.querySelectorAll('.view-section').forEach(sec => sec.classList.remove('active'));
            event.target.classList.add('active');
            document.getElementById('view-' + viewId).classList.add('active');
        }

        async function loadDailyRecommendations() {
            try {
                const res = await fetch('/get_daily_setups');
                const data = await res.json();
                document.getElementById('lastUpdated').innerText = data.last_updated || 'Not run yet';
                if (data.setups && data.setups.length > 0) {
                    currentSetups = data.setups;
                    renderFeed();
                } else {
                    document.getElementById('recomFeed').innerHTML = '<div style="background:#0f172a; padding:16px; border-radius:8px; color:#64748b;">No EOD scan results found. Run master scan.</div>';
                }
            } catch (e) {
                document.getElementById('recomFeed').innerText = 'No data available.';
            }
        }

        function renderFeed() {
            const feed = document.getElementById('recomFeed');
            const capitalInput = document.getElementById('capitalInput').value;
            const totalCapital = parseFloat(capitalInput);
            
            let html = '';
            let hasCapital = !isNaN(totalCapital) && totalCapital > 0;
            let capitalPerStock = hasCapital ? (totalCapital / currentSetups.length) : 0;
            
            if(hasCapital) {
                document.getElementById('allocSummary').innerText = `Allocating approx ₹${capitalPerStock.toFixed(0)} per stock (${currentSetups.length} stocks)`;
            } else {
                document.getElementById('allocSummary').innerText = `Enter amount to auto-calculate share quantities.`;
            }

            currentSetups.forEach(s => {
                let entryPrice = parseFloat(s.TradeSetup.entry);
                let qtyHtml = '';
                if (hasCapital) {
                    let qty = Math.floor(capitalPerStock / entryPrice);
                    if (qty > 0) {
                        let cost = (qty * entryPrice).toFixed(2);
                        qtyHtml = `<div class="qty-badge">Buy ${qty} Shares (Cost: ₹${cost})</div>`;
                    } else {
                        qtyHtml = `<div class="qty-badge" style="color:#ef4444; border-color:#ef4444; background:rgba(239,68,68,0.15);">Not enough capital</div>`;
                    }
                }
                html += `
                    <div class="recom-card">
                        <div>
                            <div class="recom-sym">🟢 ${s.Stock.replace('.NS','')} ${qtyHtml}</div>
                            <div class="recom-details">
                                <span>Entry: <b>₹${s.TradeSetup.entry}</b></span>
                                <span>SL: <b style="color:#ef4444;">₹${s.TradeSetup.stop_loss}</b></span>
                                <span>T1: <b style="color:#00e676;">₹${s.TradeSetup.target_1}</b></span>
                            </div>
                        </div>
                        <button class="recom-btn" onclick="quickScan('${s.Stock.replace('.NS','')}')">View Details</button>
                    </div>`;
            });
            feed.innerHTML = html;
        }

        function quickScan(symbol) {
            document.getElementById('symbolInput').value = symbol;
            analyze();
        }

        function setTimeframe(tf) {
            currentTimeframe = tf;
            document.querySelectorAll('.tab').forEach(t => t.classList.remove('active'));
            document.getElementById('tab-' + tf).classList.add('active');
            if(document.getElementById('symbolInput').value) analyze();
        }

        async function analyze() {
            let symbol = document.getElementById('symbolInput').value.trim().toUpperCase();
            if(!symbol) return;
            document.getElementById('tradeCard').style.display = 'none';
            document.getElementById('loader').style.display = 'block';

            try {
                const response = await fetch(`/analyze/${symbol}?timeframe=${currentTimeframe}`);
                const data = await response.json();
                
                document.getElementById('c-sym').innerText = data.Stock.replace('.NS','');
                document.getElementById('c-price').innerText = `Current: ₹${data.Price}`;
                
                const badge = document.getElementById('c-badge');
                badge.innerText = data.Decision;
                badge.className = data.Decision === 'STRONG_BUY' ? 'badge buy' : 'badge wait';

                const setup = data.TradeSetup || {};
                let entry = parseFloat(setup.entry) || 0;
                let sl = parseFloat(setup.stop_loss) || 0;
                let t1 = parseFloat(setup.target_1) || 0;
                let t2 = parseFloat(setup.target_2) || 0;

                document.getElementById('c-entry').innerText = entry ? `₹${entry}` : '--';
                document.getElementById('c-sl').innerText = sl ? `₹${sl}` : '--';
                document.getElementById('c-t1').innerText = t1 ? `₹${t1}` : '--';
                document.getElementById('c-t2').innerText = t2 ? `₹${t2}` : '--';
                document.getElementById('c-trail').innerText = setup.trailing_sl ? `Trailing SL Strategy: ${setup.trailing_sl}` : 'No active trade setup.';

                const capitalInput = parseFloat(document.getElementById('capitalInput').value);
                if (!isNaN(capitalInput) && capitalInput > 0 && entry > 0) {
                    let count = currentSetups.length > 0 ? currentSetups.length : 1;
                    let allocatedCap = capitalInput / count;
                    let qty = Math.floor(allocatedCap / entry);

                    if (qty > 0) {
                        document.getElementById('c-alloc-shares').innerText = `Allocated: ${qty} shares (₹${(qty * entry).toFixed(2)})`;
                        document.getElementById('c-risk-amt').innerText = `Total Risk: -₹${((entry - sl) * qty).toFixed(2)}`;
                        document.getElementById('c-t1-profit').innerText = `Est. Profit: +₹${((t1 - entry) * qty).toFixed(2)}`;
                        document.getElementById('c-t2-profit').innerText = `Est. Profit: +₹${((t2 - entry) * qty).toFixed(2)}`;
                    } else {
                        document.getElementById('c-alloc-shares').innerText = `Insufficient capital`;
                        document.getElementById('c-risk-amt').innerText = `Total Risk: --`;
                        document.getElementById('c-t1-profit').innerText = `Est. Profit: --`;
                        document.getElementById('c-t2-profit').innerText = `Est. Profit: --`;
                    }
                } else {
                    document.getElementById('c-alloc-shares').innerText = `Allocated: Enter capital above`;
                    document.getElementById('c-risk-amt').innerText = `Total Risk: --`;
                    document.getElementById('c-t1-profit').innerText = `Est. Profit: --`;
                    document.getElementById('c-t2-profit').innerText = `Est. Profit: --`;
                }
                document.getElementById('tradeCard').style.display = 'block';
            } catch (err) {
                alert("Could not load data for this stock.");
            } finally {
                document.getElementById('loader').style.display = 'none';
            }
        }

        async function loadHistory() {
            try {
                const res = await fetch('/get_history');
                const data = await res.json();
                const tbody = document.getElementById('historyBody');
                
                let wonCount = 0;
                let closedTrades = 0;

                if (data.length > 0) {
                    tbody.innerHTML = data.reverse().map(row => {
                        let status = row[6];
                        if (status === 'WON') { wonCount++; closedTrades++; }
                        if (status === 'LOST') { closedTrades++; }
                        
                        return `
                        <tr>
                            <td style="color:#94a3b8;">${row[1]}</td>
                            <td style="font-weight:700; color:#fff;">${row[2].replace('.NS','')}</td>
                            <td>₹${row[3]}</td>
                            <td style="color:#00e676;">₹${row[4]}</td>
                            <td style="color:#ef4444;">₹${row[5]}</td>
                            <td><span class="status-badge ${status}">${status}</span></td>
                        </tr>
                    `}).join('');
                    
                    if (closedTrades > 0) {
                        let winRate = ((wonCount / closedTrades) * 100).toFixed(1);
                        document.getElementById('winRateDisplay').innerText = `${winRate}%`;
                        document.getElementById('winRateDisplay').style.color = winRate >= 50 ? '#00e676' : '#ef4444';
                    } else {
                        document.getElementById('winRateDisplay').innerText = 'N/A';
                    }
                } else {
                    tbody.innerHTML = '<tr><td colspan="6" style="text-align:center;">No trades logged yet.</td></tr>';
                }
            } catch (e) {
                document.getElementById('historyBody').innerHTML = '<tr><td colspan="6">Error loading data.</td></tr>';
            }
        }

        loadDailyRecommendations();
    </script>
</body>
</html>
"""

@app.get("/", response_class=HTMLResponse)
def get_dashboard():
    return HTML_LAYOUT

@app.get("/get_daily_setups")
def get_daily_setups():
    file_path = r"C:\BrainTrader\daily_setups.json"
    if os.path.exists(file_path):
        with open(file_path, "r", encoding="utf-8") as f:
            return json.load(f)
    return {"last_updated": "Never", "setups": []}

@app.get("/get_history")
def get_history():
    if not os.path.exists(DB_PATH):
        return []
    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()
    c.execute("SELECT * FROM trades")
    rows = c.fetchall()
    conn.close()
    return rows

@app.get("/analyze/{symbol}")
def analyze_single_stock(symbol: str, timeframe: str = "short"):
    symbol = symbol.upper()
    if not symbol.endswith(".NS"):
         symbol += ".NS"
    result = analyze_stock(symbol, timeframe)
    if not result:
        return {"Stock": symbol, "Price": 0, "Decision": "ERROR"}
    return result

if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8000)