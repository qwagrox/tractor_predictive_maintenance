#!/usr/bin/env python3
"""
T-BOX数据模拟器 - 支持告警测试场景
基于原始tbox_simulator.py，添加了告警测试场景支持

新增功能：
- 预定义的告警测试场景
- 命令行参数支持场景选择
- 自动化告警测试模式
- 实时进度显示
"""

import json
import time
import random
import math
import argparse
from datetime import datetime
from typing import Dict, List, Any
import numpy as np

try:
    import paho.mqtt.client as mqtt
    MQTT_AVAILABLE = True
except ImportError:
    MQTT_AVAILABLE = False
    print("警告: paho-mqtt库未安装，将只输出到控制台")
    print("安装命令: pip install paho-mqtt")


class TractorDataSimulatorWithAlerts:
    """拖拉机数据模拟器 - 支持告警测试场景"""
    
    def __init__(self, vehicle_id: str, scenario: str = "normal"):
        self.vehicle_id = vehicle_id
        self.timestamp = time.time()
        self.operation_hours = 0
        self.battery_cycles = 0
        self.scenario = scenario
        self.scenario_start_time = time.time()
        self.message_count = 0
        
        # 故障模式标志
        self.fault_modes = {
            'engine_degradation': False,
            'battery_aging': False,
            'sensor_drift': False,
            'hydraulic_leak': False,
        }
        
        # 场景配置
        self.scenario_config = self._get_scenario_config()
        
        print(f"\n{'='*80}")
        print(f"  T-BOX模拟器 - 告警测试场景")
        print(f"{'='*80}")
        print(f"车辆ID: {self.vehicle_id}")
        print(f"测试场景: {scenario}")
        print(f"场景描述: {self.scenario_config.get('description', 'N/A')}")
        print(f"{'='*80}\n")
    
    def _get_scenario_config(self) -> Dict[str, Any]:
        """获取场景配置"""
        scenarios = {
            "normal": {
                "description": "正常运行 - 所有参数在正常范围内",
                "duration": None,  # 持续运行
                "overrides": {}
            },
            "engine_overheating": {
                "description": "发动机过热 - 冷却液温度>105°C",
                "duration": 300,  # 5分钟
                "overrides": {
                    "engine_coolant_temp": 110.0,
                    "engine_oil_temp": 105.0
                }
            },
            "low_fuel": {
                "description": "燃油不足 - 燃油液位<15%",
                "duration": 300,
                "overrides": {
                    "fuel_level": 12.0
                }
            },
            "low_oil_pressure": {
                "description": "机油压力低 - 压力<2bar",
                "duration": 300,
                "overrides": {
                    "engine_oil_pressure": 1.5
                }
            },
            "battery_low": {
                "description": "电池低电 - SOC<20%",
                "duration": 300,
                "overrides": {
                    "battery_soc": 15.0
                }
            },
            "battery_critical": {
                "description": "电池严重低电 - SOC<10%",
                "duration": 300,
                "overrides": {
                    "battery_soc": 8.0
                }
            },
            "hydraulic_failure": {
                "description": "液压系统故障 - 压力<100bar",
                "duration": 300,
                "overrides": {
                    "hydraulic_system_pressure": 85.0
                }
            },
            "transmission_overheat": {
                "description": "变速箱过热 - 温度>100°C",
                "duration": 300,
                "overrides": {
                    "transmission_oil_temp": 105.0
                }
            },
            "multiple_faults": {
                "description": "多重故障 - 同时触发多个告警",
                "duration": 300,
                "overrides": {
                    "engine_coolant_temp": 110.0,
                    "fuel_level": 12.0,
                    "battery_soc": 15.0,
                    "hydraulic_system_pressure": 85.0
                }
            },
            "auto_test": {
                "description": "自动化测试 - 按顺序测试所有告警场景",
                "duration": None,  # 由自动化流程控制
                "overrides": {}
            }
        }
        
        return scenarios.get(self.scenario, scenarios["normal"])
    
    def _add_noise(self, value: float, noise_level: float = 0.02) -> float:
        """添加高斯噪声"""
        return value * (1 + np.random.normal(0, noise_level))
    
    def _apply_scenario_override(self, metric_name: str, base_value: float) -> float:
        """应用场景覆盖值"""
        overrides = self.scenario_config.get("overrides", {})
        if metric_name in overrides:
            # 添加小幅度噪声使数据更真实
            return self._add_noise(overrides[metric_name], 0.02)
        return base_value
    
    def generate_engine_data(self) -> Dict[str, Any]:
        """生成发动机数据"""
        base_rpm = 1800 + 400 * math.sin(self.timestamp / 100)
        base_torque = 350 + 50 * math.sin(self.timestamp / 80)
        base_temp = 85 + 10 * math.sin(self.timestamp / 200)
        base_fuel_rate = 15 + 5 * abs(math.sin(self.timestamp / 150))
        base_oil_pressure = 4.5 + 0.5 * math.sin(self.timestamp / 120)
        base_oil_temp = 90 + 10 * math.sin(self.timestamp / 180)
        
        # 应用场景覆盖
        coolant_temp = self._apply_scenario_override("engine_coolant_temp", base_temp)
        oil_pressure = self._apply_scenario_override("engine_oil_pressure", base_oil_pressure)
        oil_temp = self._apply_scenario_override("engine_oil_temp", base_oil_temp)
        
        return {
            'engine_rpm': self._add_noise(base_rpm, 0.03),
            'engine_torque': self._add_noise(base_torque, 0.05),
            'engine_coolant_temp': self._add_noise(coolant_temp, 0.02),
            'engine_oil_pressure': self._add_noise(oil_pressure, 0.03),
            'engine_oil_temp': self._add_noise(oil_temp, 0.02),
            'engine_fuel_rate': self._add_noise(base_fuel_rate, 0.04),
            'engine_air_intake_temp': self._add_noise(30 + 15 * math.sin(self.timestamp / 300), 0.03),
            'engine_load': self._add_noise(60 + 20 * math.sin(self.timestamp / 150), 0.05),
            'engine_throttle_position': self._add_noise(50 + 30 * math.sin(self.timestamp / 100), 0.03),
        }
    
    def generate_fuel_data(self) -> Dict[str, Any]:
        """生成燃油系统数据"""
        base_level = 50 + 30 * math.sin(self.timestamp / 1000)  # 缓慢变化
        fuel_level = self._apply_scenario_override("fuel_level", base_level)
        
        return {
            'fuel_level': max(0, min(100, self._add_noise(fuel_level, 0.01))),
            'fuel_pressure': self._add_noise(3.5 + 0.5 * math.sin(self.timestamp / 150), 0.03),
            'fuel_temp': self._add_noise(25 + 10 * math.sin(self.timestamp / 300), 0.02),
        }
    
    def generate_battery_data(self) -> Dict[str, Any]:
        """生成电池系统数据"""
        base_soc = 50 + 30 * math.sin(self.timestamp / 500)
        soc = self._apply_scenario_override("battery_soc", base_soc)
        
        base_soh = 100 - (self.battery_cycles / 5000) * 20
        soh = max(80, self._add_noise(base_soh, 0.01))
        
        base_current = 50 + 30 * math.sin(self.timestamp / 100)
        voltage = 600 + 50 * (soc / 100)
        
        return {
            'battery_soc': max(0, min(100, soc)),
            'battery_soh': soh,
            'battery_voltage': self._add_noise(voltage, 0.01),
            'battery_current': self._add_noise(base_current, 0.05),
            'battery_temp_avg': self._add_noise(32 + 8 * abs(base_current) / 80, 0.03),
            'battery_temp_max': self._add_noise(35 + 10 * abs(base_current) / 80, 0.03),
            'battery_temp_min': self._add_noise(30 + 6 * abs(base_current) / 80, 0.03),
            'battery_cell_voltage_max': self._add_noise(3.7, 0.005),
            'battery_cell_voltage_min': self._add_noise(3.6, 0.005),
            'battery_cell_voltage_diff': self._add_noise(0.05, 0.1),
            'battery_charge_cycles': self.battery_cycles,
        }
    
    def generate_hydraulic_data(self) -> Dict[str, Any]:
        """生成液压系统数据"""
        base_pressure = 180 + 20 * math.sin(self.timestamp / 120)
        pressure = self._apply_scenario_override("hydraulic_system_pressure", base_pressure)
        
        return {
            'hydraulic_system_pressure': self._add_noise(pressure, 0.04),
            'hydraulic_oil_temp': self._add_noise(55 + 15 * math.sin(self.timestamp / 300), 0.03),
            'hydraulic_oil_level': self._add_noise(85, 0.02),
            'hydraulic_pump_pressure': self._add_noise(pressure * 0.9, 0.04),
            'hydraulic_flow_rate': self._add_noise(40 + 10 * abs(math.sin(self.timestamp / 150)), 0.05),
        }
    
    def generate_transmission_data(self) -> Dict[str, Any]:
        """生成变速箱数据"""
        base_temp = 70 + 15 * math.sin(self.timestamp / 250)
        temp = self._apply_scenario_override("transmission_oil_temp", base_temp)
        
        return {
            'transmission_oil_temp': self._add_noise(temp, 0.03),
            'transmission_oil_pressure': self._add_noise(6 + 2 * math.sin(self.timestamp / 180), 0.04),
            'transmission_gear': random.choice([1, 2, 3, 4]),
        }
    
    def generate_vehicle_state(self) -> Dict[str, Any]:
        """生成车辆状态数据"""
        base_speed = 8 + 4 * abs(math.sin(self.timestamp / 150))
        
        return {
            'vehicle_speed': self._add_noise(base_speed, 0.05),
            'wheel_speed_fl': self._add_noise(base_speed * 1.02, 0.03),
            'wheel_speed_fr': self._add_noise(base_speed * 1.01, 0.03),
            'wheel_speed_rl': self._add_noise(base_speed * 0.99, 0.03),
            'wheel_speed_rr': self._add_noise(base_speed * 0.98, 0.03),
            'steering_angle': self._add_noise(15 * math.sin(self.timestamp / 200), 0.05),
            'brake_pressure': self._add_noise(2 + 3 * abs(math.sin(self.timestamp / 180)), 0.05),
        }
    
    def generate_gnss_data(self) -> Dict[str, Any]:
        """生成GNSS定位数据"""
        base_lat = 39.9042 + 0.001 * math.sin(self.timestamp / 500)
        base_lon = 116.4074 + 0.001 * math.cos(self.timestamp / 500)
        
        return {
            'gnss_latitude': self._add_noise(base_lat, 0.00001),
            'gnss_longitude': self._add_noise(base_lon, 0.00001),
            'gnss_altitude': self._add_noise(50, 0.01),
            'gnss_speed': self._add_noise(8, 0.05),
            'gnss_heading': self._add_noise(90 + 45 * math.sin(self.timestamp / 300), 0.02),
            'gnss_satellite_count': random.randint(12, 20),
            'gnss_hdop': self._add_noise(0.8, 0.1),
            'gnss_fix_quality': random.choice(['fixed', 'float']),
        }
    
    def update_state(self, delta_time: float = 1.0):
        """更新模拟器状态"""
        self.timestamp += delta_time
        self.operation_hours += delta_time / 3600
        
        if random.random() < 0.0001:
            self.battery_cycles += 1
    
    def generate_complete_data_packet(self) -> Dict[str, Any]:
        """生成完整的数据包"""
        self.message_count += 1
        
        data = {
            'vehicle_id': self.vehicle_id,
            'timestamp': datetime.now().isoformat(),
            'operation_hours': round(self.operation_hours, 2),
        }
        
        # 合并所有子系统数据到顶层
        data.update(self.generate_engine_data())
        data.update(self.generate_fuel_data())
        data.update(self.generate_battery_data())
        data.update(self.generate_hydraulic_data())
        data.update(self.generate_transmission_data())
        data.update(self.generate_vehicle_state())
        data.update(self.generate_gnss_data())
        
        return data
    
    def print_status(self, data: Dict[str, Any]):
        """打印当前状态"""
        elapsed = time.time() - self.scenario_start_time
        timestamp = datetime.now().strftime("%H:%M:%S")
        
        # 提取关键指标
        temp = data.get('engine_coolant_temp', 0)
        oil = data.get('engine_oil_pressure', 0)
        fuel = data.get('fuel_level', 0)
        batt = data.get('battery_soc', 0)
        speed = data.get('vehicle_speed', 0)
        
        print(f"[{timestamp}] 📤 #{self.message_count:04d} | "
              f"Temp={temp:.1f}°C | Oil={oil:.1f}bar | Fuel={fuel:.1f}% | "
              f"Batt={batt:.1f}% | Speed={speed:.1f}km/h | "
              f"Elapsed={int(elapsed)}s")


