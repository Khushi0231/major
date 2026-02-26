@echo off
title DRAVIS — Stop

echo.
echo [DRAVIS] Stopping all containers...
docker compose down
echo [OK] All containers stopped.
echo.
echo To remove all data volumes (models, database, uploads):
echo     docker compose down -v
echo.
pause
