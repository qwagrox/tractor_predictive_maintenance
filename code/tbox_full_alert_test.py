#!/usr/bin/env python3
"""
T-BOX Full Alert Scenario Test
全场景自动化告警测试脚本

自动测试所有告警场景，无需手动干预
"""

import json
import time
import random
import math
from datetime import datetime, timezone
import paho.mqtt.client as mqtt

# ============================================================================
# Configuration
# ============================================================================

MQTT_BROKER = "localhost"
MQTT_PORT = 1883
MQTT_TOPIC = "tractor/telemetry"
VEHICLE_ID = "TRACTOR_001"

# ============================================================================
# Test Scenarios Configuration
# ============================================================================

TEST_SCENARIOS = [
    {
        "name": "正常运行",
        "duration": 180,  # 3分钟
        "emoji": "✅",
        "description": "建立基线数据",
        "params": {
            "engine_coolant_temp": 85.0,
            "engine_oil_pressure": 4.5,
            "fuel_level": 75.0,
            "battery_soc": 85.0,
            "hydraulic_system_pressure": 180.0,
        }
    },
    {
        "name": "发动机过热",
        "duration": 300,  # 5分钟
        "emoji": "🔥",
        "description": "冷却液温度>105°C，触发Critical告警",
        "params": {
            "engine_coolant_temp": 112.0,
            "engine_oil_temp": 115.0,
            "engine_oil_pressure": 4.2,
            "fuel_level": 73.0,
            "battery_soc": 83.0,
            "hydraulic_system_pressure": 178.0,
        }
    },
    {
        "name": "恢复正常",
        "duration": 120,  # 2分钟
        "emoji": "✅",
        "description": "告警自动解除",
        "params": {
            "engine_coolant_temp": 88.0,
            "engine_oil_temp": 92.0,
            "engine_oil_pressure": 4.5,
            "fuel_level": 72.0,
            "battery_soc": 82.0,
            "hydraulic_system_pressure": 179.0,
        }
    },
    {
        "name": "燃油不足",
        "duration": 300,  # 5分钟
        "emoji": "⛽",
        "description": "燃油液位<15%，触发Warning告警",
        "params": {
            "engine_coolant_temp": 87.0,
            "engine_oil_pressure": 4.4,
            "fuel_level": 12.0,
            "battery_soc": 81.0,
            "hydraulic_system_pressure": 177.0,
        }
    },
    {
        "name": "恢复正常",
        "duration": 120,  # 2分钟
        "emoji": "✅",
        "description": "告警自动解除",
        "params": {
            "engine_coolant_temp": 86.0,
            "engine_oil_pressure": 4.5,
            "fuel_level": 70.0,
            "battery_soc": 80.0,
            "hydraulic_system_pressure": 178.0,
        }
    },
    {
        "name": "机油压力低",
        "duration": 300,  # 5分钟
        "emoji": "💧",
        "description": "机油压力<2.0bar，触发Critical告警",
        "params": {
            "engine_coolant_temp": 87.0,
            "engine_oil_pressure": 1.5,
            "engine_oil_temp": 105.0,
            "fuel_level": 68.0,
            "battery_soc": 79.0,
            "hydraulic_system_pressure": 176.0,
        }
    },
    {
        "name": "恢复正常",
        "duration": 120,  # 2分钟
        "emoji": "✅",
        "description": "告警自动解除",
        "params": {
            "engine_coolant_temp": 85.0,
            "engine_oil_pressure": 4.5,
            "engine_oil_temp": 90.0,
            "fuel_level": 67.0,
            "battery_soc": 78.0,
            "hydraulic_system_pressure": 177.0,
        }
    },
    {
        "name": "电池低电",
        "duration": 300,  # 5分钟
        "emoji": "🔋",
        "description": "电池SOC<20%，触发Warning告警",
        "params": {
            "engine_coolant_temp": 86.0,
            "engine_oil_pressure": 4.4,
            "fuel_level": 66.0,
            "battery_soc": 15.0,
            "battery_voltage": 22.5,
            "hydraulic_system_pressure": 175.0,
        }
    },
    {
        "name": "恢复正常",
        "duration": 120,  # 2分钟
        "emoji": "✅",
        "description": "告警自动解除",
        "params": {
            "engine_coolant_temp": 85.0,
            "engine_oil_pressure": 4.5,
            "fuel_level": 65.0,
            "battery_soc": 75.0,
            "battery_voltage": 24.5,
            "hydraulic_system_pressure": 176.0,
        }
    },
    {
        "name": "多重故障",
        "duration": 300,  # 5分钟
        "emoji": "💥",
        "description": "同时触发多个告警",
        "params": {
            "engine_coolant_temp": 108.0,
            "engine_oil_pressure": 1.8,
            "fuel_level": 12.0,
            "battery_soc": 18.0,
            "hydraulic_system_pressure": 120.0,
        }
    },
    {
        "name": "最终恢复",
        "duration": 180,  # 3分钟
        "emoji": "✅",
        "description": "所有告警解除",
        "params": {
            "engine_coolant_temp": 85.0,
            "engine_oil_pressure": 4.5,
            "fuel_level": 60.0,
            "battery_soc": 70.0,
            "hydraulic_system_pressure": 180.0,
        }
    },
]

