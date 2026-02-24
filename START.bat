@echo off
title DRAVIS - AI Study Assistant
color 0B

echo.
echo  ██████╗ ██████╗  █████╗ ██╗   ██╗██╗███████╗
echo  ██╔══██╗██╔══██╗██╔══██╗██║   ██║██║██╔════╝
echo  ██║  ██║██████╔╝███████║██║   ██║██║███████╗
echo  ██║  ██║██╔══██╗██╔══██║╚██╗ ██╔╝██║╚════██║
echo  ██████╔╝██║  ██║██║  ██║ ╚████╔╝ ██║███████║
echo  ╚═════╝ ╚═╝  ╚═╝╚═╝  ╚═╝  ╚═══╝  ╚═╝╚══════╝
echo.
echo  Offline AI Study Assistant — Powered by Mistral 7B
echo  =====================================================
echo.

:: Check Docker
docker --version >nul 2>&1
if errorlevel 1 (
    echo  [ERROR] Docker is not installed or not running!
    echo  Please install Docker Desktop: https://www.docker.com/products/docker-desktop
    echo.
    pause
    exit /b 1
)

echo  [OK] Docker found
echo.

:: Check if first run
docker volume inspect dravis_ollama_data >nul 2>&1
if errorlevel 1 (
    echo  [INFO] First time setup - this will download Mistral 7B ^(~4.5 GB^)
    echo  [INFO] Subsequent starts will be instant.
    echo.
)

echo  Starting DRAVIS...
echo  Open http://localhost when green indicator appears.
echo.

docker-compose up --build -d

if errorlevel 1 (
    echo.
    echo  [ERROR] Failed to start. Check Docker is running and has enough disk space.
    pause
    exit /b 1
)

echo.
echo  =====================================================
echo   DRAVIS is starting up!
echo   Open your browser: http://localhost
echo   Green dot = AI ready. Takes ~60s on first run.
echo  =====================================================
echo.

:: Open browser after 5s
timeout /t 5 /nobreak >nul
start http://localhost

pause
