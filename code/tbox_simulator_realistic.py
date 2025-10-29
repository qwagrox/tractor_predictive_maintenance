#!/usr/bin/env python3
"""
T-BOX数据模拟器 - 真实工况版本
生成更真实的拖拉机工作数据，包含突变、尖峰、平台期等特征
"""

import json
import time
import random
import math
from datetime import datetime
from typing import Dict, List, Any
from enum import Enum
import numpy as np

try:
    import paho.mqtt.client as mqtt
    MQTT_AVAILABLE = True
except ImportError:
    MQTT_AVAILABLE = False
    print("警告: paho-mqtt库未安装，将只输出到控制台")
    print("安装命令: pip install paho-mqtt")


class TractorState(Enum):
    """拖拉机工作状态"""
    STOPPED = 0      # 停止
    STARTING = 1     # 启动
    IDLE = 2         # 怠速
    ACCELERATING = 3 # 加速
    WORKING = 4      # 作业
    HEAVY_LOAD = 5   # 重载
    DECELERATING = 6 # 减速


class RealisticTractorSimulator:
    """真实工况拖拉机数据模拟器"""
    
    def __init__(self, vehicle_id: str):
        self.vehicle_id = vehicle_id
        self.timestamp = time.time()
        self.operation_hours = 0
        self.battery_cycles = 0
        
        # 状态机
        self.current_state = TractorState.STOPPED
        self.state_start_time = time.time()
        self.state_duration = 0
        
        # 当前值（用于平滑过渡）
        self.current_values = {
            'vehicle_speed': 0.0,
            'engine_rpm': 0.0,
            'engine_torque': 0.0,
            'battery_voltage': 24.5,
            'fuel_consumption_rate': 0.0,
        }
        
        # 故障模式
        self.fault_modes = {
            'engine_degradation': False,
            'battery_aging': False,
            'sensor_drift': False,
            'hydraulic_leak': False,
        }
        
        # 随机触发重载事件
        self.heavy_load_event = False
        self.heavy_load_start = 0
        
    def _update_state(self):
        """更新工作状态"""
        current_time = time.time()
        time_in_state = current_time - self.state_start_time
        
        # 检查是否需要切换状态
        if time_in_state >= self.state_duration:
            self._transition_to_next_state()
    
    def _transition_to_next_state(self):
        """状态转换"""
        current_time = time.time()
        
        # 定义状态转换规则和持续时间
        transitions = {
            TractorState.STOPPED: (TractorState.STARTING, random.uniform(2, 3)),
            TractorState.STARTING: (TractorState.IDLE, random.uniform(5, 10)),
            TractorState.IDLE: (TractorState.ACCELERATING, random.uniform(3, 5)),
            TractorState.ACCELERATING: (TractorState.WORKING, random.uniform(30, 60)),
            TractorState.WORKING: (TractorState.DECELERATING, random.uniform(2, 4)),
            TractorState.DECELERATING: (TractorState.IDLE, random.uniform(5, 10)),
        }
        
        # 特殊处理：从IDLE可能回到STOPPED或继续工作
        if self.current_state == TractorState.IDLE:
            if random.random() < 0.3:  # 30%概率停止
                self.current_state = TractorState.STOPPED
                self.state_duration = random.uniform(10, 30)
            else:  # 70%概率继续工作
                self.current_state = TractorState.ACCELERATING
                self.state_duration = random.uniform(3, 5)
        elif self.current_state in transitions:
            self.current_state, self.state_duration = transitions[self.current_state]
        else:
            # 默认回到STOPPED
            self.current_state = TractorState.STOPPED
            self.state_duration = random.uniform(10, 30)
        
        self.state_start_time = current_time
        
        # 随机触发重载事件（在WORKING状态时）
        if self.current_state == TractorState.WORKING and random.random() < 0.3:
            self.heavy_load_event = True
            self.heavy_load_start = current_time
    
    def _get_target_values(self) -> Dict[str, float]:
        """根据当前状态获取目标值"""
        state_params = {
            TractorState.STOPPED: {
                'vehicle_speed': 0.0,
                'engine_rpm': 0.0,
                'engine_torque': 0.0,
                'battery_voltage': 24.5,
                'fuel_consumption_rate': 0.0,
            },
            TractorState.STARTING: {
                'vehicle_speed': 0.0,
                'engine_rpm': random.uniform(800, 900),
                'engine_torque': random.uniform(70, 90),
                'battery_voltage': random.uniform(22.0, 23.0),  # 启动时电压下降
                'fuel_consumption_rate': random.uniform(2.0, 3.0),
            },
            TractorState.IDLE: {
                'vehicle_speed': 0.0,
                'engine_rpm': random.uniform(800, 900),
                'engine_torque': random.uniform(70, 90),
                'battery_voltage': random.uniform(24.0, 25.0),
                'fuel_consumption_rate': random.uniform(2.0, 3.0),
            },
            TractorState.ACCELERATING: {
                'vehicle_speed': random.uniform(6.0, 10.0),
                'engine_rpm': random.uniform(1400, 1600),
                'engine_torque': random.uniform(250, 320),
                'battery_voltage': random.uniform(24.0, 25.0),
                'fuel_consumption_rate': random.uniform(6.0, 9.0),
            },
            TractorState.WORKING: {
                'vehicle_speed': random.uniform(4.0, 8.0),
                'engine_rpm': random.uniform(1400, 1700),
                'engine_torque': random.uniform(280, 350),
                'battery_voltage': random.uniform(24.0, 25.5),
                'fuel_consumption_rate': random.uniform(8.0, 11.0),
            },
            TractorState.HEAVY_LOAD: {
                'vehicle_speed': random.uniform(2.0, 5.0),
                'engine_rpm': random.uniform(1800, 2200),
                'engine_torque': random.uniform(400, 500),
                'battery_voltage': random.uniform(23.0, 24.0),
                'fuel_consumption_rate': random.uniform(12.0, 16.0),
            },
            TractorState.DECELERATING: {
                'vehicle_speed': random.uniform(1.0, 3.0),
                'engine_rpm': random.uniform(1000, 1200),
                'engine_torque': random.uniform(150, 200),
                'battery_voltage': random.uniform(24.5, 25.5),
                'fuel_consumption_rate': random.uniform(4.0, 6.0),
            },
        }
        
        # 检查是否在重载事件中
        current_time = time.time()
        if self.heavy_load_event:
            if current_time - self.heavy_load_start < random.uniform(5, 15):
                return state_params[TractorState.HEAVY_LOAD]
            else:
                self.heavy_load_event = False
        
        return state_params.get(self.current_state, state_params[TractorState.STOPPED])
    
    def _smooth_transition(self, current: float, target: float, alpha: float = 0.3) -> float:
        """平滑过渡"""
        return current * (1 - alpha) + target * alpha
    
    def _add_noise(self, value: float, noise_std: float) -> float:
        """添加高斯噪声"""
        return value + random.gauss(0, noise_std)
    
    def _add_spike(self, value: float, spike_prob: float = 0.05, spike_range: float = 0.1) -> float:
        """随机添加尖峰"""
        if random.random() < spike_prob:
            return value * (1 + random.uniform(-spike_range, spike_range))
        return value
    
    def generate_vehicle_data(self) -> Dict[str, Any]:
        """生成车辆基础数据"""
        # 更新状态
        self._update_state()
        
        # 获取目标值
        targets = self._get_target_values()
        
        # 平滑过渡到目标值
        for key in self.current_values:
            if key in targets:
                self.current_values[key] = self._smooth_transition(
                    self.current_values[key],
                    targets[key],
                    alpha=0.2 if self.current_state in [TractorState.ACCELERATING, TractorState.DECELERATING] else 0.1
                )
        
        # 添加噪声和尖峰
        vehicle_speed = self._add_noise(self.current_values['vehicle_speed'], 0.3)
        vehicle_speed = self._add_spike(vehicle_speed, 0.05, 0.1)
        vehicle_speed = max(0, vehicle_speed)
        
        return {
            'vehicle_speed': round(vehicle_speed, 2),
            'odometer': round(self.operation_hours * 8.5, 1),  # 假设平均速度8.5km/h
            'operation_hours': round(self.operation_hours, 1),
            'heading': round(random.uniform(0, 360), 1),
        }
    
    def generate_engine_data(self) -> Dict[str, Any]:
        """生成发动机数据"""
        # 使用当前值并添加噪声
        rpm = self._add_noise(self.current_values['engine_rpm'], 30)
        rpm = self._add_spike(rpm, 0.08, 0.05)
        rpm = max(0, rpm)
        
        torque = self._add_noise(self.current_values['engine_torque'], 15)
        torque = self._add_spike(torque, 0.1, 0.08)
        torque = max(0, torque)
        
        # 温度基于负载缓慢变化
        base_temp = 85 + (self.current_values['engine_rpm'] / 2200) * 15
        coolant_temp = self._add_noise(base_temp, 1.5)
        
        fuel_rate = self._add_noise(self.current_values['fuel_consumption_rate'], 0.5)
        fuel_rate = max(0, fuel_rate)
        
        # 燃油液位（根据运行时间缓慢下降）
        fuel_level = max(10, 100 - (self.operation_hours / 10) * 5)  # 每10小时下降5%
        fuel_level = self._add_noise(fuel_level, 1.0)
        
        return {
            'rpm': round(rpm, 0),
            'torque': round(torque, 1),
            'coolant_temp': round(coolant_temp, 1),
            'oil_pressure': round(self._add_noise(4.5, 0.15), 2),
            'fuel_consumption_rate': round(fuel_rate, 2),
            'fuel_level': round(fuel_level, 1),
            'intake_air_temp': round(self._add_noise(35, 2), 1),
        }
    
    def generate_battery_data(self) -> Dict[str, Any]:
        """生成电池系统数据"""
        # 使用当前电压值并添加噪声
        voltage = self._add_noise(self.current_values['battery_voltage'], 0.15)
        
        # SOC基于电压估算
        soc = 50 + (voltage - 24.5) * 20
        soc = max(20, min(90, soc))
        
        # 电流基于负载
        load_factor = self.current_values['engine_rpm'] / 2200
        current = self._add_noise(30 + load_factor * 40, 5)
        
        return {
            'voltage': round(voltage, 2),
            'current': round(current, 1),
            'soc': round(soc, 1),
            'soh': round(self._add_noise(95, 0.5), 1),
            'temperature': round(self._add_noise(28 + load_factor * 7, 1), 1),
            'charge_cycles': self.battery_cycles,
        }
    
    def generate_hydraulic_data(self) -> Dict[str, Any]:
        """生成液压系统数据"""
        # 液压压力基于负载
        load_factor = self.current_values['engine_torque'] / 500
        base_pressure = 150 + load_factor * 50
        pressure = self._add_noise(base_pressure, 5)
        pressure = self._add_spike(pressure, 0.1, 0.1)
        
        return {
            'system_pressure': round(pressure, 1),
            'oil_temperature': round(self._add_noise(55 + load_factor * 15, 2), 1),
            'flow_rate': round(self._add_noise(40 + load_factor * 20, 2), 1),
            'filter_pressure_drop': round(self._add_noise(0.5, 0.05), 2),
        }
    
    def generate_gnss_data(self) -> Dict[str, Any]:
        """生成GNSS定位数据"""
        return {
            'latitude': round(39.9042 + random.uniform(-0.001, 0.001), 6),
            'longitude': round(116.4074 + random.uniform(-0.001, 0.001), 6),
            'altitude': round(50 + random.uniform(-2, 2), 1),
            'heading': round(random.uniform(0, 360), 1),
            'satellite_count': random.randint(10, 15),
            'positioning_accuracy': round(random.uniform(0.01, 0.05), 3),
        }
    
    def generate_autonomous_data(self) -> Dict[str, Any]:
        """生成自动驾驶数据"""
        # 自动驾驶模式基于状态
        auto_mode = self.current_state in [TractorState.WORKING, TractorState.ACCELERATING]
        
        return {
            'auto_mode_enabled': auto_mode,
            'steering_angle': round(self._add_noise(0, 5), 1) if auto_mode else 0,
            'path_deviation': round(abs(self._add_noise(0, 0.15)), 2) if auto_mode else 0,
            'obstacle_distance': round(self._add_noise(10, 2), 1),
            'gnss_rtk_status': random.choice([4, 5]),  # 4=RTK Fixed, 5=RTK Float
            'imu_pitch': round(self._add_noise(0, 2), 1),
            'imu_roll': round(self._add_noise(0, 1.5), 1),
        }
    
    def generate_sensor_health(self) -> Dict[str, Any]:
        """生成传感器健康度数据"""
        base_health = 95
        
        return {
            'gps_signal_quality': round(self._add_noise(base_health, 2), 1),
            'can_bus_error_rate': round(abs(self._add_noise(0.1, 0.05)), 3),
            'imu_calibration_status': round(self._add_noise(base_health, 1), 1),
            'camera_visibility': round(self._add_noise(90, 5), 1),
            'lidar_point_density': round(self._add_noise(85, 3), 1),
        }
    
    def generate_fault_codes(self) -> List[str]:
        """生成故障码"""
        fault_codes = []
        
        # 基于状态和随机事件生成故障码
        if self.current_state == TractorState.HEAVY_LOAD and random.random() < 0.1:
            fault_codes.append("P0234:涡轮增压器过压")
        
        if self.current_values['battery_voltage'] < 23.0:
            fault_codes.append("U0100:电池电压过低")
        
        if self.current_values['engine_rpm'] > 2100 and random.random() < 0.05:
            fault_codes.append("P0217:发动机过热")
        
        return fault_codes
    
    def generate_complete_data(self) -> Dict[str, Any]:
        """生成完整的T-BOX数据"""
        self.timestamp = time.time()
        self.operation_hours += 1 / 3600  # 每秒增加
        
        data = {
            'vehicle_id': self.vehicle_id,
            'timestamp': datetime.now().isoformat(),
            'unix_timestamp': self.timestamp,
            'state': self.current_state.name,  # 添加状态信息
            
            # 各子系统数据
            'vehicle': self.generate_vehicle_data(),
            'engine': self.generate_engine_data(),
            'battery': self.generate_battery_data(),
            'hydraulic': self.generate_hydraulic_data(),
            'gnss': self.generate_gnss_data(),
            'autonomous': self.generate_autonomous_data(),
            'sensor_health': self.generate_sensor_health(),
            'fault_codes': self.generate_fault_codes(),
        }
        
        return data


