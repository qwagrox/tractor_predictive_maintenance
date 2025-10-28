#!/usr/bin/env python3
"""
Nixtla TimeGPT集成示例
演示如何使用TimeGPT进行长期趋势预测和异常检测
"""

import pandas as pd
import numpy as np
from datetime import datetime, timedelta
from typing import Dict, List, Any
import warnings
warnings.filterwarnings('ignore')


class NixtlaTimeGPTIntegration:
    """Nixtla TimeGPT集成类"""
    
    def __init__(self, api_key: str = None):
        """
        初始化TimeGPT客户端
        
        Args:
            api_key: Nixtla API密钥（如果使用公共API）
        """
        self.api_key = api_key
        self.client = None
        
        # 如果提供了API密钥，初始化客户端
        if api_key:
            try:
                from nixtla import NixtlaClient
                self.client = NixtlaClient(api_key=api_key)
                print("✓ TimeGPT客户端初始化成功")
            except ImportError:
                print("⚠️  nixtla包未安装，请运行: pip install nixtla")
            except Exception as e:
                print(f"⚠️  TimeGPT客户端初始化失败: {e}")
    
    def forecast_with_timegpt(self, 
                             df: pd.DataFrame,
                             horizon: int = 168,  # 预测7天（168小时）
                             freq: str = 'H') -> pd.DataFrame:
        """
        使用TimeGPT进行时序预测
        
        Args:
            df: 历史数据DataFrame，需包含'timestamp'和'value'列
            horizon: 预测时长
            freq: 数据频率（'H'=小时, 'D'=天）
            
        Returns:
            预测结果DataFrame
        """
        if self.client is None:
            print("⚠️  TimeGPT客户端未初始化，使用模拟预测")
            return self._simulate_forecast(df, horizon, freq)
        
        try:
            # TimeGPT需要特定的数据格式
            # unique_id: 时间序列标识符
            # ds: 时间戳
            # y: 目标值
            forecast_df = df.copy()
            forecast_df.columns = ['ds', 'y']
            forecast_df['unique_id'] = 'series_1'
            
            # 调用TimeGPT进行预测
            forecast = self.client.forecast(
                df=forecast_df,
                h=horizon,
                freq=freq,
                level=[80, 95]  # 预测区间
            )
            
            return forecast
        
        except Exception as e:
            print(f"⚠️  TimeGPT预测失败: {e}")
            return self._simulate_forecast(df, horizon, freq)
    
    def _simulate_forecast(self, 
                          df: pd.DataFrame,
                          horizon: int,
                          freq: str) -> pd.DataFrame:
        """
        模拟预测（当TimeGPT不可用时）
        使用简单的趋势+季节性模型
        """
        # 提取最后的值和趋势
        values = df.iloc[:, 1].values
        
        # 计算线性趋势
        x = np.arange(len(values))
        coeffs = np.polyfit(x, values, 1)
        trend = coeffs[0]
        
        # 计算季节性（简化为24小时周期）
        if len(values) >= 24:
            seasonal = values[-24:]
        else:
            seasonal = values
        
        # 生成预测
        last_timestamp = df.iloc[-1, 0]
        if freq == 'H':
            freq_delta = timedelta(hours=1)
        elif freq == 'D':
            freq_delta = timedelta(days=1)
        else:
            freq_delta = timedelta(hours=1)
        
        forecast_timestamps = [last_timestamp + freq_delta * (i + 1) for i in range(horizon)]
        
        # 预测值 = 趋势 + 季节性 + 噪声
        forecast_values = []
        for i in range(horizon):
            trend_component = values[-1] + trend * (i + 1)
            seasonal_component = seasonal[i % len(seasonal)] - np.mean(seasonal)
            noise = np.random.normal(0, np.std(values) * 0.1)
            forecast_values.append(trend_component + seasonal_component * 0.3 + noise)
        
        forecast_df = pd.DataFrame({
            'timestamp': forecast_timestamps,
            'forecast': forecast_values,
            'lower_80': [v - np.std(values) * 1.28 for v in forecast_values],
            'upper_80': [v + np.std(values) * 1.28 for v in forecast_values],
            'lower_95': [v - np.std(values) * 1.96 for v in forecast_values],
            'upper_95': [v + np.std(values) * 1.96 for v in forecast_values],
        })
        
        return forecast_df
    
    def detect_anomaly_with_timegpt(self, 
                                   df: pd.DataFrame) -> pd.DataFrame:
        """
        使用TimeGPT进行异常检测
        
        Args:
            df: 历史数据DataFrame
            
        Returns:
            异常检测结果DataFrame
        """
        if self.client is None:
            print("⚠️  TimeGPT客户端未初始化，使用模拟异常检测")
            return self._simulate_anomaly_detection(df)
        
        try:
            # TimeGPT异常检测
            forecast_df = df.copy()
            forecast_df.columns = ['ds', 'y']
            forecast_df['unique_id'] = 'series_1'
            
            anomalies = self.client.detect_anomalies(
                df=forecast_df,
                freq='H'
            )
            
            return anomalies
        
        except Exception as e:
            print(f"⚠️  TimeGPT异常检测失败: {e}")
            return self._simulate_anomaly_detection(df)
    
    def _simulate_anomaly_detection(self, df: pd.DataFrame) -> pd.DataFrame:
        """模拟异常检测"""
        values = df.iloc[:, 1].values
        
        # 使用3-sigma规则
        mean = np.mean(values)
        std = np.std(values)
        
        anomalies = []
        for i, v in enumerate(values):
            z_score = abs((v - mean) / std) if std > 0 else 0
            is_anomaly = z_score > 3.0
            anomalies.append({
                'timestamp': df.iloc[i, 0],
                'value': v,
                'z_score': z_score,
                'is_anomaly': is_anomaly
            })
        
        return pd.DataFrame(anomalies)


