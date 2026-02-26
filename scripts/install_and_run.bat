@echo off
setlocal

echo ########################################################
echo #             DRAVIS ENTERPRISE INSTALLER                #
echo ########################################################
echo.

rem Check for Docker
where docker >nul 2>nul
if %ERRORLEVEL% neq 0 (
    echo [ERROR] Docker not found! Please install Docker Desktop first.
    echo Visit: https://www.docker.com/products/docker-desktop/
    pause
    exit /b
)

echo [1/3] Pulling latest containers and AI models...
echo (This may take a few minutes as it downloads the LLM model weights)

rem Optionally set the remote image if not building locally
rem set LLM_IMAGE=ghcr.io/khushi0231/major/dravis-llm:latest

docker-compose pull

echo [2/3] Starting DRAVIS Services...
docker-compose up -d

echo [3/3] Waiting for LLM to initialize...
echo (The model is being verified/pulled inside the container)
:WAIT_LOOP
docker exec dravis-llm ollama list | findstr "mistral" >nul
if %ERRORLEVEL% neq 0 (
    echo . . . still setting up model . . . 
    timeout /t 5 >nul
    goto WAIT_LOOP
)

echo.
echo [SUCCESS] DRAVIS is now running!
echo Access the application at: http://localhost:8080
echo ########################################################
pause
