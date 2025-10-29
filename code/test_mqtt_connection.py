#!/usr/bin/env python3
"""
测试MQTT Broker连接
"""

import socket
import time

def test_mqtt_port(host, port):
    """测试MQTT端口是否可访问"""
    print(f"测试连接到 {host}:{port}...")
    try:
        sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        sock.settimeout(5)
        result = sock.connect_ex((host, port))
        sock.close()
        
        if result == 0:
            print(f"✓ 端口 {port} 可访问")
            return True
        else:
            print(f"✗ 端口 {port} 不可访问 (错误代码: {result})")
            return False
    except Exception as e:
        print(f"✗ 连接测试失败: {e}")
        return False

def test_mqtt_client():
    """测试MQTT客户端连接"""
    try:
        import paho.mqtt.client as mqtt
        
        print("\n测试MQTT客户端连接...")
        
        connected = False
        
        def on_connect(client, userdata, flags, rc):
            nonlocal connected
            if rc == 0:
                print("✓ MQTT客户端连接成功")
                connected = True
            else:
                print(f"✗ MQTT客户端连接失败 (错误代码: {rc})")
        
        client = mqtt.Client()
        client.on_connect = on_connect
        
        print("正在连接...")
        client.connect("localhost", 1883, 60)
        client.loop_start()
        
        # 等待连接
        for i in range(10):
            if connected:
                break
            time.sleep(0.5)
        
        client.loop_stop()
        client.disconnect()
        
        return connected
    except ImportError:
        print("\n✗ paho-mqtt库未安装")
        print("  请运行: pip install paho-mqtt")
        return False
    except Exception as e:
        print(f"\n✗ MQTT客户端测试失败: {e}")
        return False

def main():
    print("=" * 60)
    print("MQTT Broker连接测试")
    print("=" * 60)
    print()
    
    # 测试端口
    port_ok = test_mqtt_port("localhost", 1883)
    
    # 测试MQTT客户端
    if port_ok:
        client_ok = test_mqtt_client()
    else:
        print("\n跳过MQTT客户端测试（端口不可访问）")
        client_ok = False
    
    print()
    print("=" * 60)
    print("测试结果")
    print("=" * 60)
    print(f"端口测试: {'✓ 通过' if port_ok else '✗ 失败'}")
    print(f"客户端测试: {'✓ 通过' if client_ok else '✗ 失败'}")
    print()
    
    if not port_ok:
        print("建议:")
        print("1. 检查Mosquitto容器是否运行:")
        print("   docker ps | grep mosquitto")
        print()
        print("2. 检查端口映射:")
        print("   docker port mosquitto")
        print()
        print("3. 重启Mosquitto容器:")
        print("   docker-compose -f victoriametrics_deployment.yaml restart mosquitto")
        print()
        print("4. 检查防火墙设置")
        print()
    
    if port_ok and not client_ok:
        print("建议:")
        print("1. 检查Mosquitto配置是否允许匿名连接")
        print("2. 查看Mosquitto日志:")
        print("   docker logs mosquitto")
        print()

if __name__ == "__main__":
    main()
