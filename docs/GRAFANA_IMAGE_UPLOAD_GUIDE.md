# Grafana拖拉机图片上传指南

## 📋 概述

本指南介绍如何将拖拉机图片上传到Grafana容器，并在仪表板中显示。

---

## 🎯 方案说明

我们使用**Grafana内置图片服务器**方案：

- **优点**：不依赖外部服务，图片加载快，完全本地化
- **原理**：将图片复制到Grafana容器的 `/usr/share/grafana/public/img/` 目录
- **访问**：通过 `/public/img/` 路径在仪表板中引用图片

---

## 🚀 快速开始（Windows）

### 方法1: 一键自动化脚本（推荐）

```powershell
cd D:\tractor_pdm
.\scripts\upload_tractor_image.bat
```

这个脚本会自动完成：
1. ✅ 上传图片到Grafana容器
2. ✅ 更新仪表板配置
3. ✅ 重新部署仪表板

### 方法2: 分步执行

#### 步骤1: 上传图片到Grafana容器

```powershell
cd D:\tractor_pdm\code
python upload_tractor_image_to_grafana.py
```

**输出示例**：
```
╔══════════════════════════════════════════════════════════════╗
║     拖拉机图片上传到Grafana容器                              ║
╚══════════════════════════════════════════════════════════════╝

[信息] 图片文件: D:\tractor_pdm\assets\tractor_001.png
[信息] 文件大小: 245.67 KB

步骤1: 检查Grafana容器状态
[成功] 检查Grafana容器

步骤2: 创建Grafana图片目录
[成功] 创建图片目录

步骤3: 复制图片到Grafana容器
[成功] 复制图片文件

步骤4: 验证图片
[成功] 验证图片文件

步骤5: 设置文件权限
[成功] 设置文件权限

╔══════════════════════════════════════════════════════════════╗
║     ✓ 图片上传成功！                                        ║
╚══════════════════════════════════════════════════════════════╝
```

#### 步骤2: 更新仪表板配置

```powershell
python update_dashboard_with_image.py
```

**输出示例**：
```
╔══════════════════════════════════════════════════════════════╗
║     更新Grafana仪表板配置                                    ║
╚══════════════════════════════════════════════════════════════╝

[信息] 读取仪表板配置: D:\tractor_pdm\config\grafana_tractor_fleet_dashboard.json
[信息] 更新车辆信息面板图片...
[成功] 已更新车辆信息面板
[成功] 配置已保存

╔══════════════════════════════════════════════════════════════╗
║     ✓ 仪表板配置更新成功！                                  ║
╚══════════════════════════════════════════════════════════════╝
```

#### 步骤3: 重新部署仪表板

```powershell
python deploy_grafana_dashboard.py
```

#### 步骤4: 验证图片显示

1. 在浏览器中打开Grafana：http://localhost:3000
2. 进入"拖拉机车队管理仪表板"
3. 左上角"车辆信息"面板应该显示拖拉机图片

---

## 🔍 验证图片上传

### 方法1: 浏览器直接访问

在浏览器中访问：
```
http://localhost:3000/public/img/tractors/tractor_001.png
```

如果能看到拖拉机图片，说明上传成功！

### 方法2: Docker命令验证

```powershell
# 查看Grafana容器中的图片文件
docker exec grafana ls -lh /usr/share/grafana/public/img/tractors/

# 应该看到：
# -rw-r--r-- 1 root root 246K Jan 15 10:30 tractor_001.png
```

---

## 🖼️ 图片技术细节

### 图片信息

- **文件名**: `tractor_001.png`
- **格式**: PNG（支持透明背景）
- **尺寸**: 适配仪表板显示（自动缩放）
- **内容**: 油电混动无人拖拉机，配有太阳能板和自动驾驶传感器

### Grafana中的图片路径

| 位置 | 路径 |
|------|------|
| **容器内部路径** | `/usr/share/grafana/public/img/tractors/tractor_001.png` |
| **HTML引用路径** | `/public/img/tractors/tractor_001.png` |
| **浏览器访问路径** | `http://localhost:3000/public/img/tractors/tractor_001.png` |

### 仪表板HTML配置

```html
<div style='text-align:center; padding: 10px;'>
  <img src='/public/img/tractors/tractor_001.png' 
       style='width:100%; max-width:280px; border-radius: 8px; box-shadow: 0 2px 8px rgba(0,0,0,0.1);'/>
  <h3 style='margin-top: 15px; color: #333; font-size: 18px;'>$vehicle_id</h3>
  <p style='color: #666; font-size: 14px; margin-top: 5px;'>油电混动无人拖拉机</p>
</div>
```

---

## 🎨 自定义图片

### 使用自己的拖拉机图片

如果您想使用自己的拖拉机图片：

#### 步骤1: 准备图片

- **格式**: PNG或JPG
- **建议尺寸**: 800x600像素（宽x高）
- **建议大小**: < 500KB
- **背景**: 建议使用白色或透明背景

#### 步骤2: 替换图片文件

将您的图片文件复制到：
```
D:\tractor_pdm\assets\tractor_001.png
```

#### 步骤3: 重新上传

```powershell
cd D:\tractor_pdm
.\scripts\upload_tractor_image.bat
```

### 添加多个拖拉机图片

