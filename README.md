# 油电混动无人拖拉机预测性维护系统

**版本**: 2.0  
**交付日期**: 2025年10月29日  
**作者**: tangyong@stmail.ujs.edu.cn ， 目前就读于江苏大学农机控制理论与工程博士

---

## 📦 系统代码结构

### 目录结构

```
├── README.md                           # 本文件
├── DELIVERY_CHECKLIST.md              # 交付清单
├── docs/                               # 文档目录
│   ├── final_commercial_proposal.md   # 完整商业化方案（主文档）
│   ├── tractor_system_summary.md      # 拖拉机系统关键信息摘要
│   ├── timeseries_tech_comparison.md  # 时序数据库和分析引擎对比研究
│   ├── nixtla_timegpt_summary.md      # Nixtla TimeGPT关键信息
│   ├── predictive_maintenance_system_design_victoriametrics.md  # 系统设计方案
│   ├── predictive_maintenance_architecture_victoriametrics.png  # 系统架构图
│   ├── GRAFANA_DASHBOARD_INTEGRATION.md  # Grafana仪表板集成指南（新增）
│   └── css_electronics_grafana_dashboard_summary.md  # CSS Electronics方案总结（新增）
├── code/                               # 代码目录
│   ├── tbox_simulator.py              # T-BOX数据模拟器
│   ├── mqtt_to_victoriametrics_bridge.py  # MQTT到VictoriaMetrics数据桥接服务
│   ├── predictive_maintenance_engine.py   # 预测性维护分析引擎
│   ├── nixtla_timegpt_integration.py  # Nixtla TimeGPT集成示例
│   └── deploy_grafana_dashboard.py    # Grafana仪表板自动部署脚本（新增）
├── config/                             # 配置目录
│   ├── victoriametrics_deployment.yaml  # VictoriaMetrics集群部署配置
│   └── grafana_tractor_fleet_dashboard.json  # Grafana仪表板配置（新增）
└── tests/                              # 测试目录
    └── end_to_end_system_test.py      # 端到端系统集成测试
```

---

## 🚀 快速开始

### 环境要求

- **操作系统**: Ubuntu 22.04 或更高版本
- **Python**: 3.11+
- **Docker**: 20.10+
- **Docker Compose**: 2.0+

### 安装依赖

```bash
# 安装Python依赖
pip3 install pandas numpy requests

# 可选：安装Nixtla TimeGPT（需要API密钥）
pip3 install nixtla
```

### 启动系统

#### 1. 启动VictoriaMetrics集群

```bash
cd config/
docker-compose -f victoriametrics_deployment.yaml up -d
```

#### 2. 运行T-BOX数据模拟器

```bash
cd code/
python3 tbox_simulator.py
```

#### 3. 运行端到端测试

```bash
cd tests/
python3 end_to_end_system_test.py
```

#### 4. 访问Grafana仪表板

```
URL: http://localhost:3000
用户名: admin
密码: admin
```

---

## 📖 核心文档说明

### 1. 完整商业化方案 (`docs/final_commercial_proposal.md`)

这是**主文档**，包含完整的商业化方案，涵盖：
- 执行摘要
- 核心需求分析
- 系统总体架构
- T-BOX数据模拟方案
- 商业化落地策略
- 技术选型对比
- 附录：拖拉机系统关键信息摘要

### 2. 系统设计方案 (`docs/predictive_maintenance_system_design_victoriametrics.md`)

详细的技术设计方案，包含：
- 项目背景与目标
- 核心需求分析
- 系统总体架构（车端、云端、用户交互层）
- T-BOX数据模拟方案
- 商业化落地策略

### 3. 技术对比研究 (`docs/timeseries_tech_comparison.md`)

时序数据库和分析引擎的详细对比，包括：
- VictoriaMetrics vs TDengine vs InfluxDB
- Nixtla TimeGPT的特性和优势
- 技术选型建议

---

## 💻 核心代码说明

### 1. T-BOX数据模拟器 (`code/tbox_simulator.py`)

模拟拖拉机T-BOX采集的各类时序数据，包括：
- 发动机数据（转速、扭矩、温度、油压、油耗）
- 电池系统数据（SOC、SOH、电压、电流、温度）
- 车辆状态数据（车速、加速度、转向角、轮速、制动压力）
- 变速箱数据（档位、油温、油压）
- 液压系统数据（压力、油温、流量）
- GNSS定位数据（经纬度、高度、精度、卫星数）
- 传感器健康度数据（激光雷达、相机、IMU）
- 智驾系统数据（感知、规划、控制、计算资源）
- 故障日志（故障代码、严重程度）

