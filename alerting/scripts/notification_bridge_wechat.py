#!/usr/bin/env python3
"""
WeChat Work Notification Bridge for Alertmanager
企业微信通知桥接服务 - 接收Alertmanager Webhook并转发到企业微信

Features:
- Receives Alertmanager webhook notifications
- Formats messages for WeChat Work
- Supports alert severity levels (critical, warning, info)
- Handles both firing and resolved alerts
"""

import json
import requests
from flask import Flask, request, jsonify
from datetime import datetime

app = Flask(__name__)

# ============================================================================
# Configuration
# ============================================================================

# WeChat Work webhook URL
WECHAT_WEBHOOK_URL = "https://qyapi.weixin.qq.com/cgi-bin/webhook/send?key=49f99d9c-4996-41fc-aad2-874f9fcd70f1"

# Severity colors for WeChat messages
SEVERITY_COLORS = {
    "critical": "warning",  # Red color in WeChat
    "warning": "comment",   # Yellow/Orange color
    "info": "info"          # Blue color
}

# Severity emojis
SEVERITY_EMOJIS = {
    "critical": "🔴",
    "warning": "🟡",
    "info": "🔵"
}

# ============================================================================
# WeChat Message Formatting
# ============================================================================

def format_wechat_message(alert_data):
    """Format Alertmanager alert data for WeChat Work"""
    
    alerts = alert_data.get('alerts', [])
    if not alerts:
        return None
    
    # Group alerts by status
    firing_alerts = [a for a in alerts if a.get('status') == 'firing']
    resolved_alerts = [a for a in alerts if a.get('status') == 'resolved']
    
    messages = []
    
    # Format firing alerts
    for alert in firing_alerts:
        labels = alert.get('labels', {})
        annotations = alert.get('annotations', {})
        
        severity = labels.get('severity', 'info')
        emoji = SEVERITY_EMOJIS.get(severity, '⚠️')
        alertname = labels.get('alertname', 'Unknown Alert')
        vehicle_id = labels.get('vehicle_id', 'Unknown')
        category = labels.get('category', 'system')
        
        summary = annotations.get('summary', 'No summary')
        description = annotations.get('description', 'No description')
        
        # Format timestamp
        starts_at = alert.get('startsAt', '')
        if starts_at:
            try:
                dt = datetime.fromisoformat(starts_at.replace('Z', '+00:00'))
                timestamp = dt.strftime('%Y-%m-%d %H:%M:%S')
            except:
                timestamp = starts_at
        else:
            timestamp = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        
        message = {
            "msgtype": "markdown",
            "markdown": {
                "content": f"""## {emoji} 拖拉机告警通知
                
**告警名称**: <font color=\\"{SEVERITY_COLORS.get(severity, 'info')}\\">{alertname}</font>
**严重程度**: {severity.upper()}
**车辆ID**: {vehicle_id}
**类别**: {category}
**状态**: 🔥 FIRING

**摘要**: {summary}
**详情**: {description}

**触发时间**: {timestamp}

> 请及时处理此告警！"""
            }
        }
        messages.append(message)
    
    # Format resolved alerts
    for alert in resolved_alerts:
        labels = alert.get('labels', {})
        annotations = alert.get('annotations', {})
        
        alertname = labels.get('alertname', 'Unknown Alert')
        vehicle_id = labels.get('vehicle_id', 'Unknown')
        
        summary = annotations.get('summary', 'No summary')
        
        # Format timestamp
        ends_at = alert.get('endsAt', '')
        if ends_at:
            try:
                dt = datetime.fromisoformat(ends_at.replace('Z', '+00:00'))
                timestamp = dt.strftime('%Y-%m-%d %H:%M:%S')
            except:
                timestamp = ends_at
        else:
            timestamp = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        
        message = {
            "msgtype": "markdown",
            "markdown": {
                "content": f"""## ✅ 告警已恢复

**告警名称**: {alertname}
**车辆ID**: {vehicle_id}
**状态**: ✅ RESOLVED

**摘要**: {summary}

**恢复时间**: {timestamp}

> 告警已自动恢复"""
            }
        }
        messages.append(message)
    
    return messages

