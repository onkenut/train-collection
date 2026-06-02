@echo off
echo ========================================
echo  MindVault - 前端启动脚本
echo ========================================
echo.

cd /d "%~dp0"

echo 检查 Node.js...
node --version >nul 2>&1
if errorlevel 1 (
    echo 错误: 未找到 Node.js，请先安装 Node.js
    pause
    exit /b 1
)

echo 安装依赖（含开发依赖）...
call npm install --include=dev

echo.
echo 启动 Vite 开发服务器...
echo 前端地址: http://localhost:5173
echo.
echo 请确保后端服务器已启动 (端口 8080)
echo ========================================
echo.

call npm run dev
