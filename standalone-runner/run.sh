#!/bin/bash

echo ""
echo "========================================"
echo "  Automation Flow Runner"
echo "========================================"
echo ""

if ! command -v python3 &> /dev/null; then
    echo "[ERROR] Python3 not detected"
    echo "Please install Python 3.8 or higher"
    read -p "Press Enter to exit..."
    exit 1
fi

echo "[1/3] Checking dependencies..."
if ! python3 -c "import pyautogui" &> /dev/null; then
    echo "Dependencies not installed, installing..."
    pip3 install -r requirements.txt
    if [ $? -ne 0 ]; then
        echo "[ERROR] Dependency installation failed"
        read -p "Press Enter to exit..."
        exit 1
    fi
fi

echo "[2/3] Loading flow file..."
echo "[3/3] Starting execution..."
echo ""

python3 runner.py

read -p "Press Enter to exit..."
