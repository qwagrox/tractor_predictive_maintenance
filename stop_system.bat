@echo off
REM ========================================
REM 拖拉机预测性维护系统 - 停止脚本
REM 适用于 Windows 11 / Windows 10
REM ========================================

echo.
echo ========================================
echo 拖拉机预测性维护系统 - 停止服务
echo ========================================
echo.

REM 检查Docker是否运行
echo [1/2] 检查Docker状态...
docker info >nul 2>&1
if %errorlevel% neq 0 (
    echo [警告] Docker未运行
    echo.
    pause
    exit /b 0
)
echo [成功] Docker正在运行
echo.

REM 停止Docker容器
echo [2/2] 停止Docker容器...
cd config
docker-compose -f victoriametrics_deployment.yaml down
if %errorlevel% neq 0 (
    echo [错误] 停止Docker容器失败
    echo.
    pause
    exit /b 1
)
echo [成功] Docker容器已停止
cd ..
echo.

echo ========================================
echo 系统已停止
echo ========================================
echo.
echo 提示: 如需清理所有数据，请运行 cleanup_system.bat
echo.
pause
