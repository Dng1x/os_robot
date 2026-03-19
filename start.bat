@echo off
echo ========================================
echo 自动化脚本设计工具 - 启动脚本
echo ========================================
echo.

echo [1/2] 启动前端开发服务器...
start "Frontend" cmd /k "cd /d %~dp0 && npm run dev"

echo.
echo [2/2] 等待后端准备...
echo 注意：后端服务需要单独启动
echo 请在另一个终端运行: cd backend && uvicorn main:app --reload --port 8000
echo.

echo ========================================
echo 启动完成！
echo 前端地址: http://localhost:5173
echo 后端地址: http://localhost:8000
echo ========================================
echo.
pause
