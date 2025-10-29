@echo off
chcp 65001 > nul
echo.
echo ========================================
echo   拖拉机图片上传到Grafana
echo ========================================
echo.

cd /d %~dp0..

echo [步骤1] 上传图片到Grafana容器...
echo.
python code\upload_tractor_image_to_grafana.py
if errorlevel 1 (
    echo.
    echo [错误] 图片上传失败！
    pause
    exit /b 1
)

echo.
echo [步骤2] 更新仪表板配置...
echo.
python code\update_dashboard_with_image.py
if errorlevel 1 (
    echo.
    echo [错误] 配置更新失败！
    pause
    exit /b 1
)

echo.
echo [步骤3] 重新部署Grafana仪表板...
echo.
python code\deploy_grafana_dashboard.py
if errorlevel 1 (
    echo.
    echo [错误] 仪表板部署失败！
    pause
    exit /b 1
)

echo.
echo ========================================
echo   拖拉机图片配置完成！
echo ========================================
echo.
echo 请在浏览器中访问: http://localhost:3000
echo 查看更新后的仪表板，应该可以看到拖拉机图片！
echo.
pause
