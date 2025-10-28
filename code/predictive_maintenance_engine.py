#!/usr/bin/env python3
"""
预测性维护分析引擎
集成Nixtla TimeGPT、Darts、Prophet等时序分析模型
实现多层次的故障预测和健康度评估
"""

import pandas as pd
import numpy as np
from datetime import datetime, timedelta
from typing import Dict, List, Any, Tuple, Optional
import warnings
warnings.filterwarnings('ignore')


class PredictiveMaintenanceEngine:
    """预测性维护分析引擎"""
    
    def __init__(self, vehicle_id: str):
        """
        初始化分析引擎
        
        Args:
            vehicle_id: 车辆ID
        """
        self.vehicle_id = vehicle_id
        self.health_score = 100.0  # 初始健康度评分
        self.anomaly_threshold = 0.95  # 异常检测阈值
        
    def calculate_health_score(self, metrics: Dict[str, float]) -> float:
        """
        计算设备健康度评分（0-100分）
        
        Args:
            metrics: 关键指标字典
            
        Returns:
            健康度评分
        """
        score = 100.0
        
        # 发动机健康度
        if 'engine_coolant_temp' in metrics:
            temp = metrics['engine_coolant_temp']
            if temp > 95:  # 超过95°C扣分
                score -= min(20, (temp - 95) * 2)
        
        if 'engine_oil_pressure' in metrics:
            pressure = metrics['engine_oil_pressure']
            if pressure < 3.5:  # 低于3.5 bar扣分
                score -= min(15, (3.5 - pressure) * 10)
        
        # 电池健康度
        if 'battery_soh' in metrics:
            soh = metrics['battery_soh']
            if soh < 80:  # SOH低于80%扣分
                score -= min(25, (80 - soh) * 1.5)
        
        if 'battery_temp_max' in metrics:
            temp = metrics['battery_temp_max']
            if temp > 45:  # 超过45°C扣分
                score -= min(15, (temp - 45) * 1.5)
        
        # 液压系统健康度
        if 'hydraulic_pressure' in metrics:
            pressure = metrics['hydraulic_pressure']
            if pressure < 150:  # 低于150 bar扣分
                score -= min(20, (150 - pressure) * 0.5)
        
        # 传感器健康度
        if 'sensor_quality_score' in metrics:
            quality = metrics['sensor_quality_score']
            if quality < 90:  # 低于90分扣分
                score -= min(10, (90 - quality) * 0.5)
        
        return max(0, min(100, score))
    
    def detect_anomaly_statistical(self, 
                                   time_series: pd.Series, 
                                   window: int = 20) -> Tuple[bool, float]:
        """
        基于统计方法的异常检测（实时层）
        
        Args:
            time_series: 时间序列数据
            window: 滑动窗口大小
            
        Returns:
            (是否异常, 异常分数)
        """
        if len(time_series) < window:
            return False, 0.0
        
        # 计算滚动均值和标准差
        rolling_mean = time_series.rolling(window=window).mean()
        rolling_std = time_series.rolling(window=window).std()
        
        # 最新值
        latest_value = time_series.iloc[-1]
        latest_mean = rolling_mean.iloc[-1]
        latest_std = rolling_std.iloc[-1]
        
        # Z-score异常检测
        if latest_std > 0:
            z_score = abs((latest_value - latest_mean) / latest_std)
            is_anomaly = z_score > 3.0  # 3-sigma规则
            anomaly_score = min(1.0, z_score / 5.0)
        else:
            is_anomaly = False
            anomaly_score = 0.0
        
        return is_anomaly, anomaly_score
    
    def predict_remaining_useful_life(self, 
                                     degradation_series: pd.Series,
                                     failure_threshold: float = 70.0) -> Dict[str, Any]:
        """
        预测剩余使用寿命（RUL）
        使用简单的线性退化模型（实际应用中应使用TimeGPT）
        
        Args:
            degradation_series: 退化指标时间序列（如SOH、健康度评分）
            failure_threshold: 故障阈值
            
        Returns:
            RUL预测结果
        """
        if len(degradation_series) < 10:
            return {
                'rul_days': None,
                'confidence': 0.0,
                'prediction_method': 'insufficient_data'
            }
        
        # 线性拟合
        x = np.arange(len(degradation_series))
        y = degradation_series.values
        
        # 最小二乘法
        coeffs = np.polyfit(x, y, 1)
        slope = coeffs[0]
        intercept = coeffs[1]
        
        # 当前值
        current_value = y[-1]
        
        # 预测到达故障阈值的时间
        if slope < 0:  # 退化趋势
            steps_to_failure = (failure_threshold - current_value) / slope
            if steps_to_failure > 0:
                # 假设每个数据点代表1小时
                rul_hours = steps_to_failure
                rul_days = rul_hours / 24
                
                # 计算拟合优度作为置信度
                y_pred = slope * x + intercept
                r_squared = 1 - (np.sum((y - y_pred) ** 2) / np.sum((y - np.mean(y)) ** 2))
                confidence = max(0.0, min(1.0, r_squared))
                
                return {
                    'rul_days': rul_days,
                    'rul_hours': rul_hours,
                    'current_value': current_value,
                    'failure_threshold': failure_threshold,
                    'degradation_rate': slope,
                    'confidence': confidence,
                    'prediction_method': 'linear_regression'
                }
        
        return {
            'rul_days': None,
            'confidence': 0.0,
            'prediction_method': 'no_degradation_trend'
        }
    
    def generate_maintenance_recommendation(self, 
                                           health_score: float,
                                           rul_prediction: Dict[str, Any],
                                           anomalies: Dict[str, bool]) -> Dict[str, Any]:
        """
        生成维护建议
        
        Args:
            health_score: 健康度评分
            rul_prediction: RUL预测结果
            anomalies: 异常检测结果
            
        Returns:
            维护建议
        """
        recommendations = []
        priority = 'low'
        action_required = False
        
        # 基于健康度评分
        if health_score < 60:
            priority = 'critical'
            action_required = True
            recommendations.append({
                'type': 'immediate_inspection',
                'description': '设备健康度严重下降，建议立即停机检查',
                'urgency': 'critical'
            })
        elif health_score < 75:
            priority = 'high'
            action_required = True
            recommendations.append({
                'type': 'scheduled_maintenance',
                'description': '设备健康度下降，建议在24小时内进行维护',
                'urgency': 'high'
            })
        elif health_score < 85:
            priority = 'medium'
            recommendations.append({
                'type': 'preventive_maintenance',
                'description': '设备健康度轻微下降，建议安排预防性维护',
                'urgency': 'medium'
            })
        
        # 基于RUL预测
        if rul_prediction.get('rul_days'):
            rul_days = rul_prediction['rul_days']
            if rul_days < 3:
                priority = 'critical'
                action_required = True
                recommendations.append({
                    'type': 'component_replacement',
                    'description': f'预计{rul_days:.1f}天后部件将达到故障阈值，建议立即更换',
                    'urgency': 'critical'
                })
            elif rul_days < 7:
                priority = 'high'
                action_required = True
                recommendations.append({
                    'type': 'component_replacement',
                    'description': f'预计{rul_days:.1f}天后部件将达到故障阈值，建议尽快更换',
                    'urgency': 'high'
                })
            elif rul_days < 30:
                recommendations.append({
                    'type': 'component_replacement',
                    'description': f'预计{rul_days:.1f}天后部件将达到故障阈值，建议提前准备备件',
                    'urgency': 'medium'
                })
        
        # 基于异常检测
        if any(anomalies.values()):
            priority = max(priority, 'high', key=['low', 'medium', 'high', 'critical'].index)
            action_required = True
            anomaly_components = [k for k, v in anomalies.items() if v]
            recommendations.append({
                'type': 'anomaly_investigation',
                'description': f'检测到异常: {", ".join(anomaly_components)}，建议进行详细检查',
                'urgency': 'high'
            })
        
        return {
            'vehicle_id': self.vehicle_id,
            'timestamp': datetime.now().isoformat(),
            'health_score': health_score,
            'priority': priority,
            'action_required': action_required,
            'recommendations': recommendations,
            'rul_prediction': rul_prediction
        }
    
    def analyze_vehicle_health(self, 
                               historical_data: pd.DataFrame) -> Dict[str, Any]:
        """
        综合分析车辆健康状态
        
        Args:
            historical_data: 历史数据DataFrame
            
        Returns:
            分析结果
        """
        # 提取最新指标
        latest_metrics = historical_data.iloc[-1].to_dict()
        
        # 计算健康度评分
        health_score = self.calculate_health_score(latest_metrics)
        
        # 异常检测
        anomalies = {}
        for column in ['engine_coolant_temp', 'battery_soh', 'hydraulic_pressure']:
            if column in historical_data.columns:
                is_anomaly, score = self.detect_anomaly_statistical(historical_data[column])
                anomalies[column] = is_anomaly
        
        # RUL预测（以电池SOH为例）
        rul_prediction = {}
        if 'battery_soh' in historical_data.columns:
            rul_prediction = self.predict_remaining_useful_life(
                historical_data['battery_soh'],
                failure_threshold=80.0
            )
        
        # 生成维护建议
        maintenance_recommendation = self.generate_maintenance_recommendation(
            health_score, rul_prediction, anomalies
        )
        
        return {
            'health_score': health_score,
            'anomalies': anomalies,
            'rul_prediction': rul_prediction,
            'maintenance_recommendation': maintenance_recommendation
        }