def demo_nixtla_integration():
    """演示Nixtla TimeGPT集成"""
    print("=" * 80)
    print("Nixtla TimeGPT集成 - 演示")
    print("=" * 80)
    
    # 创建集成实例（不使用真实API密钥，演示模拟模式）
    timegpt = NixtlaTimeGPTIntegration(api_key=None)
    
    # 生成模拟历史数据（电池SOH）
    dates = pd.date_range(start='2025-01-01', periods=720, freq='H')  # 30天数据
    
    # 模拟电池SOH退化趋势 + 日周期波动
    trend = 100 - np.linspace(0, 10, 720)  # 线性退化
    daily_cycle = 2 * np.sin(2 * np.pi * np.arange(720) / 24)  # 日周期
    noise = np.random.normal(0, 0.5, 720)
    battery_soh = trend + daily_cycle + noise
    
    # 注入异常
    battery_soh[500:510] -= 5  # 在第500-510小时注入异常下降
    
    historical_data = pd.DataFrame({
        'timestamp': dates,
        'battery_soh': battery_soh
    })
    
    print(f"\n【数据概况】")
    print(f"  - 历史数据: {len(historical_data)} 条记录（{len(historical_data)/24:.0f}天）")
    print(f"  - 时间范围: {historical_data['timestamp'].min()} 至 {historical_data['timestamp'].max()}")
    print(f"  - 电池SOH范围: {historical_data['battery_soh'].min():.2f}% - {historical_data['battery_soh'].max():.2f}%")
    
    # 1. 长期趋势预测
    print(f"\n【长期趋势预测】（使用TimeGPT或模拟）")
    print(f"  - 预测未来7天（168小时）的电池SOH趋势...")
    
    forecast_result = timegpt.forecast_with_timegpt(
        df=historical_data[['timestamp', 'battery_soh']],
        horizon=168,
        freq='H'
    )
    
    print(f"  - 预测结果: {len(forecast_result)} 个时间点")
    print(f"  - 预测时间范围: {forecast_result['timestamp'].min()} 至 {forecast_result['timestamp'].max()}")
    print(f"  - 预测SOH范围: {forecast_result['forecast'].min():.2f}% - {forecast_result['forecast'].max():.2f}%")
    print(f"  - 7天后预测值: {forecast_result['forecast'].iloc[-1]:.2f}%")
    
    # 判断是否会在预测期内跌破阈值
    failure_threshold = 80.0
    below_threshold = forecast_result[forecast_result['forecast'] < failure_threshold]
    if len(below_threshold) > 0:
        first_failure = below_threshold.iloc[0]
        days_to_failure = (first_failure['timestamp'] - historical_data['timestamp'].max()).total_seconds() / 86400
        print(f"  - ⚠️  预警: 预计在 {days_to_failure:.1f} 天后SOH将跌破{failure_threshold}%阈值")
    else:
        print(f"  - ✓ 预测期内SOH不会跌破{failure_threshold}%阈值")
    
    # 2. 异常检测
    print(f"\n【异常检测】（使用TimeGPT或模拟）")
    print(f"  - 检测历史数据中的异常点...")
    
    anomaly_result = timegpt.detect_anomaly_with_timegpt(
        df=historical_data[['timestamp', 'battery_soh']]
    )
    
    anomalies = anomaly_result[anomaly_result['is_anomaly'] == True]
    print(f"  - 检测到 {len(anomalies)} 个异常点")
    
    if len(anomalies) > 0:
        print(f"  - 异常时间点:")
        for idx, row in anomalies.head(5).iterrows():
            print(f"    • {row['timestamp']}: SOH={row['value']:.2f}%, Z-score={row['z_score']:.2f}")
    
    # 3. 商业化应用场景
    print(f"\n【商业化应用场景】")
    print(f"  1. 长期预测（TimeGPT）:")
    print(f"     - 预测未来7-30天的关键部件健康度趋势")
    print(f"     - 估算剩余使用寿命（RUL）")
    print(f"     - 优化备件采购和维修计划")
    print(f"  ")
    print(f"  2. 异常检测（TimeGPT）:")
    print(f"     - 实时检测设备运行异常")
    print(f"     - 识别潜在故障模式")
    print(f"     - 触发智能告警")
    print(f"  ")
    print(f"  3. 多车队管理:")
    print(f"     - 同时预测数千台拖拉机的健康状态")
    print(f"     - 优化整体车队的维护资源分配")
    print(f"     - 降低非计划停机时间")
    
    print("\n" + "=" * 80)
    print("注意事项:")
    print("  • 生产环境需要申请Nixtla API密钥或私有部署TimeGPT")
    print("  • API调用: export NIXTLA_API_KEY='your_api_key'")
    print("  • 私有部署: 联系Nixtla获取企业版授权")
    print("  • 安装: pip install nixtla")
    print("=" * 80)


if __name__ == '__main__':
    demo_nixtla_integration()
