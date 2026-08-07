"""
BrainTrader Cloud API & Web App V2
------------------------------
Includes Instant Search + Daily Auto-Scan Feed
"""

from fastapi import FastAPI, HTTPException
from fastapi.responses import HTMLResponse
from fastapi.middleware.cors import CORSMiddleware
from scanner import analyze_stock
import uvicorn
import os
import re

app = FastAPI(title="BrainTrader OS")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

HTML_LAYOUT = """
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>BrainTrader OS</title>
    <link href="https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700&display=swap" rel="stylesheet">
    <style>
        * { box-sizing: border-box; margin: 0; padding: 0; font-family: 'Inter', sans-serif; }
        body { background-color: #0b0e14; color: #e1e7ef; padding: 20px; min-height: 100vh; }
        .container { max-width: 900px; margin: 0 auto; }
        
        .header { display: flex; align-items: center; justify-content: space-between; padding-bottom: 24px; border-bottom: 1px solid #1e2638; margin-bottom: 28px; }
        .logo { font-size: 24px; font-weight: 700; color: #ffffff; display: flex; align-items: center; gap: 10px; }
        .logo span { color: #00e676; }
        .status-badge { background: #132219; color: #00e676; border: 1px solid #1b432a; padding: 6px 12px; border-radius: 20px; font-size: 13px; font-weight: 600; }

        /* Search Box */
        .search-box { background: #131822; border: 1px solid #222b3e; padding: 20px; border-radius: 12px; margin-bottom: 28px; }
        .section-title { font-size: 14px; font-weight: 600; color: #8a99ad; margin-bottom: 12px; text-transform: uppercase; letter-spacing: 0.5px; }
        .input-group { display: flex; gap: 10px; }
        input[type="text"] { flex: 1; background: #0b0e14; border: 1px solid #2a364f; color: #fff; padding: 14px 18px; border-radius: 8px; font-size: 16px; outline: none; transition: border 0.2s; }
        input[type="text"]:focus { border-color: #00e676; }
        button { background: #00e676; color: #000; border: none; padding: 14px 24px; border-radius: 8px; font-weight: 700; font-size: 15px; cursor: pointer; transition: all 0.2s; }
        button:hover { background: #00c853; }
        button:disabled { background: #2a364f; color: #62728d; cursor: not-allowed; }

        /* Daily Feed Section */
        .daily-feed { margin-bottom: 28px; }
        .feed-card { background: linear-gradient(145deg, #131822 0%, #0b0e14 100%); border: 1px solid #222b3e; border-left: 4px solid #00e676; padding: 20px; border-radius: 12px; margin-bottom: 12px; display: flex; justify-content: space-between; align-items: center;}
        .feed-symbol { font-size: 20px; font-weight: 700; color: #fff; }
        .feed-price { font-size: 16px; color: #a0aec0; margin-top: 4px; }
        .feed-btn { background: #1e2638; color: #fff; border: 1px solid #2a364f; padding: 8px 16px; border-radius: 6px; font-size: 13px; cursor: pointer; }
        .feed-btn:hover { background: #2a364f; }

        /* Result Card */
        .result-card { background: #131822; border: 1px solid #222b3e; border-radius: 12px; padding: 24px; display: none; margin-bottom: 40px;}
        .card-header { display: flex; justify-content: space-between; align-items: flex-start; margin-bottom: 20px; padding-bottom: 16px; border-bottom: 1px solid #1e2638; }
        .symbol-title { font-size: 28px; font-weight: 700; color: #fff; }
        .price-tag { font-size: 22px; font-weight: 600; color: #a0aec0; margin-top: 4px; }
        
        .badge { padding: 8px 16px; border-radius: 8px; font-size: 14px; font-weight: 700; letter-spacing: 0.5px; }
        .badge-buy { background: rgba(0, 230, 118, 0.15); color: #00e676; border: 1px solid #00e676; }
        .badge-wait { background: rgba(255, 193, 7, 0.15); color: #ffc107; border: 1px solid #ffc107; }

        .metrics-grid { display: grid; grid-template-columns: repeat(auto-fit, minmax(180px, 1fr)); gap: 14px; margin-bottom: 24px; }
        .metric-item { background: #0b0e14; border: 1px solid #1e2638; padding: 16px; border-radius: 8px; }
        .metric-label { font-size: 12px; color: #718096; text-transform: uppercase; margin-bottom: 6px; font-weight: 600; }
        .metric-val { font-size: 18px; font-weight: 700; color: #fff; }

        .list-item { background: #0b0e14; border-left: 3px solid #00e676; padding: 10px 14px; margin-bottom: 8px; border-radius: 0 6px 6px 0; font-size: 14px; color: #e2e8f0; }
        .warning-item { border-left-color: #ffc107; color: #e2e8f0; }
        .spinner { display: none; text-align: center; padding: 40px 0; color: #00e676; font-size: 16px; font-weight: 600; }
    </style>
</head>
<body>
    <div class="container">
        <div class="header">
            <div class="logo">🧠 BrainTrader <span>OS</span></div>
            <div class="status-badge">● Engine Online</div>
        </div>

        <div class="daily-feed" id="dailyFeedBlock">
            <div class="section-title">Today's Top Algorithmic Setups</div>
            <div id="feedContent">Loading daily market scan...</div>
        </div>

        <div class="search-box">
            <div class="section-title">Instant Stock Analyzer</div>
            <div class="input-group">
                <input type="text" id="symbolInput" placeholder="Enter NSE Symbol (e.g. RELIANCE)" onkeypress="if(event.key==='Enter') analyzeStock()">
                <button id="searchBtn" onclick="analyzeStock()">Analyze</button>
            </div>
        </div>

        <div id="loader" class="spinner">
            ⚡ Running Quantitative & Smart Money Analysis... Please wait.
        </div>

        <div id="resultCard" class="result-card">
            <div class="card-header">
                <div>
                    <div id="stockSymbol" class="symbol-title">--</div>
                    <div id="stockPrice" class="price-tag">₹0.00</div>
                </div>
                <div id="decisionBadge" class="badge badge-wait">WAIT</div>
            </div>

            <div class="metrics-grid">
                <div class="metric-item"><div class="metric-label">Score</div><div id="mScore" class="metric-val">0</div></div>
                <div class="metric-item"><div class="metric-label">Confidence</div><div id="mConfidence" class="metric-val">0%</div></div>
                <div class="metric-item"><div class="metric-label">Entry Zone</div><div id="mEntry" class="metric-val">-</div></div>
                <div class="metric-item"><div class="metric-label">Stop Loss</div><div id="mSL" class="metric-val">-</div></div>
                <div class="metric-item"><div class="metric-label">Target 1</div><div id="mTarget" class="metric-val">-</div></div>
                <div class="metric-item"><div class="metric-label">Risk : Reward</div><div id="mRR" class="metric-val">-</div></div>
            </div>

            <div class="section-title">Institutional Reasons</div>
            <div id="reasonsList"></div>

            <div class="section-title">Risk Warnings</div>
            <div id="warningsList"></div>
        </div>
    </div>

    <script>
        // Load Daily Report on Startup
        async function loadDailyFeed() {
            try {
                const res = await fetch('/daily_report');
                const data = await res.json();
                const feed = document.getElementById('feedContent');
                
                if(data.trades && data.trades.length > 0) {
                    feed.innerHTML = data.trades.map(t => `
                        <div class="feed-card">
                            <div>
                                <div class="feed-symbol">🟢 ${t.stock}</div>
                                <div class="feed-price">Entry Level: ₹${t.price}</div>
                            </div>
                            <button class="feed-btn" onclick="document.getElementById('symbolInput').value='${t.stock}'; analyzeStock();">Deep Dive</button>
                        </div>
                    `).join('');
                } else {
                    feed.innerHTML = `<div style="padding: 20px; background: #131822; border-radius: 8px; color: #8a99ad;">No STRONG_BUY setups detected in today's scan. Capital preserved.</div>`;
                }
            } catch (err) {
                document.getElementById('feedContent').innerHTML = `<div style="color: #ff5252;">Could not load daily report.</div>`;
            }
        }

        async function analyzeStock() {
            const input = document.getElementById('symbolInput');
            const symbol = input.value.trim();
            if(!symbol) return;

            const loader = document.getElementById('loader');
            const card = document.getElementById('resultCard');
            const btn = document.getElementById('searchBtn');

            card.style.display = 'none';
            loader.style.display = 'block';
            btn.disabled = true;

            try {
                const response = await fetch(`/analyze/${symbol}`);
                if (!response.ok) throw new Error("Stock not found or failed to load data.");
                const data = await response.json();

                document.getElementById('stockSymbol').innerText = data.Stock;
                document.getElementById('stockPrice').innerText = `₹${data.Price.toFixed(2)}`;
                
                const badge = document.getElementById('decisionBadge');
                badge.innerText = data.Decision;
                badge.className = (data.Decision === 'STRONG_BUY' || data.Decision === 'BUY_WATCH') ? 'badge badge-buy' : 'badge badge-wait';

                document.getElementById('mScore').innerText = data.Score;
                document.getElementById('mConfidence').innerText = `${data.Confidence}%`;

                const setup = data.TradeSetup || {};
                document.getElementById('mEntry').innerText = setup.entry_zone || 'N/A';
                document.getElementById('mSL').innerText = setup.stop_loss ? `₹${setup.stop_loss}` : 'N/A';
                document.getElementById('mTarget').innerText = setup.target1 ? `₹${setup.target1}` : 'N/A';
                document.getElementById('mRR').innerText = setup.risk_reward ? `${setup.risk_reward} R` : 'N/A';

                document.getElementById('reasonsList').innerHTML = data.Reasons.length > 0 
                    ? data.Reasons.map(r => `<div class="list-item">✓ ${r}</div>`).join('') 
                    : '<div style="color:#718096; font-size:14px;">No specific bullish triggers.</div>';

                document.getElementById('warningsList').innerHTML = data.Warnings.length > 0 
                    ? data.Warnings.map(w => `<div class="list-item warning-item">⚠️ ${w}</div>`).join('') 
                    : '<div style="color:#718096; font-size:14px;">No major risk flags.</div>';

                card.style.display = 'block';
            } catch (err) {
                alert("Error: " + err.message);
            } finally {
                loader.style.display = 'none';
                btn.disabled = false;
            }
        }
        
        // Initialize Feed
        loadDailyFeed();
    </script>
</body>
</html>
"""

