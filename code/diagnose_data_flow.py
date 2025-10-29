#!/usr/bin/env python3
"""
数据流诊断脚本
检查T-BOX → MQTT → VictoriaMetrics的数据流是否正常
"""

import requests
import json
import subprocess
import time

def check_docker_containers():
    """检查Docker容器状态"""
    print("=" * 60)
    print("1. 检查Docker容器状态")
    print("=" * 60)
    
    required_containers = [
        "mosquitto",
        "vmstorage-1",
        "vmstorage-2",
        "vminsert",
        "vmselect",
        "vmagent",
        "grafana"
    ]
    
    try:
        result = subprocess.run(
            ["docker", "ps", "--format", "{{.Names}}\t{{.Status}}"],
            capture_output=True,
            text=True,
            check=True
        )
        
        running_containers = {}
        for line in result.stdout.strip().split('\n'):
            if line:
                parts = line.split('\t')
                if len(parts) >= 2:
                    running_containers[parts[0]] = parts[1]
        
        all_running = True
        for container in required_containers:
            if container in running_containers:
                print(f"✓ {container}: {running_containers[container]}")
            else:
                print(f"✗ {container}: 未运行")
                all_running = False
        
        print()
        return all_running
    except Exception as e:
        print(f"✗ 无法检查Docker容器: {e}")
        print()
        return False

def check_mqtt_broker():
    """检查MQTT Broker是否可访问"""
    print("=" * 60)
    print("2. 检查MQTT Broker")
    print("=" * 60)
    
    try:
        import socket
        sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        sock.settimeout(2)
        result = sock.connect_ex(('localhost', 1883))
        sock.close()
        
        if result == 0:
            print("✓ MQTT Broker (端口1883) 可访问")
            print()
            return True
        else:
            print("✗ MQTT Broker (端口1883) 不可访问")
            print()
            return False
    except Exception as e:
        print(f"✗ 检查MQTT Broker失败: {e}")
        print()
        return False

def check_victoriametrics():
    """检查VictoriaMetrics是否可访问"""
    print("=" * 60)
    print("3. 检查VictoriaMetrics")
    print("=" * 60)
    
    try:
        # 检查vmselect查询接口
        response = requests.get(
            "http://localhost:8481/select/0/prometheus/api/v1/query",
            params={"query": "up"},
            timeout=5
        )
        
        if response.status_code == 200:
            print("✓ VictoriaMetrics查询接口可访问")
            data = response.json()
            print(f"  查询结果: {len(data.get('data', {}).get('result', []))} 个指标")
        else:
            print(f"✗ VictoriaMetrics查询接口返回错误: HTTP {response.status_code}")
            return False
        
        # 检查vminsert写入接口
        response = requests.get("http://localhost:8480/health", timeout=5)
        if response.status_code == 200:
            print("✓ VictoriaMetrics写入接口可访问")
        else:
            print(f"✗ VictoriaMetrics写入接口返回错误: HTTP {response.status_code}")
            return False
        
        print()
        return True
    except Exception as e:
        print(f"✗ 检查VictoriaMetrics失败: {e}")
        print()
        return False

def check_tractor_data():
    """检查是否有拖拉机数据"""
    print("=" * 60)
    print("4. 检查拖拉机数据")
    print("=" * 60)
    
    try:
        # 查询拖拉机相关指标
        queries = [
            "tractor_vehicle_speed",
            "tractor_engine_rpm",
            "tractor_battery_soc",
            "tractor_operation_hours"
        ]
        
        has_data = False
        for query in queries:
            response = requests.get(
                "http://localhost:8481/select/0/prometheus/api/v1/query",
                params={"query": query},
                timeout=5
            )
            
            if response.status_code == 200:
                data = response.json()
                results = data.get('data', {}).get('result', [])
                if results:
                    print(f"✓ {query}: {len(results)} 个数据点")
                    has_data = True
                    # 显示第一个数据点的详细信息
                    if results:
                        first_result = results[0]
                        labels = first_result.get('metric', {})
                        value = first_result.get('value', [None, None])[1]
                        print(f"  标签: {labels}")
                        print(f"  值: {value}")
                else:
                    print(f"✗ {query}: 无数据")
            else:
                print(f"✗ {query}: 查询失败 (HTTP {response.status_code})")
        
        print()
        return has_data
    except Exception as e:
        print(f"✗ 检查拖拉机数据失败: {e}")
        print()
        return False

