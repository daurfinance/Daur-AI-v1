"""
Messaging Platform Integration for Daur-AI v2.0
Интеграция со Slack, Discord, Telegram для уведомлений

Поддерживает:
- Отправка уведомлений в Slack
- Отправка уведомлений в Discord
- Отправка уведомлений в Telegram
- Получение команд из мессенджеров
- Форматирование сообщений
- Обработка ошибок
"""

import requests
import json
import logging
import threading
from typing import Dict, Optional, Callable, List
from dataclasses import dataclass
from datetime import datetime
from enum import Enum

# Настройка логирования
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class MessageType(Enum):
    """Типы сообщений"""
    INFO = "info"
    WARNING = "warning"
    ERROR = "error"
    SUCCESS = "success"
    METRIC = "metric"
    ALERT = "alert"


@dataclass
class Message:
    """Сообщение"""
    title: str
    text: str
    message_type: MessageType = MessageType.INFO
    timestamp: str = None
    extra_data: Dict = None
    
    def __post_init__(self):
        if self.timestamp is None:
            self.timestamp = datetime.now().isoformat()
        if self.extra_data is None:
            self.extra_data = {}


class SlackNotifier:
    """Отправка уведомлений в Slack"""
    
    def __init__(self, webhook_url: str):
        """
        Инициализация Slack нотификатора
        
        Args:
            webhook_url: Webhook URL из Slack (https://hooks.slack.com/services/...)
        """
        self.webhook_url = webhook_url
        self.session = requests.Session()
        
        # Проверяем webhook
        if not self._test_webhook():
            logger.warning("Slack webhook URL may be invalid")
        
        logger.info("Slack Notifier initialized")
    
    def _test_webhook(self) -> bool:
        """Проверить webhook"""
        try:
            response = self.session.post(
                self.webhook_url,
                json={"text": "Daur-AI Slack integration test"},
                timeout=5
            )
            return response.status_code == 200
        except Exception as e:
            logger.warning(f"Webhook test failed: {e}")
            return False
    
    def send_message(self, message: Message) -> bool:
        """Отправить сообщение в Slack"""
        try:
            # Определяем цвет по типу сообщения
            color_map = {
                MessageType.INFO: "#0099ff",
                MessageType.WARNING: "#ffaa00",
                MessageType.ERROR: "#ff0000",
                MessageType.SUCCESS: "#00aa00",
                MessageType.METRIC: "#0099ff",
                MessageType.ALERT: "#ff0000"
            }
            
            color = color_map.get(message.message_type, "#0099ff")
            
            payload = {
                "attachments": [
                    {
                        "color": color,
                        "title": message.title,
                        "text": message.text,
                        "ts": int(datetime.fromisoformat(message.timestamp).timestamp()),
                        "fields": [
                            {
                                "title": key,
                                "value": str(value),
                                "short": True
                            }
                            for key, value in message.extra_data.items()
                        ]
                    }
                ]
            }
            
            response = self.session.post(
                self.webhook_url,
                json=payload,
                timeout=10
            )
            
            if response.status_code == 200:
                logger.info(f"Message sent to Slack: {message.title}")
                return True
            else:
                logger.error(f"Failed to send Slack message: {response.status_code}")
                return False
        
        except Exception as e:
            logger.error(f"Error sending Slack message: {e}")
            return False
    
    def send_alert(self, title: str, text: str, **extra) -> bool:
        """Отправить алерт"""
        message = Message(title, text, MessageType.ALERT, extra_data=extra)
        return self.send_message(message)
    
    def send_metric(self, metric_name: str, value: float, unit: str = "", **extra) -> bool:
        """Отправить метрику"""
        text = f"{metric_name}: {value}{unit}"
        message = Message(metric_name, text, MessageType.METRIC, extra_data=extra)
        return self.send_message(message)


class DiscordNotifier:
    """Отправка уведомлений в Discord"""
    
    def __init__(self, webhook_url: str):
        """
        Инициализация Discord нотификатора
        
        Args:
            webhook_url: Webhook URL из Discord
        """
        self.webhook_url = webhook_url
        self.session = requests.Session()
        
        # Проверяем webhook
        if not self._test_webhook():
            logger.warning("Discord webhook URL may be invalid")
        
        logger.info("Discord Notifier initialized")
    
    def _test_webhook(self) -> bool:
        """Проверить webhook"""
        try:
            response = self.session.post(
                self.webhook_url,
                json={"content": "Daur-AI Discord integration test"},
                timeout=5
            )
            return response.status_code in [200, 204]
        except Exception as e:
            logger.warning(f"Webhook test failed: {e}")
            return False
    
    def send_message(self, message: Message) -> bool:
        """Отправить сообщение в Discord"""
        try:
            # Определяем цвет по типу сообщения
            color_map = {
                MessageType.INFO: 0x0099ff,
                MessageType.WARNING: 0xffaa00,
                MessageType.ERROR: 0xff0000,
                MessageType.SUCCESS: 0x00aa00,
                MessageType.METRIC: 0x0099ff,
                MessageType.ALERT: 0xff0000
            }
            
            color = color_map.get(message.message_type, 0x0099ff)
            
            # Форматируем поля
            fields = [
                {
                    "name": key,
                    "value": str(value),
                    "inline": True
                }
                for key, value in message.extra_data.items()
            ]
            
            payload = {
                "embeds": [
                    {
                        "title": message.title,
                        "description": message.text,
                        "color": color,
                        "timestamp": message.timestamp,
                        "fields": fields
                    }
                ]
            }
            
            response = self.session.post(
                self.webhook_url,
                json=payload,
                timeout=10
            )
            
            if response.status_code in [200, 204]:
                logger.info(f"Message sent to Discord: {message.title}")
                return True
            else:
                logger.error(f"Failed to send Discord message: {response.status_code}")
                return False
        
        except Exception as e:
            logger.error(f"Error sending Discord message: {e}")
            return False
    
    def send_alert(self, title: str, text: str, **extra) -> bool:
        """Отправить алерт"""
        message = Message(title, text, MessageType.ALERT, extra_data=extra)
        return self.send_message(message)
    
    def send_metric(self, metric_name: str, value: float, unit: str = "", **extra) -> bool:
        """Отправить метрику"""
        text = f"{metric_name}: {value}{unit}"
        message = Message(metric_name, text, MessageType.METRIC, extra_data=extra)
        return self.send_message(message)


