@echo off
title NexusAI PC Assistant
cd /d "D:\Ai assistent"

if not exist "venv\Scripts\python.exe" (
    echo [ERROR] Virtual environment not found. Please install prerequisites.
    pause
    exit /b 1
)

echo Starting NexusAI PC Assistant Server on http://127.0.0.1:8765 ...
.\venv\Scripts\python.exe -c "import urllib.request; urllib.request.urlopen('http://127.0.0.1:8765/api/stats', timeout=1)" 2>nul
if %ERRORLEVEL% NEQ 0 (
    start "" http://127.0.0.1:8765
)
.\venv\Scripts\python.exe main.py
pause
