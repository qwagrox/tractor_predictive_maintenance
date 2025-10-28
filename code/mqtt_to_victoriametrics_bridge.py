#!/usr/bin/env python3
"""
MQTT到VictoriaMetrics数据桥接服务
接收T-BOX通过MQTT上传的数据，转换为VictoriaMetrics格式并写入
"""

import json
import time
from datetime import datetime
from typing import Dict, Any, List
import requests


class MQTTToVictoriaMetricsBridge:
    """MQTT到VictoriaMetrics的数据桥接器"""
    
    def __init__(self, vm_url: str = "http://localhost:8480"):
        """
        初始化桥接器
        
        Args:
            vm_url: VictoriaMetrics vminsert的URL
        """
        self.vm_url = vm_url
        self.write_endpoint = f"{vm_url}/insert/0/prometheus/api/v1/import/prometheus"
        
    def flatten_dict(self, d: Dict[str, Any], parent_key: str = '', sep: str = '_') -> Dict[str, Any]:
        """
        将嵌套字典展平
        
        Args:
            d: 嵌套字典
            parent_key: 父键名
            sep: 分隔符
            
        Returns:
            展平后的字典
        """
        items = []
        for k, v in d.items():
            new_key = f"{parent_key}{sep}{k}" if parent_key else k
            if isinstance(v, dict):
                items.extend(self.flatten_dict(v, new_key, sep=sep).items())
            elif isinstance(v, (int, float)):
                items.append((new_key, v))
            elif isinstance(v, str):
                # 字符串类型作为标签，不作为指标值
                pass
        return dict(items)
    
    def convert_to_prometheus_format(self, data_packet: Dict[str, Any]) -> List[str]:
        """
        将T-BOX数据包转换为Prometheus文本格式
        
        Args:
            data_packet: T-BOX数据包
            
        Returns:
            Prometheus格式的指标行列表
        """
        lines = []
        vehicle_id = data_packet.get('vehicle_id', 'unknown')
        timestamp_str = data_packet.get('timestamp', datetime.now().isoformat())
        
        # 转换时间戳为毫秒
        try:
            dt = datetime.fromisoformat(timestamp_str.replace('Z', '+00:00'))
            timestamp_ms = int(dt.timestamp() * 1000)
        except:
            timestamp_ms = int(time.time() * 1000)
        
        # 基础标签
        base_labels = f'vehicle_id="{vehicle_id}"'
        
        # 处理运行时长
        if 'operation_hours' in data_packet:
            lines.append(f'tractor_operation_hours{{{base_labels}}} {data_packet["operation_hours"]} {timestamp_ms}')
        
        # 处理发动机数据
        if 'engine' in data_packet:
            engine = data_packet['engine']
            for key, value in engine.items():
                if isinstance(value, (int, float)):
                    metric_name = f'tractor_engine_{key}'
                    lines.append(f'{metric_name}{{{base_labels}}} {value} {timestamp_ms}')
        
        # 处理电池数据
        if 'battery' in data_packet:
            battery = data_packet['battery']
            for key, value in battery.items():
                if isinstance(value, (int, float)):
                    metric_name = f'tractor_battery_{key}'
                    lines.append(f'{metric_name}{{{base_labels}}} {value} {timestamp_ms}')
        
        # 处理车辆状态
        if 'vehicle_state' in data_packet:
            vehicle_state = data_packet['vehicle_state']
            for key, value in vehicle_state.items():
                if isinstance(value, (int, float)):
                    metric_name = f'tractor_vehicle_{key}'
                    lines.append(f'{metric_name}{{{base_labels}}} {value} {timestamp_ms}')
        
        # 处理变速箱数据
        if 'transmission' in data_packet:
            transmission = data_packet['transmission']
            for key, value in transmission.items():
                if isinstance(value, (int, float)):
                    metric_name = f'tractor_transmission_{key}'
                    lines.append(f'{metric_name}{{{base_labels}}} {value} {timestamp_ms}')
        
        # 处理液压系统数据
        if 'hydraulic' in data_packet:
            hydraulic = data_packet['hydraulic']
            for key, value in hydraulic.items():
                if isinstance(value, (int, float)):
                    metric_name = f'tractor_hydraulic_{key}'
                    lines.append(f'{metric_name}{{{base_labels}}} {value} {timestamp_ms}')
        
        # 处理GNSS数据
        if 'gnss' in data_packet:
            gnss = data_packet['gnss']
            for key, value in gnss.items():
                if isinstance(value, (int, float)):
                    metric_name = f'tractor_gnss_{key}'
                    lines.append(f'{metric_name}{{{base_labels}}} {value} {timestamp_ms}')
        
        # 处理传感器健康度
        if 'sensor_health' in data_packet:
            sensor_health = self.flatten_dict(data_packet['sensor_health'])
            for key, value in sensor_health.items():
                if isinstance(value, (int, float)):
                    metric_name = f'tractor_sensor_{key}'
                    lines.append(f'{metric_name}{{{base_labels}}} {value} {timestamp_ms}')
        
        # 处理智驾系统数据
        if 'intelligent_driving' in data_packet:
            intelligent_driving = self.flatten_dict(data_packet['intelligent_driving'])
            for key, value in intelligent_driving.items():
                if isinstance(value, (int, float)):
                    metric_name = f'tractor_intelligent_driving_{key}'
                    lines.append(f'{metric_name}{{{base_labels}}} {value} {timestamp_ms}')
        
        return lines
    
    def write_to_victoriametrics(self, prometheus_lines: List[str]) -> bool:
        """
        将Prometheus格式数据写入VictoriaMetrics
        
        Args:
            prometheus_lines: Prometheus格式的指标行
            
        Returns:
            是否写入成功
        """
        if not prometheus_lines:
            return True
        
        data = '\n'.join(prometheus_lines)
        
        try:
            response = requests.post(
                self.write_endpoint,
                data=data,
                headers={'Content-Type': 'text/plain'},
                timeout=10
            )
            
            if response.status_code == 204:
                return True
            else:
                print(f"写入VictoriaMetrics失败: {response.status_code}, {response.text}")
                return False
        except Exception as e:
            print(f"写入VictoriaMetrics异常: {e}")
            return False
    
    def process_tbox_data(self, data_packet: Dict[str, Any]) -> bool:
        """
        处理T-BOX数据包
        
        Args:
            data_packet: T-BOX数据包
            
        Returns:
            是否处理成功
        """
        # 转换为Prometheus格式
        prometheus_lines = self.convert_to_prometheus_format(data_packet)
        
        # 写入VictoriaMetrics
        success = self.write_to_victoriametrics(prometheus_lines)
        
        if success:
            print(f"✓ 成功写入 {len(prometheus_lines)} 个指标到VictoriaMetrics")
        
        return success


