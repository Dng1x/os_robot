#!/bin/bash

echo "========================================"
echo "自动化工具 - 修复脚本"
echo "========================================"
echo ""
echo "正在清理不需要的配置文件..."
echo ""

if [ -f postcss.config.js ]; then
    rm postcss.config.js
    echo "[OK] 已删除 postcss.config.js"
else
    echo "[--] postcss.config.js 不存在"
fi

if [ -f tailwind.config.js ]; then
    rm tailwind.config.js
    echo "[OK] 已删除 tailwind.config.js"
else
    echo "[--] tailwind.config.js 不存在"
fi

echo ""
echo "========================================"
echo "清理完成！"
echo "========================================"
echo ""
echo "现在启动项目..."
echo ""

npm run dev
