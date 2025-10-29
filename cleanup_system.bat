@echo off
REM ========================================
REM 拖拉机预测性维护系统 - 清理脚本
REM 适用于 Windows 11 / Windows 10
REM ========================================

echo.
echo ========================================
echo 拖拉机预测性维护系统 - 清理数据
echo ========================================
echo.
echo [警告] 此操作将删除所有容器和数据卷
echo [警告] 所有历史数据将被永久删除
echo.
set /p confirm="确认清理? (Y/N): "
if /i not "%confirm%"=="Y" (
    echo 已取消清理操作
    pause
    exit /b 0
)
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

REM 停止并删除容器和卷
echo [2/2] 停止并删除容器和数据卷...
cd config
docker-compose -f victoriametrics_deployment.yaml down -v
if %errorlevel% neq 0 (
    echo [错误] 清理失败
    echo.
    pause
    exit /b 1
)
echo [成功] 容器和数据卷已删除
cd ..
echo.

echo ========================================
echo 清理完成
echo ========================================
echo.
echo 提示: 运行 start_system.bat 可重新启动系统
echo.
pause
