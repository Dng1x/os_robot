@echo off
chcp 65001 > nul
title Prepare Portable Python

echo.
echo Running Python preparation script...
echo.

python prepare_portable.py

if errorlevel 1 (
    echo.
    echo [ERROR] Preparation failed
    pause
    exit /b 1
)

pause
