@echo off
echo ========================================
echo   PriceTracker - Quick Start Script
echo ========================================
echo.

cd /d C:\projects\price-tracker

echo [1/3] Starting Backend...
start "PriceTracker Backend" cmd /k "cd backend && venv\Scripts\python.exe main.py"
timeout /t 3 /nobreak >nul

echo [2/3] Starting Frontend...
start "PriceTracker Frontend" cmd /k "cd frontend && npm run dev"
timeout /t 3 /nobreak >nul

echo [3/3] Starting Telegram Bot...
start "PriceTracker Bot" cmd /k "cd bot && venv\Scripts\python.exe main.py"
timeout /t 3 /nobreak >nul

echo.
echo ========================================
echo   All services started!
echo ========================================
echo.
echo   Frontend: http://localhost:3000
echo   API Docs: http://localhost:8000/docs
echo   Health:   http://localhost:8000/health
echo.
echo   Keep these windows open!
echo ========================================
pause