class TelegramNotifier:
    """Отправка уведомлений в Telegram"""
    
    def __init__(self, bot_token: str, chat_id: str):
        """
        Инициализация Telegram нотификатора
        
        Args:
            bot_token: Токен бота Telegram
            chat_id: ID чата для отправки сообщений
        """
        self.bot_token = bot_token
        self.chat_id = chat_id
        self.api_url = f"https://api.telegram.org/bot{bot_token}"
        self.session = requests.Session()
        
        # Проверяем токен
        if not self._test_token():
            logger.warning("Telegram bot token may be invalid")
        
        logger.info("Telegram Notifier initialized")
    
    def _test_token(self) -> bool:
        """Проверить токен"""
        try:
            response = self.session.get(
                f"{self.api_url}/getMe",
                timeout=5
            )
            return response.status_code == 200
        except Exception as e:
            logger.warning(f"Token test failed: {e}")
            return False
    
    def send_message(self, message: Message) -> bool:
        """Отправить сообщение в Telegram"""
        try:
            # Форматируем сообщение
            text = f"*{message.title}*\n\n{message.text}"
            
            if message.extra_data:
                text += "\n\n"
                for key, value in message.extra_data.items():
                    text += f"• {key}: {value}\n"
            
            payload = {
                "chat_id": self.chat_id,
                "text": text,
                "parse_mode": "Markdown"
            }
            
            response = self.session.post(
                f"{self.api_url}/sendMessage",
                json=payload,
                timeout=10
            )
            
            if response.status_code == 200:
                logger.info(f"Message sent to Telegram: {message.title}")
                return True
            else:
                logger.error(f"Failed to send Telegram message: {response.status_code}")
                return False
        
        except Exception as e:
            logger.error(f"Error sending Telegram message: {e}")
            return False
    
    def send_alert(self, title: str, text: str, **extra) -> bool:
        """Отправить алерт"""
        message = Message(title, text, MessageType.ALERT, extra_data=extra)
        return self.send_message(message)
    
    def send_metric(self, metric_name: str, value: float, unit: str = "", **extra) -> bool:
        """Отправить метрику"""
        text = f"{metric_name}: {value}{unit}"
        message = Message(metric_name, text, MessageType.METRIC, extra_data=extra)
        return self.send_message(message)


class MultiNotifier:
    """Отправка уведомлений в несколько платформ одновременно"""
    
    def __init__(self):
        """Инициализация"""
        self.notifiers: Dict[str, object] = {}
        logger.info("Multi Notifier initialized")
    
    def add_slack(self, webhook_url: str) -> bool:
        """Добавить Slack"""
        try:
            self.notifiers['slack'] = SlackNotifier(webhook_url)
            logger.info("Slack notifier added")
            return True
        except Exception as e:
            logger.error(f"Error adding Slack notifier: {e}")
            return False
    
    def add_discord(self, webhook_url: str) -> bool:
        """Добавить Discord"""
        try:
            self.notifiers['discord'] = DiscordNotifier(webhook_url)
            logger.info("Discord notifier added")
            return True
        except Exception as e:
            logger.error(f"Error adding Discord notifier: {e}")
            return False
    
    def add_telegram(self, bot_token: str, chat_id: str) -> bool:
        """Добавить Telegram"""
        try:
            self.notifiers['telegram'] = TelegramNotifier(bot_token, chat_id)
            logger.info("Telegram notifier added")
            return True
        except Exception as e:
            logger.error(f"Error adding Telegram notifier: {e}")
            return False
    
    def send_message(self, message: Message) -> Dict[str, bool]:
        """Отправить сообщение во все платформы"""
        results = {}
        
        for name, notifier in self.notifiers.items():
            try:
                results[name] = notifier.send_message(message)
            except Exception as e:
                logger.error(f"Error sending message to {name}: {e}")
                results[name] = False
        
        return results
    
    def send_alert(self, title: str, text: str, **extra) -> Dict[str, bool]:
        """Отправить алерт"""
        message = Message(title, text, MessageType.ALERT, extra_data=extra)
        return self.send_message(message)
    
    def send_metric(self, metric_name: str, value: float, unit: str = "", **extra) -> Dict[str, bool]:
        """Отправить метрику"""
        text = f"{metric_name}: {value}{unit}"
        message = Message(metric_name, text, MessageType.METRIC, extra_data=extra)
        return self.send_message(message)