def main():
    """主函数"""
    print("="*60)
    print("T-BOX数据模拟器 - 真实工况版本")
    print("="*60)
    print()
    
    # 配置
    MQTT_BROKER = "localhost"
    MQTT_PORT = 1883
    MQTT_TOPIC_PREFIX = "tractor"
    VEHICLE_IDS = ["TRACTOR_001", "TRACTOR_002", "TRACTOR_003"]
    PUBLISH_INTERVAL = 1  # 秒
    
    # 创建模拟器实例
    simulators = {vid: RealisticTractorSimulator(vid) for vid in VEHICLE_IDS}
    
    # 连接MQTT
    mqtt_client = None
    if MQTT_AVAILABLE:
        try:
            mqtt_client = mqtt.Client()
            mqtt_client.connect(MQTT_BROKER, MQTT_PORT, 60)
            mqtt_client.loop_start()
            print(f"[成功] 连接到MQTT Broker: {MQTT_BROKER}:{MQTT_PORT}")
        except Exception as e:
            print(f"[警告] 无法连接到MQTT Broker: {e}")
            print("[信息] 将只输出到控制台")
            mqtt_client = None
    
    print(f"[信息] 模拟 {len(VEHICLE_IDS)} 辆拖拉机")
    print(f"[信息] 发布间隔: {PUBLISH_INTERVAL}秒")
    print(f"[信息] MQTT主题: {MQTT_TOPIC_PREFIX}/{{vehicle_id}}/data")
    print()
    print("开始生成数据... (按Ctrl+C停止)")
    print("="*60)
    print()
    
    try:
        while True:
            for vehicle_id, simulator in simulators.items():
                # 生成数据
                data = simulator.generate_complete_data()
                
                # 发布到MQTT
                if mqtt_client:
                    topic = f"{MQTT_TOPIC_PREFIX}/{vehicle_id}/data"
                    payload = json.dumps(data, ensure_ascii=False)
                    mqtt_client.publish(topic, payload)
                
                # 控制台输出（简化版）
                print(f"[{datetime.now().strftime('%H:%M:%S')}] {vehicle_id} | "
                      f"状态:{data['state']:12s} | "
                      f"速度:{data['vehicle']['vehicle_speed']:5.1f}km/h | "
                      f"转速:{data['engine']['rpm']:4.0f}rpm | "
                      f"扭矩:{data['engine']['torque']:5.1f}Nm | "
                      f"电压:{data['battery']['voltage']:4.1f}V")
            
            time.sleep(PUBLISH_INTERVAL)
            
    except KeyboardInterrupt:
        print("\n\n[信息] 停止数据生成")
        if mqtt_client:
            mqtt_client.loop_stop()
            mqtt_client.disconnect()
        print("[信息] 已断开MQTT连接")


if __name__ == "__main__":
    main()
