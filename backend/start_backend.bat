@echo off
echo ========================================
echo 自动化工具后端服务
echo ========================================
echo.

REM 检查是否在 backend 目录
if not exist "main.py" (
    echo 错误：请在 backend 目录下运行此脚本
    pause
    exit /b 1
)

REM 检查 Python
python --version >nul 2>&1
if errorlevel 1 (
    echo 错误：未找到 Python
    pause
    exit /b 1
)

echo 检查依赖...
python -c "import fastapi" >nul 2>&1
if errorlevel 1 (
    echo 依赖未安装，正在安装...
    pip install -r requirements.txt
)

echo.
echo 启动后端服务...
echo API 服务: http://localhost:8000
echo API 文档: http://localhost:8000/docs
echo.
echo 按 Ctrl+C 停止服务
echo ========================================
echo.

python main.py
