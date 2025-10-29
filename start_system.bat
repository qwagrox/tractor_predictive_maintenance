@echo off
REM ========================================
REM 拖拉机预测性维护系统 - 一键启动脚本
REM 适用于 Windows 11 / Windows 10
REM ========================================

echo.
echo ========================================
echo 拖拉机预测性维护系统 - 一键启动
echo ========================================
echo.

REM 检查Docker是否运行
echo [1/5] 检查Docker状态...
docker info >nul 2>&1
if %errorlevel% neq 0 (
    echo [错误] Docker未运行，请先启动Docker Desktop
    echo.
    pause
    exit /b 1
)
echo [成功] Docker正在运行
echo.

REM 启动VictoriaMetrics和Grafana
echo [2/5] 启动VictoriaMetrics和Grafana...
cd config
docker-compose -f victoriametrics_deployment.yaml up -d
if %errorlevel% neq 0 (
    echo [错误] 启动Docker容器失败
    echo.
    pause
    exit /b 1
)
echo [成功] Docker容器已启动
cd ..
echo.

REM 等待Grafana启动
echo [3/5] 等待Grafana启动 (30秒)...
timeout /t 30 /nobreak >nul
echo [成功] Grafana已启动
echo.

REM 部署Grafana仪表板
echo [4/5] 部署Grafana仪表板...
cd code
python deploy_grafana_dashboard.py
if %errorlevel% neq 0 (
    echo [警告] 仪表板部署失败，但系统已启动
    echo 您可以手动导入仪表板: config\grafana_tractor_fleet_dashboard.json
)
cd ..
echo.

REM 启动T-BOX模拟器
echo [5/5] 启动T-BOX数据模拟器...
echo.
echo ========================================
echo 系统启动完成!
echo ========================================
echo.
echo 访问Grafana: http://localhost:3000
echo 用户名: admin
echo 密码: admin
echo.
echo T-BOX数据模拟器将在新窗口中启动...
echo 按任意键继续...
pause >nul

REM 在新窗口中启动T-BOX模拟器
start "T-BOX数据模拟器" cmd /k "cd code && python tbox_simulator.py"

echo.
echo 提示: 关闭T-BOX模拟器窗口可停止数据生成
echo.
pause
