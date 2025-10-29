# Windows部署常见错误及解决方案

**版本**: 2.1  
**日期**: 2025年10月29日

---

## 错误1: Mosquitto容器启动失败

### 错误信息
```
Error response from daemon: failed to create task for container: 
failed to create shim task: OCI runtime create failed: 
runc create failed: unable to start container process: 
error mounting "/run/desktop/mnt/host/d/tractor_pdm/config/mosquitto.conf" 
to rootfs at "/mosquitto/config/mosquitto.conf": 
not a directory: unknown: Are you trying to mount a directory onto a file 
(or vice-versa)?
```

### 原因分析
Docker Compose配置文件中试图挂载 `mosquitto.conf` 文件，但该文件不存在或路径不正确。

### 解决方案

#### 方法1: 使用默认配置（推荐）

最新版本的 `victoriametrics_deployment.yaml` 已经移除了配置文件挂载，使用Mosquitto镜像的默认配置。

**操作步骤**:
1. 确保使用最新版本的 `victoriametrics_deployment.yaml`
2. 重新启动容器：
   ```powershell
   docker-compose -f victoriametrics_deployment.yaml down
   docker-compose -f victoriametrics_deployment.yaml up -d
   ```

#### 方法2: 使用自定义配置

如果需要自定义Mosquitto配置：

1. 在 `config` 目录下创建 `mosquitto.conf` 文件：
   ```powershell
   cd D:\tractor_pdm\config
   New-Item -Path mosquitto.conf -ItemType File
   ```

2. 编辑 `mosquitto.conf`，添加以下内容：
   ```conf
   # Mosquitto MQTT Broker配置文件
   
   # 监听端口
   listener 1883
   protocol mqtt
   
   # WebSocket监听端口
   listener 9001
   protocol websockets
   
   # 允许匿名连接
   allow_anonymous true
   
   # 日志配置
   log_dest file /mosquitto/log/mosquitto.log
   log_dest stdout
   log_type all
   
   # 持久化配置
   persistence true
   persistence_location /mosquitto/data/
   
   # 自动保存间隔（秒）
   autosave_interval 300
   ```

3. 在 `victoriametrics_deployment.yaml` 中取消注释配置文件挂载：
   ```yaml
   mosquitto:
     volumes:
       - mosquitto-data:/mosquitto/data
       - mosquitto-logs:/mosquitto/log
       - ./mosquitto.conf:/mosquitto/config/mosquitto.conf  # 取消注释
   ```

4. 重新启动容器：
   ```powershell
   docker-compose -f victoriametrics_deployment.yaml down
   docker-compose -f victoriametrics_deployment.yaml up -d
   ```

---

## 错误2: Docker Compose版本警告

### 错误信息
```
time="2025-10-29T13:28:53+08:00" level=warning 
msg="D:\\tractor_pdm\\config\\victoriametrics_deployment.yaml: 
the attribute 'version' is obsolete, it will be ignored, 
please remove it to avoid potential confusion"
```

### 原因分析
Docker Compose v2不再需要 `version` 字段，但配置文件中仍包含此字段。

### 解决方案

这只是一个警告，不影响系统运行。最新版本的配置文件已经移除了 `version` 字段。

**操作步骤**（可选）:
1. 编辑 `victoriametrics_deployment.yaml`
2. 删除或注释掉 `version: '3.8'` 行
3. 保存文件

---

## 错误3: vmagent配置文件缺失

### 错误信息
```
Error: failed to read config file "/etc/vmagent/config.yml": 
open /etc/vmagent/config.yml: no such file or directory
```

### 原因分析
vmagent容器启动时尝试读取配置文件，但文件不存在。

### 解决方案

最新版本的配置文件已经移除了vmagent的配置文件依赖。

**如果仍遇到此错误**:
1. 确保使用最新版本的 `victoriametrics_deployment.yaml`
2. 检查vmagent的command配置，确保没有 `--promscrape.config` 参数
3. 重新启动容器

---

## 错误4: Grafana数据源配置失败

### 错误信息
Grafana启动时无法加载数据源配置文件。

### 原因分析
Grafana配置文件挂载路径不正确或文件不存在。

### 解决方案

#### 方法1: 使用自动部署脚本（推荐）

使用 `deploy_grafana_dashboard.py` 自动配置数据源：
```powershell
cd D:\tractor_pdm\code
python deploy_grafana_dashboard.py
```

#### 方法2: 手动配置

1. 访问Grafana: http://localhost:3000
2. 登录（admin/admin）
3. 进入 "Configuration" → "Data Sources"
4. 点击 "Add data source"
5. 选择 "Prometheus"
6. 配置：
   - Name: `VictoriaMetrics`
   - URL: `http://vmselect:8481/select/0/prometheus`
7. 点击 "Save & Test"

---

## 错误5: 容器无法通信

### 错误信息
容器之间无法相互访问，例如Grafana无法连接到VictoriaMetrics。

### 原因分析
容器不在同一个Docker网络中。

### 解决方案

1. 检查所有容器是否在同一个网络中：
   ```powershell
   docker network inspect vm-network
   ```

