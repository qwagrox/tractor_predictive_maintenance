# 拖拉机车队管理Grafana仪表板集成指南

**版本**: 2.1  
**日期**: 2025年10月29日  
**集成方案**: CSS Electronics风格 + VictoriaMetrics

---

## 概述

本文档介绍如何将CSS Electronics的车队管理仪表板设计理念集成到我们基于VictoriaMetrics的预测性维护系统中。通过结合CSS Electronics的优秀UI/UX设计和VictoriaMetrics的高性能时序数据库，我们创建了一套专为油电混动无人拖拉机车队设计的Grafana仪表板。

## CSS Electronics方案分析

CSS Electronics提供了一套成熟的车队管理可视化方案，其核心特点包括：

### 架构特点
- **数据流**: CANedge设备 → Azure Blob Storage → Azure Functions (DBC解码) → Parquet数据湖 → Azure Synapse → Grafana
- **存储格式**: Parquet列式存储，按设备/消息/日期分区
- **查询接口**: Azure Synapse提供SQL接口
- **成本优势**: 存储成本比InfluxDB低95%以上

### 仪表板设计亮点
1. **清晰的信息层次**: 顶部KPI卡片 → 中部时序图表 → 右侧地图和统计
2. **大号数字卡片**: 关键指标（速度、RPM、油耗、电池SOC）一目了然
3. **颜色编码**: 绿色=正常，黄色=警告，红色=危险
4. **图标增强**: 使用图标提升可读性和专业感
5. **GPS地图集成**: 实时显示车辆位置和行驶轨迹
6. **多维度可视化**: 时序图、直方图、高度图等多种图表类型

## 我们的集成方案

### 架构对比

| **组件** | **CSS Electronics** | **我们的方案** |
| :--- | :--- | :--- |
| 数据采集 | CANedge设备 | T-BOX模拟器 + MQTT |
| 数据传输 | WiFi/LTE → Azure Blob | MQTT → MQTT Broker |
| 数据解码 | Azure Functions | MQTT Bridge |
| 数据存储 | Parquet数据湖 | VictoriaMetrics集群 |
| 查询接口 | Azure Synapse (SQL) | VictoriaMetrics (PromQL) |
| 可视化 | Grafana + MS SQL数据源 | Grafana + Prometheus数据源 |

### 技术优势

我们的方案在保留CSS Electronics优秀设计的同时，提供了以下优势：

1. **更低的成本**: 自托管VictoriaMetrics，无需支付云查询费用
2. **更快的实时性**: 秒级数据写入和查询，无函数触发延迟
3. **更简单的部署**: Docker Compose一键部署，无需配置多个Azure服务
4. **更强的扩展性**: VictoriaMetrics专为高基数场景优化
5. **更好的生态**: 与Prometheus生态无缝集成

## 仪表板设计

### 整体布局

```
+------------------+------------------+------------------+------------------+
|   车辆图片       |   车速           |   发动机转速     |   油耗率         |
|   (4格宽)        |   (4格宽)        |   (4格宽)        |   (4格宽)        |
+------------------+------------------+------------------+------------------+
|                  |   发动机温度     |   机油压力       |   液压压力       |
|                  |   (4格宽)        |   (4格宽)        |   (4格宽)        |
+------------------+------------------+------------------+------------------+
|                        车速趋势图 (12格宽)                                |
|                                                                           |
+------------------+------------------+------------------+------------------+
|                  发动机转速与扭矩图 (12格宽)           |   GPS地图        |
|                                                         |   (12格宽)       |
+------------------+------------------+------------------+------------------+
|   发动机温度图   |   液压系统图     |   加速度直方图   |                  |
|   (8格宽)        |   (8格宽)        |   (8格宽)        |                  |
+------------------+------------------+------------------+------------------+
```

### 面板详细说明

#### 1. 车辆信息面板
- **类型**: Text面板
- **内容**: 车辆图片 + 车辆ID
- **位置**: 左上角
- **尺寸**: 4格宽 × 6格高

#### 2. 关键指标卡片（Stat面板）
包含以下KPI卡片：
- **车速**: 绿色/黄色/红色阈值（0/10/15 km/h）
- **发动机转速**: 绿色/黄色/红色阈值（0/2000/2500 RPM）
- **油耗率**: 绿色/黄色/红色阈值（0/18/22 L/h）
- **电池SOC**: 红色/黄色/绿色阈值（0/20/50%）
- **电池SOH**: 红色/黄色/绿色阈值（0/80/90%）
- **发动机温度**: 蓝色/绿色/黄色/红色阈值（0/80/95/105°C）
- **机油压力**: 红色/黄色/绿色阈值（0/3/4 bar）
- **液压压力**: 红色/黄色/绿色阈值（0/150/170 bar）
- **GNSS卫星数**: 红色/黄色/绿色阈值（0/8/12个）
- **定位精度**: 绿色/黄色/红色阈值（0/0.05/0.1 m）

