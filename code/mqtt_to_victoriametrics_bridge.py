#!/usr/bin/env python3
"""
MQTT到VictoriaMetrics数据桥接服务 - 完整版
支持T-BOX发送的所有60+指标
"""

import json
import time
import requests
from datetime import datetime
from typing import Dict, Any, List

try:
    import paho.mqtt.client as mqtt
    MQTT_AVAILABLE = True
except ImportError:
    print("错误: paho-mqtt库未安装")
    print("安装命令: pip install paho-mqtt")
    exit(1)

# 配置
MQTT_BROKER = "localhost"
MQTT_PORT = 1883
MQTT_TOPIC = "tractor/telemetry"
VICTORIAMETRICS_URL = "http://localhost:8480/insert/0/prometheus/api/v1/import/prometheus"

# 统计信息
stats = {
    "messages_received": 0,
    "metrics_sent": 0,
    "errors": 0,
    "last_message_time": None
}


def flatten_dict(d: Dict[str, Any], parent_key: str = '', sep: str = '_') -> Dict[str, Any]:
    """
    将嵌套字典扁平化
    例如: {'engine': {'rpm': 1800}} -> {'engine_rpm': 1800}
    """
    items = []
    for k, v in d.items():
        new_key = f"{parent_key}{sep}{k}" if parent_key else k
        if isinstance(v, dict):
            items.extend(flatten_dict(v, new_key, sep=sep).items())
        else:
            items.append((new_key, v))
    return dict(items)


def convert_to_prometheus_format(data: Dict[str, Any]) -> str:
    """
    将T-BOX JSON数据转换为Prometheus格式
    
    输入格式:
    {
        "vehicle_id": "TRACTOR_001",
        "timestamp": "2025-10-30T10:48:39.123456",
        "engine_rpm": 1800,
        "engine_coolant_temp": 110.5,
        ...
    }
    
    输出格式:
    engine_rpm{vehicle_id="TRACTOR_001"} 1800 1698654519123
    engine_coolant_temp{vehicle_id="TRACTOR_001"} 110.5 1698654519123
    ...
    """
    lines = []
    
    # 提取vehicle_id和timestamp
    vehicle_id = data.get('vehicle_id', 'UNKNOWN')
    timestamp_str = data.get('timestamp', datetime.now().isoformat())
    
    # 转换timestamp为毫秒时间戳
    try:
        dt = datetime.fromisoformat(timestamp_str.replace('Z', '+00:00'))
        timestamp_ms = int(dt.timestamp() * 1000)
    except:
        timestamp_ms = int(time.time() * 1000)
    
    # 扁平化嵌套结构（如果有）
    flat_data = flatten_dict(data)
    
    # 转换每个指标
    for key, value in flat_data.items():
        # 跳过非数值字段
        if key in ['vehicle_id', 'timestamp', 'operation_hours']:
            continue
        
        # 跳过字符串类型的值
        if isinstance(value, str):
            continue
        
        # 跳过None值
        if value is None:
            continue
        
        # 转换为数值
        try:
            numeric_value = float(value)
        except (ValueError, TypeError):
            continue
        
        # 生成Prometheus格式的行
        # 格式: metric_name{label1="value1"} value timestamp
        line = f'{key}{{vehicle_id="{vehicle_id}"}} {numeric_value} {timestamp_ms}'
        lines.append(line)
    
    return '\n'.join(lines)


def send_to_victoriametrics(prometheus_data: str) -> bool:
    """发送数据到VictoriaMetrics"""
    try:
        response = requests.post(
            VICTORIAMETRICS_URL,
            data=prometheus_data,
            headers={'Content-Type': 'text/plain'},
            timeout=5
        )
        
        if response.status_code == 204:
            return True
        else:
            print(f"[错误] VictoriaMetrics返回状态码: {response.status_code}")
            print(f"[错误] 响应内容: {response.text}")
            return False
            
    except Exception as e:
        print(f"[错误] 发送到VictoriaMetrics失败: {e}")
        return False


def on_connect(client, userdata, flags, rc):
    """MQTT连接回调"""
    if rc == 0:
        print(f"[成功] 连接到MQTT Broker")
        client.subscribe(MQTT_TOPIC)
        print(f"[成功] 订阅主题: {MQTT_TOPIC}")
    else:
        print(f"[错误] 连接失败，返回码: {rc}")


def on_message(client, userdata, msg):
    """MQTT消息回调"""
    global stats
    
    try:
        # 解析JSON数据
        data = json.loads(msg.payload.decode('utf-8'))
        vehicle_id = data.get('vehicle_id', 'UNKNOWN')
        
        stats["messages_received"] += 1
        stats["last_message_time"] = datetime.now()
        
        # 转换为Prometheus格式
        prometheus_data = convert_to_prometheus_format(data)
        
        # 计算指标数量
        metric_count = len(prometheus_data.split('\n'))
        
        # 发送到VictoriaMetrics
        if send_to_victoriametrics(prometheus_data):
            stats["metrics_sent"] += metric_count
            print(f"[接收] 车辆 {vehicle_id} 的数据 ({len(msg.payload)} 字节)")
            print(f"[转换] 生成 {metric_count} 个指标")
            print(f"[成功] 写入 {metric_count} 个指标到VictoriaMetrics")
            print(f"[统计] 总消息: {stats['messages_received']}, 总指标: {stats['metrics_sent']}, 错误: {stats['errors']}")
            print()
        else:
            stats["errors"] += 1
            print(f"[错误] 发送失败")
            print()
            
    except json.JSONDecodeError as e:
        stats["errors"] += 1
        print(f"[错误] JSON解析失败: {e}")
        print(f"[数据] {msg.payload[:200]}")
        print()
    except Exception as e:
        stats["errors"] += 1
        print(f"[错误] 处理消息失败: {e}")
        print()


def on_disconnect(client, userdata, rc):
    """MQTT断开连接回调"""
    if rc != 0:
        print(f"[警告] 意外断开连接，返回码: {rc}")
        print("[信息] 尝试重新连接...")


def main():
    print("=" * 80)
    print("  MQTT到VictoriaMetrics数据桥接服务 - 完整版")
    print("=" * 80)
    print()
    print(f"MQTT Broker: {MQTT_BROKER}:{MQTT_PORT}")
    print(f"MQTT Topic: {MQTT_TOPIC}")
    print(f"VictoriaMetrics: {VICTORIAMETRICS_URL}")
    print()
    print("=" * 80)
    print()
    
    # 创建MQTT客户端
    client = mqtt.Client()
    client.on_connect = on_connect
    client.on_message = on_message
    client.on_disconnect = on_disconnect
    
    # 连接到MQTT Broker
    print("[连接] 正在连接到MQTT Broker...")
    try:
        client.connect(MQTT_BROKER, MQTT_PORT, 60)
    except Exception as e:
        print(f"[错误] 无法连接到MQTT Broker: {e}")
        print("[提示] 请确保Mosquitto容器正在运行")
        return
    
    # 开始循环
    print()
    print("等待T-BOX数据...")
    print()
    
    try:
        client.loop_forever()
    except KeyboardInterrupt:
        print()
        print()
        print("=" * 80)
        print("  停止服务")
        print("=" * 80)
        print()
        print(f"总消息数: {stats['messages_received']}")
        print(f"总指标数: {stats['metrics_sent']}")
        print(f"错误数: {stats['errors']}")
        if stats['last_message_time']:
            print(f"最后消息时间: {stats['last_message_time'].strftime('%Y-%m-%d %H:%M:%S')}")
        print()
        client.disconnect()


if __name__ == "__main__":
    main()
