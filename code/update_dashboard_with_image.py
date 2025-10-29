#!/usr/bin/env python3
"""
更新Grafana仪表板配置，使用本地拖拉机图片
"""

import json
import sys
from pathlib import Path

def main():
    print("\n" + "="*60)
    print("更新Grafana仪表板配置")
    print("="*60)
    
    # 读取仪表板配置文件
    dashboard_path = Path(__file__).parent.parent / "config" / "grafana_tractor_fleet_dashboard.json"
    
    print(f"[信息] 读取仪表板配置: {dashboard_path}")
    
    with open(dashboard_path, 'r', encoding='utf-8') as f:
        config = json.load(f)
    
    # 更新车辆信息面板的图片URL
    print("\n[信息] 更新车辆信息面板图片...")
    
    # 找到车辆信息面板（id=1）
    for panel in config['dashboard']['panels']:
        if panel.get('id') == 1 and panel.get('title') == '车辆信息':
            old_content = panel['options']['content']
            
            # 新的HTML内容，使用Grafana本地图片
            new_content = """<div style='text-align:center; padding: 10px;'>
  <img src='/public/img/tractors/tractor_001.png' style='width:100%; max-width:280px; border-radius: 8px; box-shadow: 0 2px 8px rgba(0,0,0,0.1);'/>
  <h3 style='margin-top: 15px; color: #333; font-size: 18px;'>$vehicle_id</h3>
  <p style='color: #666; font-size: 14px; margin-top: 5px;'>油电混动无人拖拉机</p>
</div>"""
            
            panel['options']['content'] = new_content
            
            print(f"[成功] 已更新车辆信息面板")
            print(f"[旧配置] {old_content[:80]}...")
            print(f"[新配置] {new_content[:80]}...")
            break
    else:
        print("[警告] 未找到车辆信息面板")
    
    # 保存更新后的配置
    print(f"\n[信息] 保存更新后的配置...")
    
    with open(dashboard_path, 'w', encoding='utf-8') as f:
        json.dump(config, f, ensure_ascii=False, indent=2)
    
    print(f"[成功] 配置已保存到: {dashboard_path}")
    
    print("\n" + "="*60)
    print("仪表板配置更新成功！")
    print("="*60)
    print("\n下一步:")
    print("  1. 重新部署Grafana仪表板")
    print("     命令: python deploy_grafana_dashboard.py")
    print("  ")
    print("  2. 在浏览器中打开Grafana")
    print("     地址: http://localhost:3000")
    print("  ")
    print("  3. 查看'拖拉机车队管理仪表板'")
    print("     应该可以看到专业的拖拉机图片！")

if __name__ == "__main__":
    main()