# ============================================================================
# Complete Tractor Data Generator
# ============================================================================

class TractorDataGenerator:
    """生成完整的拖拉机遥测数据"""
    
    def __init__(self):
        self.running_time = 0
        self.total_distance = 0
        
        # 基准参数
        self.base_params = {
            # Engine
            "engine_coolant_temp": 85.0,
            "engine_oil_pressure": 4.5,
            "engine_oil_temp": 90.0,
            "engine_rpm": 1800,
            "engine_load": 45.0,
            "engine_torque": 850.0,
            "engine_power": 120.0,
            "engine_fuel_rate": 15.5,
            "engine_air_intake_temp": 35.0,
            "engine_exhaust_temp": 450.0,
            "engine_throttle_position": 45.0,
            
            # Fuel
            "fuel_level": 75.0,
            "fuel_pressure": 3.5,
            "fuel_temp": 25.0,
            
            # Battery
            "battery_voltage": 24.5,
            "battery_current": 15.0,
            "battery_soc": 85.0,
            "battery_soh": 95.0,
            "battery_temp_avg": 28.0,
            "battery_temp_max": 30.0,
            "battery_temp_min": 26.0,
            "battery_cell_voltage_max": 3.45,
            "battery_cell_voltage_min": 3.42,
            "battery_cell_voltage_diff": 0.03,
            "battery_charge_cycles": 245,
            
            # Hydraulic
            "hydraulic_system_pressure": 180.0,
            "hydraulic_oil_temp": 55.0,
            "hydraulic_oil_level": 85.0,
            "hydraulic_pump_pressure": 185.0,
            "hydraulic_flow_rate": 45.0,
            
            # Transmission
            "transmission_oil_temp": 75.0,
            "transmission_oil_pressure": 5.5,
            "transmission_gear": 3,
            
            # Vehicle
            "vehicle_speed": 12.0,
            "wheel_speed_fl": 12.1,
            "wheel_speed_fr": 12.0,
            "wheel_speed_rl": 11.9,
            "wheel_speed_rr": 12.0,
            "steering_angle": 0.0,
            "brake_pressure": 0.0,
            
            # GNSS
            "gnss_latitude": 39.9042,
            "gnss_longitude": 116.4074,
            "gnss_altitude": 50.0,
            "gnss_speed": 12.0,
            "gnss_heading": 90.0,
            "gnss_satellite_count": 12,
            "gnss_hdop": 0.8,
            "gnss_rtk_status": 2,
            
            # IMU
            "imu_pitch": 2.5,
            "imu_roll": -1.2,
            "imu_yaw": 90.0,
            
            # System
            "operation_hours": 1245.5,
        }
    
    def add_noise(self, value, noise_percent=2.0):
        """添加随机噪声"""
        if not isinstance(value, (int, float)):
            return value
        noise = value * (noise_percent / 100.0)
        return value + random.uniform(-noise, noise)
    
    def generate(self, scenario_params):
        """生成遥测数据"""
        data = {
            "vehicle_id": VEHICLE_ID,
            "timestamp": datetime.now(timezone.utc).isoformat(),
            "running_time": self.running_time,
        }
        
        # 合并基准参数和场景参数
        params = self.base_params.copy()
        params.update(scenario_params)
        
        # 添加噪声
        for key, value in params.items():
            if isinstance(value, (int, float)):
                data[key] = self.add_noise(value, noise_percent=2.0)
            else:
                data[key] = value
        
        return data

# ============================================================================
# MQTT Client
# ============================================================================

