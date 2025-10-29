#!/usr/bin/env python3
"""
测试VictoriaMetrics连接
"""

import requests
import socket
import time

def test_port(host, port, name):
    """测试端口是否可访问"""
    print(f"\n测试 {name} ({host}:{port})...")
    try:
        sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        sock.settimeout(5)
        result = sock.connect_ex((host, port))
        sock.close()
        
        if result == 0:
            print(f"  ✓ 端口 {port} 可访问")
            return True
        else:
            print(f"  ✗ 端口 {port} 不可访问 (错误代码: {result})")
            return False
    except Exception as e:
        print(f"  ✗ 测试失败: {e}")
        return False

def test_http_endpoint(url, name, method='GET', data=None, timeout=5):
    """测试HTTP端点"""
    print(f"\n测试 {name}...")
    print(f"  URL: {url}")
    try:
        if method == 'GET':
            response = requests.get(url, timeout=timeout, proxies={'http': None, 'https': None})
        elif method == 'POST':
            response = requests.post(
                url, 
                data=data, 
                headers={'Content-Type': 'text/plain'},
                timeout=timeout,
                proxies={'http': None, 'https': None}
            )
        
        print(f"  ✓ HTTP {method} 成功")
        print(f"  状态码: {response.status_code}")
        if len(response.text) < 200:
            print(f"  响应: {response.text[:200]}")
        else:
            print(f"  响应长度: {len(response.text)} 字节")
        return True
    except requests.exceptions.Timeout:
        print(f"  ✗ 请求超时")
        return False
    except requests.exceptions.ConnectionError as e:
        print(f"  ✗ 连接错误: {e}")
        return False
    except Exception as e:
        print(f"  ✗ 请求失败: {e}")
        return False

def main():
    print("=" * 70)
    print("VictoriaMetrics连接测试")
    print("=" * 70)
    
    # 测试端口
    print("\n" + "=" * 70)
    print("1. 端口连接测试")
    print("=" * 70)
    
    ports = {
        8480: "vminsert (写入接口)",
        8481: "vmselect (查询接口)",
        8089: "vmagent (代理)",
    }
    
    port_results = {}
    for port, name in ports.items():
        port_results[port] = test_port("localhost", port, name)
    
    # 测试HTTP端点
    print("\n" + "=" * 70)
    print("2. HTTP端点测试")
    print("=" * 70)
    
    # 测试vmselect查询接口
    test_http_endpoint(
        "http://localhost:8481/select/0/prometheus/api/v1/query?query=up",
        "vmselect查询接口 (GET)"
    )
    
    # 测试vminsert写入接口（发送测试数据）
    test_data = 'test_metric{label="value"} 123 ' + str(int(time.time() * 1000))
    result = test_http_endpoint(
        "http://localhost:8480/insert/0/prometheus/api/v1/import/prometheus",
        "vminsert写入接口 (POST)",
        method='POST',
        data=test_data,
        timeout=15  # 增加超时时间
    )
    
    # 如果写入成功，等待一下再查询
    if result:
        print("\n  等待2秒后查询测试数据...")
        time.sleep(2)
        test_http_endpoint(
            "http://localhost:8481/select/0/prometheus/api/v1/query?query=test_metric",
            "查询刚写入的测试数据"
        )
    
    # 总结
    print("\n" + "=" * 70)
    print("测试总结")
    print("=" * 70)
    
    all_ports_ok = all(port_results.values())
    
    if all_ports_ok:
        print("✓ 所有端口可访问")
    else:
        print("✗ 部分端口不可访问")
        for port, ok in port_results.items():
            if not ok:
                print(f"  - 端口 {port} ({ports[port]}) 不可访问")
    
    print("\n建议:")
    if not all_ports_ok:
        print("1. 检查Docker容器状态:")
        print("   docker ps | findstr vm")
        print("\n2. 检查容器日志:")
        print("   docker logs vminsert")
        print("   docker logs vmselect")
        print("\n3. 重启VictoriaMetrics集群:")
        print("   cd D:\\tractor_pdm\\config")
        print("   docker-compose -f victoriametrics_deployment.yaml restart")

if __name__ == "__main__":
    main()