2. 如果网络不存在，重新创建：
   ```powershell
   docker network create vm-network
   ```

3. 重新启动所有容器：
   ```powershell
   docker-compose -f victoriametrics_deployment.yaml down
   docker-compose -f victoriametrics_deployment.yaml up -d
   ```

---

## 错误6: 端口已被占用

### 错误信息
```
Error starting userland proxy: listen tcp4 0.0.0.0:3000: 
bind: Only one usage of each socket address is normally permitted.
```

### 原因分析
端口3000（Grafana）或其他端口已被其他程序占用。

### 解决方案

#### 方法1: 查找并停止占用端口的程序

1. 查找占用端口的进程：
   ```powershell
   netstat -ano | findstr :3000
   ```

2. 记下PID（最后一列的数字）

3. 停止该进程：
   ```powershell
   taskkill /PID <PID> /F
   ```

#### 方法2: 修改端口映射

编辑 `victoriametrics_deployment.yaml`，修改端口映射：
```yaml
grafana:
  ports:
    - "3001:3000"  # 将主机端口改为3001
```

然后访问 http://localhost:3001

---

## 错误7: Docker Desktop未启动

### 错误信息
```
error during connect: This error may indicate that the docker daemon is not running
```

### 原因分析
Docker Desktop未启动或Docker服务未运行。

### 解决方案

1. 启动Docker Desktop：
   - 从开始菜单或桌面启动 "Docker Desktop"
   - 等待Docker图标变为绿色

2. 验证Docker状态：
   ```powershell
   docker info
   ```

3. 如果Docker Desktop无法启动，参考主文档中的"问题1: Docker Desktop无法启动"

---

## 错误8: WSL 2后端错误

### 错误信息
```
Docker Desktop requires a newer WSL kernel version
```

### 原因分析
WSL 2内核版本过旧。

### 解决方案

1. 更新WSL 2：
   ```powershell
   wsl --update
   ```

2. 重启电脑

3. 重新启动Docker Desktop

---

## 错误9: 虚拟化未启用

### 错误信息
```
Hardware assisted virtualization and data execution protection must be enabled in the BIOS
```

### 原因分析
CPU虚拟化功能未在BIOS中启用。

### 解决方案

1. 重启电脑，进入BIOS设置（通常按F2、F10、Del键）
2. 找到虚拟化选项（Intel VT-x 或 AMD-V）
3. 启用虚拟化
4. 保存并退出BIOS
5. 重新启动Docker Desktop

---

## 错误10: Python依赖缺失

### 错误信息
```
ModuleNotFoundError: No module named 'pandas'
```

### 原因分析
Python依赖包未安装。

### 解决方案

安装所需的Python包：
```powershell
pip install pandas numpy requests
```

如果需要使用Nixtla TimeGPT：
```powershell
pip install nixtla
```

---

## 完整的重新部署流程

如果遇到多个错误或系统状态混乱，建议完全清理并重新部署：

### 步骤1: 停止并清理所有容器

```powershell
cd D:\tractor_pdm\config
docker-compose -f victoriametrics_deployment.yaml down -v
```

### 步骤2: 清理Docker资源（可选）

```powershell
# 清理未使用的容器
docker container prune -f

# 清理未使用的网络
docker network prune -f

# 清理未使用的卷（警告：会删除所有数据）
docker volume prune -f
```

### 步骤3: 确保配置文件正确

1. 确认 `victoriametrics_deployment.yaml` 是最新版本
2. 确认配置文件中没有挂载不存在的文件
3. 确认所有路径使用Windows格式（`\`而不是`/`）

### 步骤4: 重新启动系统

```powershell
# 启动Docker容器
docker-compose -f victoriametrics_deployment.yaml up -d

# 等待30秒
Start-Sleep -Seconds 30

# 部署Grafana仪表板
cd ..\code
python deploy_grafana_dashboard.py

# 启动T-BOX模拟器
python tbox_simulator.py
```

---

## 验证系统状态

### 检查容器状态

```powershell
docker ps
```

应该看到以下容器正在运行：
- vmstorage-1
- vmstorage-2
- vminsert
- vmselect
- vmagent
- grafana
- mosquitto

### 检查容器日志

如果某个容器未运行，查看日志：
```powershell
docker logs <container_name>
```

例如：
```powershell
docker logs mosquitto
docker logs grafana
docker logs vmselect
```

### 测试服务可访问性

在浏览器中访问：
- Grafana: http://localhost:3000
- VictoriaMetrics: http://localhost:8481/select/0/prometheus/api/v1/query?query=up

### 测试MQTT连接

使用MQTT客户端工具（如MQTT Explorer）连接到：
- Host: localhost
- Port: 1883

---

## 获取帮助

如果以上解决方案无法解决您的问题，请：

1. 收集以下信息：
   - Windows版本
   - Docker Desktop版本
   - 错误信息截图
   - 相关容器日志

2. 参考完整文档：
   - `WINDOWS_DEPLOYMENT_GUIDE.md` - Windows部署指南
   - `GRAFANA_DASHBOARD_INTEGRATION.md` - Grafana集成指南
   - `README.md` - 系统总体说明

---

**祝您部署顺利！** 🎉
