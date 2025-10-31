# 油电混动无人拖拉机预测性维护系统

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

#### 1. 启动所有Docker容器

```bash
cd config/
docker-compose -f docker-compose-with-alerting.yml up -d
```

#### 2. 等待服务启动

```bash
# 等待30秒让Grafana完全启动
sleep 30
```

#### 3. 验证容器状态

```bash
docker ps --format "table {{.Names}}\t{{.Status}}"
```

应该看到9个容器都在运行：

✅ mosquitto

✅ vmstorage-1

✅ vmstorage-2

✅ vminsert

✅ vmselect

✅ vmagent

✅ vmalert

✅ alertmanager

✅ grafana


#### 4. 启动MQTT桥接

```bash
cd code/
python mqtt_to_victoriametrics_bridge.py
```

输出示例：
```
已连接到MQTT Broker
等待T-BOX数据...
```

#### 5. 启动notification_bridge

```
cd alerting\scripts
python notification_bridge_wechat.py

```

输出示例：
```
在Grafana中：
企业微信通知桥接服务
监听端口: 5001
```

#### 6. 运行全场景告警测试

```bash
cd code/
python tbox_full_alert_test.py
```

按Enter开始39分钟的自动化测试！

---

📊 测试期间观察

vmalert: http://127.0.0.1:8880

Alertmanager: http://localhost:9093

Grafana: http://localhost:3000

企业微信群: 等待告警通知
