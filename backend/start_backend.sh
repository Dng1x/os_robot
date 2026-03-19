#!/bin/bash

echo "========================================"
echo "自动化工具后端服务"
echo "========================================"
echo ""

# 检查是否在 backend 目录
if [ ! -f "main.py" ]; then
    echo "错误：请在 backend 目录下运行此脚本"
    exit 1
fi

# 检查 Python
if ! command -v python3 &> /dev/null; then
    echo "错误：未找到 Python 3"
    exit 1
fi

echo "检查依赖..."
python3 -c "import fastapi" 2>/dev/null
if [ $? -ne 0 ]; then
    echo "依赖未安装，正在安装..."
    pip3 install -r requirements.txt --break-system-packages
fi

echo ""
echo "启动后端服务..."
echo "API 服务: http://localhost:8000"
echo "API 文档: http://localhost:8000/docs"
echo ""
echo "按 Ctrl+C 停止服务"
echo "========================================"
echo ""

python3 main.py
