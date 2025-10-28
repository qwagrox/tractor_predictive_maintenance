#!/usr/bin/env python3
"""
T-BOX数据模拟器 - 油电混动无人拖拉机预测性维护系统
模拟生成车辆CAN总线数据、智驾系统数据、传感器健康度数据和故障日志
通过MQTT协议上传到云端VictoriaMetrics
"""

import json
import time
import random
import math
from datetime import datetime
from typing import Dict, List, Any
import numpy as np


class TractorDataSimulator:
    """拖拉机数据模拟器"""
    
    def __init__(self, vehicle_id: str):
        self.vehicle_id = vehicle_id
        self.timestamp = time.time()
        self.operation_hours = 0  # 累计运行小时数
        self.battery_cycles = 0  # 电池充放电循环次数
        
        # 故障模式标志
        self.fault_modes = {
            'engine_degradation': False,  # 发动机性能退化
            'battery_aging': False,  # 电池老化
            'sensor_drift': False,  # 传感器漂移
            'hydraulic_leak': False,  # 液压系统泄漏
        }
        
    def _add_noise(self, value: float, noise_level: float = 0.02) -> float:
        """添加高斯噪声"""
        return value * (1 + np.random.normal(0, noise_level))
    
    def _add_fault_effect(self, value: float, fault_type: str, severity: float = 0.1) -> float:
        """根据故障类型添加异常效应"""
        if not self.fault_modes.get(fault_type, False):
            return value
        
        if fault_type == 'engine_degradation':
            # 发动机退化导致效率下降、温度升高
            return value * (1 + severity * np.random.uniform(0.5, 1.5))
        elif fault_type == 'battery_aging':
            # 电池老化导致容量下降、内阻增加
            return value * (1 - severity * np.random.uniform(0.3, 0.8))
        elif fault_type == 'sensor_drift':
            # 传感器漂移导致读数偏移
            return value + severity * np.random.uniform(-10, 10)
        elif fault_type == 'hydraulic_leak':
            # 液压泄漏导致压力下降
            return value * (1 - severity * np.random.uniform(0.2, 0.6))
        
        return value
    
    def generate_engine_data(self) -> Dict[str, Any]:
        """生成发动机数据"""
        # 基础值
        base_rpm = 1800 + 400 * math.sin(self.timestamp / 100)  # 1400-2200 rpm
        base_torque = 350 + 50 * math.sin(self.timestamp / 80)  # 300-400 Nm
        base_temp = 85 + 10 * math.sin(self.timestamp / 200)  # 75-95°C
        base_fuel_rate = 15 + 5 * abs(math.sin(self.timestamp / 150))  # 10-20 L/h
        
        # 添加故障效应
        temp = self._add_fault_effect(base_temp, 'engine_degradation', 0.15)
        fuel_rate = self._add_fault_effect(base_fuel_rate, 'engine_degradation', 0.2)
        
        return {
            'rpm': self._add_noise(base_rpm, 0.03),
            'torque': self._add_noise(base_torque, 0.05),
            'coolant_temp': self._add_noise(temp, 0.02),
            'oil_pressure': self._add_noise(4.5 + 0.5 * math.sin(self.timestamp / 120), 0.03),  # 4-5 bar
            'fuel_consumption_rate': self._add_noise(fuel_rate, 0.04),
            'intake_air_temp': self._add_noise(30 + 15 * math.sin(self.timestamp / 300), 0.03),
        }
    
    def generate_battery_data(self) -> Dict[str, Any]:
        """生成电池系统数据"""
        # 电池SOC随时间缓慢变化
        base_soc = 50 + 30 * math.sin(self.timestamp / 500)  # 20-80%
        soc = self._add_fault_effect(base_soc, 'battery_aging', 0.1)
        
        # 电池SOH随循环次数退化
        base_soh = 100 - (self.battery_cycles / 5000) * 20  # 每5000次循环退化20%
        soh = max(80, self._add_noise(base_soh, 0.01))
        
        # 电流和功率
        base_current = 50 + 30 * math.sin(self.timestamp / 100)  # -20A到80A (充放电)
        voltage = 600 + 50 * (soc / 100)  # 600-650V
        
        return {
            'soc': max(0, min(100, soc)),
            'soh': soh,
            'voltage': self._add_noise(voltage, 0.01),
            'current': self._add_noise(base_current, 0.05),
            'power': self._add_noise(voltage * base_current / 1000, 0.05),  # kW
            'temp_max': self._add_noise(35 + 10 * abs(base_current) / 80, 0.03),
            'temp_min': self._add_noise(30 + 8 * abs(base_current) / 80, 0.03),
            'cell_voltage_max': self._add_noise(3.7, 0.005),
            'cell_voltage_min': self._add_noise(3.6, 0.005),
        }
    
    def generate_vehicle_state(self) -> Dict[str, Any]:
        """生成车辆状态数据"""
        # 车速变化
        base_speed = 8 + 4 * abs(math.sin(self.timestamp / 150))  # 4-12 km/h
        
        return {
            'speed': self._add_noise(base_speed, 0.05),
            'acceleration': self._add_noise(0.1 * math.cos(self.timestamp / 150), 0.1),
            'steering_angle': self._add_noise(15 * math.sin(self.timestamp / 200), 0.05),
            'wheel_speed_fl': self._add_noise(base_speed * 1.02, 0.03),
            'wheel_speed_fr': self._add_noise(base_speed * 1.01, 0.03),
            'wheel_speed_rl': self._add_noise(base_speed * 0.99, 0.03),
            'wheel_speed_rr': self._add_noise(base_speed * 0.98, 0.03),
            'brake_pressure': self._add_noise(2 + 3 * abs(math.sin(self.timestamp / 180)), 0.05),
        }
    
    def generate_transmission_data(self) -> Dict[str, Any]:
        """生成变速箱数据"""
        return {
            'gear': random.choice([1, 2, 3, 4]),
            'oil_temp': self._add_noise(70 + 15 * math.sin(self.timestamp / 250), 0.03),
            'oil_pressure': self._add_noise(6 + 2 * math.sin(self.timestamp / 180), 0.04),
            'clutch_status': random.choice([0, 1]),  # 0=分离, 1=结合
        }
    
    def generate_hydraulic_data(self) -> Dict[str, Any]:
        """生成液压系统数据"""
        base_pressure = 180 + 20 * math.sin(self.timestamp / 120)  # 160-200 bar
        pressure = self._add_fault_effect(base_pressure, 'hydraulic_leak', 0.3)
        
        return {
            'pressure': self._add_noise(pressure, 0.04),
            'oil_temp': self._add_noise(55 + 15 * math.sin(self.timestamp / 300), 0.03),
            'flow_rate': self._add_noise(40 + 10 * abs(math.sin(self.timestamp / 150)), 0.05),
            'implement_position': self._add_noise(50 + 30 * math.sin(self.timestamp / 200), 0.02),
        }
    
    def generate_gnss_data(self) -> Dict[str, Any]:
        """生成GNSS/INS定位数据"""
        # 模拟在农田中作业的轨迹
        base_lat = 39.9042 + 0.001 * math.sin(self.timestamp / 500)
        base_lon = 116.4074 + 0.001 * math.cos(self.timestamp / 500)
        
        return {
            'latitude': self._add_noise(base_lat, 0.00001),
            'longitude': self._add_noise(base_lon, 0.00001),
            'altitude': self._add_noise(50, 0.01),
            'heading': self._add_noise(90 + 45 * math.sin(self.timestamp / 300), 0.02),
            'positioning_accuracy': self._add_noise(0.015, 0.1),  # 1.5cm ± 10%
            'satellite_count': random.randint(12, 20),
            'rtk_status': random.choice(['fixed', 'float', 'single']),
        }
    
    def generate_sensor_health(self) -> Dict[str, Any]:
        """生成传感器健康度数据"""
        base_quality = 95
        if self.fault_modes['sensor_drift']:
            base_quality = 70 + 10 * random.random()
        
        return {
            'lidar_health': {
                'data_rate': self._add_noise(200000, 0.02),  # 点/秒
                'temperature': self._add_noise(45, 0.05),
                'voltage': self._add_noise(12, 0.01),
                'quality_score': self._add_noise(base_quality, 0.03),
            },
            'camera_health': {
                'frame_rate': self._add_noise(30, 0.01),
                'temperature': self._add_noise(50, 0.05),
                'quality_score': self._add_noise(base_quality, 0.03),
            },
            'imu_health': {
                'drift_rate': self._add_noise(0.01, 0.1),  # deg/h
                'temperature': self._add_noise(40, 0.03),
                'quality_score': self._add_noise(base_quality, 0.03),
            },
        }
    
    def generate_intelligent_driving_data(self) -> Dict[str, Any]:
        """生成智驾系统数据"""
        return {
            'perception': {
                'obstacle_count': random.randint(0, 5),
                'drivable_area_confidence': self._add_noise(0.95, 0.02),
                'processing_time_ms': self._add_noise(50, 0.1),
            },
            'planning': {
                'trajectory_quality': self._add_noise(0.92, 0.03),
                'planning_time_ms': self._add_noise(30, 0.1),
            },
            'control': {
                'lateral_error': self._add_noise(0.03, 0.2),  # 3cm
                'longitudinal_error': self._add_noise(0.05, 0.2),  # 5cm
                'control_mode': random.choice(['auto', 'manual', 'remote']),
            },
            'computing': {
                'cpu_usage': self._add_noise(60, 0.1),  # %
                'gpu_usage': self._add_noise(70, 0.1),  # %
                'memory_usage': self._add_noise(65, 0.1),  # %
                'temperature': self._add_noise(65, 0.05),  # °C
            },
        }
    
    def generate_fault_log(self) -> List[Dict[str, Any]]:
        """生成故障日志（事件驱动）"""
        logs = []
        
        # 随机生成故障事件
        if random.random() < 0.001:  # 0.1%概率
            fault_codes = [
                {'code': 'P0101', 'description': 'MAF传感器范围/性能问题', 'severity': 'warning'},
                {'code': 'P0420', 'description': '催化转换器效率低', 'severity': 'warning'},
                {'code': 'B1001', 'description': '电池SOC过低', 'severity': 'critical'},
                {'code': 'C0035', 'description': '左前轮速传感器故障', 'severity': 'error'},
                {'code': 'U0100', 'description': 'CAN通信丢失', 'severity': 'critical'},
            ]
            
            fault = random.choice(fault_codes)
            logs.append({
                'timestamp': datetime.now().isoformat(),
                'fault_code': fault['code'],
                'description': fault['description'],
                'severity': fault['severity'],
                'vehicle_id': self.vehicle_id,
            })
        
        return logs
    
    def update_state(self, delta_time: float = 1.0):
        """更新模拟器状态"""
        self.timestamp += delta_time
        self.operation_hours += delta_time / 3600
        
        # 模拟电池充放电循环
        if random.random() < 0.0001:  # 平均10000秒一次循环
            self.battery_cycles += 1
        
        # 随机触发故障模式
        if self.operation_hours > 100 and random.random() < 0.00001:
            self.fault_modes['engine_degradation'] = True
        
        if self.battery_cycles > 500 and random.random() < 0.00001:
            self.fault_modes['battery_aging'] = True
        
        if self.operation_hours > 200 and random.random() < 0.00001:
            self.fault_modes['sensor_drift'] = True
    
    def generate_complete_data_packet(self) -> Dict[str, Any]:
        """生成完整的数据包"""
        return {
            'vehicle_id': self.vehicle_id,
            'timestamp': datetime.now().isoformat(),
            'operation_hours': round(self.operation_hours, 2),
            'engine': self.generate_engine_data(),
            'battery': self.generate_battery_data(),
            'vehicle_state': self.generate_vehicle_state(),
            'transmission': self.generate_transmission_data(),
            'hydraulic': self.generate_hydraulic_data(),
            'gnss': self.generate_gnss_data(),
            'sensor_health': self.generate_sensor_health(),
            'intelligent_driving': self.generate_intelligent_driving_data(),
            'fault_logs': self.generate_fault_log(),
            'fault_modes_active': {k: v for k, v in self.fault_modes.items() if v},
        }


