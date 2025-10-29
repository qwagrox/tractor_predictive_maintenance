#!/usr/bin/env python3
"""
Grafana仪表板自动部署脚本
将拖拉机车队管理仪表板自动导入到Grafana
"""

import json
import requests
import os
from typing import Dict, Any

class GrafanaDashboardDeployer:
    def __init__(self, grafana_url: str = "http://localhost:3000", 
                 api_key: str = None, 
                 username: str = "admin", 
                 password: str = "admin"):
        """
        初始化Grafana仪表板部署器
        
        Args:
            grafana_url: Grafana服务器URL
            api_key: Grafana API密钥（可选，如果提供则优先使用）
            username: Grafana用户名（当没有API密钥时使用）
            password: Grafana密码（当没有API密钥时使用）
        """
        self.grafana_url = grafana_url.rstrip('/')
        self.api_key = api_key
        self.username = username
        self.password = password
        
        # 设置认证头
        if self.api_key:
            self.headers = {
                "Authorization": f"Bearer {self.api_key}",
                "Content-Type": "application/json"
            }
            self.auth = None
        else:
            self.headers = {"Content-Type": "application/json"}
            self.auth = (self.username, self.password)
    
    def test_connection(self) -> bool:
        """测试Grafana连接"""
        try:
            response = requests.get(
                f"{self.grafana_url}/api/health",
                headers=self.headers,
                auth=self.auth,
                timeout=5
            )
            if response.status_code == 200:
                print(f"✓ 成功连接到Grafana: {self.grafana_url}")
                return True
            else:
                print(f"✗ Grafana连接失败: HTTP {response.status_code}")
                return False
        except Exception as e:
            print(f"✗ 无法连接到Grafana: {e}")
            return False
    
    def create_datasource(self, datasource_config: Dict[str, Any]) -> bool:
        """创建VictoriaMetrics数据源"""
        try:
            # 检查数据源是否已存在
            response = requests.get(
                f"{self.grafana_url}/api/datasources/name/{datasource_config['name']}",
                headers=self.headers,
                auth=self.auth
            )
            
            if response.status_code == 200:
                print(f"✓ 数据源 '{datasource_config['name']}' 已存在")
                return True
            
            # 创建新数据源
            response = requests.post(
                f"{self.grafana_url}/api/datasources",
                headers=self.headers,
                auth=self.auth,
                json=datasource_config
            )
            
            if response.status_code == 200:
                print(f"✓ 成功创建数据源: {datasource_config['name']}")
                return True
            else:
                print(f"✗ 创建数据源失败: HTTP {response.status_code}")
                print(f"  响应: {response.text}")
                return False
        except Exception as e:
            print(f"✗ 创建数据源时出错: {e}")
            return False
    
    def import_dashboard(self, dashboard_json_path: str, folder_name: str = "Tractor Fleet") -> bool:
        """导入仪表板"""
        try:
            # 读取仪表板JSON
            with open(dashboard_json_path, 'r', encoding='utf-8') as f:
                dashboard_data = json.load(f)
            
            # 准备导入请求
            import_request = {
                "dashboard": dashboard_data.get("dashboard", dashboard_data),
                "overwrite": True,
                "folderUid": "",
                "message": "Imported by automated deployment script"
            }
            
            # 导入仪表板
            response = requests.post(
                f"{self.grafana_url}/api/dashboards/db",
                headers=self.headers,
                auth=self.auth,
                json=import_request
            )
            
            if response.status_code == 200:
                result = response.json()
                dashboard_url = f"{self.grafana_url}{result.get('url', '')}"
                print(f"✓ 成功导入仪表板: {dashboard_data['dashboard']['title']}")
                print(f"  访问URL: {dashboard_url}")
                return True
            else:
                print(f"✗ 导入仪表板失败: HTTP {response.status_code}")
                print(f"  响应: {response.text}")
                return False
        except Exception as e:
            print(f"✗ 导入仪表板时出错: {e}")
            return False
    
    def create_victoriametrics_datasource(self, vm_url: str = "http://vmselect:8481/select/0/prometheus") -> bool:
        """创建VictoriaMetrics数据源"""
        datasource_config = {
            "name": "VictoriaMetrics",
            "type": "prometheus",
            "access": "proxy",
            "url": vm_url,
            "isDefault": True,
            "jsonData": {
                "httpMethod": "POST",
                "timeInterval": "30s"
            }
        }
        return self.create_datasource(datasource_config)


def main():
    """主函数"""
    print("=" * 60)
    print("拖拉机车队管理Grafana仪表板自动部署")
    print("=" * 60)
    print()
    
    # 从环境变量读取配置
    grafana_url = os.getenv("GRAFANA_URL", "http://localhost:3000")
    grafana_api_key = os.getenv("GRAFANA_API_KEY")
    grafana_username = os.getenv("GRAFANA_USERNAME", "admin")
    grafana_password = os.getenv("GRAFANA_PASSWORD", "admin")
    vm_url = os.getenv("VICTORIAMETRICS_URL", "http://vmselect:8481/select/0/prometheus")
    
    # 创建部署器
    deployer = GrafanaDashboardDeployer(
        grafana_url=grafana_url,
        api_key=grafana_api_key,
        username=grafana_username,
        password=grafana_password
    )
    
    # 测试连接
    print("1. 测试Grafana连接...")
    if not deployer.test_connection():
        print("\n✗ 部署失败: 无法连接到Grafana")
        print("  请确保Grafana正在运行: docker-compose -f victoriametrics_deployment.yaml up -d")
        return False
    print()
    
    # 创建VictoriaMetrics数据源
    print("2. 创建VictoriaMetrics数据源...")
    if not deployer.create_victoriametrics_datasource(vm_url):
        print("\n✗ 部署失败: 无法创建数据源")
        return False
    print()
    
    # 导入仪表板
    print("3. 导入拖拉机车队管理仪表板...")
    dashboard_path = "/home/ubuntu/grafana_tractor_fleet_dashboard.json"
    if not os.path.exists(dashboard_path):
        print(f"✗ 仪表板文件不存在: {dashboard_path}")
        return False
    
    if not deployer.import_dashboard(dashboard_path):
        print("\n✗ 部署失败: 无法导入仪表板")
        return False
    print()
    
    # 部署成功
    print("=" * 60)
    print("✓ 仪表板部署成功!")
    print("=" * 60)
    print()
    print(f"访问Grafana: {grafana_url}")
    print(f"用户名: {grafana_username}")
    print(f"密码: {grafana_password}")
    print()
    print("提示: 在Grafana中选择车辆ID变量以查看特定车辆的数据")
    print()
    
    return True


if __name__ == "__main__":
    success = main()
    exit(0 if success else 1)
