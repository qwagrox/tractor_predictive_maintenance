@echo off
REM 一键启动拖拉机预测性维护系统的所有服务
REM 包括: VictoriaMetrics集群、Mosquitto MQTT、Grafana

echo ================================================================================
echo 启动拖拉机预测性维护系统
echo ================================================================================
echo.

REM 切换到配置文件目录
cd /d %~dp0config

echo [步骤1] 检查Docker是否运行...
docker info >nul 2>&1
if %errorlevel% neq 0 (
    echo [错误] Docker未运行，请先启动Docker Desktop
    pause
    exit /b 1
)
echo [成功] Docker正在运行
echo.

echo [步骤2] 停止并删除旧的容器（如果存在）...
docker-compose -f victoriametrics_deployment.yaml down
echo.

echo [步骤3] 启动所有服务...
docker-compose -f victoriametrics_deployment.yaml up -d
if %errorlevel% neq 0 (
    echo [错误] 服务启动失败
    pause
    exit /b 1
)
echo.

echo [步骤4] 等待服务初始化（10秒）...
timeout /t 10 /nobreak >nul
echo.

echo [步骤5] 检查服务状态...
docker-compose -f victoriametrics_deployment.yaml ps
echo.

echo ================================================================================
echo 所有服务启动完成！
echo ================================================================================
echo.
echo 运行中的服务:
echo   - VictoriaMetrics vminsert: http://localhost:8480
echo   - VictoriaMetrics vmselect: http://localhost:8481
echo   - VictoriaMetrics vmstorage-1: http://localhost:8482
echo   - VictoriaMetrics vmstorage-2: http://localhost:8483
echo   - Mosquitto MQTT: localhost:1883
echo   - Mosquitto WebSocket: localhost:9001
echo   - Grafana: http://localhost:3000 (admin/admin)
echo.
echo 下一步:
echo   1. 启动MQTT桥接服务: cd ..\code ^&^& python mqtt_to_victoriametrics_bridge.py
echo   2. 启动T-BOX模拟器: cd ..\code ^&^& python tbox_simulator_realistic.py
echo   3. 部署Grafana仪表板: cd ..\code ^&^& python deploy_fixed_dashboard.py
echo   4. 访问Grafana: http://localhost:3000
echo.
echo ================================================================================
pause
