#!/usr/bin/env python3
"""
拖拉机图片上传到Grafana容器脚本
将拖拉机图片复制到Grafana容器的public目录中
"""

import subprocess
import sys
import os
from pathlib import Path

def run_command(command, description):
    """执行命令并返回结果"""
    print(f"\n{'='*60}")
    print(f"[执行] {description}")
    print(f"[命令] {command}")
    print(f"{'='*60}")
    
    try:
        result = subprocess.run(
            command,
            shell=True,
            capture_output=True,
            text=True,
            timeout=30
        )
        
        if result.returncode == 0:
            print(f"[成功] {description}")
            if result.stdout:
                print(f"[输出]\n{result.stdout}")
            return True
        else:
            print(f"[失败] {description}")
            print(f"[错误] {result.stderr}")
            return False
            
    except subprocess.TimeoutExpired:
        print(f"[超时] {description}")
        return False
    except Exception as e:
        print(f"[异常] {str(e)}")
        return False

def main():
    print("\n" + "="*60)
    print("拖拉机图片上传到Grafana容器")
    print("="*60)
    
    # 检查图片文件是否存在
    image_path = Path(__file__).parent.parent / "assets" / "tractor_001.png"
    
    if not image_path.exists():
        print(f"[错误] 图片文件不存在: {image_path}")
        sys.exit(1)
    
    print(f"[信息] 图片文件: {image_path}")
    print(f"[信息] 文件大小: {image_path.stat().st_size / 1024:.2f} KB")
    
    # 步骤1: 检查Grafana容器是否运行
    print("\n步骤1: 检查Grafana容器状态")
    if not run_command(
        "docker ps --filter name=grafana --format '{{.Names}}\t{{.Status}}'",
        "检查Grafana容器"
    ):
        print("[错误] Grafana容器未运行，请先启动容器")
        sys.exit(1)
    
    # 步骤2: 在Grafana容器中创建图片目录
    print("\n步骤2: 创建Grafana图片目录")
    run_command(
        "docker exec grafana mkdir -p /usr/share/grafana/public/img/tractors",
        "创建图片目录"
    )
    
    # 步骤3: 复制图片到Grafana容器
    print("\n步骤3: 复制图片到Grafana容器")
    if not run_command(
        f"docker cp {image_path} grafana:/usr/share/grafana/public/img/tractors/tractor_001.png",
        "复制图片文件"
    ):
        print("[错误] 图片复制失败")
        sys.exit(1)
    
    # 步骤4: 验证图片是否成功复制
    print("\n步骤4: 验证图片")
    if not run_command(
        "docker exec grafana ls -lh /usr/share/grafana/public/img/tractors/",
        "验证图片文件"
    ):
        print("[警告] 无法验证图片文件")
    
    # 步骤5: 设置文件权限
    print("\n步骤5: 设置文件权限")
    run_command(
        "docker exec grafana chmod 644 /usr/share/grafana/public/img/tractors/tractor_001.png",
        "设置文件权限"
    )
    
    print("\n" + "="*60)
    print("图片上传成功！")
    print("="*60)
    print("\n图片访问路径:")
    print("  - Grafana内部路径: /public/img/tractors/tractor_001.png")
    print("  - 浏览器访问路径: http://localhost:3000/public/img/tractors/tractor_001.png")
    print("\n下一步:")
    print("  1. 在浏览器中访问: http://localhost:3000/public/img/tractors/tractor_001.png")
    print("  2. 确认图片可以正常显示")
    print("  3. 运行更新仪表板脚本: python update_dashboard_with_image.py")

if __name__ == "__main__":
    main()
