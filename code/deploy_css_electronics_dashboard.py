#!/usr/bin/env python3
"""
部署CSS Electronics风格的Grafana仪表板
"""

import json
import requests
from pathlib import Path

def deploy_dashboard():
    """部署仪表板到Grafana"""
    
    print("="*60)
    print("部署CSS Electronics风格仪表板到Grafana")
    print("="*60)
    print()
    
    # Grafana配置
    GRAFANA_URL = "http://localhost:3000"
    GRAFANA_API_KEY = "admin:admin"  # 默认用户名:密码
    
    # 读取仪表板配置
    dashboard_path = Path(__file__).parent.parent / "config" / "grafana_css_electronics_dashboard.json"
    
    print(f"[信息] 读取仪表板配置: {dashboard_path}")
    
    with open(dashboard_path, 'r', encoding='utf-8') as f:
        dashboard_config = json.load(f)
    
    # 准备API请求
    api_url = f"{GRAFANA_URL}/api/dashboards/db"
    headers = {
        "Content-Type": "application/json",
    }
    
    print(f"[信息] Grafana URL: {GRAFANA_URL}")
    print(f"[信息] 仪表板标题: {dashboard_config['dashboard']['title']}")
    print()
    
    # 发送请求
    print("[执行] 部署仪表板...")
    
    try:
        response = requests.post(
            api_url,
            json=dashboard_config,
            headers=headers,
            auth=tuple(GRAFANA_API_KEY.split(':')),
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
            print("请在浏览器中访问:")
            print(f"{GRAFANA_URL}{result.get('url')}")
            print("="*60)
            return True
        else:
            print(f"[错误] 部署失败")
            print(f"[状态码] {response.status_code}")
            print(f"[响应] {response.text}")
            return False
            
    except requests.exceptions.ConnectionError:
        print("[错误] 无法连接到Grafana")
        print("[提示] 请确保Grafana容器正在运行")
        print("[命令] docker ps | findstr grafana")
        return False
    except Exception as e:
        print(f"[错误] {str(e)}")
        return False

if __name__ == "__main__":
    deploy_dashboard()
