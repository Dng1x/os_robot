@echo off
echo ========================================
echo 自动化工具 - 修复脚本
echo ========================================
echo.
echo 正在清理不需要的配置文件...
echo.

if exist postcss.config.js (
    del postcss.config.js
    echo [OK] 已删除 postcss.config.js
) else (
    echo [--] postcss.config.js 不存在
)

if exist tailwind.config.js (
    del tailwind.config.js
    echo [OK] 已删除 tailwind.config.js
) else (
    echo [--] tailwind.config.js 不存在
)

echo.
echo ========================================
echo 清理完成！
echo ========================================
echo.
echo 现在启动项目...
echo.

npm run dev
