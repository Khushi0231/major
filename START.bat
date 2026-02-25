@echo off
setlocal enabledelayedexpansion
title DRAVIS — Container Startup

echo.
echo  ================================================================
echo    DRAVIS Local Container Stack
echo    docker compose up --build
echo  ================================================================
echo.

REM ─── Check Docker is running ────────────────────────────────────
where docker >nul 2>nul
if %ERRORLEVEL% neq 0 (
    echo [ERROR] Docker not found. Install Docker Desktop first.
    echo         https://www.docker.com/products/docker-desktop/
    pause & exit /b 1
)

docker info >nul 2>nul
if %ERRORLEVEL% neq 0 (
    echo [ERROR] Docker Desktop is not running. Please start it and try again.
    pause & exit /b 1
)

echo [OK] Docker is running.

REM ─── Warn about first-run model download ────────────────────────
echo.
echo [NOTICE] On first run, the Mistral 7B model (~4.5GB^) will be downloaded.
echo          This is a one-time operation. Subsequent starts are fast.
echo          The model is stored in the Docker volume 'ollama_data'.
echo.

REM ─── Build + Start all services ─────────────────────────────────
echo [1/3] Building and starting containers...
docker compose up --build -d
if %ERRORLEVEL% neq 0 (
    echo.
    echo [ERROR] docker compose up failed. Check the output above.
    pause & exit /b 1
)

REM ─── Wait for gateway to be ready ───────────────────────────────
echo.
echo [2/3] Waiting for services to come online...
echo       (LLM model download may take several minutes on first run)
echo.

set /a ATTEMPTS=0
:HEALTH_LOOP
set /a ATTEMPTS+=1
if %ATTEMPTS% gtr 60 (
    echo [WARN] Gateway did not respond after 5 minutes.
    echo        Services may still be starting. Try opening http://localhost:8080
    goto DONE
)

REM Poll gateway health endpoint
docker compose exec -T gateway wget -qO- http://localhost/api/health >nul 2>nul
if %ERRORLEVEL% equ 0 (
    goto DONE
)

echo  . . . still starting (attempt %ATTEMPTS%/60^) . . .
timeout /t 5 /nobreak >nul
goto HEALTH_LOOP

:DONE
echo.
echo [3/3] Checking LLM model status...
docker compose exec -T llm ollama list 2>nul || echo       (LLM is still downloading model — this is normal on first run)

echo.
echo  ================================================================
echo   [SUCCESS] DRAVIS is running!
echo.
echo   App:     http://localhost:8080
echo   Logs:    docker compose logs -f
echo   Stop:    docker compose down
echo  ================================================================
echo.

REM Open browser
start "" "http://localhost:8080"
pause