# ============================================================================
# Webhook Endpoints
# ============================================================================

@app.route('/webhook/wechat', methods=['POST'])
def wechat_webhook():
    """Receive Alertmanager webhook and forward to WeChat Work"""
    
    try:
        # Get alert data from Alertmanager
        alert_data = request.json
        
        if not alert_data:
            return jsonify({"status": "error", "message": "No data received"}), 400
        
        print(f"\n{'='*80}")
        print(f"[{datetime.now().strftime('%Y-%m-%d %H:%M:%S')}] Received alert from Alertmanager")
        print(f"{'='*80}")
        print(json.dumps(alert_data, indent=2, ensure_ascii=False))
        
        # Format messages for WeChat
        messages = format_wechat_message(alert_data)
        
        if not messages:
            print("No alerts to send")
            return jsonify({"status": "success", "message": "No alerts to send"}), 200
        
        # Send each message to WeChat Work
        success_count = 0
        error_count = 0
        
        for message in messages:
            try:
                response = requests.post(
                    WECHAT_WEBHOOK_URL,
                    json=message,
                    headers={'Content-Type': 'application/json'},
                    timeout=10
                )
                
                if response.status_code == 200:
                    result = response.json()
                    if result.get('errcode') == 0:
                        print(f"✅ Message sent to WeChat Work successfully")
                        success_count += 1
                    else:
                        print(f"❌ WeChat API error: {result.get('errmsg')}")
                        error_count += 1
                else:
                    print(f"❌ HTTP error: {response.status_code}")
                    error_count += 1
                    
            except Exception as e:
                print(f"❌ Error sending to WeChat: {e}")
                error_count += 1
        
        print(f"\n📊 Summary: {success_count} sent, {error_count} failed")
        print(f"{'='*80}\n")
        
        return jsonify({
            "status": "success",
            "messages_sent": success_count,
            "messages_failed": error_count
        }), 200
        
    except Exception as e:
        print(f"❌ Error processing webhook: {e}")
        import traceback
        traceback.print_exc()
        return jsonify({"status": "error", "message": str(e)}), 500

@app.route('/health', methods=['GET'])
def health_check():
    """Health check endpoint"""
    return jsonify({
        "status": "ok",
        "service": "notification_bridge",
        "notification_channels": 1,
        "wechat_configured": bool(WECHAT_WEBHOOK_URL)
    }), 200

@app.route('/test', methods=['POST'])
def test_notification():
    """Test endpoint to send a test message to WeChat"""
    
    test_message = {
        "msgtype": "markdown",
        "markdown": {
            "content": """## 🧪 测试通知

**服务**: notification_bridge
**状态**: ✅ 运行正常
**时间**: """ + datetime.now().strftime('%Y-%m-%d %H:%M:%S') + """

> 这是一条测试消息，用于验证企业微信通知功能是否正常工作。"""
        }
    }
    
    try:
        response = requests.post(
            WECHAT_WEBHOOK_URL,
            json=test_message,
            headers={'Content-Type': 'application/json'},
            timeout=10
        )
        
        if response.status_code == 200:
            result = response.json()
            if result.get('errcode') == 0:
                return jsonify({"status": "success", "message": "Test message sent"}), 200
            else:
                return jsonify({"status": "error", "message": result.get('errmsg')}), 500
        else:
            return jsonify({"status": "error", "message": f"HTTP {response.status_code}"}), 500
            
    except Exception as e:
        return jsonify({"status": "error", "message": str(e)}), 500

# ============================================================================
# Main
# ============================================================================

if __name__ == '__main__':
    print("="*80)
    print("  WeChat Work Notification Bridge")
    print("  For Tractor Predictive Maintenance System")
    print("="*80)
    print()
    print(f"📱 WeChat Webhook: {WECHAT_WEBHOOK_URL[:50]}...")
    print(f"🌐 Starting Flask server on port 5001...")
    print()
    print("Endpoints:")
    print("  POST /webhook/wechat - Receive Alertmanager webhooks")
    print("  GET  /health         - Health check")
    print("  POST /test           - Send test message")
    print()
    print("="*80)
    print()
    
    app.run(host='0.0.0.0', port=5001, debug=False)
