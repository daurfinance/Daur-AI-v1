#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
Daur-AI: Система взаимодействия с клиентом
Управление коммуникацией через Telegram, Email, Webhook и другие каналы

Версия: 2.0
Дата: 25.10.2025
Автор: Manus AI
"""

import logging
import json
import time
import asyncio
from typing import Dict, List, Any, Optional, Callable
from pathlib import Path
from enum import Enum
from dataclasses import dataclass, field
from datetime import datetime
import hashlib


class CommunicationChannel(Enum):
    """Каналы коммуникации"""
    TELEGRAM = "telegram"
    EMAIL = "email"
    WEBHOOK = "webhook"
    REST_API = "rest_api"
    WEBSOCKET = "websocket"
    SMS = "sms"


class MessageType(Enum):
    """Типы сообщений"""
    TEXT = "text"
    AUDIO = "audio"
    VIDEO = "video"
    IMAGE = "image"
    FILE = "file"
    COMMAND = "command"
    NOTIFICATION = "notification"


class TaskStatus(Enum):
    """Статусы задач"""
    PENDING = "pending"
    RUNNING = "running"
    COMPLETED = "completed"
    FAILED = "failed"
    CANCELLED = "cancelled"


@dataclass
class ClientMessage:
    """Сообщение от клиента"""
    message_id: str
    sender_id: str
    content: str
    message_type: MessageType = MessageType.TEXT
    channel: CommunicationChannel = CommunicationChannel.TELEGRAM
    timestamp: datetime = field(default_factory=datetime.now)
    attachments: List[str] = field(default_factory=list)
    metadata: Dict[str, Any] = field(default_factory=dict)


@dataclass
class ClientTask:
    """Задача от клиента"""
    task_id: str
    client_id: str
    title: str
    description: str
    status: TaskStatus = TaskStatus.PENDING
    priority: int = 5  # 1-10, где 10 - максимальный приоритет
    created_at: datetime = field(default_factory=datetime.now)
    updated_at: datetime = field(default_factory=datetime.now)
    completed_at: Optional[datetime] = None
    result: Optional[str] = None
    error: Optional[str] = None
    metadata: Dict[str, Any] = field(default_factory=dict)


@dataclass
class ClientProfile:
    """Профиль клиента"""
    client_id: str
    name: str
    email: str = ""
    phone: str = ""
    telegram_id: str = ""
    created_at: datetime = field(default_factory=datetime.now)
    last_seen: datetime = field(default_factory=datetime.now)
    preferences: Dict[str, Any] = field(default_factory=dict)
    status: str = "active"


class TelegramConnector:
    """Коннектор Telegram"""
    
    def __init__(self, bot_token: str):
        """
        Args:
            bot_token: Токен Telegram бота
        """
        self.bot_token = bot_token
        self.logger = logging.getLogger('daur_ai.telegram_connector')
        self.api_url = f"https://api.telegram.org/bot{bot_token}"
    
    def send_message(self, chat_id: str, text: str) -> bool:
        """
        Отправить сообщение
        
        Args:
            chat_id: ID чата
            text: Текст сообщения
            
        Returns:
            bool: Успешность отправки
        """
        try:
            import requests
            
            url = f"{self.api_url}/sendMessage"
            data = {
                'chat_id': chat_id,
                'text': text,
                'parse_mode': 'HTML'
            }
            
            response = requests.post(url, json=data)
            
            if response.status_code == 200:
                self.logger.info(f"Сообщение отправлено в {chat_id}")
                return True
            else:
                self.logger.error(f"Ошибка отправки: {response.text}")
                return False
        
        except Exception as e:
            self.logger.error(f"Ошибка отправки сообщения: {e}")
            return False
    
    def send_audio(self, chat_id: str, audio_path: str) -> bool:
        """
        Отправить аудио
        
        Args:
            chat_id: ID чата
            audio_path: Путь к аудио файлу
            
        Returns:
            bool: Успешность отправки
        """
        try:
            import requests
            
            url = f"{self.api_url}/sendAudio"
            
            with open(audio_path, 'rb') as f:
                files = {'audio': f}
                data = {'chat_id': chat_id}
                response = requests.post(url, files=files, data=data)
            
            if response.status_code == 200:
                self.logger.info(f"Аудио отправлено в {chat_id}")
                return True
            else:
                self.logger.error(f"Ошибка отправки: {response.text}")
                return False
        
        except Exception as e:
            self.logger.error(f"Ошибка отправки аудио: {e}")
            return False
    
    def send_document(self, chat_id: str, document_path: str) -> bool:
        """
        Отправить документ
        
        Args:
            chat_id: ID чата
            document_path: Путь к документу
            
        Returns:
            bool: Успешность отправки
        """
        try:
            import requests
            
            url = f"{self.api_url}/sendDocument"
            
            with open(document_path, 'rb') as f:
                files = {'document': f}
                data = {'chat_id': chat_id}
                response = requests.post(url, files=files, data=data)
            
            if response.status_code == 200:
                self.logger.info(f"Документ отправлен в {chat_id}")
                return True
            else:
                self.logger.error(f"Ошибка отправки: {response.text}")
                return False
        
        except Exception as e:
            self.logger.error(f"Ошибка отправки документа: {e}")
            return False


class EmailConnector:
    """Коннектор Email"""
    
    def __init__(self, smtp_server: str, smtp_port: int, email: str, password: str):
        """
        Args:
            smtp_server: SMTP сервер
            smtp_port: SMTP порт
            email: Email адрес
            password: Пароль
        """
        self.smtp_server = smtp_server
        self.smtp_port = smtp_port
        self.email = email
        self.password = password
        self.logger = logging.getLogger('daur_ai.email_connector')
    
    def send_email(self, recipient: str, subject: str, body: str) -> bool:
        """
        Отправить email
        
        Args:
            recipient: Адрес получателя
            subject: Тема
            body: Тело письма
            
        Returns:
            bool: Успешность отправки
        """
        try:
            import smtplib
            from email.mime.text import MIMEText
            from email.mime.multipart import MIMEMultipart
            
            msg = MIMEMultipart()
            msg['From'] = self.email
            msg['To'] = recipient
            msg['Subject'] = subject
            
            msg.attach(MIMEText(body, 'html'))
            
            with smtplib.SMTP(self.smtp_server, self.smtp_port) as server:
                server.starttls()
                server.login(self.email, self.password)
                server.send_message(msg)
            
            self.logger.info(f"Email отправлен на {recipient}")
            return True
        
        except Exception as e:
            self.logger.error(f"Ошибка отправки email: {e}")
            return False


class WebhookConnector:
    """Коннектор Webhook"""
    
    def __init__(self, webhook_url: str):
        """
        Args:
            webhook_url: URL webhook
        """
        self.webhook_url = webhook_url
        self.logger = logging.getLogger('daur_ai.webhook_connector')
    
    def send_event(self, event_type: str, data: Dict[str, Any]) -> bool:
        """
        Отправить событие
        
        Args:
            event_type: Тип события
            data: Данные события
            
        Returns:
            bool: Успешность отправки
        """
        try:
            import requests
            
            payload = {
                'event_type': event_type,
                'timestamp': datetime.now().isoformat(),
                'data': data
            }
            
            response = requests.post(self.webhook_url, json=payload)
            
            if response.status_code in [200, 201, 202]:
                self.logger.info(f"Событие отправлено: {event_type}")
                return True
            else:
                self.logger.error(f"Ошибка отправки: {response.text}")
                return False
        
        except Exception as e:
            self.logger.error(f"Ошибка отправки события: {e}")
            return False


class ClientInteractionManager:
    """Менеджер взаимодействия с клиентом"""
    
    def __init__(self):
        """Инициализация"""
        self.logger = logging.getLogger('daur_ai.client_interaction_manager')
        self.clients: Dict[str, ClientProfile] = {}
        self.tasks: Dict[str, ClientTask] = {}
        self.messages: List[ClientMessage] = []
        self.connectors: Dict[CommunicationChannel, Any] = {}
        self.message_handlers: Dict[MessageType, Callable] = {}
    
    def register_client(self, client_id: str, name: str, email: str = "",
                       phone: str = "", telegram_id: str = "") -> ClientProfile:
        """
        Зарегистрировать клиента
        
        Args:
            client_id: ID клиента
            name: Имя клиента
            email: Email
            phone: Телефон
            telegram_id: Telegram ID
            
        Returns:
            ClientProfile: Профиль клиента
        """
        profile = ClientProfile(
            client_id=client_id,
            name=name,
            email=email,
            phone=phone,
            telegram_id=telegram_id
        )
        
        self.clients[client_id] = profile
        self.logger.info(f"Клиент зарегистрирован: {client_id}")
        return profile
    
    def create_task(self, client_id: str, title: str, description: str,
                   priority: int = 5) -> ClientTask:
        """
        Создать задачу
        
        Args:
            client_id: ID клиента
            title: Название задачи
            description: Описание
            priority: Приоритет
            
        Returns:
            ClientTask: Объект задачи
        """
        task_id = hashlib.md5(f"{client_id}{title}{time.time()}".encode()).hexdigest()
        
        task = ClientTask(
            task_id=task_id,
            client_id=client_id,
            title=title,
            description=description,
            priority=priority
        )
        
        self.tasks[task_id] = task
        self.logger.info(f"Задача создана: {task_id}")
        return task
    
    def update_task_status(self, task_id: str, status: TaskStatus,
                          result: Optional[str] = None, error: Optional[str] = None):
        """
        Обновить статус задачи
        
        Args:
            task_id: ID задачи
            status: Новый статус
            result: Результат
            error: Ошибка
        """
        if task_id in self.tasks:
            task = self.tasks[task_id]
            task.status = status
            task.updated_at = datetime.now()
            
            if result:
                task.result = result
            
            if error:
                task.error = error
            
            if status == TaskStatus.COMPLETED:
                task.completed_at = datetime.now()
            
            self.logger.info(f"Статус задачи обновлен: {task_id} -> {status.value}")
    
    def add_message(self, message: ClientMessage):
        """
        Добавить сообщение
        
        Args:
            message: Сообщение
        """
        self.messages.append(message)
        self.logger.info(f"Сообщение добавлено: {message.message_id}")
        
        # Вызываем обработчик сообщения
        if message.message_type in self.message_handlers:
            handler = self.message_handlers[message.message_type]
            handler(message)
    
    def register_telegram_connector(self, bot_token: str):
        """
        Зарегистрировать Telegram коннектор
        
        Args:
            bot_token: Токен бота
        """
        connector = TelegramConnector(bot_token)
        self.connectors[CommunicationChannel.TELEGRAM] = connector
        self.logger.info("Telegram коннектор зарегистрирован")
    
    def register_email_connector(self, smtp_server: str, smtp_port: int,
                                email: str, password: str):
        """
        Зарегистрировать Email коннектор
        
        Args:
            smtp_server: SMTP сервер
            smtp_port: SMTP порт
            email: Email адрес
            password: Пароль
        """
        connector = EmailConnector(smtp_server, smtp_port, email, password)
        self.connectors[CommunicationChannel.EMAIL] = connector
        self.logger.info("Email коннектор зарегистрирован")
    
    def register_webhook_connector(self, webhook_url: str):
        """
        Зарегистрировать Webhook коннектор
        
        Args:
            webhook_url: URL webhook
        """
        connector = WebhookConnector(webhook_url)
        self.connectors[CommunicationChannel.WEBHOOK] = connector
        self.logger.info("Webhook коннектор зарегистрирован")
    
    def send_notification(self, client_id: str, message: str,
                         channel: CommunicationChannel = CommunicationChannel.TELEGRAM) -> bool:
        """
        Отправить уведомление
        
        Args:
            client_id: ID клиента
            message: Сообщение
            channel: Канал отправки
            
        Returns:
            bool: Успешность отправки
        """
        if client_id not in self.clients:
            self.logger.error(f"Клиент не найден: {client_id}")
            return False
        
        client = self.clients[client_id]
        
        if channel == CommunicationChannel.TELEGRAM:
            if client.telegram_id and CommunicationChannel.TELEGRAM in self.connectors:
                connector = self.connectors[CommunicationChannel.TELEGRAM]
                return connector.send_message(client.telegram_id, message)
        
        elif channel == CommunicationChannel.EMAIL:
            if client.email and CommunicationChannel.EMAIL in self.connectors:
                connector = self.connectors[CommunicationChannel.EMAIL]
                return connector.send_email(client.email, "Уведомление", message)
        
        return False
    
    def get_client_tasks(self, client_id: str) -> List[ClientTask]:
        """
        Получить задачи клиента
        
        Args:
            client_id: ID клиента
            
        Returns:
            List[ClientTask]: Список задач
        """
        return [task for task in self.tasks.values() if task.client_id == client_id]
    
    def get_client_messages(self, client_id: str) -> List[ClientMessage]:
        """
        Получить сообщения клиента
        
        Args:
            client_id: ID клиента
            
        Returns:
            List[ClientMessage]: Список сообщений
        """
        return [msg for msg in self.messages if msg.sender_id == client_id]
    
    def get_status(self) -> Dict[str, Any]:
        """Получить статус менеджера"""
        return {
            'clients': len(self.clients),
            'tasks': len(self.tasks),
            'messages': len(self.messages),
            'connectors': list(self.connectors.keys())
        }


# Глобальный экземпляр
_client_interaction_manager = None


def get_client_interaction_manager() -> ClientInteractionManager:
    """Получить менеджер взаимодействия с клиентом"""
    global _client_interaction_manager
    if _client_interaction_manager is None:
        _client_interaction_manager = ClientInteractionManager()
    return _client_interaction_manager

