# 真实工况数据模式设计

## 📋 需求分析

基于CSS Electronics的CAN数据可视化风格，我们需要实现：

### 1. 数据特征
- ❌ **不要**：平滑的正弦波（不真实）
- ✅ **要**：真实的工况数据模式
  - 突变（加速、刹车）
  - 尖峰（瞬时负载）
  - 平台期（稳定工况）
  - 随机波动（传感器噪声）
  - 工作循环（启动-运行-停止）

### 2. 可视化效果
- 鼠标悬停显示数值和时间戳
- 参考线标注关键阈值
- 信号名称和路径标注
- 时间轴清晰可读

---

## 🎯 真实数据模式设计

### 拖拉机工作循环

典型的拖拉机作业包含以下阶段：

```
启动 → 怠速 → 加速 → 作业 → 减速 → 怠速 → 停止 → 重复
```

### 各参数的真实模式

#### 1. 车速 (vehicle_speed)
- **怠速/停止**: 0 km/h
- **转场**: 5-15 km/h（随机波动）
- **作业**: 3-8 km/h（缓慢变化）
- **突变**: 加速/刹车时快速变化
- **噪声**: ±0.5 km/h

**模式**：
```
0 → 快速上升到8 → 保持5-8波动 → 突然降到0 → 保持0 → 重复
```

#### 2. 发动机转速 (engine_rpm)
- **停止**: 0 rpm
- **怠速**: 800-900 rpm
- **轻载**: 1200-1500 rpm
- **重载**: 1800-2200 rpm
- **噪声**: ±50 rpm

**模式**：
```
0 → 快速上升到850 → 跳到1500 → 波动到2000 → 降到850 → 降到0
```

#### 3. 发动机扭矩 (engine_torque)
- **怠速**: 50-100 Nm
- **轻载**: 200-300 Nm
- **重载**: 400-500 Nm（有尖峰）
- **噪声**: ±20 Nm

**模式**：
```
与转速相关，但有延迟和尖峰（遇到障碍物时）
```

#### 4. 电池电压 (battery_voltage)
- **正常**: 24-26V（缓慢波动）
- **启动**: 短暂降到22V
- **充电**: 缓慢上升到26V
- **噪声**: ±0.2V

**模式**：
```
25V → 启动时降到22V → 恢复到24V → 运行中缓慢上升到26V
```

#### 5. 燃油消耗率 (fuel_consumption_rate)
- **怠速**: 2-3 L/h
- **轻载**: 5-8 L/h
- **重载**: 10-15 L/h
- **噪声**: ±0.5 L/h

**模式**：
```
与发动机负载直接相关，有尖峰
```

---

## 🔧 实现策略

### 1. 状态机模式

定义拖拉机的工作状态：

```python
class TractorState:
    STOPPED = 0      # 停止
    STARTING = 1     # 启动
    IDLE = 2         # 怠速
    ACCELERATING = 3 # 加速
    WORKING = 4      # 作业
    HEAVY_LOAD = 5   # 重载
    DECELERATING = 6 # 减速
```

### 2. 状态转换

```python
状态持续时间（秒）：
- STOPPED: 10-30
- STARTING: 2-3
- IDLE: 5-10
- ACCELERATING: 3-5
- WORKING: 30-60
- HEAVY_LOAD: 5-15（随机插入）
- DECELERATING: 2-4
```

### 3. 参数映射

每个状态对应一组参数范围：

| 状态 | 车速 | 转速 | 扭矩 | 电压 | 油耗 |
|------|------|------|------|------|------|
| STOPPED | 0 | 0 | 0 | 24-25V | 0 |
| STARTING | 0 | 0→850 | 0→80 | 22→24V | 0→2 |
| IDLE | 0 | 850±50 | 80±20 | 24-25V | 2-3 |
| ACCELERATING | 0→8 | 850→1500 | 80→300 | 24V | 3→8 |
| WORKING | 5-8 | 1500±100 | 300±50 | 24-25V | 8-10 |
| HEAVY_LOAD | 3-5 | 1800-2200 | 400-500 | 23-24V | 12-15 |
| DECELERATING | 8→0 | 1500→850 | 300→80 | 24-25V | 8→3 |

### 4. 噪声和波动

```python
# 添加真实的传感器噪声
value = base_value + random.gauss(0, noise_std)

# 添加突变（10%概率）
if random.random() < 0.1:
    value += random.uniform(-spike_range, spike_range)

# 平滑过渡（避免阶跃）
value = previous_value * 0.7 + target_value * 0.3
```

---

## 📊 Grafana配置优化

### 1. 图表配置

```json
{
  "type": "timeseries",
  "options": {
    "tooltip": {
      "mode": "multi",
      "sort": "none"
    },
    "legend": {
      "displayMode": "table",
      "placement": "bottom",
      "showLegend": true,
      "values": ["value", "min", "max", "mean"]
    }
  },
  "fieldConfig": {
    "defaults": {
      "custom": {
        "lineWidth": 2,
        "fillOpacity": 10,
        "pointSize": 5,
        "showPoints": "never",
        "spanNulls": true
      }
    },
    "overrides": [
      {
        "matcher": {"id": "byName", "options": "车速"},
        "properties": [
          {"id": "color", {"mode": "fixed", "fixedColor": "blue"}},
          {"id": "custom.thresholdsStyle", {"mode": "dashed"}},
          {"id": "thresholds", {
            "mode": "absolute",
            "steps": [
              {"value": 0, "color": "green"},
              {"value": 10, "color": "yellow"},
              {"value": 15, "color": "red"}
            ]
          }}
        ]
      }
    ]
  }
}
```

### 2. 参考线配置

```json
{
  "fieldConfig": {
    "defaults": {
      "custom": {
        "thresholdsStyle": {
          "mode": "dashed"
        }
      },
      "thresholds": {
        "mode": "absolute",
        "steps": [
          {"value": 50, "color": "transparent"},
          {"value": 50, "color": "semi-dark-red"}
        ]
      }
    }
  }
}
```

### 3. 信号标注

在面板标题或描述中添加：
```
message: CAN_TRACTOR_01 | signal: vehicle_speed_kmh
```

---

## 🎨 CSS Electronics风格特点

### 视觉特点
1. **蓝色为主色调**（车速）
2. **绿色为辅助色**（电压、状态）
3. **黄色/红色为警告色**（超限）
4. **半透明填充**（区域图）
5. **虚线参考线**（阈值）

### 交互特点
1. **鼠标悬停显示详细信息**
2. **时间戳精确到秒**
3. **多信号对比**
4. **图例显示统计值**（min/max/mean）

---

## 📝 实现清单

### T-BOX模拟器修改
- [ ] 实现状态机
- [ ] 定义状态转换逻辑
- [ ] 为每个状态定义参数范围
- [ ] 添加真实噪声和突变
- [ ] 添加平滑过渡
- [ ] 添加随机事件（重载、故障）

### Grafana仪表板修改
- [ ] 更新图表类型为timeseries
- [ ] 配置tooltip显示详细信息
- [ ] 添加参考线
- [ ] 配置图例显示统计值
- [ ] 添加信号路径标注
- [ ] 优化颜色方案

---

**版本**: v1.0
**日期**: 2025-01-15