def demo_bridge():
    """演示桥接器功能"""
    # 创建桥接器实例
    bridge = MQTTToVictoriaMetricsBridge(vm_url="http://localhost:8480")
    
    # 模拟T-BOX数据包
    sample_data = {
        'vehicle_id': 'TRACTOR_001',
        'timestamp': datetime.now().isoformat(),
        'operation_hours': 123.5,
        'engine': {
            'rpm': 1850,
            'torque': 360,
            'coolant_temp': 88.5,
            'oil_pressure': 4.8,
            'fuel_consumption_rate': 14.2,
        },
        'battery': {
            'soc': 75.5,
            'soh': 98.2,
            'voltage': 625,
            'current': 45,
            'power': 28.125,
            'temp_max': 42,
            'temp_min': 38,
        },
        'vehicle_state': {
            'speed': 9.5,
            'acceleration': 0.05,
            'steering_angle': 12,
        },
        'gnss': {
            'latitude': 39.9042,
            'longitude': 116.4074,
            'altitude': 50,
            'positioning_accuracy': 0.015,
            'satellite_count': 16,
        },
    }
    
    print("=" * 80)
    print("MQTT到VictoriaMetrics数据桥接器 - 演示")
    print("=" * 80)
    print(f"\n处理车辆 {sample_data['vehicle_id']} 的数据包...")
    
    # 转换数据
    prometheus_lines = bridge.convert_to_prometheus_format(sample_data)
    
    print(f"\n转换后的Prometheus格式指标（前10条）:")
    print("-" * 80)
    for line in prometheus_lines[:10]:
        print(line)
    print(f"... 共 {len(prometheus_lines)} 条指标")
    
    print("\n" + "=" * 80)
    print("注意: 实际写入VictoriaMetrics需要先启动VictoriaMetrics服务")
    print("使用 docker-compose up -d 启动服务后，可以调用 write_to_victoriametrics() 方法")
    print("=" * 80)


if __name__ == '__main__':
    demo_bridge()