def run_normal_mode(vehicle_id: str, mqtt_broker: str, mqtt_port: int, interval: float):
    """运行正常模式"""
    simulator = TractorDataSimulatorWithAlerts(vehicle_id, "normal")
    
    if MQTT_AVAILABLE:
        client = mqtt.Client()
        client.connect(mqtt_broker, mqtt_port, 60)
        print(f"✅ 已连接到MQTT代理: {mqtt_broker}:{mqtt_port}")
    else:
        client = None
        print("⚠️  MQTT不可用，仅输出到控制台")
    
    print("\n开始发送数据...\n")
    
    try:
        while True:
            data = simulator.generate_complete_data_packet()
            simulator.print_status(data)
            
            if client:
                topic = f"tractor/telemetry"
                client.publish(topic, json.dumps(data))
            
            simulator.update_state(interval)
            time.sleep(interval)
            
    except KeyboardInterrupt:
        print("\n\n⚠️  用户中断")
        if client:
            client.disconnect()


def run_scenario_mode(vehicle_id: str, mqtt_broker: str, mqtt_port: int, 
                      interval: float, scenario: str):
    """运行特定场景模式"""
    simulator = TractorDataSimulatorWithAlerts(vehicle_id, scenario)
    
    if MQTT_AVAILABLE:
        client = mqtt.Client()
        client.connect(mqtt_broker, mqtt_port, 60)
        print(f"✅ 已连接到MQTT代理: {mqtt_broker}:{mqtt_port}")
    else:
        client = None
        print("⚠️  MQTT不可用，仅输出到控制台")
    
    duration = simulator.scenario_config.get("duration")
    if duration:
        print(f"\n场景将运行 {duration} 秒\n")
    
    print("开始发送数据...\n")
    
    start_time = time.time()
    
    try:
        while True:
            data = simulator.generate_complete_data_packet()
            simulator.print_status(data)
            
            if client:
                topic = f"tractor/telemetry"
                client.publish(topic, json.dumps(data))
            
            simulator.update_state(interval)
            time.sleep(interval)
            
            # 检查是否达到场景持续时间
            if duration and (time.time() - start_time) >= duration:
                print(f"\n✅ 场景完成 ({duration}秒)")
                break
                
    except KeyboardInterrupt:
        print("\n\n⚠️  用户中断")
    finally:
        if client:
            client.disconnect()


