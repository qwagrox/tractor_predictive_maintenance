#!/usr/bin/env python3
"""
部署修复后的Grafana仪表板
修复了指标名称不匹配的问题
"""

import requests
import json
import sys

# Grafana配置
GRAFANA_URL = "http://localhost:3000"
GRAFANA_USER = "admin"
GRAFANA_PASSWORD = "admin"

# 仪表板配置文件路径
DASHBOARD_FILE = "../config/grafana_css_electronics_dashboard.json"

def deploy_dashboard():
    """部署仪表板到Grafana"""
    print("=" * 80)
    print("部署修复后的Grafana仪表板")
    print("=" * 80)
    print()
    
    # 1. 读取仪表板配置
    print("1️⃣ 读取仪表板配置文件...")
    try:
        with open(DASHBOARD_FILE, 'r', encoding='utf-8') as f:
            dashboard_config = json.load(f)
        print(f"   ✅ 成功读取配置文件")
        print()
    except Exception as e:
        print(f"   ❌ 读取配置文件失败: {e}")
        return False
    
    # 2. 部署到Grafana
    print("2️⃣ 部署到Grafana...")
    try:
        response = requests.post(
            f"{GRAFANA_URL}/api/dashboards/db",
            auth=(GRAFANA_USER, GRAFANA_PASSWORD),
            headers={'Content-Type': 'application/json'},
            json=dashboard_config,
            timeout=30
        )
        
        if response.status_code == 200:
            result = response.json()
            dashboard_uid = result.get('uid', 'unknown')
            dashboard_url = f"{GRAFANA_URL}/d/{dashboard_uid}"
            
            print(f"   ✅ 仪表板部署成功！")
            print(f"   📊 仪表板URL: {dashboard_url}")
            print()
        else:
            print(f"   ❌ 部署失败: HTTP {response.status_code}")
            print(f"   错误信息: {response.text}")
            return False
    except Exception as e:
        print(f"   ❌ 部署失败: {e}")
        return False
    
    # 3. 显示修复的指标
    print("3️⃣ 修复的指标名称:")
    print()
    fixes = [
        ("tractor_vehicle_speed", "tractor_vehicle_vehicle_speed", "车速"),
        ("tractor_odometer", "tractor_vehicle_odometer", "里程"),
        ("tractor_gps_altitude", "tractor_gnss_altitude", "海拔"),
        ("tractor_gps_satellites", "tractor_gnss_satellite_count", "卫星数"),
        ("tractor_gps_fix", "tractor_gnss_positioning_accuracy", "定位精度"),
    ]
    
    for old, new, desc in fixes:
        print(f"   {desc:10s} {old:30s} → {new}")
    
    print()
    print("=" * 80)
    print("✅ 部署完成！")
    print()
    print("📌 下一步:")
    print("   1. 打开浏览器访问: http://localhost:3000")
    print("   2. 进入仪表板: 拖拉机数据监控 - CSS Electronics风格")
    print("   3. 按 Ctrl+F5 强制刷新")
    print("   4. 所有面板应该都有数据了！")
    print("=" * 80)
    
    return True

if __name__ == "__main__":
    success = deploy_dashboard()
    sys.exit(0 if success else 1)
