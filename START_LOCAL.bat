@echo off
setlocal enabledelayedexpansion
title DRAVIS — Native Developer Start

echo.
echo  ================================================================
echo    DRAVIS Native Local Stack (No Docker)
echo  ================================================================
echo.

REM ─── Check Python ──────────────────────────────────────────────
where python >nul 2>nul
if %ERRORLEVEL% neq 0 (
    echo [ERROR] Python not found. Please install Python 3.11.
    pause & exit /b 1
)

REM ─── Install/Update Dependencies ───────────────────────────────
echo [1/3] Verifying Python dependencies...
pip install -r services/desktop_requirements.txt --quiet
if %ERRORLEVEL% neq 0 (
    echo [ERROR] Dependency installation failed. Check your internet connection.
    pause & exit /b 1
)

REM ─── Start Backend (Desktop Bridge) ────────────────────────────
echo [2/3] Starting backend services (Auth, Chat, Document, Quiz)...
start "DRAVIS Backend" cmd /k "set PYTHONPATH=services&& python services/desktop_bridge.py"

REM ─── Start Frontend ───────────────────────────────────────────
echo [3/3] Starting frontend (Vite)...
if not exist "frontend\node_modules" (
    echo       (First run: installing node_modules...)
    cd frontend && npm install && cd ..
)

start "DRAVIS Frontend" cmd /k "cd frontend && npm run dev"

echo.
echo  ================================================================
echo   [SUCCESS] DRAVIS is starting!
echo.
echo   Frontend:  http://localhost:5173
echo   Backend:   http://localhost:8080 (Gateway)
echo.
echo   NOTE: Please ensure OLLAMA is running in your system.
echo  ================================================================
echo.

timeout /t 5 >nul
start "" "http://localhost:5173"
exit /b 0
