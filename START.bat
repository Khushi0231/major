@echo off
REM ═══════════════════════════════════════════════
REM  DRAVIS Enterprise - Docker Compose Launcher
REM ═══════════════════════════════════════════════

cd /d "%~dp0"

echo.
echo ╔════════════════════════════════════════════╗
echo ║    DRAVIS Enterprise - Microservices       ║
echo ╚════════════════════════════════════════════╝
echo.

REM Check Docker
docker info >nul 2>&1
if errorlevel 1 (
    echo ❌ Docker is not running! Please start Docker Desktop.
    pause
    exit /b 1
)

echo ✓ Docker detected
echo.
echo Starting services...
echo   • MySQL          (port 3306)
echo   • ChromaDB       (port 8010)
echo   • Auth Service   (internal 8001)
echo   • Chat Service   (internal 8002)
echo   • Document Svc   (internal 8003)
echo   • Quiz Service   (internal 8004)
echo   • API Gateway    (port 8080)
echo.

docker-compose up --build -d

echo.
echo ╔════════════════════════════════════════════╗
echo ║    All services starting...                ║
echo ╚════════════════════════════════════════════╝
echo.
echo 🌐 Application:  http://localhost:8080
echo 📊 Gateway Health: http://localhost:8080/api/health
echo.
echo To view logs:     docker-compose logs -f
echo To stop:          docker-compose down
echo To include STT:   docker-compose --profile full up --build -d
echo.
pause
