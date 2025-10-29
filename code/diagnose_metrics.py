#!/usr/bin/env python3
"""
诊断VictoriaMetrics中的指标
列出所有可用的指标名称和最新值
"""

import requests
import json
from datetime import datetime

def diagnose_metrics():
    """诊断VictoriaMetrics中的指标"""
    
    print("="*80)
    print("VictoriaMetrics指标诊断")
    print("="*80)
    print()
    
    # VictoriaMetrics配置（集群版本）
    VM_URL = "http://localhost:8481/select/0/prometheus"
    
    # 步骤1: 获取所有指标名称
    print("[步骤1] 获取所有指标名称...")
    try:
        # 查询所有以tractor_开头的指标
        query_url = f"{VM_URL}/api/v1/label/__name__/values"
        response = requests.get(query_url, timeout=10)
        
        if response.status_code == 200:
            result = response.json()
            all_metrics = result.get('data', [])
            tractor_metrics = [m for m in all_metrics if m.startswith('tractor_')]
            
            print(f"[成功] 找到 {len(tractor_metrics)} 个拖拉机相关指标")
            print()
            
            if not tractor_metrics:
                print("[警告] 未找到任何拖拉机指标！")
                print("[提示] 请确保:")
                print("  1. T-BOX模拟器正在运行")
                print("  2. MQTT桥接服务正在运行")
                print("  3. VictoriaMetrics容器正在运行")
                return
            
            # 步骤2: 查询每个指标的最新值
            print("[步骤2] 查询每个指标的最新值...")
            print()
            print("="*80)
            print(f"{'指标名称':<50} {'最新值':<15} {'车辆ID':<15}")
            print("="*80)
            
            for metric in sorted(tractor_metrics):
                try:
                    # 查询最新值
                    query = metric
                    query_url = f"{VM_URL}/api/v1/query?query={query}"
                    resp = requests.get(query_url, timeout=5)
                    
                    if resp.status_code == 200:
                        data = resp.json()
                        results = data.get('data', {}).get('result', [])
                        
                        if results:
                            for result in results:
                                vehicle_id = result.get('metric', {}).get('vehicle_id', 'N/A')
                                value = result.get('value', [None, 'N/A'])[1]
                                print(f"{metric:<50} {value:<15} {vehicle_id:<15}")
                        else:
                            print(f"{metric:<50} {'No data':<15} {'N/A':<15}")
                    else:
                        print(f"{metric:<50} {'Query failed':<15} {'N/A':<15}")
                        
                except Exception as e:
                    print(f"{metric:<50} {'Error: {str(e)}':<15} {'N/A':<15}")
            
            print("="*80)
            print()
            
            # 步骤3: 检查CSS Electronics仪表板需要的指标
            print("[步骤3] 检查CSS Electronics仪表板需要的指标...")
            print()
            
            required_metrics = {
                'Speed': 'tractor_vehicle_speed',
                'Distance': 'tractor_odometer',
                'RPM': 'tractor_engine_rpm',
                'Fuel (%)': 'tractor_fuel_level',
                'Load (%)': 'tractor_engine_torque',
                'Torque (%)': 'tractor_engine_torque',
                'Altitude': 'tractor_gps_altitude',
                'Satellites': 'tractor_gps_satellites',
                'Fix': 'tractor_gps_fix',
            }
            
            print(f"{'面板名称':<20} {'需要的指标':<35} {'状态':<10}")
            print("-"*80)
            
            for panel_name, metric_name in required_metrics.items():
                if metric_name in tractor_metrics:
                    print(f"{panel_name:<20} {metric_name:<35} {'✅ 有数据':<10}")
                else:
                    print(f"{panel_name:<20} {metric_name:<35} {'❌ 无数据':<10}")
            
            print()
            print("="*80)
            print()
            
            # 步骤4: 提供修复建议
            print("[步骤4] 修复建议...")
            print()
            
            missing_metrics = [m for m in required_metrics.values() if m not in tractor_metrics]
            
            if missing_metrics:
                print(f"[警告] 缺少 {len(missing_metrics)} 个指标:")
                for metric in missing_metrics:
                    print(f"  - {metric}")
                print()
                print("[建议] 请检查:")
                print("  1. T-BOX模拟器是否发送了这些数据字段")
                print("  2. MQTT桥接服务是否正确映射了这些字段")
                print("  3. 数据字段名称是否匹配")
            else:
                print("[成功] 所有需要的指标都存在！")
                print("[提示] 如果仪表板仍显示'No data'，请:")
                print("  1. 检查时间范围（默认是最近5分钟）")
                print("  2. 检查车辆ID过滤器是否正确")
                print("  3. 强制刷新浏览器（Ctrl+F5）")
            
        else:
            print(f"[错误] 查询失败: {response.status_code}")
            print(f"[响应] {response.text}")
            
    except requests.exceptions.ConnectionError:
        print("[错误] 无法连接到VictoriaMetrics")
        print("[提示] 请确保VictoriaMetrics容器正在运行")
        print("       docker ps | grep vmselect")
    except Exception as e:
        print(f"[错误] {str(e)}")

if __name__ == "__main__":
    diagnose_metrics()
