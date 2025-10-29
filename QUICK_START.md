# 🚀 快速启动指南

## 一键启动整个系统

### 方法1: 完整自动部署（推荐）

**双击运行**：
```
deploy_complete_system.bat
```

这个脚本会自动：
1. ✅ 启动所有Docker容器（VictoriaMetrics + Mosquitto + Grafana）
2. ✅ 部署Grafana仪表板
3. ✅ 启动MQTT桥接服务（新窗口）
4. ✅ 启动T-BOX模拟器（新窗口）

**等待1-2分钟后**：
- 打开浏览器: http://localhost:3000
- 用户名/密码: `admin/admin`
- 进入仪表板: "拖拉机数据监控 - CSS Electronics风格"
- 按 Ctrl+F5 强制刷新

---

### 方法2: 分步启动

#### 步骤1: 启动Docker服务
```
双击运行: start_all_services.bat
```

#### 步骤2: 部署仪表板
```powershell
cd code
python deploy_fixed_dashboard.py
```

#### 步骤3: 启动MQTT桥接服务（新窗口）
```powershell
cd code
python mqtt_to_victoriametrics_bridge.py
```

#### 步骤4: 启动T-BOX模拟器（新窗口）
```powershell
cd code
python tbox_simulator_realistic.py
```

---

## 停止系统

### 停止Python进程
在MQTT桥接服务和T-BOX模拟器窗口中按 `Ctrl+C`

### 停止Docker容器
```
双击运行: stop_all_services.bat
```

---

## 服务地址

| 服务 | 地址 | 说明 |
|------|------|------|
| Grafana | http://localhost:3000 | 用户名/密码: admin/admin |
| VictoriaMetrics vminsert | http://localhost:8480 | 数据写入端点 |
| VictoriaMetrics vmselect | http://localhost:8481 | 数据查询端点 |
| Mosquitto MQTT | localhost:1883 | MQTT代理 |
| Mosquitto WebSocket | localhost:9001 | WebSocket端点 |

---

## 验证系统运行

### 检查Docker容器状态
```powershell
cd config
docker-compose -f victoriametrics_deployment.yaml ps
```

应该看到所有容器都是 `Up` 状态：
- ✅ vminsert
- ✅ vmselect
- ✅ vmstorage-1
- ✅ vmstorage-2
- ✅ vmagent
- ✅ grafana
- ✅ mosquitto

### 检查数据是否写入
```powershell
cd code
python diagnose_metrics.py
```

应该看到所有指标都有数据。

---

## 故障排查

### 问题1: Docker容器启动失败
**检查**: Docker Desktop是否运行？
```powershell
docker info
```

**解决**: 启动Docker Desktop

### 问题2: 端口被占用
**检查**: 哪个端口被占用？
```powershell
netstat -ano | findstr "3000"
netstat -ano | findstr "1883"
netstat -ano | findstr "8480"
```

**解决**: 
- 停止占用端口的程序
- 或修改 `config/victoriametrics_deployment.yaml` 中的端口映射

### 问题3: Grafana显示"No data"
**检查**: 
1. MQTT桥接服务是否运行？
2. T-BOX模拟器是否运行？
3. 是否等待了1-2分钟让数据积累？

**解决**: 
```powershell
cd code
python diagnose_metrics.py
```
查看哪些指标缺失数据

### 问题4: 仪表板部署失败
**手动部署**:
```powershell
cd code
python deploy_fixed_dashboard.py
```

---

## 系统架构

```
T-BOX模拟器 (Python)
    ↓ MQTT (tractor/+/data)
Mosquitto MQTT Broker (Docker)
    ↓ 订阅
MQTT桥接服务 (Python)
    ↓ HTTP POST (/api/v1/import/prometheus)
VictoriaMetrics vminsert (Docker)
    ↓ 分发数据
VictoriaMetrics vmstorage x2 (Docker)
    ↑ 查询数据
VictoriaMetrics vmselect (Docker)
    ↑ PromQL查询
Grafana (Docker)
```

---

## 文件说明

| 文件 | 说明 |
|------|------|
| `deploy_complete_system.bat` | 一键完整部署 |
| `start_all_services.bat` | 启动Docker服务 |
| `stop_all_services.bat` | 停止Docker服务 |
| `config/victoriametrics_deployment.yaml` | Docker Compose配置 |
| `code/mqtt_to_victoriametrics_bridge.py` | MQTT桥接服务 |
| `code/tbox_simulator_realistic.py` | T-BOX模拟器 |
| `code/deploy_fixed_dashboard.py` | 仪表板部署脚本 |
| `code/diagnose_metrics.py` | 诊断工具 |

---

## 下一步

系统运行后，您可以：

1. **查看实时数据**
   - 打开Grafana仪表板
   - 查看16个监控面板
   - 观察数据实时更新（每5秒）

2. **添加更多车辆**
   - 修改 `tbox_simulator_realistic.py`
   - 更改 `vehicle_id`
   - 运行多个模拟器实例

3. **自定义仪表板**
   - 在Grafana中编辑面板
   - 调整颜色和布局
   - 添加新的可视化

4. **设置告警**
   - 配置Grafana告警规则
   - 设置阈值
   - 配置通知渠道

5. **集成真实硬件**
   - 替换模拟器为真实T-BOX
   - 配置MQTT连接
   - 验证数据格式

---

**版本**: v3.3 Final  
**更新日期**: 2025-10-29  
**状态**: ✅ 生产就绪
