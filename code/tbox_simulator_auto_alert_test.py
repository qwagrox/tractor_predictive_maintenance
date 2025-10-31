#!/usr/bin/env python3
"""
Automated Alert Testing T-BOX Simulator
自动化告警测试 - T-BOX模拟器

Features:
- Continuously sends complete telemetry data (60+ metrics)
- Automatically injects anomalies to trigger alerts
- Tests all alert rules sequentially
- Real-time progress display
"""

import json
import time
import random
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
# Complete Tractor Simulator with Auto Alert Testing
# ============================================================================

class AutoAlertTractorSimulator:
    """T-BOX simulator with automated alert testing"""
    
    def __init__(self):
        self.client = mqtt.Client()
        self.client.on_connect = self.on_connect
        self.running_time = 0
        self.total_distance = 0
        self.total_fuel_consumed = 0
        self.message_count = 0
        
        # Complete normal parameters (60+ metrics)
        self.normal_params = {
            # Engine (发动机)
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
            
            # Fuel (燃油)
            "fuel_level": 75.0,
            "fuel_pressure": 3.5,
            "fuel_temp": 25.0,
            
            # Battery (电池)
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
            "battery_remaining_capacity": 180.0,
            "battery_full_capacity": 200.0,
            
            # Motor (电机)
            "motor_speed": 1200,
            "motor_torque": 450.0,
            "motor_power": 55.0,
            "motor_temp": 65.0,
            "motor_controller_temp": 55.0,
            "hybrid_mode": "hybrid",
            "energy_recovery_power": 8.5,
            
            # Hydraulic (液压)
            "hydraulic_system_pressure": 180.0,
            "hydraulic_oil_temp": 55.0,
            "hydraulic_oil_level": 85.0,
            "hydraulic_pump_pressure": 185.0,
            "hydraulic_flow_rate": 45.0,
            
            # Transmission (变速箱)
            "transmission_oil_temp": 75.0,
            "transmission_oil_pressure": 5.5,
            "transmission_gear": 3,
            "transmission_mode": "auto",
            
            # Vehicle Dynamics (车辆动力学)
            "vehicle_speed": 12.0,
            "wheel_speed_fl": 12.1,
            "wheel_speed_fr": 12.0,
            "wheel_speed_rl": 11.9,
            "wheel_speed_rr": 12.0,
            "steering_angle": 0.0,
            "brake_pressure": 0.0,
            
            # GPS/GNSS (定位)
            "gnss_latitude": 39.9042,
            "gnss_longitude": 116.4074,
            "gnss_altitude": 50.0,
            "gnss_speed": 12.0,
            "gnss_heading": 90.0,
            "gnss_satellite_count": 12,
            "gnss_hdop": 0.8,
            "gnss_fix_quality": 4,
            
            # IMU (惯性测量)
            "imu_pitch": 2.5,
            "imu_roll": -1.2,
            "imu_yaw": 90.0,
            "imu_accel_x": 0.5,
            "imu_accel_y": 0.2,
            "imu_accel_z": 9.8,
            
            # Environment (环境)
            "ambient_temp": 25.0,
            "ambient_humidity": 60.0,
            "ambient_pressure": 101.3,
            
            # Implements (作业机具)
            "implement_status": "working",
            "implement_depth": 25.0,
            "implement_width": 3.5,
            "pto_speed": 540,
            "pto_torque": 250.0,
            
            # System (系统)
            "system_voltage": 24.2,
            "alternator_output": 28.5,
            "cabin_temp": 22.0,
            "air_filter_pressure_diff": 2.5,
            "dtc_count": 0,
            "warning_count": 0,
            "system_health_score": 95.0,
        }
        
    def on_connect(self, client, userdata, flags, rc):
        if rc == 0:
            print("✅ Connected to MQTT broker")
        else:
            print(f"❌ Connection failed: {rc}")
            
    def connect(self):
        try:
            self.client.connect(MQTT_BROKER, MQTT_PORT, 60)
            self.client.loop_start()
            time.sleep(2)
            return True
        except Exception as e:
            print(f"❌ Connection failed: {e}")
            return False
            
    def disconnect(self):
        self.client.loop_stop()
        self.client.disconnect()
        
    def add_noise(self, value, noise_percent=2.0):
        """Add realistic noise to sensor values"""
        if isinstance(value, (int, float)):
            noise = value * (noise_percent / 100.0)
            return value + random.uniform(-noise, noise)
        return value
        
    def generate_telemetry(self, anomalies=None):
        """Generate complete telemetry with optional anomalies"""
        data = {
            "vehicle_id": VEHICLE_ID,
            "timestamp": datetime.now(timezone.utc).isoformat(),
            "running_time": self.running_time,
            "total_distance": self.total_distance,
            "fuel_consumption_total": self.total_fuel_consumed,
        }
        
        # Add all normal parameters with noise
        for key, value in self.normal_params.items():
            data[key] = self.add_noise(value, noise_percent=2.0)
        
        # Apply anomalies if specified
        if anomalies:
            data.update(anomalies)
            data["warning_count"] = len(anomalies)
        
        # Update cumulative values
        self.running_time += 10
        self.total_distance += (data["vehicle_speed"] * 10 / 3600) * 1000
        self.total_fuel_consumed += (data["engine_fuel_rate"] * 10 / 3600)
        
        return data
        
    def send_telemetry(self, data, show_details=False):
        """Send telemetry via MQTT"""
        payload = json.dumps(data)
        result = self.client.publish(MQTT_TOPIC, payload, qos=1)
        
        self.message_count += 1
        timestamp = datetime.now().strftime("%H:%M:%S")
        
        if show_details or self.message_count % 6 == 0:
            print(f"[{timestamp}] 📤 #{self.message_count:04d} | "
                  f"Temp={data['engine_coolant_temp']:.1f}°C | "
                  f"Oil={data['engine_oil_pressure']:.1f}bar | "
                  f"Fuel={data['fuel_level']:.1f}% | "
                  f"Batt={data['battery_soc']:.1f}% | "
                  f"Speed={data['vehicle_speed']:.1f}km/h")
        
        return result.rc == mqtt.MQTT_ERR_SUCCESS
        
    def run_automated_alert_test(self):
        """Run automated alert testing sequence"""
        
        print("\n" + "="*80)
        print("🚨 AUTOMATED ALERT TESTING SEQUENCE")
        print("="*80)
        print()
        print("📋 Test Plan:")
        print("  Phase 1: Normal Operation (3 min) - Baseline data")
        print("  Phase 2: Engine Overheating (5 min) - Critical alert")
        print("  Phase 3: Recovery (2 min) - Return to normal")
        print("  Phase 4: Low Fuel (5 min) - Warning alert")
        print("  Phase 5: Recovery (2 min) - Return to normal")
        print("  Phase 6: Low Oil Pressure (5 min) - Critical alert")
        print("  Phase 7: Recovery (2 min) - Return to normal")
        print("  Phase 8: Battery Low (5 min) - Warning alert")
        print("  Phase 9: Recovery (2 min) - Return to normal")
        print("  Phase 10: Multiple Faults (5 min) - Multiple alerts")
        print("  Phase 11: Final Recovery (2 min) - Return to normal")
        print()
        print("⏱️  Total Duration: ~38 minutes")
        print("📊 Total Messages: ~228 (every 10 seconds)")
        print()
        print("⚠️  Expected Alerts:")
        print("  🔥 EngineOverheating (Critical) - after 2 min in Phase 2")
        print("  ⛽ LowFuelLevel (Warning) - after 5 min in Phase 4")
        print("  💧 LowOilPressure (Critical) - after 2 min in Phase 6")
        print("  🔋 BatteryLow (Warning) - after 5 min in Phase 8")
        print("  💥 Multiple alerts simultaneously in Phase 10")
        print()
        
        input("Press Enter to start automated testing...")
        print()
        
        start_time = time.time()
        
        try:
            # Phase 1: Normal Operation (3 min = 180s)
            self.run_phase("Phase 1: Normal Operation", 180, None)
            
            # Phase 2: Engine Overheating (5 min = 300s)
            self.run_phase("Phase 2: Engine Overheating 🔥", 300, {
                "engine_coolant_temp": lambda: 110.0 + random.uniform(-2, 2),
                "engine_oil_temp": lambda: 115.0 + random.uniform(-2, 2),
                "engine_exhaust_temp": lambda: 650.0 + random.uniform(-20, 20),
            }, alert_expected="EngineOverheating (Critical) after 2 minutes")
            
            # Phase 3: Recovery (2 min = 120s)
            self.run_phase("Phase 3: Recovery", 120, None)
            
            # Phase 4: Low Fuel (5 min = 300s)
            self.run_phase("Phase 4: Low Fuel ⛽", 300, {
                "fuel_level": lambda: 12.0 + random.uniform(-1, 1),
            }, alert_expected="LowFuelLevel (Warning) after 5 minutes")
            
            # Phase 5: Recovery (2 min = 120s)
            self.run_phase("Phase 5: Recovery", 120, None)
            
            # Phase 6: Low Oil Pressure (5 min = 300s)
            self.run_phase("Phase 6: Low Oil Pressure 💧", 300, {
                "engine_oil_pressure": lambda: 1.5 + random.uniform(-0.2, 0.2),
                "engine_oil_temp": lambda: 105.0 + random.uniform(-3, 3),
            }, alert_expected="LowOilPressure (Critical) after 2 minutes")
            
            # Phase 7: Recovery (2 min = 120s)
            self.run_phase("Phase 7: Recovery", 120, None)
            
            # Phase 8: Battery Low (5 min = 300s)
            self.run_phase("Phase 8: Battery Low 🔋", 300, {
                "battery_soc": lambda: 15.0 + random.uniform(-2, 2),
                "battery_voltage": lambda: 22.5 + random.uniform(-0.5, 0.5),
            }, alert_expected="BatteryLow (Warning) after 5 minutes")
            
            # Phase 9: Recovery (2 min = 120s)
            self.run_phase("Phase 9: Recovery", 120, None)
            
            # Phase 10: Multiple Faults (5 min = 300s)
            self.run_phase("Phase 10: Multiple Faults 💥", 300, {
                "engine_coolant_temp": lambda: 108.0 + random.uniform(-2, 2),
                "engine_oil_pressure": lambda: 1.8 + random.uniform(-0.2, 0.2),
                "fuel_level": lambda: 12.0 + random.uniform(-1, 1),
                "battery_soc": lambda: 18.0 + random.uniform(-2, 2),
                "hydraulic_system_pressure": lambda: 120.0 + random.uniform(-5, 5),
            }, alert_expected="Multiple alerts simultaneously")
            
            # Phase 11: Final Recovery (2 min = 120s)
            self.run_phase("Phase 11: Final Recovery", 120, None)
            
            # Test completed
            total_time = time.time() - start_time
            print("\n" + "="*80)
            print("🎉 AUTOMATED ALERT TEST COMPLETED!")
            print("="*80)
            print(f"⏱️  Total Time: {total_time/60:.1f} minutes")
            print(f"📊 Total Messages: {self.message_count}")
            print(f"📏 Total Distance: {self.total_distance/1000:.2f} km")
            print(f"⛽ Total Fuel: {self.total_fuel_consumed:.2f} L")
            print()
            print("📋 Verification Checklist:")
            print("  ☐ Check vmalert UI (http://127.0.0.1:8880) for fired alerts")
            print("  ☐ Check Alertmanager (http://localhost:9093) for alert history")
            print("  ☐ Check WeChat Work group for notifications")
            print("  ☐ Check Grafana (http://localhost:3000) for data visualization")
            print("  ☐ Review notification_bridge logs")
            print()
            
        except KeyboardInterrupt:
            print("\n⚠️  Test interrupted by user")
        except Exception as e:
            print(f"\n❌ Test error: {e}")
            import traceback
            traceback.print_exc()
            
    def run_phase(self, phase_name, duration, anomalies, alert_expected=None):
        """Run a single test phase"""
        print("\n" + "-"*80)
        print(f"▶️  {phase_name}")
        print("-"*80)
        print(f"⏱️  Duration: {duration}s ({duration//60}min {duration%60}s)")
        if alert_expected:
            print(f"🔔 Expected Alert: {alert_expected}")
        print()
        
        phase_start = time.time()
        count = 0
        
        while time.time() - phase_start < duration:
            elapsed = time.time() - phase_start
            
            # Prepare anomaly values
            anomaly_data = {}
            if anomalies:
                for key, value_func in anomalies.items():
                    anomaly_data[key] = value_func() if callable(value_func) else value_func
            
            # Generate and send telemetry
            data = self.generate_telemetry(anomaly_data if anomalies else None)
            self.send_telemetry(data, show_details=(count == 0))
            
            count += 1
            
            # Show progress for alert phases
            if alert_expected and count % 12 == 0:  # Every 2 minutes
                print(f"  ⏳ {elapsed:.0f}s elapsed... (waiting for alert)")
            
            time.sleep(10)
        
        print(f"✅ {phase_name} completed ({count} messages)")

# ============================================================================
# Main Function
# ============================================================================

def main():
    print("="*80)
    print("🚜 Automated Alert Testing - T-BOX Simulator")
    print("   Tractor Predictive Maintenance System")
    print("="*80)
    print()
    print("📌 This script will:")
    print("  ✅ Send complete telemetry data (60+ metrics) every 10 seconds")
    print("  ✅ Automatically inject anomalies to trigger alerts")
    print("  ✅ Test all alert rules in sequence")
    print("  ✅ Show real-time progress and expected alerts")
    print()
    print("⚠️  Prerequisites:")
    print("  ✅ Mosquitto MQTT (port 1883)")
    print("  ✅ VictoriaMetrics cluster (vminsert:8480, vmselect:8481)")
    print("  ✅ vmalert (port 8880)")
    print("  ✅ Alertmanager (port 9093)")
    print("  ✅ notification_bridge (port 5001)")
    print()
    
    simulator = AutoAlertTractorSimulator()
    
    if not simulator.connect():
        print("❌ Cannot connect to MQTT broker")
        print("   Please check: docker ps | findstr mosquitto")
        return
    
    try:
        simulator.run_automated_alert_test()
    finally:
        simulator.disconnect()

if __name__ == "__main__":
    main()
