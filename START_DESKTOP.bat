@echo off
title DRAVIS Desktop Development
echo [1/2] Starting Backend Bridge (Python)...
start /B python services/desktop_bridge.py
echo [2/2] Starting Frontend (Tauri)...
cd frontend
npm run tauri dev
