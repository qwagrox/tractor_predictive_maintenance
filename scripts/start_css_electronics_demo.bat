@echo off
chcp 65001 >nul
echo ============================================================
echo   CSS Electronics风格演示 - 快速启动
echo ============================================================
echo.

echo [步骤1] 检查Docker容器状态...
docker ps --filter name=grafana --format "{{.Names}}: {{.Status}}"
echo.

echo [步骤2] 部署CSS Electronics风格仪表板...
cd /d %~dp0..\code
python deploy_css_electronics_dashboard.py
echo.

echo [步骤3] 启动MQTT桥接服务...
echo [提示] 请在新窗口中运行: python mqtt_to_victoriametrics_bridge.py
echo.

echo [步骤4] 启动真实工况模拟器...
echo [提示] 请在新窗口中运行: python tbox_simulator_realistic.py
echo.

echo ============================================================
echo   部署完成！
echo ============================================================
echo.
echo 接下来请手动执行:
echo.
echo 1. 打开新的PowerShell窗口，运行:
echo    cd D:\tractor_pdm\code
echo    python mqtt_to_victoriametrics_bridge.py
echo.
echo 2. 再打开一个PowerShell窗口，运行:
echo    cd D:\tractor_pdm\code
echo    python tbox_simulator_realistic.py
echo.
echo 3. 在浏览器中访问: http://localhost:3000
echo.
pause
