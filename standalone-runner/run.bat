@echo off
chcp 65001 > nul
title Automation Flow Runner

echo.
echo ========================================
echo   Automation Flow Runner
echo ========================================
echo.

REM Check if portable Python exists
if not exist python\python.exe (
    echo [ERROR] Portable Python not found!
    echo.
    echo This package seems incomplete.
    echo Please re-download the complete package or contact support.
    echo.
    pause
    exit /b 1
)

echo [*] Using portable Python environment
echo [*] Starting flow execution...
echo.

python\python.exe runner.py

pause