class MQTTClient:
    """MQTT客户端"""
    
    def __init__(self):
        self.client = mqtt.Client()
        self.client.on_connect = self.on_connect
        self.connected = False
    
    def on_connect(self, client, userdata, flags, rc):
        if rc == 0:
            self.connected = True
            print("✅ 已连接到MQTT代理: localhost:1883\n")
        else:
            print(f"❌ 连接失败，错误代码: {rc}\n")
    
    def connect(self):
        """连接到MQTT代理"""
        try:
            self.client.connect(MQTT_BROKER, MQTT_PORT, 60)
            self.client.loop_start()
            time.sleep(2)
            return self.connected
        except Exception as e:
            print(f"❌ 连接失败: {e}\n")
            return False
    
    def publish(self, data):
        """发布数据"""
        try:
            payload = json.dumps(data, ensure_ascii=False)
            self.client.publish(MQTT_TOPIC, payload)
            return True
        except Exception as e:
            print(f"❌ 发布失败: {e}")
            return False
    
    def disconnect(self):
        """断开连接"""
        self.client.loop_stop()
        self.client.disconnect()

# ============================================================================
# Main Test Runner
# ============================================================================

def print_header():
    """打印测试头部"""
    print("=" * 80)
    print("  T-BOX全场景自动化告警测试")
    print("  Tractor Predictive Maintenance System - Full Alert Test")
    print("=" * 80)
    print()

def print_scenario_header(scenario, index, total):
    """打印场景头部"""
    print("\n" + "=" * 80)
    print(f"  阶段 {index}/{total}: {scenario['emoji']} {scenario['name']}")
    print("=" * 80)
    print(f"  描述: {scenario['description']}")
    print(f"  持续时间: {scenario['duration']}秒 ({scenario['duration']//60}分钟)")
    print(f"  关键参数:")
    for key, value in scenario['params'].items():
        print(f"    - {key}: {value}")
    print("=" * 80)
    print()

def print_progress(current, total, scenario_name):
    """打印进度"""
    percent = (current / total) * 100
    bar_length = 50
    filled = int(bar_length * current / total)
    bar = "█" * filled + "░" * (bar_length - filled)
    print(f"\r  [{bar}] {percent:.1f}% | {scenario_name} | {current}/{total}秒", end="", flush=True)

def main():
    """主测试流程"""
    print_header()
    
    # 初始化
    mqtt_client = MQTTClient()
    data_generator = TractorDataGenerator()
    
    # 连接MQTT
    print("🔌 正在连接到MQTT代理...")
    if not mqtt_client.connect():
        print("❌ 无法连接到MQTT，测试终止")
        return
    
    # 计算总时长
    total_duration = sum(s['duration'] for s in TEST_SCENARIOS)
    total_minutes = total_duration // 60
    
    print(f"📋 测试计划:")
    print(f"  - 场景数量: {len(TEST_SCENARIOS)}")
    print(f"  - 总时长: {total_duration}秒 ({total_minutes}分钟)")
    print(f"  - 发送间隔: 10秒")
    print()
    
    input("按Enter键开始测试...")
    print()
    
    # 执行测试
    try:
        for idx, scenario in enumerate(TEST_SCENARIOS, 1):
            print_scenario_header(scenario, idx, len(TEST_SCENARIOS))
            
            duration = scenario['duration']
            interval = 10  # 10秒发送一次
            iterations = duration // interval
            
            for i in range(iterations):
                # 生成数据
                data = data_generator.generate(scenario['params'])
                
                # 发送数据
                mqtt_client.publish(data)
                
                # 更新进度
                elapsed = (i + 1) * interval
                print_progress(elapsed, duration, scenario['name'])
                
                # 等待
                if i < iterations - 1:
                    time.sleep(interval)
            
            print()  # 换行
            
            # 场景完成提示
            if idx < len(TEST_SCENARIOS):
                print(f"\n✅ 场景 {idx} 完成，进入下一场景...\n")
                time.sleep(2)
        
        # 测试完成
        print("\n" + "=" * 80)
        print("  🎉 全场景测试完成！")
        print("=" * 80)
        print()
        print("📊 验证清单:")
        print("  1. 检查vmalert: http://127.0.0.1:8880")
        print("  2. 检查Alertmanager: http://localhost:9093")
        print("  3. 检查企业微信群消息")
        print("  4. 检查Grafana仪表板: http://localhost:3000")
        print()
        print("预期告警:")
        print("  - 🔥 发动机过热 (Critical)")
        print("  - ⛽ 燃油不足 (Warning)")
        print("  - 💧 机油压力低 (Critical)")
        print("  - 🔋 电池低电 (Warning)")
        print("  - 💥 多重故障 (Multiple)")
        print()
        
    except KeyboardInterrupt:
        print("\n\n⚠️  测试被用户中断")
    finally:
        mqtt_client.disconnect()
        print("\n🔌 已断开MQTT连接")

if __name__ == "__main__":
    main()
