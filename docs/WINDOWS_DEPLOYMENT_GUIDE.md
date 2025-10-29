# Windows 11 部署指南 - 拖拉机预测性维护系统

**版本**: 2.1  
**适用系统**: Windows 11 / Windows 10  
**日期**: 2025年10月29日

---

## 📋 目录

1. [环境准备](#环境准备)
2. [安装Docker Desktop](#安装docker-desktop)
3. [安装Python](#安装python)
4. [下载并解压交付包](#下载并解压交付包)
5. [部署VictoriaMetrics和Grafana](#部署victoriametrics和grafana)
6. [部署Grafana仪表板](#部署grafana仪表板)
7. [运行T-BOX数据模拟器](#运行t-box数据模拟器)
8. [访问Grafana仪表板](#访问grafana仪表板)
9. [运行系统测试](#运行系统测试)
10. [常见问题排查](#常见问题排查)

---

## 环境准备

### 系统要求

- **操作系统**: Windows 11 或 Windows 10 (64位)
- **处理器**: 支持虚拟化的64位处理器
- **内存**: 至少8GB RAM（推荐16GB）
- **硬盘**: 至少20GB可用空间
- **网络**: 可访问互联网

### 需要安装的软件

1. **Docker Desktop for Windows** - 容器化平台
2. **Python 3.11+** - 运行Python脚本
3. **Git for Windows** (可选) - 版本控制工具

---

## 安装Docker Desktop

### 步骤1: 下载Docker Desktop

1. 访问Docker官网: https://www.docker.com/products/docker-desktop/
2. 点击 "Download for Windows"
3. 下载 `Docker Desktop Installer.exe`

### 步骤2: 安装Docker Desktop

1. 双击运行 `Docker Desktop Installer.exe`
2. 在安装向导中：
   - ✅ 勾选 "Use WSL 2 instead of Hyper-V" (推荐)
   - ✅ 勾选 "Add shortcut to desktop"
3. 点击 "OK" 开始安装
4. 安装完成后，点击 "Close and restart" 重启电脑

### 步骤3: 启动Docker Desktop

1. 重启后，Docker Desktop会自动启动
2. 如果没有自动启动，从桌面或开始菜单启动 "Docker Desktop"
3. 首次启动需要接受服务条款
4. 等待Docker Engine启动（状态栏显示绿色表示已启动）

### 步骤4: 验证Docker安装

打开 **PowerShell** 或 **命令提示符**，运行：

```powershell
docker --version
docker-compose --version
```

应该看到类似输出：
```
Docker version 24.0.6, build ed223bc
Docker Compose version v2.23.0
```

### 步骤5: 配置Docker资源

1. 右键点击系统托盘中的Docker图标
2. 选择 "Settings" → "Resources"
3. 建议配置：
   - **CPUs**: 4核（根据您的CPU调整）
   - **Memory**: 8GB（根据您的内存调整）
   - **Disk image size**: 64GB
4. 点击 "Apply & Restart"

---

## 安装Python

### 步骤1: 下载Python

1. 访问Python官网: https://www.python.org/downloads/
2. 点击 "Download Python 3.11.x" (或更高版本)
3. 下载 `python-3.11.x-amd64.exe`

### 步骤2: 安装Python

1. 双击运行安装程序
2. **重要**: ✅ 勾选 "Add Python to PATH"
3. 选择 "Install Now"
4. 等待安装完成

### 步骤3: 验证Python安装

打开 **PowerShell** 或 **命令提示符**，运行：

```powershell
python --version
pip --version
```

应该看到类似输出：
```
Python 3.11.6
pip 23.3.1 from ...
```

### 步骤4: 安装Python依赖

```powershell
pip install pandas numpy requests
```

---

## 下载并解压交付包

### 方法1: 从交付包解压

1. 将 `predictive_maintenance_delivery_v2.1.tar.gz` 复制到您的工作目录，例如：
   ```
   C:\Projects\tractor-maintenance\
   ```

2. 解压文件：
   - 如果安装了7-Zip，右键点击文件 → "7-Zip" → "Extract Here"
   - 如果安装了WinRAR，右键点击文件 → "Extract Here"
   - 或使用PowerShell命令：
     ```powershell
     tar -xzf predictive_maintenance_delivery_v2.1.tar.gz
     ```

3. 解压后的目录结构：
   ```
   C:\Projects\tractor-maintenance\
   └── delivery_package\
       ├── README.md
       ├── DELIVERY_CHECKLIST.md
       ├── code\
       ├── config\
       ├── docs\
       └── tests\
   ```

### 方法2: 手动创建目录结构

如果无法解压，可以手动创建目录并复制文件：

```powershell
# 创建目录结构
mkdir C:\Projects\tractor-maintenance\delivery_package
cd C:\Projects\tractor-maintenance\delivery_package
mkdir code, config, docs, tests

# 然后手动复制文件到对应目录
```

---

## 部署VictoriaMetrics和Grafana

### 步骤1: 进入配置目录

打开 **PowerShell**，运行：

```powershell
cd C:\Projects\tractor-maintenance\delivery_package\config
```

### 步骤2: 启动Docker容器

```powershell
docker-compose -f victoriametrics_deployment.yaml up -d
```

**说明**:
- `-d` 表示后台运行
- 首次运行会下载Docker镜像，可能需要几分钟

### 步骤3: 验证容器状态

```powershell
docker ps
```

应该看到以下容器正在运行：
- `vmstorage` - VictoriaMetrics存储节点
- `vminsert` - VictoriaMetrics写入代理
- `vmselect` - VictoriaMetrics查询代理
- `grafana` - Grafana可视化平台
- `mosquitto` - MQTT消息代理

### 步骤4: 等待服务启动

```powershell
# 等待30秒让Grafana完全启动
Start-Sleep -Seconds 30
```

### 步骤5: 验证服务可访问

在浏览器中访问以下URL：

- **Grafana**: http://localhost:3000
  - 用户名: `admin`
  - 密码: `admin`
  
- **VictoriaMetrics查询接口**: http://localhost:8481/select/0/prometheus/api/v1/query?query=up

如果能正常访问，说明服务部署成功！

---

## 部署Grafana仪表板

### 步骤1: 进入代码目录

```powershell
cd C:\Projects\tractor-maintenance\delivery_package\code
```

### 步骤2: 运行自动部署脚本

```powershell
python deploy_grafana_dashboard.py
```

### 步骤3: 查看部署结果

脚本会自动完成以下操作：
1. ✓ 测试Grafana连接
2. ✓ 创建VictoriaMetrics数据源
3. ✓ 导入拖拉机车队管理仪表板

成功输出示例：
```
============================================================
拖拉机车队管理Grafana仪表板自动部署
============================================================

1. 测试Grafana连接...
✓ 成功连接到Grafana: http://localhost:3000

2. 创建VictoriaMetrics数据源...
✓ 成功创建数据源: VictoriaMetrics

3. 导入拖拉机车队管理仪表板...
✓ 成功导入仪表板: 拖拉机车队管理仪表板
  访问URL: http://localhost:3000/d/...

============================================================
✓ 仪表板部署成功!
============================================================
```

---

## 运行T-BOX数据模拟器

### 步骤1: 打开新的PowerShell窗口

保持之前的窗口运行，打开一个新的PowerShell窗口。

### 步骤2: 进入代码目录

```powershell
cd C:\Projects\tractor-maintenance\delivery_package\code
```

### 步骤3: 运行T-BOX模拟器

```powershell
python tbox_simulator.py
```

### 步骤4: 观察输出

模拟器会持续生成并发送数据：
```
========================================
拖拉机T-BOX数据模拟器
========================================
配置:
  车辆ID: TRACTOR_001
  设备ID: DEVICE_001
  MQTT Broker: localhost:1883
  发送间隔: 1.0秒
  运行时长: 3600秒
========================================

[2025-10-29 14:00:01] 发送数据包 #1
  车速: 8.5 km/h
  发动机转速: 1850 RPM
  电池SOC: 85.2%
  ...

[2025-10-29 14:00:02] 发送数据包 #2
  车速: 9.1 km/h
  发动机转速: 1920 RPM
  电池SOC: 85.1%
  ...
```

**提示**: 
- 按 `Ctrl+C` 可以停止模拟器
- 模拟器默认运行1小时后自动停止
- 可以修改 `tbox_simulator.py` 中的参数来调整运行时长

---

## 访问Grafana仪表板

### 步骤1: 打开浏览器

访问: http://localhost:3000

### 步骤2: 登录Grafana

- 用户名: `admin`
- 密码: `admin`

首次登录会提示修改密码，可以选择 "Skip" 跳过。

### 步骤3: 打开仪表板

1. 点击左侧菜单 "Dashboards" (四个方块图标)
2. 点击 "Browse"
3. 找到并点击 "拖拉机车队管理仪表板"

### 步骤4: 选择车辆

1. 在仪表板顶部找到 "车辆ID" 下拉菜单
2. 选择 "TRACTOR_001"
3. 仪表板会自动刷新并显示该车辆的实时数据

### 步骤5: 调整时间范围

1. 点击右上角的时间范围选择器（默认显示 "Last 6 hours"）
2. 选择 "Last 5 minutes" 或 "Last 15 minutes" 查看最近的数据
3. 或点击 "Custom range" 自定义时间范围

### 步骤6: 探索仪表板

仪表板包含以下面板：
- **车辆信息**: 显示车辆图片和ID
- **关键指标卡片**: 车速、RPM、油耗、电池SOC/SOH等
- **时序图表**: 车速趋势、发动机状态、电池状态等
- **GPS地图**: 实时位置和轨迹（如果有GPS数据）
- **统计图表**: 加速度直方图

---

## 运行系统测试

### 步骤1: 进入测试目录

```powershell
cd C:\Projects\tractor-maintenance\delivery_package\tests
```

### 步骤2: 运行端到端测试

```powershell
python end_to_end_system_test.py
```

### 步骤3: 查看测试结果

测试会依次执行以下阶段：
1. ✓ 数据采集测试
2. ✓ 数据接入测试
3. ✓ 数据分析测试
4. ✓ 长期预测测试
5. ✓ 维护建议生成测试
6. ✓ 智能告警系统测试

成功输出示例：
```
========================================
端到端系统集成测试
========================================

阶段1: 数据采集测试
✓ 成功生成 10 个数据包

阶段2: 数据接入测试
✓ 成功转换为 590 个时序指标

阶段3: 数据分析测试
✓ 健康度评分: 100.0/100

...

========================================
✓ 所有测试通过!
========================================
```

---

## 常见问题排查

### 问题1: Docker Desktop无法启动

**症状**: Docker Desktop启动失败，显示 "Docker Engine starting..." 一直不变

**解决方案**:
1. 确保已启用Windows虚拟化功能：
   - 打开 "控制面板" → "程序" → "启用或关闭Windows功能"
   - 勾选 "Hyper-V" 或 "适用于Linux的Windows子系统"
   - 重启电脑

2. 如果使用WSL 2，确保已安装WSL 2：
   ```powershell
   wsl --install
   wsl --set-default-version 2
   ```

3. 重启Docker Desktop：
   - 右键点击系统托盘中的Docker图标
   - 选择 "Quit Docker Desktop"
   - 重新启动Docker Desktop

### 问题2: docker-compose命令不存在

**症状**: 运行 `docker-compose` 时提示 "命令不存在"

**解决方案**:
使用 `docker compose`（没有连字符）代替：
```powershell
docker compose -f victoriametrics_deployment.yaml up -d
```

### 问题3: Python脚本无法运行

**症状**: 运行Python脚本时提示 "python不是内部或外部命令"

**解决方案**:
1. 确保安装Python时勾选了 "Add Python to PATH"
2. 如果没有勾选，手动添加Python到环境变量：
   - 右键 "此电脑" → "属性" → "高级系统设置"
   - 点击 "环境变量"
   - 在 "系统变量" 中找到 "Path"，点击 "编辑"
   - 添加Python安装路径（例如 `C:\Python311\`）
   - 点击 "确定" 保存
3. 重新打开PowerShell窗口

### 问题4: 无法访问Grafana

**症状**: 浏览器访问 http://localhost:3000 无法打开

**解决方案**:
1. 检查Docker容器是否正在运行：
   ```powershell
   docker ps | findstr grafana
   ```

2. 检查Grafana日志：
   ```powershell
   docker logs grafana
   ```

3. 确保端口3000没有被占用：
   ```powershell
   netstat -ano | findstr :3000
   ```

4. 如果端口被占用，可以修改 `victoriametrics_deployment.yaml` 中的端口映射：
   ```yaml
   grafana:
     ports:
       - "3001:3000"  # 改为3001端口
   ```

### 问题5: T-BOX模拟器无法连接到MQTT

**症状**: T-BOX模拟器显示 "无法连接到MQTT Broker"

**解决方案**:
1. 检查Mosquitto容器是否正在运行：
   ```powershell
   docker ps | findstr mosquitto
   ```

2. 检查Mosquitto日志：
   ```powershell
   docker logs mosquitto
   ```

3. 确保端口1883没有被占用：
   ```powershell
   netstat -ano | findstr :1883
   ```

### 问题6: Grafana仪表板没有数据

**症状**: Grafana仪表板显示 "No data"

**解决方案**:
1. 确保T-BOX模拟器正在运行
2. 检查VictoriaMetrics是否有数据：
   - 访问: http://localhost:8481/select/0/prometheus/api/v1/query?query=tractor_vehicle_speed
   - 应该看到JSON格式的查询结果

3. 检查Grafana数据源配置：
   - 进入Grafana → "Configuration" → "Data Sources"
   - 点击 "VictoriaMetrics"
   - 点击 "Save & Test"，确保显示绿色的成功消息

4. 调整时间范围：
   - 点击右上角的时间选择器
   - 选择 "Last 5 minutes" 或更短的时间范围

### 问题7: 防火墙阻止连接

**症状**: 无法访问本地服务，或Docker容器无法通信

**解决方案**:
1. 临时关闭Windows防火墙测试：
   - 打开 "Windows安全中心" → "防火墙和网络保护"
   - 关闭 "专用网络" 和 "公用网络" 的防火墙
   - 测试是否能访问服务

2. 如果关闭防火墙后能访问，则需要添加防火墙规则：
   - 打开 "Windows Defender 防火墙" → "高级设置"
   - 点击 "入站规则" → "新建规则"
   - 选择 "端口"，添加端口 3000, 8481, 1883
   - 允许连接

---

## 停止和清理系统

### 停止所有服务

```powershell
# 停止Docker容器
cd C:\Projects\tractor-maintenance\delivery_package\config
docker-compose -f victoriametrics_deployment.yaml down

# 停止T-BOX模拟器（在运行模拟器的窗口中按 Ctrl+C）
```

### 清理数据

如果需要清理所有数据并重新开始：

```powershell
# 停止并删除容器和卷
docker-compose -f victoriametrics_deployment.yaml down -v

# 重新启动
docker-compose -f victoriametrics_deployment.yaml up -d
```

### 完全卸载

如果需要完全卸载系统：

1. 停止并删除Docker容器：
   ```powershell
   docker-compose -f victoriametrics_deployment.yaml down -v
   ```

2. 删除项目目录：
   ```powershell
   Remove-Item -Recurse -Force C:\Projects\tractor-maintenance
   ```

3. 卸载Docker Desktop（可选）：
   - 打开 "设置" → "应用" → "应用和功能"
   - 找到 "Docker Desktop"，点击 "卸载"

---

## 下一步

恭喜！您已经成功在Windows 11上部署了完整的拖拉机预测性维护系统。

接下来您可以：

1. **探索Grafana仪表板**: 熟悉各个面板和功能
2. **定制仪表板**: 根据实际需求调整面板布局和阈值
3. **集成真实数据**: 将T-BOX模拟器替换为真实的车载设备
4. **添加更多车辆**: 修改模拟器配置，模拟多台拖拉机
5. **配置告警**: 在Grafana中设置告警规则
6. **开发自定义功能**: 基于现有代码开发新功能

---

## 技术支持

如有任何问题，请参考：
- **完整文档**: `delivery_package\docs\`
- **交付清单**: `delivery_package\DELIVERY_CHECKLIST.md`
- **Grafana集成指南**: `delivery_package\docs\GRAFANA_DASHBOARD_INTEGRATION.md`

---

**祝您使用愉快！** 🎉
