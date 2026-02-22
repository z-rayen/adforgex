@echo off
cd /d "%~dp0"

echo Starting Backend (port 8000)...
start "AdForge Backend" cmd /k "cd /d %~dp0 && python -m uvicorn backend.main:app --reload --port 8000"

echo Starting Frontend (port 3000)...
start "AdForge Frontend" cmd /k "cd /d %~dp0frontend-react && npm run dev"

echo.
echo Both servers are starting.
echo Open http://localhost:3000 in your browser.
timeout /t 3 >nul
start http://localhost:3000