@app.get("/", response_class=HTMLResponse)
def get_dashboard():
    return HTML_LAYOUT

@app.get("/daily_report")
def get_daily_report():
    """Reads the local daily_trade_report.txt and parses the setups to display on the web"""
    report_path = r"C:\BrainTrader\daily_trade_report.txt"
    trades = []
    
    if os.path.exists(report_path):
        with open(report_path, "r") as f:
            content = f.read()
            # Regex to find BOUGHT lines: -> BOUGHT 100 shares of TCS.NS @ ₹3500.5
            pattern = r"BOUGHT\s+\d+\s+shares of\s+([A-Z0-9.-]+)\s+@\s+₹([0-9.]+)"
            matches = re.findall(pattern, content)
            
            # Remove duplicates just in case multiple scans ran
            seen = set()
            for stock, price in matches:
                if stock not in seen:
                    trades.append({"stock": stock, "price": price})
                    seen.add(stock)
                    
    return {"trades": trades}

@app.get("/analyze/{symbol}")
def analyze_single_stock(symbol: str):
    symbol = symbol.upper()
    if not symbol.endswith(".NS"):
         symbol += ".NS"
         
    try:
        result = analyze_stock(symbol)
        if not result:
            raise HTTPException(status_code=404, detail="Could not analyze stock.")
        return result
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8000)