#### 3. 时序图表（Time Series面板）
- **车速趋势**: 平滑曲线，填充透明度10%
- **发动机转速与扭矩**: 双Y轴，左轴RPM，右轴Nm
- **电池状态**: SOC、电压、电流三条曲线
- **发动机温度**: 单曲线，带阈值告警线
- **液压系统**: 液压压力和液压油温双Y轴

#### 4. GPS地图（Geomap面板）
- **类型**: Geomap面板
- **数据源**: 纬度和经度指标
- **功能**: 显示实时位置和历史轨迹
- **位置**: 右侧中部

#### 5. 统计图表
- **加速度直方图**: 显示加速度分布

### 变量配置

仪表板支持以下变量：

1. **vehicle_id**: 车辆ID选择器
   - 类型: Query变量
   - 查询: `label_values(tractor_operation_hours, vehicle_id)`
   - 多选: 否

2. **interval**: 时间粒度选择器
   - 类型: Interval变量
   - 选项: 1分钟、5分钟、10分钟、30分钟、1小时
   - 自动模式: 开启

## 部署步骤

### 前置条件

1. VictoriaMetrics集群已部署并运行
2. Grafana已部署并运行（通过victoriametrics_deployment.yaml）
3. T-BOX模拟器正在生成数据

### 自动部署

使用提供的自动部署脚本：

```bash
# 1. 确保VictoriaMetrics和Grafana正在运行
docker-compose -f victoriametrics_deployment.yaml up -d

# 2. 等待Grafana启动（约30秒）
sleep 30

# 3. 运行自动部署脚本
python3 deploy_grafana_dashboard.py
```

脚本将自动完成以下操作：
- 测试Grafana连接
- 创建VictoriaMetrics数据源
- 导入拖拉机车队管理仪表板

### 手动部署

如果需要手动部署，请按以下步骤操作：

#### 步骤1: 访问Grafana

```
URL: http://localhost:3000
用户名: admin
密码: admin
```

#### 步骤2: 添加VictoriaMetrics数据源

1. 点击左侧菜单 "Configuration" → "Data Sources"
2. 点击 "Add data source"
3. 选择 "Prometheus"
4. 配置如下：
   - Name: `VictoriaMetrics`
   - URL: `http://vmselect:8481/select/0/prometheus`
   - Access: `Server (default)`
   - HTTP Method: `POST`
5. 点击 "Save & Test"

#### 步骤3: 导入仪表板

1. 点击左侧菜单 "+" → "Import"
2. 点击 "Upload JSON file"
3. 选择 `grafana_tractor_fleet_dashboard.json`
4. 选择数据源: `VictoriaMetrics`
5. 点击 "Import"

## 数据指标映射

### VictoriaMetrics指标命名规范

所有指标遵循以下命名规范：

```
tractor_{subsystem}_{metric_name}{labels}
```

示例：
```
tractor_engine_rpm{vehicle_id="TRACTOR_001",device_id="DEVICE_001"}
tractor_battery_soc{vehicle_id="TRACTOR_001",device_id="DEVICE_001"}
```

### 完整指标列表

#### 发动机指标
- `tractor_engine_rpm`: 发动机转速 (RPM)
- `tractor_engine_torque`: 发动机扭矩 (Nm)
- `tractor_engine_coolant_temp`: 冷却液温度 (°C)
- `tractor_engine_oil_pressure`: 机油压力 (bar)
- `tractor_engine_fuel_consumption_rate`: 油耗率 (L/h)

#### 电池指标
- `tractor_battery_soc`: 电池SOC (%)
- `tractor_battery_soh`: 电池SOH (%)
- `tractor_battery_voltage`: 电池电压 (V)
- `tractor_battery_current`: 电池电流 (A)
- `tractor_battery_temperature`: 电池温度 (°C)

#### 车辆状态指标
- `tractor_vehicle_speed`: 车速 (km/h)
- `tractor_vehicle_acceleration`: 加速度 (m/s²)
- `tractor_vehicle_steering_angle`: 转向角 (度)

#### 变速箱指标
- `tractor_transmission_gear`: 档位
- `tractor_transmission_oil_temp`: 变速箱油温 (°C)

#### 液压系统指标
- `tractor_hydraulic_pressure`: 液压压力 (bar)
- `tractor_hydraulic_oil_temp`: 液压油温 (°C)
- `tractor_hydraulic_flow_rate`: 液压流量 (L/min)

#### GNSS指标
- `tractor_gnss_latitude`: 纬度 (度)
- `tractor_gnss_longitude`: 经度 (度)
- `tractor_gnss_altitude`: 海拔 (m)
- `tractor_gnss_positioning_accuracy`: 定位精度 (m)
- `tractor_gnss_satellite_count`: 卫星数量

#### 传感器健康度指标
- `tractor_sensor_lidar_health`: 激光雷达健康度 (0-100)
- `tractor_sensor_camera_health`: 相机健康度 (0-100)
- `tractor_sensor_imu_health`: IMU健康度 (0-100)

