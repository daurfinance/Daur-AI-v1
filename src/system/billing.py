"""Daur AI Billing System

This module provides comprehensive billing and subscription management functionality.
Supports multiple subscription tiers, payment processing, and usage tracking.

Version: 2.0
Date: 2025-11-12
"""

from typing import Dict, Any, Optional, List
from datetime import datetime, timedelta
import logging
from pathlib import Path
import json
import uuid
from enum import Enum

class SubscriptionTier(Enum):
    """Уровни подписки."""
    FREE = "free"
    BASIC = "basic"
    PRO = "pro"
    ENTERPRISE = "enterprise"

class PaymentStatus(Enum):
    """Статусы платежей."""
    PENDING = "pending"
    COMPLETED = "completed"
    FAILED = "failed"
    REFUNDED = "refunded"

class BillingSystem:
    """Система управления подписками и биллингом."""
    
    def __init__(self, data_dir: Path):
        self.data_dir = data_dir
        self.logger = logging.getLogger(__name__)
        
        # Создаем директории для данных
        self.users_dir = data_dir / "users"
        self.transactions_dir = data_dir / "transactions"
        self.users_dir.mkdir(parents=True, exist_ok=True)
        self.transactions_dir.mkdir(parents=True, exist_ok=True)
        
        # Загружаем тарифы
        self.plans = self._load_plans()
        
    def _load_plans(self) -> Dict[str, Dict[str, Any]]:
        """Загружает конфигурацию тарифных планов."""
        plans_file = self.data_dir / "plans.json"
        
        if not plans_file.exists():
            # Создаем базовые тарифы
            default_plans = {
                "free": {
                    "name": "Free",
                    "price": 0,
                    "features": {
                        "requests_per_day": 100,
                        "max_storage": 100,  # MB
                        "plugins": False,
                        "priority_support": False
                    }
                },
                "basic": {
                    "name": "Basic",
                    "price": 9.99,
                    "features": {
                        "requests_per_day": 1000,
                        "max_storage": 1000,  # MB
                        "plugins": True,
                        "priority_support": False
                    }
                },
                "pro": {
                    "name": "Professional",
                    "price": 29.99,
                    "features": {
                        "requests_per_day": 10000,
                        "max_storage": 10000,  # MB
                        "plugins": True,
                        "priority_support": True
                    }
                },
                "enterprise": {
                    "name": "Enterprise",
                    "price": 99.99,
                    "features": {
                        "requests_per_day": -1,  # Unlimited
                        "max_storage": -1,  # Unlimited
                        "plugins": True,
                        "priority_support": True
                    }
                }
            }
            
            with open(plans_file, 'w') as f:
                json.dump(default_plans, f, indent=2)
                
            return default_plans
            
        with open(plans_file, 'r') as f:
            return json.load(f)
            
    def create_user(self, 
                    user_id: str,
                    email: str,
                    tier: SubscriptionTier = SubscriptionTier.FREE) -> Dict[str, Any]:
        """Создает нового пользователя.
        
        Args:
            user_id: Уникальный идентификатор пользователя
            email: Email пользователя
            tier: Уровень подписки
            
        Returns:
            Данные пользователя
        """
        user_file = self.users_dir / f"{user_id}.json"
        
        if user_file.exists():
            raise ValueError(f"User {user_id} already exists")
            
        user_data = {
            "user_id": user_id,
            "email": email,
            "subscription": {
                "tier": tier.value,
                "start_date": datetime.now().isoformat(),
                "end_date": None if tier == SubscriptionTier.FREE else
                          (datetime.now() + timedelta(days=30)).isoformat(),
                "auto_renew": False,
                "status": "active"
            },
            "usage": {
                "requests_today": 0,
                "last_request": None,
                "storage_used": 0
            },
            "payment_info": None
        }
        
        with open(user_file, 'w') as f:
            json.dump(user_data, f, indent=2)
            
        return user_data
        
    def get_user(self, user_id: str) -> Optional[Dict[str, Any]]:
        """Получает данные пользователя."""
        user_file = self.users_dir / f"{user_id}.json"
        
        if not user_file.exists():
            return None
            
        with open(user_file, 'r') as f:
            return json.load(f)
            
    def update_subscription(self,
                          user_id: str,
                          tier: SubscriptionTier,
                          months: int = 1) -> bool:
        """Обновляет подписку пользователя.
        
        Args:
            user_id: ID пользователя
            tier: Новый уровень подписки
            months: Количество месяцев
            
        Returns:
            True если обновление успешно
        """
        user_data = self.get_user(user_id)
        if not user_data:
            return False
            
        user_data["subscription"].update({
            "tier": tier.value,
            "start_date": datetime.now().isoformat(),
            "end_date": (datetime.now() + timedelta(days=30 * months)).isoformat(),
            "status": "active"
        })
        
        user_file = self.users_dir / f"{user_id}.json"
        with open(user_file, 'w') as f:
            json.dump(user_data, f, indent=2)
            
        return True
        
    def record_usage(self, user_id: str, requests: int = 1, storage: int = 0) -> bool:
        """Записывает использование ресурсов пользователем.
        
        Args:
            user_id: ID пользователя
            requests: Количество запросов
            storage: Использованное хранилище в MB
            
        Returns:
            True если лимиты не превышены
        """
        user_data = self.get_user(user_id)
        if not user_data:
            return False
            
        plan = self.plans[user_data["subscription"]["tier"]]
        
        # Проверяем лимиты
        if plan["features"]["requests_per_day"] != -1:
            if user_data["usage"]["requests_today"] + requests > plan["features"]["requests_per_day"]:
                return False
                
        if plan["features"]["max_storage"] != -1:
            if user_data["usage"]["storage_used"] + storage > plan["features"]["max_storage"]:
                return False
                
        # Обновляем использование
        user_data["usage"].update({
            "requests_today": user_data["usage"]["requests_today"] + requests,
            "last_request": datetime.now().isoformat(),
            "storage_used": user_data["usage"]["storage_used"] + storage
        })
        
        user_file = self.users_dir / f"{user_id}.json"
        with open(user_file, 'w') as f:
            json.dump(user_data, f, indent=2)
            
        return True
        
    def process_payment(self,
                       user_id: str,
                       amount: float,
                       payment_method: Dict[str, Any]) -> Dict[str, Any]:
        """Обрабатывает платеж.
        
        Args:
            user_id: ID пользователя
            amount: Сумма платежа
            payment_method: Данные способа оплаты
            
        Returns:
            Данные транзакции
        """
        transaction = {
            "transaction_id": str(uuid.uuid4()),
            "user_id": user_id,
            "amount": amount,
            "status": PaymentStatus.PENDING.value,
            "timestamp": datetime.now().isoformat(),
            "payment_method": payment_method
        }
        
        # В реальной системе здесь была бы интеграция с платежным шлюзом
        
        # Сохраняем транзакцию
        transaction_file = self.transactions_dir / f"{transaction['transaction_id']}.json"
        with open(transaction_file, 'w') as f:
            json.dump(transaction, f, indent=2)
            
        return transaction
        
    def get_transaction(self, transaction_id: str) -> Optional[Dict[str, Any]]:
        """Получает данные транзакции."""
        transaction_file = self.transactions_dir / f"{transaction_id}.json"
        
        if not transaction_file.exists():
            return None
            
        with open(transaction_file, 'r') as f:
            return json.load(f)
            
    def list_transactions(self, 
                         user_id: str,
                         start_date: Optional[datetime] = None,
                         end_date: Optional[datetime] = None) -> List[Dict[str, Any]]:
        """Получает список транзакций пользователя."""
        transactions = []
        
        for transaction_file in self.transactions_dir.glob("*.json"):
            with open(transaction_file, 'r') as f:
                transaction = json.load(f)
                
            if transaction["user_id"] != user_id:
                continue
                
            transaction_date = datetime.fromisoformat(transaction["timestamp"])
            
            if start_date and transaction_date < start_date:
                continue
                
            if end_date and transaction_date > end_date:
                continue
                
            transactions.append(transaction)
            
        return sorted(transactions, 
                     key=lambda x: datetime.fromisoformat(x["timestamp"]),
                     reverse=True)