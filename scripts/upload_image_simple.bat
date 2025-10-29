@echo off
cd /d %~dp0..

echo.
echo ========================================
echo   Grafana Image Upload
echo ========================================
echo.

echo Step 1: Upload image...
python code\upload_tractor_image_to_grafana.py
if errorlevel 1 goto error

echo.
echo Step 2: Update dashboard...
python code\update_dashboard_with_image.py
if errorlevel 1 goto error

echo.
echo Step 3: Deploy dashboard...
python code\deploy_grafana_dashboard.py
if errorlevel 1 goto error

echo.
echo ========================================
echo   Success!
echo ========================================
echo.
echo Open: http://localhost:3000
echo.
pause
exit /b 0

:error
echo.
echo ERROR: Failed!
echo.
pause
exit /b 1
