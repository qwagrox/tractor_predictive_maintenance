# 拖拉机图片上传到Grafana - PowerShell脚本

Write-Host ""
Write-Host "========================================"
Write-Host "  拖拉机图片上传到Grafana"
Write-Host "========================================"
Write-Host ""

# 切换到项目根目录
Set-Location $PSScriptRoot\..

# 步骤1: 上传图片
Write-Host "[步骤1] 上传图片到Grafana容器..."
Write-Host ""
python code\upload_tractor_image_to_grafana.py
if ($LASTEXITCODE -ne 0) {
    Write-Host ""
    Write-Host "[错误] 图片上传失败！" -ForegroundColor Red
    Read-Host "按Enter键退出"
    exit 1
}

# 步骤2: 更新配置
Write-Host ""
Write-Host "[步骤2] 更新仪表板配置..."
Write-Host ""
python code\update_dashboard_with_image.py
if ($LASTEXITCODE -ne 0) {
    Write-Host ""
    Write-Host "[错误] 配置更新失败！" -ForegroundColor Red
    Read-Host "按Enter键退出"
    exit 1
}

# 步骤3: 部署仪表板
Write-Host ""
Write-Host "[步骤3] 重新部署Grafana仪表板..."
Write-Host ""
python code\deploy_grafana_dashboard.py
if ($LASTEXITCODE -ne 0) {
    Write-Host ""
    Write-Host "[错误] 仪表板部署失败！" -ForegroundColor Red
    Read-Host "按Enter键退出"
    exit 1
}

# 完成
Write-Host ""
Write-Host "========================================"
Write-Host "  拖拉机图片配置完成！"
Write-Host "========================================"
Write-Host ""
Write-Host "请在浏览器中访问: http://localhost:3000"
Write-Host "查看更新后的仪表板，应该可以看到拖拉机图片！"
Write-Host ""
Read-Host "按Enter键退出"