def check_vehicle_ids():
    """检查可用的车辆ID"""
    print("=" * 60)
    print("5. 检查车辆ID")
    print("=" * 60)
    
    try:
        response = requests.get(
            "http://localhost:8481/select/0/prometheus/api/v1/label/vehicle_id/values",
            timeout=5
        )
        
        if response.status_code == 200:
            data = response.json()
            vehicle_ids = data.get('data', [])
            if vehicle_ids:
                print(f"✓ 找到 {len(vehicle_ids)} 个车辆ID:")
                for vid in vehicle_ids:
                    print(f"  - {vid}")
            else:
                print("✗ 未找到车辆ID")
                print("  这意味着没有数据写入VictoriaMetrics")
            print()
            return len(vehicle_ids) > 0
        else:
            print(f"✗ 查询车辆ID失败: HTTP {response.status_code}")
            print()
            return False
    except Exception as e:
        print(f"✗ 检查车辆ID失败: {e}")
        print()
        return False

def main():
    """主函数"""
    print()
    print("=" * 60)
    print("拖拉机预测性维护系统 - 数据流诊断")
    print("=" * 60)
    print()
    
    # 检查Docker容器
    containers_ok = check_docker_containers()
    
    # 检查MQTT Broker
    mqtt_ok = check_mqtt_broker()
    
    # 检查VictoriaMetrics
    vm_ok = check_victoriametrics()
    
    # 检查拖拉机数据
    data_ok = check_tractor_data()
    
    # 检查车辆ID
    vehicle_ids_ok = check_vehicle_ids()
    
    # 总结
    print("=" * 60)
    print("诊断总结")
    print("=" * 60)
    print(f"Docker容器: {'✓ 正常' if containers_ok else '✗ 异常'}")
    print(f"MQTT Broker: {'✓ 正常' if mqtt_ok else '✗ 异常'}")
    print(f"VictoriaMetrics: {'✓ 正常' if vm_ok else '✗ 异常'}")
    print(f"拖拉机数据: {'✓ 有数据' if data_ok else '✗ 无数据'}")
    print(f"车辆ID: {'✓ 有车辆' if vehicle_ids_ok else '✗ 无车辆'}")
    print()
    
    # 给出建议
    if not containers_ok:
        print("⚠️  建议: 请先启动所有Docker容器")
        print("   运行: docker-compose -f victoriametrics_deployment.yaml up -d")
        print()
    
    if containers_ok and not data_ok:
        print("⚠️  问题: T-BOX模拟器生成的数据没有到达VictoriaMetrics")
        print("   原因: 缺少MQTT到VictoriaMetrics的数据桥接服务")
        print()
        print("   解决方案:")
        print("   1. 在新的PowerShell窗口中运行MQTT桥接服务:")
        print("      cd D:\\tractor_pdm\\code")
        print("      python mqtt_to_victoriametrics_bridge.py")
        print()
        print("   2. 保持T-BOX模拟器运行")
        print()
        print("   3. 等待1-2分钟后刷新Grafana仪表板")
        print()
    
    if data_ok and not vehicle_ids_ok:
        print("⚠️  问题: 有数据但没有车辆ID标签")
        print("   这可能是数据格式问题，请检查MQTT桥接服务")
        print()
    
    if data_ok and vehicle_ids_ok:
        print("✓ 数据流正常！")
        print()
        print("下一步:")
        print("1. 访问Grafana: http://localhost:3000")
        print("2. 在仪表板顶部选择车辆ID")
        print("3. 调整时间范围为 'Last 5 minutes'")
        print()

if __name__ == "__main__":
    main()
