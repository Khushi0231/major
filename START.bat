@echo off
REM DRAVIS Project - Start Script
REM This script starts both Frontend and Backend servers

cd /d "%~dp0"

echo.
echo ╔════════════════════════════════════════════╗
echo ║      DRAVIS - Starting Services            ║
echo ╚════════════════════════════════════════════╝
echo.

REM Start Backend in a new window
echo ✓ Starting Backend on port 8000...
start "DRAVIS Backend" cmd /k "call venv\Scripts\activate.bat && python -m uvicorn backend.main:app --host 0.0.0.0 --port 8000"

REM Wait a bit for backend to start
timeout /t 3 /nobreak

REM Start Frontend in a new window
echo ✓ Starting Frontend on port 5173...
start "DRAVIS Frontend" cmd /k "cd frontend && npm run dev"

echo.
echo ╔════════════════════════════════════════════╗
echo ║      Services Starting...                   ║
echo ╚════════════════════════════════════════════╝
echo.
echo Frontend: http://localhost:5173
echo Backend:  http://localhost:8000
echo API Docs: http://localhost:8000/docs
echo.
echo Note: Windows will open two new command windows
echo Close them to stop the services
echo.
timeout /t 3 /nobreak
