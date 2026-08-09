from fastapi import FastAPI
from fastapi.responses import HTMLResponse
from fastapi.middleware.cors import CORSMiddleware
import uvicorn
import json
import os
import sys
import sqlite3

# Ensure Code folder is in system path to import Fund Manager cleanly
CODE_DIR = os.path.dirname(os.path.abspath(__file__))
if CODE_DIR not in sys.path:
    sys.path.append(CODE_DIR)

# Import from the SMC Fund Manager instead of the old scanner
from fund_manager import analyze_stock, run_master_scan

app = FastAPI(title="BrainTrader OS Pro V4.3")

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
        
        .main-nav { display: flex; gap: 15px; margin-bottom: 24px; border-bottom: 1px solid #1e293b; padding-bottom: 10px; }
        .nav-btn { background: transparent; border: none; color: #64748b; font-size: 16px; font-weight: 700; cursor: pointer; padding: 8px 12px; transition: 0.2s; }
        .nav-btn.active { color: #00e676; border-bottom: 2px solid #00e676; }
        .nav-btn.wealth-active { color: #c084fc; border-bottom: 2px solid #c084fc; }
        
        .view-section { display: none; }
        .view-section.active { display: block; }

        .capital-box { background: #0f172a; padding: 20px; border-radius: 10px; border: 1px solid #1e293b; margin-bottom: 20px; }
        .cap-top { display: flex; align-items: center; gap: 15px; flex-wrap: wrap; margin-bottom: 10px; }
        .capital-label { color: #94a3b8; font-weight: 700; font-size: 14px; text-transform: uppercase; }
        .capital-input { background: #0b0e14; border: 1px solid #1e293b; color: #fff; padding: 10px 16px; border-radius: 6px; font-size: 18px; font-weight: 700; width: 150px; outline: none; }
        .capital-input:focus { border-color: #00e676; }
        .capital-summary { color: #38bdf8; font-weight: 600; font-size: 14px; background: rgba(56,189,248,0.1); padding: 8px 12px; border-radius: 6px; display: inline-block;}
        .clear-btn { background: transparent; border: 1px solid #ef4444; color: #ef4444; padding: 8px 16px; border-radius: 6px; font-weight: 700; cursor: pointer; font-size: 14px; }
        .clear-btn:hover { background: rgba(239, 68, 68, 0.1); }

        .controls-row { display: flex; justify-content: space-between; align-items: center; margin-bottom: 14px; background: #0f172a; padding: 12px 16px; border-radius: 8px; border: 1px solid #1e293b;}
        .section-header { font-size: 14px; font-weight: 700; color: #64748b; text-transform: uppercase; display: flex; align-items: center; gap: 10px;}
        .sort-select { background: #1e293b; color: #fff; border: 1px solid #334155; padding: 8px 12px; border-radius: 6px; font-weight: 600; outline: none; cursor: pointer;}
        
        .recom-card { background: #0f172a; border: 1px solid #1e293b; border-left: 4px solid #00e676; border-radius: 10px; margin-bottom: 12px; overflow: hidden; transition: 0.2s;}
        .recom-card.wealth { border-left: 4px solid #c084fc; }
        .rc-main { padding: 18px; display: flex; justify-content: space-between; align-items: center; }
        .rc-left { display: flex; align-items: center; gap: 15px; }
        .rc-checkbox { width: 22px; height: 22px; accent-color: #00e676; cursor: pointer; }
        .rc-checkbox.wealth { accent-color: #c084fc; }
        
        .recom-sym { font-size: 20px; font-weight: 800; color: #fff; display: flex; align-items: center; gap: 10px; }
        .recom-details { font-size: 13px; color: #94a3b8; margin-top: 8px; display: flex; gap: 16px; }
        .qty-badge { background: rgba(56,189,248,0.15); color: #38bdf8; padding: 4px 10px; border-radius: 6px; font-size: 14px; font-weight: 800; border: 1px solid rgba(56,189,248,0.3); }
        .qty-badge.wealth { background: rgba(192,132,252,0.15); color: #c084fc; border: 1px solid rgba(192,132,252,0.3); }
        
        .recom-btn { background: #1e293b; color: #00e676; border: 1px solid #00e676; padding: 8px 16px; border-radius: 6px; font-weight: 700; cursor: pointer; }
        .recom-btn:hover { background: #00e676; color: #000; }
        .recom-btn.wealth { color: #c084fc; border-color: #c084fc; }
        .recom-btn.wealth:hover { background: #c084fc; color: #000; }
        
        .inline-details { display: none; background: #0b0e14; padding: 20px; border-top: 1px solid #1e293b; }
        .tc-grid { display: grid; grid-template-columns: 1fr 1fr; gap: 16px; margin-bottom: 12px; }
        .tc-box { background: #0f172a; padding: 12px; border-radius: 8px; border: 1px solid #1e293b; }
        .tc-label { font-size: 11px; color: #64748b; text-transform: uppercase; font-weight: 700; margin-bottom: 4px; }
        .tc-value { font-size: 18px; font-weight: 700; color: #fff; }
        .tc-value.green { color: #00e676; }
        .tc-value.purple { color: #c084fc; }
        .tc-value.red { color: #ef4444; }
        .tc-subtext { font-size: 12px; font-weight: 600; margin-top: 4px; }
        .trail-box { background: rgba(56, 189, 248, 0.1); border: 1px solid rgba(56, 189, 248, 0.3); padding: 12px; border-radius: 8px; color: #38bdf8; font-size: 13px; font-weight: 600; }
        
        .pagination { display: flex; justify-content: center; align-items: center; gap: 15px; margin-top: 20px; margin-bottom: 40px; }
        .page-btn { background: #1e293b; color: #fff; border: 1px solid #334155; padding: 10px 16px; border-radius: 6px; font-weight: 700; cursor: pointer; }
        .page-btn:hover { background: #38bdf8; color: #000; border-color: #38bdf8; }
        .page-btn:disabled { background: #0b0e14; color: #334155; cursor: not-allowed; border-color: #1e293b; }
        .page-info { font-weight: 700; color: #94a3b8; font-size: 16px; }

        /* Search Section UI */
        .search-container { margin-top: 40px; border-top: 1px solid #1e293b; padding-top: 20px; }
        .search-box { display: flex; gap: 10px; margin-bottom: 24px; }
        input.search-input { flex: 1; padding: 16px; border-radius: 8px; border: 1px solid #1e293b; background: #0f172a; color: #fff; font-size: 16px; outline: none; }
        input.search-input:focus { border-color: #00e676; }
        button.btn-search { background: #00e676; color: #000; font-weight: 700; border: none; padding: 0 24px; border-radius: 8px; cursor: pointer; font-size: 16px; }
        .tabs { display: flex; gap: 10px; margin-bottom: 20px; background: #0f172a; padding: 8px; border-radius: 10px; }
        .tab { flex: 1; text-align: center; padding: 12px; border-radius: 6px; cursor: pointer; font-weight: 600; color: #64748b; transition: 0.2s; }
        .tab.active { background: #1e293b; color: #00e676; }
        
        .trade-card { background: #0f172a; border: 1px solid #1e293b; border-radius: 12px; padding: 24px; display: none; margin-top: 20px;}
        .tc-header { display: flex; justify-content: space-between; border-bottom: 1px solid #1e293b; padding-bottom: 16px; margin-bottom: 16px; }
        .tc-symbol { font-size: 28px; font-weight: 800; }
        .tc-price { font-size: 18px; color: #94a3b8; }
        .badge { padding: 8px 16px; border-radius: 8px; font-weight: 700; font-size: 14px; }
        .badge.buy { background: rgba(0, 230, 118, 0.15); color: #00e676; border: 1px solid #00e676; }
        .badge.wait { background: rgba(239, 68, 68, 0.15); color: #ef4444; border: 1px solid #ef4444; }
        .loader { display: none; text-align: center; color: #00e676; font-weight: 600; margin: 40px 0; }

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
            <div style="color: #64748b; font-weight: 600; font-size: 14px;">Pro OS v4.3</div>
        </div>

        <div class="main-nav">
            <button class="nav-btn active" id="nav-live" onclick="switchView('live')">Swing Trades (Live)</button>
            <button class="nav-btn" id="nav-wealth" onclick="switchView('wealth')">Long-Term Wealth</button>
            <button class="nav-btn" id="nav-history" onclick="switchView('history'); loadHistory();">Past Performance</button>
        </div>

        <!-- Swing Scanner View -->
        <div id="view-live" class="view-section active">
            <div class="capital-box">
                <div class="cap-top">
                    <div class="capital-label">Investable Capital (₹) :</div>
                    <input type="number" id="capitalInput" class="capital-input" placeholder="e.g. 20000" oninput="renderFeed('live', false)">
                    <button class="clear-btn" onclick="clearSelections('live')">Clear Selections</button>
                </div>
                <div id="allocSummary" class="capital-summary">Select specific stocks below to divide your capital.</div>
            </div>
            
            <div class="controls-row">
                <div class="section-header">Top Recommendations (<span id="totalSetupsText">0</span> Found)</div>
                <select class="sort-select" id="sortOption" onchange="renderFeed('live', true)">
                    <option value="profit">Sort by: Profit % (Highest First)</option>
                    <option value="price_low">Sort by: Price (Low to High)</option>
                    <option value="price_high">Sort by: Price (High to Low)</option>
                    <option value="algo">Sort by: Alphabetical</option>
                </select>
            </div>

            <div id="recomFeed">Loading recommendations...</div>

            <div class="pagination" id="livePagination">
                <button class="page-btn" id="btnPrev" onclick="changePage(-1, 'live')">Previous</button>
                <span class="page-info" id="pageInfo">Page 1 of 1</span>
                <button class="page-btn" id="btnNext" onclick="changePage(1, 'live')">Next Page</button>
            </div>

            <!-- Restored Individual Search Tool -->
            <div class="search-container">
                <div class="section-header" style="margin-bottom: 14px;">Individual Stock Search</div>
                <div class="tabs">
                    <div class="tab active" id="tab-short" onclick="setTimeframe('short')">Short Term (Days)</div>
                    <div class="tab" id="tab-mid" onclick="setTimeframe('mid')">Mid Term (Weeks)</div>
                    <div class="tab" id="tab-long" onclick="setTimeframe('long')">Long Term (Months)</div>
                </div>

                <div class="search-box">
                    <input type="text" id="symbolInput" class="search-input" placeholder="Enter Stock Symbol (e.g. ZOMATO)" onkeypress="if(event.key==='Enter') analyze()">
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
                        </div>
                        <div class="tc-box">
                            <div class="tc-label">Stop Loss</div>
                            <div class="tc-value red" id="c-sl">--</div>
                        </div>
                        <div class="tc-box">
                            <div class="tc-label">Target 1 Profit</div>
                            <div class="tc-value green" id="c-t1">--</div>
                        </div>
                        <div class="tc-box">
                            <div class="tc-label">Target 2 Profit</div>
                            <div class="tc-value green" id="c-t2">--</div>
                        </div>
                    </div>
                    <div class="trail-box" id="c-trail">Trailing SL Strategy: --</div>
                </div>
            </div>
        </div>

        <!-- Long Term Wealth View -->
        <div id="view-wealth" class="view-section">
            <div class="capital-box" style="border-color: rgba(192,132,252,0.3);">
                <div class="cap-top">
                    <div class="capital-label" style="color: #c084fc;">Monthly SIP Capital (₹) :</div>
                    <input type="number" id="wealthCapitalInput" class="capital-input" style="border-color: #c084fc;" placeholder="e.g. 15000" oninput="renderFeed('wealth', false)">
                    <button class="clear-btn" style="border-color: #64748b; color: #64748b;" onclick="clearSelections('wealth')">Clear Selections</button>
                </div>
                <div id="wealthAllocSummary" class="capital-summary" style="background: rgba(192,132,252,0.1); color: #c084fc;">Select assets to calculate automated SIP distribution.</div>
            </div>

            <div class="controls-row">
                <div class="section-header">Long-Term Assets (<span id="wealthSetupsText">0</span> Found)</div>
                <select class="sort-select" id="wealthSortOption" onchange="renderFeed('wealth', true)">
                    <option value="algo">Sort by: Alphabetical</option>
                    <option value="price_low">Sort by: Price (Low to High)</option>
                    <option value="price_high">Sort by: Price (High to Low)</option>
                </select>
            </div>

            <div id="wealthFeed">Loading long-term assets...</div>
            
            <div class="pagination" id="wealthPagination">
                <button class="page-btn" id="wBtnPrev" onclick="changePage(-1, 'wealth')">Previous</button>
                <span class="page-info" id="wPageInfo">Page 1 of 1</span>
                <button class="page-btn" id="wBtnNext" onclick="changePage(1, 'wealth')">Next Page</button>
            </div>
        </div>

        <!-- History View -->
        <div id="view-history" class="view-section">
            <div class="controls-row">
                <span class="section-header">All Logged Trades</span>
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
        let liveSetups = [];
        let wealthSetups = [];
        let liveSelected = new Set();
        let wealthSelected = new Set();
        let livePage = 1;
        let wealthPage = 1;
        let liveSorted = false;
        let wealthSorted = false;
        const itemsPerPage = 12;

        function switchView(viewId) {
            document.querySelectorAll('.nav-btn').forEach(btn => {
                btn.classList.remove('active');
                btn.classList.remove('wealth-active');
            });
            document.querySelectorAll('.view-section').forEach(sec => sec.classList.remove('active'));
            
            if (viewId === 'wealth') {
                document.getElementById('nav-wealth').classList.add('wealth-active');
            } else {
                document.getElementById('nav-' + viewId).classList.add('active');
            }
            
            document.getElementById('view-' + viewId).classList.add('active');
            if(viewId === 'live') renderFeed('live', false);
            if(viewId === 'wealth') loadWealthRecommendations();
        }

        async function loadDailyRecommendations() {
            try {
                const res = await fetch('/get_daily_setups');
                const data = await res.json();
                if (data.setups && data.setups.length > 0) {
                    liveSetups = data.setups;
                    document.getElementById('totalSetupsText').innerText = liveSetups.length;
                    liveSetups.slice(0, 5).forEach(s => liveSelected.add(s.Stock));
                    renderFeed('live', true);
                } else {
                    document.getElementById('recomFeed').innerHTML = '<div style="color:#64748b; background:#0f172a; padding:20px; border-radius:8px;">No swing setups found. Run master scan first.</div>';
                    document.getElementById('livePagination').style.display = 'none';
                }
            } catch (e) {}
        }

        async function loadWealthRecommendations() {
            try {
                const res = await fetch('/get_wealth_setups');
                const data = await res.json();
                if (data.setups && data.setups.length > 0) {
                    wealthSetups = data.setups;
                    document.getElementById('wealthSetupsText').innerText = wealthSetups.length;
                    wealthSetups.slice(0, 3).forEach(s => wealthSelected.add(s.Stock));
                    renderFeed('wealth', true);
                } else {
                    document.getElementById('wealthFeed').innerHTML = '<div style="color:#64748b; background:#0f172a; padding:20px; border-radius:8px; border: 1px solid #1e293b;">Scanner is awaiting Long-Term Python upgrade. Run dual-scan engine to generate assets.</div>';
                    document.getElementById('wealthPagination').style.display = 'none';
                }
            } catch (e) {}
        }

        function toggleSelection(symbol, type) {
            let set = type === 'live' ? liveSelected : wealthSelected;
            if (set.has(symbol)) { set.delete(symbol); } else { set.add(symbol); }
            renderFeed(type, false); 
        }

        function clearSelections(type) {
            if (type === 'live') liveSelected.clear();
            if (type === 'wealth') wealthSelected.clear();
            renderFeed(type, false);
        }

        function toggleDetails(cleanSym) {
            const el = document.getElementById('details-' + cleanSym);
            if(el) {
                el.style.display = (el.style.display === 'none' || el.style.display === '') ? 'block' : 'none';
            }
        }

        function changePage(direction, type) {
            if (type === 'live') { livePage += direction; } else { wealthPage += direction; }
            renderFeed(type, false); 
            window.scrollTo({ top: 0, behavior: 'smooth' });
        }

        function renderFeed(type, forceSort = false) {
            const isWealth = type === 'wealth';
            const feed = document.getElementById(isWealth ? 'wealthFeed' : 'recomFeed');
            const capitalInput = parseFloat(document.getElementById(isWealth ? 'wealthCapitalInput' : 'capitalInput').value);
            let setups = isWealth ? wealthSetups : liveSetups;
            const selectedSet = isWealth ? wealthSelected : liveSelected;
            let currentPage = isWealth ? wealthPage : livePage;
            const sortMethod = document.getElementById(isWealth ? 'wealthSortOption' : 'sortOption').value;
            
            let isSorted = isWealth ? wealthSorted : liveSorted;
            if (forceSort || !isSorted) {
                setups.sort((a,b) => {
                    let priceA = isWealth ? parseFloat(a.InvestmentSetup.fair_value) : parseFloat(a.TradeSetup.entry);
                    let priceB = isWealth ? parseFloat(b.InvestmentSetup.fair_value) : parseFloat(b.TradeSetup.entry);
                    
                    if (sortMethod === 'price_low') return priceA - priceB;
                    if (sortMethod === 'price_high') return priceB - priceA;
                    if (sortMethod === 'profit' && !isWealth) {
                        let pA = (parseFloat(a.TradeSetup.target_1) - parseFloat(a.TradeSetup.entry)) / parseFloat(a.TradeSetup.entry);
                        let pB = (parseFloat(b.TradeSetup.target_1) - parseFloat(b.TradeSetup.entry)) / parseFloat(b.TradeSetup.entry);
                        return pB - pA;
                    }
                    if (sortMethod === 'algo') return a.Stock.localeCompare(b.Stock);
                    return 0;
                });
                
                if (isWealth) wealthSorted = true; else liveSorted = true;
                if (isWealth) wealthPage = 1; else livePage = 1;
                currentPage = 1;
            }

            let numSelected = selectedSet.size;
            let hasCapital = !isNaN(capitalInput) && capitalInput > 0 && numSelected > 0;
            let capitalPerStock = hasCapital ? (capitalInput / numSelected) : 0;
            
            const summaryEl = document.getElementById(isWealth ? 'wealthAllocSummary' : 'allocSummary');
            if (numSelected === 0) {
                summaryEl.innerText = `Select specific assets below to divide your capital.`;
            } else if (hasCapital) {
                summaryEl.innerText = `Allocating ₹${capitalPerStock.toFixed(0)} per selected asset (${numSelected} total)`;
            } else {
                summaryEl.innerText = `${numSelected} selected. Enter capital above to calculate shares.`;
            }

            const totalPages = Math.ceil(setups.length / itemsPerPage);
            if (currentPage < 1) currentPage = 1;
            if (currentPage > totalPages && totalPages > 0) currentPage = totalPages;
            if (isWealth) wealthPage = currentPage; else livePage = currentPage;
            
            document.getElementById(isWealth ? 'wPageInfo' : 'pageInfo').innerText = `Page ${currentPage} of ${totalPages || 1}`;
            document.getElementById(isWealth ? 'wBtnPrev' : 'btnPrev').disabled = currentPage === 1;
            document.getElementById(isWealth ? 'wBtnNext' : 'btnNext').disabled = currentPage === totalPages || totalPages === 0;

            const startIndex = (currentPage - 1) * itemsPerPage;
            const pageSetups = setups.slice(startIndex, startIndex + itemsPerPage);

            let html = '';
            pageSetups.forEach(s => {
                let sym = s.Stock;
                let cleanSym = sym.replace('.NS','').replace(/[^a-zA-Z0-9]/g, '');
                let isChecked = selectedSet.has(sym);
                let entryPrice = isWealth ? parseFloat(s.InvestmentSetup.fair_value) : parseFloat(s.TradeSetup.entry);
                
                let qtyHtml = '';
                let inlineMath = {qty: 0, profit: 0, risk: 0};

                if (isChecked && hasCapital) {
                    let qty = Math.floor(capitalPerStock / entryPrice);
                    if (qty > 0) {
                        qtyHtml = `<div class="qty-badge ${isWealth ? 'wealth' : ''}">${isWealth ? 'Accumulate' : 'Buy'} ${qty} Shares (Cost: ₹${(qty*entryPrice).toFixed(2)})</div>`;
                        inlineMath.qty = qty;
                        if (!isWealth) {
                            inlineMath.profit = (parseFloat(s.TradeSetup.target_1) - entryPrice) * qty;
                            inlineMath.risk = (entryPrice - parseFloat(s.TradeSetup.stop_loss)) * qty;
                        }
                    } else {
                        qtyHtml = `<div class="qty-badge" style="color:#ef4444; border-color:#ef4444; background:rgba(239,68,68,0.15);">Not enough capital</div>`;
                    }
                }

                if (isWealth) {
                    let zone = s.InvestmentSetup.accumulation_zone;
                    let invalid = s.InvestmentSetup.macro_invalid_level;
                    let target = s.InvestmentSetup.historical_resistance;
                    html += `
                        <div class="recom-card wealth">
                            <div class="rc-main">
                                <div class="rc-left">
                                    <input type="checkbox" class="rc-checkbox wealth" ${isChecked ? 'checked' : ''} onchange="toggleSelection('${sym}', 'wealth')">
                                    <div>
                                        <div class="recom-sym">🟣 ${cleanSym} ${qtyHtml}</div>
                                        <div class="recom-details">
                                            <span>SIP Zone: <b>${zone}</b></span>
                                            <span>Macro Invalid: <b style="color:#ef4444;">₹${invalid}</b></span>
                                        </div>
                                    </div>
                                </div>
                                <button class="recom-btn wealth" onclick="toggleDetails('${cleanSym}')">View Strategy ▾</button>
                            </div>
                            
                            <div class="inline-details" id="details-${cleanSym}">
                                <div class="tc-grid">
                                    <div class="tc-box">
                                        <div class="tc-label">Allocated Shares</div>
                                        <div class="tc-value purple">${inlineMath.qty > 0 ? inlineMath.qty : '--'}</div>
                                    </div>
                                    <div class="tc-box">
                                        <div class="tc-label">Macro Invalid Level</div>
                                        <div class="tc-value red">₹${invalid}</div>
                                        <div class="tc-subtext red">Do not panic sell above this line.</div>
                                    </div>
                                    <div class="tc-box">
                                        <div class="tc-label">Historical Resistance Target</div>
                                        <div class="tc-value green">₹${target}</div>
                                    </div>
                                </div>
                            </div>
                        </div>
                    `;
                } else {
                    let sl = parseFloat(s.TradeSetup.stop_loss);
                    let t1 = parseFloat(s.TradeSetup.target_1);
                    html += `
                        <div class="recom-card">
                            <div class="rc-main">
                                <div class="rc-left">
                                    <input type="checkbox" class="rc-checkbox" ${isChecked ? 'checked' : ''} onchange="toggleSelection('${sym}', 'live')">
                                    <div>
                                        <div class="recom-sym">🟢 ${cleanSym} ${qtyHtml}</div>
                                        <div class="recom-details">
                                            <span>Entry: <b>₹${entryPrice}</b></span>
                                            <span>SL: <b style="color:#ef4444;">₹${sl}</b></span>
                                            <span>T1: <b style="color:#00e676;">₹${t1}</b></span>
                                        </div>
                                    </div>
                                </div>
                                <button class="recom-btn" onclick="toggleDetails('${cleanSym}')">View Details ▾</button>
                            </div>
                            
                            <div class="inline-details" id="details-${cleanSym}">
                                <div class="tc-grid">
                                    <div class="tc-box">
                                        <div class="tc-label">Allocated Shares</div>
                                        <div class="tc-value">${inlineMath.qty > 0 ? inlineMath.qty : '--'}</div>
                                    </div>
                                    <div class="tc-box">
                                        <div class="tc-label">Stop Loss (Total Risk)</div>
                                        <div class="tc-value red">₹${sl}</div>
                                        <div class="tc-subtext red">Risk Amount: ${inlineMath.qty > 0 ? '-₹'+inlineMath.risk.toFixed(2) : '--'}</div>
                                    </div>
                                    <div class="tc-box">
                                        <div class="tc-label">Target 1 Profit</div>
                                        <div class="tc-value green">₹${t1}</div>
                                        <div class="tc-subtext green">Est. Profit: ${inlineMath.qty > 0 ? '+₹'+inlineMath.profit.toFixed(2) : '--'}</div>
                                    </div>
                                    <div class="tc-box">
                                        <div class="tc-label">Target 2 Profit</div>
                                        <div class="tc-value green">₹${s.TradeSetup.target_2 || '--'}</div>
                                    </div>
                                </div>
                                <div class="trail-box">Strategy: ${s.TradeSetup.trailing_sl || 'N/A'}</div>
                            </div>
                        </div>
                    `;
                }
            });
            feed.innerHTML = html;
        }

        // Search Section Logic
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
                document.getElementById('c-entry').innerText = setup.entry ? `₹${setup.entry}` : '--';
                document.getElementById('c-sl').innerText = setup.stop_loss ? `₹${setup.stop_loss}` : '--';
                document.getElementById('c-t1').innerText = setup.target_1 ? `₹${setup.target_1}` : '--';
                document.getElementById('c-t2').innerText = setup.target_2 ? `₹${setup.target_2}` : '--';
                document.getElementById('c-trail').innerText = setup.trailing_sl ? `Trailing SL Strategy: ${setup.trailing_sl}` : 'No active trade setup.';

                document.getElementById('tradeCard').style.display = 'block';
            } catch (err) {
                alert("Could not load data for this stock. Please check symbol.");
            } finally {
                document.getElementById('loader').style.display = 'none';
            }
        }

        // History Logic
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
            } catch (e) {}
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

@app.get("/get_wealth_setups")
def get_wealth_setups():
    file_path = r"C:\BrainTrader\wealth_setups.json"
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
    c.execute("SELECT * FROM trade_history ORDER BY id DESC")
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

import webbrowser
import threading
import time

def open_browser():
    """Waits 1.5 seconds for FastAPI to start listening, then opens the dashboard."""
    time.sleep(1.5)
    webbrowser.open("http://localhost:8000")

if __name__ == "__main__":
    print("\n[Step 1] Triggering SMC Confluence Scanner...")
    run_master_scan()
    
    print("\n[Step 2] Starting Dashboard Server on http://localhost:8000...")
    threading.Thread(target=open_browser, daemon=True).start()
    uvicorn.run(app, host="0.0.0.0", port=8000)