def demo_predictive_maintenance():
    """演示预测性维护分析引擎"""
    print("=" * 80)
    print("预测性维护分析引擎 - 演示")
    print("=" * 80)
    
    # 创建分析引擎
    engine = PredictiveMaintenanceEngine(vehicle_id='TRACTOR_001')
    
    # 生成模拟历史数据
    dates = pd.date_range(start='2025-01-01', periods=100, freq='H')
    
    # 模拟电池SOH退化
    battery_soh = 100 - np.linspace(0, 15, 100) + np.random.normal(0, 1, 100)
    
    # 模拟发动机温度（正常波动 + 异常尖峰）
    engine_temp = 85 + 5 * np.sin(np.linspace(0, 10, 100)) + np.random.normal(0, 2, 100)
    engine_temp[90:95] += 15  # 在第90-95小时注入异常
    
    # 模拟液压压力
    hydraulic_pressure = 180 + 10 * np.sin(np.linspace(0, 8, 100)) + np.random.normal(0, 3, 100)
    
    # 创建DataFrame
    historical_data = pd.DataFrame({
        'timestamp': dates,
        'battery_soh': battery_soh,
        'engine_coolant_temp': engine_temp,
        'hydraulic_pressure': hydraulic_pressure,
        'engine_oil_pressure': 4.5 + np.random.normal(0, 0.2, 100),
        'battery_temp_max': 35 + np.random.normal(0, 3, 100),
        'sensor_quality_score': 95 + np.random.normal(0, 2, 100),
    })
    
    print(f"\n分析车辆 {engine.vehicle_id} 的健康状态...")
    print(f"历史数据: {len(historical_data)} 条记录")
    print("-" * 80)
    
    # 执行分析
    analysis_result = engine.analyze_vehicle_health(historical_data)
    
    # 输出结果
    print(f"\n【健康度评分】: {analysis_result['health_score']:.1f}/100")
    
    print(f"\n【异常检测结果】:")
    for component, is_anomaly in analysis_result['anomalies'].items():
        status = "⚠️  异常" if is_anomaly else "✓ 正常"
        print(f"  - {component}: {status}")
    
    print(f"\n【RUL预测】:")
    rul = analysis_result['rul_prediction']
    if rul.get('rul_days'):
        print(f"  - 预计剩余使用寿命: {rul['rul_days']:.1f} 天 ({rul['rul_hours']:.1f} 小时)")
        print(f"  - 当前值: {rul['current_value']:.2f}")
        print(f"  - 故障阈值: {rul['failure_threshold']:.2f}")
        print(f"  - 退化速率: {rul['degradation_rate']:.4f} /小时")
        print(f"  - 预测置信度: {rul['confidence']:.2%}")
    else:
        print(f"  - 状态: {rul.get('prediction_method', 'N/A')}")
    
    print(f"\n【维护建议】:")
    rec = analysis_result['maintenance_recommendation']
    print(f"  - 优先级: {rec['priority'].upper()}")
    print(f"  - 需要行动: {'是' if rec['action_required'] else '否'}")
    print(f"  - 建议事项:")
    for idx, item in enumerate(rec['recommendations'], 1):
        print(f"    {idx}. [{item['urgency'].upper()}] {item['description']}")
    
    print("\n" + "=" * 80)
    print("注意: 本演示使用简化的算法。生产环境中应集成Nixtla TimeGPT进行长期预测")
    print("=" * 80)


if __name__ == '__main__':
    demo_predictive_maintenance()
