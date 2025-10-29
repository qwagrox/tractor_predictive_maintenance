#!/usr/bin/env python3
"""
强制重新部署CSS Electronics风格仪表板（删除旧版本并重新创建）
"""

import json
import requests
from pathlib import Path
import time

def force_redeploy():
    """强制重新部署仪表板"""
    
    print("="*60)
    print("强制重新部署CSS Electronics风格仪表板")
    print("="*60)
    print()
    
    # Grafana配置
    GRAFANA_URL = "http://localhost:3000"
    GRAFANA_API_KEY = "admin:admin"
    auth = tuple(GRAFANA_API_KEY.split(':'))
    
    # 步骤1: 查找现有仪表板
    print("[步骤1] 查找现有仪表板...")
    try:
        search_url = f"{GRAFANA_URL}/api/search?query=CSS%20Electronics"
        response = requests.get(search_url, auth=auth, timeout=10)
        
        if response.status_code == 200:
            dashboards = response.json()
            print(f"[信息] 找到 {len(dashboards)} 个匹配的仪表板")
            
            # 删除所有匹配的仪表板
            for dashboard in dashboards:
                uid = dashboard.get('uid')
                title = dashboard.get('title')
                if uid:
                    print(f"[执行] 删除仪表板: {title} (UID: {uid})")
                    delete_url = f"{GRAFANA_URL}/api/dashboards/uid/{uid}"
                    del_response = requests.delete(delete_url, auth=auth, timeout=10)
                    if del_response.status_code == 200:
                        print(f"[成功] 已删除")
                    else:
                        print(f"[警告] 删除失败: {del_response.status_code}")
        else:
            print(f"[信息] 未找到现有仪表板")
    except Exception as e:
        print(f"[警告] 查找仪表板时出错: {e}")
    
    print()
    time.sleep(2)
    
    # 步骤2: 读取新配置
    print("[步骤2] 读取新仪表板配置...")
    dashboard_path = Path(__file__).parent.parent / "config" / "grafana_css_electronics_dashboard.json"
    
    with open(dashboard_path, 'r', encoding='utf-8') as f:
        dashboard_config = json.load(f)
    
    print(f"[信息] 配置文件: {dashboard_path}")
    print(f"[信息] 仪表板标题: {dashboard_config['dashboard']['title']}")
    print(f"[信息] 面板数量: {len(dashboard_config['dashboard']['panels'])}")
    
    # 检查车辆信息面板
    vehicle_info_panel = None
    for panel in dashboard_config['dashboard']['panels']:
        if panel.get('title') == '车辆信息':
            vehicle_info_panel = panel
            break
    
    if vehicle_info_panel:
        print(f"[成功] 找到车辆信息面板")
        print(f"[信息] 面板位置: x={vehicle_info_panel['gridPos']['x']}, y={vehicle_info_panel['gridPos']['y']}")
        print(f"[信息] 面板大小: w={vehicle_info_panel['gridPos']['w']}, h={vehicle_info_panel['gridPos']['h']}")
    else:
        print(f"[警告] 未找到车辆信息面板")
    
    print()
    time.sleep(1)
    
    # 步骤3: 部署新仪表板
    print("[步骤3] 部署新仪表板...")
    api_url = f"{GRAFANA_URL}/api/dashboards/db"
    headers = {"Content-Type": "application/json"}
    
    try:
        response = requests.post(
            api_url,
            json=dashboard_config,
            headers=headers,
            auth=auth,
            timeout=10
        )
        
        if response.status_code == 200:
            result = response.json()
            print(f"[成功] 仪表板部署成功！")
            print(f"[信息] 仪表板ID: {result.get('id')}")
            print(f"[信息] 仪表板UID: {result.get('uid')}")
            print(f"[信息] 仪表板URL: {result.get('url')}")
            print()
            print("="*60)
            print("请在浏览器中访问（按Ctrl+F5强制刷新）:")
            print(f"{GRAFANA_URL}{result.get('url')}")
            print("="*60)
            print()
            print("[提示] 如果看不到车辆信息面板，请:")
            print("1. 按Ctrl+F5强制刷新浏览器")
            print("2. 滚动到页面最左侧")
            print("3. 检查图片URL是否正确: http://localhost:3000/public/img/tractors/tractor_001.png")
            return True
        else:
            print(f"[错误] 部署失败")
            print(f"[状态码] {response.status_code}")
            print(f"[响应] {response.text}")
            return False
            
    except requests.exceptions.ConnectionError:
        print("[错误] 无法连接到Grafana")
        print("[提示] 请确保Grafana容器正在运行")
        return False
    except Exception as e:
        print(f"[错误] {str(e)}")
        return False

if __name__ == "__main__":
    force_redeploy()
