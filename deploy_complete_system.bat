@echo off
REM 完整的一键部署脚本
REM 启动所有Docker服务 + MQTT桥接 + T-BOX模拟器 + 部署仪表板

echo ================================================================================
echo 拖拉机预测性维护系统 - 完整部署
echo ================================================================================
echo.

REM 切换到脚本所在目录
cd /d %~dp0

echo [步骤1/5] 启动Docker服务...
call start_all_services.bat
if %errorlevel% neq 0 (
    echo [错误] Docker服务启动失败
    pause
    exit /b 1
)
echo.

echo [步骤2/5] 等待服务完全启动（15秒）...
timeout /t 15 /nobreak >nul
echo.

echo [步骤3/5] 部署Grafana仪表板...
cd code
python deploy_fixed_dashboard.py
if %errorlevel% neq 0 (
    echo [警告] 仪表板部署失败，请手动运行: python deploy_fixed_dashboard.py
)
cd ..
echo.

echo [步骤4/5] 启动MQTT桥接服务（新窗口）...
start "MQTT桥接服务" cmd /k "cd /d %~dp0code && python mqtt_to_victoriametrics_bridge.py"
timeout /t 3 /nobreak >nul
echo.

echo [步骤5/5] 启动T-BOX模拟器（新窗口）...
start "T-BOX模拟器" cmd /k "cd /d %~dp0code && python tbox_simulator_realistic.py"
echo.

echo ================================================================================
echo 系统部署完成！
echo ================================================================================
echo.
echo 已启动的服务:
echo   [Docker容器]
echo   - VictoriaMetrics集群 (vminsert, vmselect, vmstorage x2)
echo   - Mosquitto MQTT Broker
echo   - Grafana
echo.
echo   [Python进程 - 在新窗口中运行]
echo   - MQTT桥接服务 (mqtt_to_victoriametrics_bridge.py)
echo   - T-BOX模拟器 (tbox_simulator_realistic.py)
echo.
echo 访问地址:
echo   - Grafana仪表板: http://localhost:3000
echo   - 用户名/密码: admin/admin
echo.
echo 下一步:
echo   1. 等待1-2分钟让数据积累
echo   2. 打开浏览器访问: http://localhost:3000
echo   3. 进入仪表板: 拖拉机数据监控 - CSS Electronics风格
echo   4. 按 Ctrl+F5 强制刷新
echo   5. 查看所有面板数据
echo.
echo 停止系统:
echo   - 关闭MQTT桥接服务和T-BOX模拟器窗口（按Ctrl+C）
echo   - 运行 stop_all_services.bat 停止Docker容器
echo.
echo ================================================================================
pause
