@echo off
title Aaveshkar 1.0 - AI Assistant & Custom Transformer
color 0B

cd /d "%~dp0"

if exist "bat\start_assistant.bat" (
    call bat\start_assistant.bat
) else (
    echo [ERROR] bat\start_assistant.bat not found!
    pause
)
