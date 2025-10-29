#!/usr/bin/env python3
"""
端到端系统集成测试
模拟完整的预测性维护系统工作流程：
1. T-BOX数据采集
2. 数据上传到VictoriaMetrics
3. 多层次分析引擎处理
4. 生成维护建议和告警
"""

import sys
import time
import pandas as pd
import numpy as np
from datetime import datetime, timedelta
from typing import Dict, List, Any

# 导入自定义模块
sys.path.append('/home/ubuntu')
from tbox_simulator import TractorDataSimulator
from mqtt_to_victoriametrics_bridge import MQTTToVictoriaMetricsBridge
from predictive_maintenance_engine import PredictiveMaintenanceEngine
from nixtla_timegpt_integration import NixtlaTimeGPTIntegration


class EndToEndSystemTest:
    """端到端系统集成测试"""
    
    def __init__(self, vehicle_id: str = 'TRACTOR_TEST_001'):
        """
        初始化测试系统
        
        Args:
            vehicle_id: 测试车辆ID
        """
        self.vehicle_id = vehicle_id
        self.tbox_simulator = TractorDataSimulator(vehicle_id)
        self.data_bridge = MQTTToVictoriaMetricsBridge(vm_url="http://localhost:8480")
        self.maintenance_engine = PredictiveMaintenanceEngine(vehicle_id)
        self.timegpt_integration = NixtlaTimeGPTIntegration(api_key=None)
        
        self.collected_data = []
        
    def test_data_collection(self, duration_seconds: int = 10, sample_rate: float = 1.0):
        """
        测试数据采集流程
        
        Args:
            duration_seconds: 测试持续时间
            sample_rate: 采样率
        """
        print("\n" + "=" * 80)
        print("【阶段1】数据采集测试")
        print("=" * 80)
        
        print(f"模拟T-BOX采集车辆 {self.vehicle_id} 的数据...")
        print(f"持续时间: {duration_seconds}秒, 采样率: {sample_rate}Hz")
        
        start_time = time.time()
        sample_count = 0
        
        while time.time() - start_time < duration_seconds:
            # 生成数据包
            data_packet = self.tbox_simulator.generate_complete_data_packet()
            self.collected_data.append(data_packet)
            
            # 更新状态
            self.tbox_simulator.update_state(1.0 / sample_rate)
            sample_count += 1
            
            time.sleep(1.0 / sample_rate)
        
        print(f"✓ 数据采集完成: 共采集 {sample_count} 个数据包")
        return sample_count
    
    def test_data_ingestion(self):
        """测试数据接入流程"""
        print("\n" + "=" * 80)
        print("【阶段2】数据接入测试")
        print("=" * 80)
        
        print(f"将采集的数据转换为VictoriaMetrics格式...")
        
        total_metrics = 0
        for data_packet in self.collected_data:
            prometheus_lines = self.data_bridge.convert_to_prometheus_format(data_packet)
            total_metrics += len(prometheus_lines)
        
        print(f"✓ 数据转换完成: 共生成 {total_metrics} 个时序指标")
        print(f"  平均每个数据包: {total_metrics / len(self.collected_data):.0f} 个指标")
        
        # 注意: 实际写入VictoriaMetrics需要服务运行
        print(f"\n注意: 实际写入VictoriaMetrics需要先启动服务")
        print(f"      使用 docker-compose up -d 启动VictoriaMetrics集群")
        
        return total_metrics
    
    def test_data_analysis(self):
        """测试数据分析流程"""
        print("\n" + "=" * 80)
        print("【阶段3】数据分析测试")
        print("=" * 80)
        
        # 从采集的数据中提取关键指标
        print(f"从 {len(self.collected_data)} 个数据包中提取关键指标...")
        
        timestamps = []
        engine_temps = []
        battery_sohs = []
        hydraulic_pressures = []
        
        for data_packet in self.collected_data:
            timestamps.append(pd.to_datetime(data_packet['timestamp']))
            engine_temps.append(data_packet['engine']['coolant_temp'])
            battery_sohs.append(data_packet['battery']['soh'])
            hydraulic_pressures.append(data_packet['hydraulic']['pressure'])
        
        # 创建DataFrame
        historical_data = pd.DataFrame({
            'timestamp': timestamps,
            'engine_coolant_temp': engine_temps,
            'battery_soh': battery_sohs,
            'hydraulic_pressure': hydraulic_pressures,
            'engine_oil_pressure': [4.5] * len(timestamps),  # 简化
            'battery_temp_max': [35] * len(timestamps),  # 简化
            'sensor_quality_score': [95] * len(timestamps),  # 简化
        })
        
        print(f"✓ 数据提取完成")
        print(f"  - 时间范围: {historical_data['timestamp'].min()} 至 {historical_data['timestamp'].max()}")
        print(f"  - 发动机温度: {historical_data['engine_coolant_temp'].min():.1f}°C - {historical_data['engine_coolant_temp'].max():.1f}°C")
        print(f"  - 电池SOH: {historical_data['battery_soh'].min():.1f}% - {historical_data['battery_soh'].max():.1f}%")
        
        # 执行健康度分析
        print(f"\n执行健康度分析...")
        analysis_result = self.maintenance_engine.analyze_vehicle_health(historical_data)
        
        print(f"✓ 健康度分析完成")
        print(f"  - 健康度评分: {analysis_result['health_score']:.1f}/100")
        print(f"  - 检测到的异常: {sum(analysis_result['anomalies'].values())} 个")
        
        if analysis_result['rul_prediction'].get('rul_days'):
            rul = analysis_result['rul_prediction']
            print(f"  - 预测RUL: {rul['rul_days']:.1f} 天")
        
        return analysis_result
    
    def test_long_term_prediction(self):
        """测试长期趋势预测"""
        print("\n" + "=" * 80)
        print("【阶段4】长期趋势预测测试（TimeGPT）")
        print("=" * 80)
        
        # 提取电池SOH数据
        timestamps = [pd.to_datetime(d['timestamp']) for d in self.collected_data]
        battery_sohs = [d['battery']['soh'] for d in self.collected_data]
        
        battery_df = pd.DataFrame({
            'timestamp': timestamps,
            'battery_soh': battery_sohs
        })
        
        print(f"使用TimeGPT预测未来7天的电池SOH趋势...")
        
        forecast_result = self.timegpt_integration.forecast_with_timegpt(
            df=battery_df,
            horizon=168,  # 7天
            freq='H'
        )
        
        print(f"✓ 长期预测完成")
        print(f"  - 预测时间点: {len(forecast_result)} 个")
        print(f"  - 当前SOH: {battery_sohs[-1]:.2f}%")
        print(f"  - 7天后预测SOH: {forecast_result['forecast'].iloc[-1]:.2f}%")
        
        # 检查是否会跌破阈值
        failure_threshold = 80.0
        below_threshold = forecast_result[forecast_result['forecast'] < failure_threshold]
        if len(below_threshold) > 0:
            first_failure = below_threshold.iloc[0]
            days_to_failure = (first_failure['timestamp'] - timestamps[-1]).total_seconds() / 86400
            print(f"  - ⚠️  预警: 预计 {days_to_failure:.1f} 天后SOH将跌破{failure_threshold}%")
        else:
            print(f"  - ✓ 预测期内SOH不会跌破{failure_threshold}%")
        
        return forecast_result
    
    def test_maintenance_recommendation(self, analysis_result: Dict[str, Any]):
        """测试维护建议生成"""
        print("\n" + "=" * 80)
        print("【阶段5】维护建议生成测试")
        print("=" * 80)
        
        recommendation = analysis_result['maintenance_recommendation']
        
        print(f"生成的维护建议:")
        print(f"  - 车辆ID: {recommendation['vehicle_id']}")
        print(f"  - 健康度评分: {recommendation['health_score']:.1f}/100")
        print(f"  - 优先级: {recommendation['priority'].upper()}")
        print(f"  - 需要行动: {'是' if recommendation['action_required'] else '否'}")
        
        if recommendation['recommendations']:
            print(f"\n  建议事项:")
            for idx, item in enumerate(recommendation['recommendations'], 1):
                print(f"    {idx}. [{item['urgency'].upper()}] {item['description']}")
        else:
            print(f"\n  ✓ 无需特殊维护，设备状态良好")
        
        return recommendation
    
    def test_alert_system(self, recommendation: Dict[str, Any]):
        """测试智能告警系统"""
        print("\n" + "=" * 80)
        print("【阶段6】智能告警系统测试")
        print("=" * 80)
        
        priority = recommendation['priority']
        
        # 根据优先级确定告警方式
        alert_methods = {
            'low': ['APP推送'],
            'medium': ['APP推送', '邮件'],
            'high': ['APP推送', '邮件', '短信'],
            'critical': ['APP推送', '邮件', '短信', '电话', '自动停车']
        }
        
        methods = alert_methods.get(priority, ['APP推送'])
        
        print(f"告警配置:")
        print(f"  - 优先级: {priority.upper()}")
        print(f"  - 告警方式: {', '.join(methods)}")
        
        if recommendation['action_required']:
            print(f"\n⚠️  触发告警!")
            print(f"  模拟发送告警通知...")
            for method in methods:
                print(f"    ✓ {method} 已发送")
        else:
            print(f"\n✓ 无需告警，设备运行正常")
        
        return methods
    
    def run_full_test(self):
        """运行完整的端到端测试"""
        print("\n")
        print("╔" + "=" * 78 + "╗")
        print("║" + " " * 20 + "预测性维护系统 - 端到端集成测试" + " " * 25 + "║")
        print("╚" + "=" * 78 + "╝")
        
        start_time = time.time()
        
        try:
            # 阶段1: 数据采集
            sample_count = self.test_data_collection(duration_seconds=10, sample_rate=1.0)
            
            # 阶段2: 数据接入
            metrics_count = self.test_data_ingestion()
            
            # 阶段3: 数据分析
            analysis_result = self.test_data_analysis()
            
            # 阶段4: 长期预测
            forecast_result = self.test_long_term_prediction()
            
            # 阶段5: 维护建议
            recommendation = self.test_maintenance_recommendation(analysis_result)
            
            # 阶段6: 智能告警
            alert_methods = self.test_alert_system(recommendation)
            
            # 测试总结
            elapsed_time = time.time() - start_time
            
            print("\n" + "=" * 80)
            print("【测试总结】")
            print("=" * 80)
            print(f"✓ 所有测试阶段完成")
            print(f"  - 总耗时: {elapsed_time:.2f} 秒")
            print(f"  - 采集数据包: {sample_count} 个")
            print(f"  - 生成指标: {metrics_count} 个")
            print(f"  - 健康度评分: {analysis_result['health_score']:.1f}/100")
            print(f"  - 维护优先级: {recommendation['priority'].upper()}")
            print(f"  - 告警方式: {len(alert_methods)} 种")
            
            print("\n" + "=" * 80)
            print("【系统就绪状态】")
            print("=" * 80)
            print("✓ T-BOX数据模拟器: 就绪")
            print("✓ 数据转换桥接器: 就绪")
            print("✓ 预测性维护引擎: 就绪")
            print("✓ TimeGPT集成: 就绪（模拟模式）")
            print("⚠  VictoriaMetrics: 需要启动（docker-compose up -d）")
            print("⚠  MQTT Broker: 需要启动")
            
            print("\n" + "=" * 80)
            print("【下一步】")
            print("=" * 80)
            print("1. 启动VictoriaMetrics集群:")
            print("   cd /home/ubuntu && docker-compose -f victoriametrics_deployment.yaml up -d")
            print("")
            print("2. 启动数据采集服务:")
            print("   python3 tbox_simulator.py")
            print("")
            print("3. 访问Grafana仪表板:")
            print("   http://localhost:3000 (admin/admin)")
            print("")
            print("4. 查看VictoriaMetrics指标:")
            print("   http://localhost:8481/select/0/prometheus/api/v1/query?query=tractor_*")
            print("=" * 80)
            
            return True
            
        except Exception as e:
            print(f"\n❌ 测试失败: {e}")
            import traceback
            traceback.print_exc()
            return False


if __name__ == '__main__':
    # 运行端到端测试
    test_system = EndToEndSystemTest(vehicle_id='TRACTOR_TEST_001')
    success = test_system.run_full_test()
    
    sys.exit(0 if success else 1)