**支持故障模式注入**：
- 发动机性能退化
- 电池老化
- 传感器漂移
- 液压系统泄漏

**运行示例**：
```bash
python3 tbox_simulator.py
```

### 2. MQTT到VictoriaMetrics数据桥接服务 (`code/mqtt_to_victoriametrics_bridge.py`)

将T-BOX通过MQTT上传的数据转换为Prometheus格式，并写入VictoriaMetrics。

**主要功能**：
- 接收MQTT消息
- 将JSON数据包转换为Prometheus文本格式
- 批量写入VictoriaMetrics
- 支持高并发写入

**运行示例**：
```bash
python3 mqtt_to_victoriametrics_bridge.py
```

### 3. 预测性维护分析引擎 (`code/predictive_maintenance_engine.py`)

实现多层次的故障预测和健康度评估。

**主要功能**：
- 健康度评分计算（0-100分）
- 基于统计方法的异常检测（3-sigma规则）
- 剩余使用寿命（RUL）预测（线性退化模型）
- 维护建议生成（根据健康度、RUL、异常情况）
- 智能告警系统（多级告警策略）

**运行示例**：
```bash
python3 predictive_maintenance_engine.py
```

### 4. Nixtla TimeGPT集成示例 (`code/nixtla_timegpt_integration.py`)

演示如何使用Nixtla TimeGPT进行长期趋势预测和异常检测。

**主要功能**：
- 长期趋势预测（7-30天）
- 异常检测
- 零样本学习能力演示
- 模拟预测（当TimeGPT不可用时）

**运行示例**：
```bash
python3 nixtla_timegpt_integration.py
```

---

## 🧪 测试说明

### 端到端系统集成测试 (`tests/end_to_end_system_test.py`)

完整的端到端测试，覆盖以下阶段：
1. 数据采集测试
2. 数据接入测试
3. 数据分析测试
4. 长期预测测试
5. 维护建议生成测试
6. 智能告警系统测试

**测试结果**：
- ✓ 所有测试阶段完成
- ✓ 采集数据包: 10个
- ✓ 生成指标: 590个
- ✓ 健康度评分: 100.0/100
- ✓ 维护优先级: LOW
- ✓ 告警方式: 1种

**运行测试**：
```bash
python3 end_to_end_system_test.py
```

---

## 🏗️ 系统架构

系统采用云-边协同架构，分为三层：

### 1. 车端（T-BOX）
- 数据采集模块
- 数据预处理
- 实时规则引擎
- 数据上传（MQTT）

### 2. 云端平台
- **数据接入层**: MQTT Broker + vmagent
- **时序数据湖**: VictoriaMetrics集群
- **数据处理层**: Apache Spark
- **多层次分析引擎**:
  - 长期趋势预测（Nixtla TimeGPT）
  - 中期异常检测（Darts + LSTM/Transformer）
  - 短期状态监控（Prophet）
- **核心服务层**:
  - 健康评估引擎
  - 故障诊断与根因分析
  - 维护建议引擎

### 3. 应用与用户交互层
- API网关
- 智能报警系统
- 维护工单系统
- 数据可视化（APP + Web）

---

## 📊 技术栈

| **组件** | **技术选型** | **选型理由** |
| :--- | :--- | :--- |
| 时序数据库 | VictoriaMetrics | 性能卓越，高基数处理能力强，与Prometheus生态兼容 |
| 时序预测大模型 | Nixtla TimeGPT | 强大的零样本学习能力，适合大规模车队管理 |
| 数据处理框架 | Apache Spark | 生态成熟，批处理和流处理能力兼备 |
| 消息队列 | MQTT (EMQ X) | 轻量级，专为物联网场景设计 |
| 数据可视化 | Grafana | 开源免费，与VictoriaMetrics无缝集成 |

---

## 💰 商业化价值

### 对用户的价值
- **减少非计划停机**: 提前预测故障，避免突发停机
- **降低维修成本**: 从被动维修转向主动预防
- **提高作业效率**: 保持设备最佳工作状态
- **延长设备寿命**: 通过科学的维护计划延长寿命
- **提升二手残值**: 完整的健康记录提升二手价值

### 对无人拖拉机厂商的价值
- **建立数据壁垒**: 积累海量运行数据，形成核心竞争力
- **提供增值服务**: 从卖产品到卖服务，开辟新收入来源
- **优化产品设计**: 基于真实数据持续改进产品
- **提升品牌竞争力**: 通过智能化服务提升品牌形象
- **降低售后成本**: 预测性维护减少紧急维修