@echo off
title BrainTrader Master Runner
cd /d C:\BrainTrader

echo [1/2] Running EOD Master Scan across market universe...
python Code/auto_trader.py

echo.
echo [2/2] Starting Web App Dashboard...
start /min python Code/api.py

echo.
echo Launching Dashboard in Google Chrome...
timeout /t 2 >nul
start http://localhost:8000

echo BrainTrader is fully running! You can close this window or leave it in the background.
pause