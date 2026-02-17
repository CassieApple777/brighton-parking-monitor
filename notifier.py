"""
Discord 通知模块
"""
import os
import logging
import requests
from datetime import datetime

logger = logging.getLogger(__name__)


class DiscordNotifier:
    """Discord Webhook 通知器"""
    
    def __init__(self, webhook_url):
        """
        初始化
        
        Args:
            webhook_url: Discord Webhook URL
        """
        self.webhook_url = webhook_url
        if not webhook_url:
            logger.warning("⚠️ 未设置 Discord Webhook URL")
    
    def send_notification(self, available_dates, all_results):
        """
        发送 Discord 通知
        
        Args:
            available_dates: 可用日期列表
            all_results: 所有检查结果
        """
        if not self.webhook_url:
            logger.info("📢 有停车位可用 (但未配置 Discord 通知): " + ", ".join(available_dates))
            return
        
        # 构建消息
        embed = {
            "title": "🚗 Brighton 停车位可购买!",
            "description": "发现可用停车位，赶快去预订!",
            "color": 0x00ff00,  # 绿色
            "fields": [],
            "footer": {
                "text": f"检查时间: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}"
            }
        }
        
        # 添加可用日期
        for date in available_dates:
            embed["fields"].append({
                "name": f"📅 {date}",
                "value": "✅ **有票! 快去订!**",
                "inline": True
            })
        
        # 添加链接
        embed["fields"].append({
            "name": "🔗 预订链接",
            "value": "https://reservenski.parkbrightonresort.com/select-parking",
            "inline": False
        })
        
        # 发送
        payload = {
            "content": "@everyone 🎉 有停车位了!",
            "embeds": [embed]
        }
        
        try:
            response = requests.post(
                self.webhook_url,
                json=payload,
                timeout=10
            )
            
            if response.status_code == 204:
                logger.info("✅ Discord 通知发送成功")
            else:
                logger.warning(f"⚠️ Discord 通知发送失败: {response.status_code}")
                
        except Exception as e:
            logger.error(f"❌ 发送通知失败: {e}")
    
    def send_test(self):
        """发送测试消息"""
        self.send_notification(["2/21", "2/22"], {"2/21": True, "2/22": True})