def simulate_tbox_data_stream(vehicle_id: str, duration_seconds: int = 60, sample_rate: float = 1.0):
    """
    模拟T-BOX数据流
    
    Args:
        vehicle_id: 车辆ID
        duration_seconds: 模拟持续时间（秒）
        sample_rate: 采样率（Hz）
    """
    simulator = TractorDataSimulator(vehicle_id)
    
    print(f"开始模拟车辆 {vehicle_id} 的T-BOX数据流...")
    print(f"持续时间: {duration_seconds}秒, 采样率: {sample_rate}Hz")
    print("-" * 80)
    
    start_time = time.time()
    sample_count = 0
    
    while time.time() - start_time < duration_seconds:
        # 生成数据包
        data_packet = simulator.generate_complete_data_packet()
        
        # 输出到控制台（实际应用中应通过MQTT发送）
        print(f"\n[样本 #{sample_count + 1}] 时间: {data_packet['timestamp']}")
        print(f"运行时长: {data_packet['operation_hours']:.2f}小时")
        print(f"发动机: RPM={data_packet['engine']['rpm']:.0f}, 温度={data_packet['engine']['coolant_temp']:.1f}°C")
        print(f"电池: SOC={data_packet['battery']['soc']:.1f}%, SOH={data_packet['battery']['soh']:.1f}%")
        print(f"车速: {data_packet['vehicle_state']['speed']:.1f} km/h")
        print(f"定位: ({data_packet['gnss']['latitude']:.6f}, {data_packet['gnss']['longitude']:.6f}), 精度={data_packet['gnss']['positioning_accuracy']:.3f}m")
        
        if data_packet['fault_logs']:
            print(f"⚠️  故障日志: {data_packet['fault_logs']}")
        
        if data_packet['fault_modes_active']:
            print(f"⚠️  激活的故障模式: {list(data_packet['fault_modes_active'].keys())}")
        
        # 更新状态
        simulator.update_state(1.0 / sample_rate)
        sample_count += 1
        
        # 控制采样率
        time.sleep(1.0 / sample_rate)
    
    print("\n" + "=" * 80)
    print(f"模拟完成! 共生成 {sample_count} 个数据样本")
    print(f"累计运行时长: {simulator.operation_hours:.2f}小时")
    print(f"电池循环次数: {simulator.battery_cycles}")


if __name__ == '__main__':
    # 模拟单台车辆的数据流，持续60秒，采样率1Hz
    simulate_tbox_data_stream(vehicle_id='TRACTOR_001', duration_seconds=60, sample_rate=1.0)
