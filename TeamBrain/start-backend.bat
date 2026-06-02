@echo off
echo ========================================
echo  MindVault - 后端启动脚本
echo ========================================
echo.

cd /d "%~dp0"

echo 检查 Python...
python --version >nul 2>&1
if errorlevel 1 (
    echo 错误: 未找到 Python，请先安装 Python
    pause
    exit /b 1
)

echo 安装依赖...
pip install -r api\requirements.txt

echo.
echo 初始化数据库...
python -m api.init_db

echo.
echo 启动 FastAPI 服务器...
echo 服务器地址: http://localhost:8080
echo API 文档: http://localhost:8080/docs
echo.
echo 按 Ctrl+C 停止服务器
echo ========================================
echo.

python -m uvicorn api.main:app --reload --host 0.0.0.0 --port 8080