如果您有多个不同型号的拖拉机：

#### 步骤1: 准备多个图片

```
D:\tractor_pdm\assets\tractor_001.png  # 型号1
D:\tractor_pdm\assets\tractor_002.png  # 型号2
D:\tractor_pdm\assets\tractor_003.png  # 型号3
```

#### 步骤2: 批量上传

```powershell
# 上传所有图片
docker cp D:\tractor_pdm\assets\tractor_001.png grafana:/usr/share/grafana/public/img/tractors/
docker cp D:\tractor_pdm\assets\tractor_002.png grafana:/usr/share/grafana/public/img/tractors/
docker cp D:\tractor_pdm\assets\tractor_003.png grafana:/usr/share/grafana/public/img/tractors/
```

#### 步骤3: 修改仪表板配置

在仪表板HTML中根据 `$vehicle_id` 动态选择图片：

```html
<div style='text-align:center; padding: 10px;'>
  <img src='/public/img/tractors/$vehicle_id.png' 
       style='width:100%; max-width:280px;'/>
  <h3>$vehicle_id</h3>
</div>
```

这样每个拖拉机会显示对应的图片！

---

## ❓ 常见问题

### Q1: 图片不显示，显示破损图标

**原因**：
- 图片文件未成功上传到Grafana容器
- 图片路径配置错误
- Grafana容器重启后图片丢失

**解决方案**：
```powershell
# 重新上传图片
cd D:\tractor_pdm
.\scripts\upload_tractor_image.bat

# 验证图片
docker exec grafana ls -lh /usr/share/grafana/public/img/tractors/
```

### Q2: 浏览器显示404错误

**原因**：图片路径不正确

**解决方案**：
确认仪表板HTML中使用的是相对路径：
```html
<img src='/public/img/tractors/tractor_001.png' />
```

而不是绝对路径：
```html
<!-- 错误示例 -->
<img src='http://localhost:3000/public/img/tractors/tractor_001.png' />
```

### Q3: Docker容器重启后图片消失

**原因**：图片存储在容器内部，容器删除后图片会丢失

**解决方案**：

#### 方案A: 使用Docker卷挂载（推荐）

修改 `victoriametrics_deployment.yaml`：

```yaml
services:
  grafana:
    volumes:
      - grafana-storage:/var/lib/grafana
      - ./grafana_images:/usr/share/grafana/public/img/tractors  # 新增
```

然后将图片放到 `D:\tractor_pdm\config\grafana_images\` 目录。

#### 方案B: 每次重启后重新上传

```powershell
cd D:\tractor_pdm
.\scripts\upload_tractor_image.bat
```

### Q4: 图片太大，加载慢

**解决方案**：压缩图片

```powershell
# 使用Python压缩图片
pip install Pillow

# 运行压缩脚本
python -c "from PIL import Image; img = Image.open('tractor_001.png'); img.save('tractor_001_compressed.png', optimize=True, quality=85)"
```

### Q5: 想使用公司Logo或品牌图片

**解决方案**：

1. 准备公司Logo（PNG格式，建议透明背景）
2. 复制到 `D:\tractor_pdm\assets\company_logo.png`
3. 上传到Grafana：
```powershell
docker cp D:\tractor_pdm\assets\company_logo.png grafana:/usr/share/grafana/public/img/
```
4. 在仪表板中引用：
```html
<img src='/public/img/company_logo.png' style='width:100px;'/>
```

---

## 🔧 高级配置

### 使用Base64编码嵌入图片

如果您希望图片完全嵌入到仪表板配置中（不依赖外部文件）：

#### 步骤1: 将图片转换为Base64

```powershell
# 使用Python转换
python -c "import base64; print(base64.b64encode(open('tractor_001.png', 'rb').read()).decode())" > image_base64.txt
```

#### 步骤2: 在HTML中使用Base64

```html
<img src='data:image/png;base64,iVBORw0KGgoAAAANSUhEUgA...' />
```

**注意**：Base64编码会使配置文件变大，不推荐用于大图片。

### 使用外部图片URL

如果您的图片托管在公司服务器或云存储：

```html
<img src='https://your-company.com/images/tractor_001.png' />
```

**优点**：
- 不需要上传到Grafana容器
- 易于更新（修改服务器上的图片即可）

**缺点**：
- 依赖外部网络
- 如果外部服务不可用，图片无法显示

---

## 📚 参考资料

- [Grafana Text Panel文档](https://grafana.com/docs/grafana/latest/panels/visualizations/text/)
- [Grafana Static Files](https://grafana.com/docs/grafana/latest/setup-grafana/configure-grafana/#static_root_path)
- [Docker CP命令文档](https://docs.docker.com/engine/reference/commandline/cp/)

---

## 📞 技术支持

如果遇到问题，请检查：

1. ✅ Grafana容器是否正常运行：`docker ps | findstr grafana`
2. ✅ 图片文件是否存在：`docker exec grafana ls /usr/share/grafana/public/img/tractors/`
3. ✅ 图片是否可以通过浏览器访问：http://localhost:3000/public/img/tractors/tractor_001.png
4. ✅ 仪表板配置是否正确：检查HTML中的图片路径

---

**最后更新**: 2025-01-15
**版本**: v1.0
