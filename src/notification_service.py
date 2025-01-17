import requests
import datetime
from typing import Dict
from logger_config import setup_logger
import os
from dotenv import load_dotenv

load_dotenv()


logger = setup_logger(__name__)

class NotificationService:
    def __init__(self):
        self.webhook_url = os.getenv('DISCORD_WEBHOOK_URL')

    def send_order_notification(self, order_info: Dict) -> None:
        """注文情報をDiscordに送信"""
        try:
            embed = {
                "title": "🎉 注文約定通知",
                "color": 0x00ff00,
                "fields": [
                    {"name": "注文ID", "value": order_info['clientOid'], "inline": True},
                    {"name": "取引サイド", "value": order_info['side'], "inline": True},
                    {"name": "価格", "value": order_info['price'], "inline": True},
                    {"name": "数量", "value": order_info['size'], "inline": True},
                    {"name": "ステータス", "value": order_info['status'], "inline": True}
                ],
                "timestamp": datetime.datetime.utcnow().isoformat()
            }
            
            payload = {"embeds": [embed]}
            response = requests.post(self.webhook_url, json=payload)
            response.raise_for_status()
            logger.info("Discord通知を送信しました")
            
        except Exception as e:
            logger.error(f"Discord通知の送信に失敗: {e}", exc_info=True)

