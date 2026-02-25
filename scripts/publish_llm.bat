@echo off
setlocal

rem --- CONFIGURATION ---
rem Docker requires lowercase repository names
set IMAGE_NAME=dravis-llm
set GH_USERNAME=khushi0231
set REPO_NAME=major
set TAG=latest
rem ---------------------

set FULL_IMAGE_PATH=ghcr.io/%GH_USERNAME%/%REPO_NAME%/%IMAGE_NAME%:%TAG%

echo [1/3] Building LLM Engine ...
docker build -t %IMAGE_NAME% ./services/llm

echo [2/3] Tagging for GHCR: %FULL_IMAGE_PATH%
docker tag %IMAGE_NAME% %FULL_IMAGE_PATH%

echo [3/3] Pushing to GHCR...
echo (Ensure you have run "docker login ghcr.io" first with your PAT token)
docker push %FULL_IMAGE_PATH%

echo Done! New users can now pull this image to get the whole model setup.
pause
