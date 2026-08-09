@echo off
title BrainTrader SMC Engine
cd /d C:\BrainTrader

echo ==================================================
echo   1. CLEANING OLD PROCESSES
echo ==================================================
taskkill /F /IM python.exe /T 2>nul
timeout /t 1 /nobreak >nul

echo ==================================================
echo   2. LAUNCHING BRAINTRADER
echo ==================================================
python Code\api.py

pause