def main():
    parser = argparse.ArgumentParser(description="T-BOX数据模拟器 - 支持告警测试场景")
    parser.add_argument("--vehicle-id", default="TRACTOR_001", help="车辆ID")
    parser.add_argument("--mqtt-broker", default="localhost", help="MQTT代理地址")
    parser.add_argument("--mqtt-port", type=int, default=1883, help="MQTT代理端口")
    parser.add_argument("--interval", type=float, default=10.0, help="发送间隔(秒)")
    parser.add_argument("--scenario", default="normal", 
                       choices=["normal", "engine_overheating", "low_fuel", 
                               "low_oil_pressure", "battery_low", "battery_critical",
                               "hydraulic_failure", "transmission_overheat", 
                               "multiple_faults", "auto_test"],
                       help="测试场景")
    
    args = parser.parse_args()
    
    if args.scenario == "auto_test":
        print("自动化测试模式尚未实现")
        print("请使用 tbox_simulator_auto_alert_test.py")
        return
    
    if args.scenario == "normal":
        run_normal_mode(args.vehicle_id, args.mqtt_broker, args.mqtt_port, args.interval)
    else:
        run_scenario_mode(args.vehicle_id, args.mqtt_broker, args.mqtt_port, 
                         args.interval, args.scenario)


if __name__ == "__main__":
    main()