#### 智驾系统指标
- `tractor_autopilot_cpu_usage`: CPU占用率 (%)
- `tractor_autopilot_gpu_usage`: GPU占用率 (%)
- `tractor_autopilot_memory_usage`: 内存占用率 (%)

#### 运行时长指标
- `tractor_operation_hours`: 累计运行时长 (小时)

## 使用指南

### 查看特定车辆数据

1. 在仪表板顶部找到 "车辆ID" 下拉菜单
2. 选择要查看的车辆（如 TRACTOR_001）
3. 仪表板将自动刷新并显示该车辆的数据

### 调整时间范围

1. 点击右上角的时间范围选择器
2. 选择预设范围（如 "Last 6 hours"）或自定义范围
3. 仪表板将显示选定时间范围内的数据

### 调整时间粒度

1. 在仪表板顶部找到 "时间粒度" 下拉菜单
2. 选择合适的粒度（1分钟、5分钟、10分钟等）
3. 时序图表将按选定粒度聚合数据

### 缩放和导航

- **缩放**: 在时序图表上拖动鼠标选择区域
- **重置缩放**: 点击图表右上角的 "Reset zoom" 按钮
- **平移**: 按住Shift键并拖动鼠标

### 查看详细数据

- 将鼠标悬停在图表上可查看精确数值
- 点击图例可隐藏/显示特定数据系列

## 扩展功能

### 添加告警规则

可以在Grafana中为关键指标配置告警规则：

1. 编辑面板
2. 切换到 "Alert" 标签
3. 配置告警条件（如 "当发动机温度 > 105°C 持续5分钟"）
4. 配置通知渠道（邮件、Slack、钉钉等）

### 创建自定义面板

可以根据需要添加新的面板：

1. 点击仪表板右上角的 "Add panel"
2. 选择面板类型（Time series、Stat、Gauge等）
3. 配置查询（使用PromQL）
4. 调整样式和阈值
5. 保存面板

### 导出和分享

- **导出仪表板**: Dashboard settings → JSON Model → Copy to clipboard
- **分享快照**: 点击 "Share" → "Snapshot" → "Publish to snapshots.raintank.io"
- **嵌入面板**: 点击面板标题 → "Share" → "Embed"

## 性能优化

### 查询优化

1. **使用合适的时间粒度**: 避免在长时间范围内使用过细的粒度
2. **限制数据点数量**: 使用 `max_data_points` 参数
3. **使用缓存**: VictoriaMetrics自动缓存查询结果

### 仪表板优化

1. **减少面板数量**: 每个仪表板建议不超过20个面板
2. **使用变量**: 避免创建大量相似的仪表板
3. **合理设置刷新间隔**: 根据实际需求设置（5s、10s、30s等）

## 故障排查

### 数据源连接失败

**问题**: Grafana无法连接到VictoriaMetrics

**解决方案**:
1. 检查VictoriaMetrics是否正在运行: `docker ps | grep victoria`
2. 检查网络连接: `curl http://vmselect:8481/select/0/prometheus/api/v1/query?query=up`
3. 检查数据源配置中的URL是否正确

### 没有数据显示

**问题**: 仪表板面板显示 "No data"

**解决方案**:
1. 检查T-BOX模拟器是否正在运行
2. 检查MQTT桥接器是否正在运行
3. 验证数据是否已写入VictoriaMetrics: 
   ```bash
   curl 'http://localhost:8481/select/0/prometheus/api/v1/query?query=tractor_vehicle_speed'
   ```
4. 检查仪表板变量是否选择了有效的车辆ID

### 查询速度慢

**问题**: 仪表板加载缓慢

**解决方案**:
1. 减少查询的时间范围
2. 增加时间粒度（如从1分钟改为5分钟）
3. 检查VictoriaMetrics资源使用情况: `docker stats`
4. 考虑增加VictoriaMetrics的CPU和内存资源

## 参考资源

- **CSS Electronics Grafana-Synapse指南**: https://www.csselectronics.com/pages/vehicle-fleet-dashboards-grafana-synapse-azure
- **VictoriaMetrics文档**: https://docs.victoriametrics.com/
- **Grafana文档**: https://grafana.com/docs/grafana/latest/
- **PromQL查询语言**: https://prometheus.io/docs/prometheus/latest/querying/basics/

## 下一步计划

1. **集成预测性维护面板**: 添加健康度评分、RUL预测、异常检测面板
2. **开发移动端适配**: 优化仪表板在移动设备上的显示
3. **添加更多可视化类型**: 热力图、桑基图、网络图等
4. **集成告警系统**: 与钉钉、企业微信、短信平台集成
5. **开发自定义插件**: 开发专用的拖拉机可视化插件

---

**备注**: 本文档提供了完整的Grafana仪表板集成方案，结合了CSS Electronics的优秀设计理念和VictoriaMetrics的高性能优势。所有配置文件和脚本均已测试通过，可直接用于生产环境。
