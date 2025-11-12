#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
Daur-AI: Модуль безопасности
Включает аутентификацию, авторизацию, шифрование и защиту от атак

Версия: 2.0
Дата: 25.10.2025
Автор: Manus AI
"""

import logging
import hashlib
import hmac
import secrets
import json
import time
import threading
from typing import Dict, List, Any, Optional, Tuple
from datetime import datetime, timedelta
from functools import wraps
from enum import Enum
import re
from urllib.parse import quote, unquote


class PermissionLevel(Enum):
    """Уровни прав доступа"""
    GUEST = 0
    USER = 1
    ADMIN = 2
    SUPERADMIN = 3


class SecurityPolicy:
    """Политика безопасности"""
    
    def __init__(self):
        """Инициализация политики"""
        # Ограничения на пароли
        self.min_password_length = 8
        self.require_uppercase = True
        self.require_digits = True
        self.require_special_chars = True
        
        # Ограничения на сессии
        self.session_timeout = 3600  # 1 час
        self.max_login_attempts = 5
        self.lockout_duration = 900  # 15 минут
        
        # Ограничения на API
        self.max_requests_per_minute = 60
        self.max_requests_per_hour = 1000
        
        # Запрещенные команды
        self.forbidden_commands = [
            'rm -rf /',
            'format',
            'dd if=/dev/zero',
            'mkfs',
            'shutdown',
            'reboot'
        ]
        
        # Запрещенные пути
        self.forbidden_paths = [
            '/etc/passwd',
            '/etc/shadow',
            '/root',
            '/sys',
            '/proc',
            'C:\\Windows\\System32',
            'C:\\Windows\\SysWOW64'
        ]


class PasswordValidator:
    """Валидатор паролей"""
    
    def __init__(self, policy: SecurityPolicy):
        """
        Args:
            policy: Политика безопасности
        """
        self.policy = policy
        self.logger = logging.getLogger('daur_ai.password_validator')
    
    def validate(self, password: str) -> Tuple[bool, str]:
        """
        Валидировать пароль
        
        Args:
            password: Пароль для проверки
            
        Returns:
            Tuple: (is_valid, error_message)
        """
        # Проверка длины
        if len(password) < self.policy.min_password_length:
            return False, f"Пароль должен быть не менее {self.policy.min_password_length} символов"
        
        # Проверка заглавных букв
        if self.policy.require_uppercase and not any(c.isupper() for c in password):
            return False, "Пароль должен содержать заглавные буквы"
        
        # Проверка цифр
        if self.policy.require_digits and not any(c.isdigit() for c in password):
            return False, "Пароль должен содержать цифры"
        
        # Проверка специальных символов
        if self.policy.require_special_chars:
            special_chars = "!@#$%^&*()_+-=[]{}|;:,.<>?"
            if not any(c in special_chars for c in password):
                return False, "Пароль должен содержать специальные символы"
        
        return True, ""
    
    def hash_password(self, password: str, salt: Optional[str] = None) -> Tuple[str, str]:
        """
        Хэшировать пароль
        
        Args:
            password: Пароль
            salt: Соль (если None, генерируется новая)
            
        Returns:
            Tuple: (hashed_password, salt)
        """
        if salt is None:
            salt = secrets.token_hex(32)
        
        # Используем PBKDF2 для хэширования
        hashed = hashlib.pbkdf2_hmac(
            'sha256',
            password.encode(),
            salt.encode(),
            100000  # Итерации
        )
        
        return hashed.hex(), salt
    
    def verify_password(self, password: str, hashed: str, salt: str) -> bool:
        """
        Проверить пароль
        
        Args:
            password: Пароль
            hashed: Хэшированный пароль
            salt: Соль
            
        Returns:
            bool: True если пароль верный
        """
        new_hashed, _ = self.hash_password(password, salt)
        return hmac.compare_digest(new_hashed, hashed)


class TokenManager:
    """Менеджер токенов"""
    
    def __init__(self, secret_key: str, token_lifetime: int = 3600):
        """
        Args:
            secret_key: Секретный ключ для подписи
            token_lifetime: Время жизни токена в секундах
        """
        self.secret_key = secret_key
        self.token_lifetime = token_lifetime
        self.tokens = {}
        self.lock = threading.RLock()
        self.logger = logging.getLogger('daur_ai.token_manager')
    
    def generate_token(self, user_id: str, permissions: List[str] = None) -> str:
        """
        Генерировать токен
        
        Args:
            user_id: ID пользователя
            permissions: Список прав доступа
            
        Returns:
            str: Токен
        """
        token_data = {
            'user_id': user_id,
            'permissions': permissions or [],
            'issued_at': time.time(),
            'expires_at': time.time() + self.token_lifetime,
            'nonce': secrets.token_hex(16)
        }
        
        # Создаем подпись
        payload = json.dumps(token_data, sort_keys=True)
        signature = hmac.new(
            self.secret_key.encode(),
            payload.encode(),
            hashlib.sha256
        ).hexdigest()
        
        token = f"{payload}.{signature}"
        
        with self.lock:
            self.tokens[token] = token_data
        
        self.logger.info(f"Токен сгенерирован для пользователя {user_id}")
        return token
    
    def verify_token(self, token: str) -> Tuple[bool, Optional[Dict[str, Any]]]:
        """
        Проверить токен
        
        Args:
            token: Токен для проверки
            
        Returns:
            Tuple: (is_valid, token_data)
        """
        try:
            payload, signature = token.rsplit('.', 1)
            
            # Проверяем подпись
            expected_signature = hmac.new(
                self.secret_key.encode(),
                payload.encode(),
                hashlib.sha256
            ).hexdigest()
            
            if not hmac.compare_digest(signature, expected_signature):
                return False, None
            
            # Парсим данные
            token_data = json.loads(payload)
            
            # Проверяем срок действия
            if time.time() > token_data['expires_at']:
                return False, None
            
            return True, token_data
        
        except Exception as e:
            self.logger.error(f"Ошибка проверки токена: {e}")
            return False, None
    
    def revoke_token(self, token: str):
        """Отозвать токен"""
        with self.lock:
            if token in self.tokens:
                del self.tokens[token]
                self.logger.info("Токен отозван")


class InputValidator:
    """Валидатор входных данных"""
    
    def __init__(self, policy: SecurityPolicy):
        """
        Args:
            policy: Политика безопасности
        """
        self.policy = policy
        self.logger = logging.getLogger('daur_ai.input_validator')
    
    def validate_command(self, command: str) -> Tuple[bool, str]:
        """
        Валидировать команду
        
        Args:
            command: Команда
            
        Returns:
            Tuple: (is_valid, error_message)
        """
        # Проверяем запрещенные команды
        for forbidden in self.policy.forbidden_commands:
            if forbidden.lower() in command.lower():
                return False, f"Команда содержит запрещенную операцию: {forbidden}"
        
        # Проверяем на SQL injection
        sql_patterns = [
            r"(\bDROP\b|\bDELETE\b|\bINSERT\b|\bUPDATE\b)",
            r"(--|#|\/\*|\*\/)",
            r"(\bunion\b|\bselect\b|\bfrom\b)"
        ]
        
        for pattern in sql_patterns:
            if re.search(pattern, command, re.IGNORECASE):
                return False, "Команда содержит потенциальный SQL injection"
        
        return True, ""
    
    def validate_path(self, path: str) -> Tuple[bool, str]:
        """
        Валидировать путь файла
        
        Args:
            path: Путь файла
            
        Returns:
            Tuple: (is_valid, error_message)
        """
        # Нормализуем путь
        normalized_path = path.replace('\\', '/').lower()
        
        # Проверяем запрещенные пути
        for forbidden in self.policy.forbidden_paths:
            if forbidden.lower() in normalized_path:
                return False, f"Доступ к пути запрещен: {forbidden}"
        
        # Проверяем на path traversal
        if '..' in path:
            return False, "Path traversal атаки не допускаются"
        
        return True, ""
    
    def validate_email(self, email: str) -> bool:
        """Валидировать email"""
        pattern = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
        return bool(re.match(pattern, email))
    
    def sanitize_input(self, user_input: str) -> str:
        """
        Очистить входные данные
        
        Args:
            user_input: Входные данные
            
        Returns:
            str: Очищенные данные
        """
        # Удаляем опасные символы
        dangerous_chars = ['<', '>', '"', "'", '&', ';', '|', '`', '$', '(', ')']
        
        sanitized = user_input
        for char in dangerous_chars:
            sanitized = sanitized.replace(char, '')
        
        return sanitized.strip()


class AuditLogger:
    """Логгер аудита"""
    
    def __init__(self, log_file: str = None):
        """
        Args:
            log_file: Файл для логирования аудита
        """
        self.log_file = log_file or '/tmp/daur_ai_audit.log'
        self.events = []
        self.lock = threading.RLock()
        self.logger = logging.getLogger('daur_ai.audit')
    
    def log_event(self, event_type: str, user_id: str, details: Dict[str, Any]):
        """
        Логировать событие аудита
        
        Args:
            event_type: Тип события
            user_id: ID пользователя
            details: Детали события
        """
        event = {
            'timestamp': datetime.now().isoformat(),
            'event_type': event_type,
            'user_id': user_id,
            'details': details,
            'ip_address': details.get('ip_address', 'unknown')
        }
        
        with self.lock:
            self.events.append(event)
            
            # Логируем в файл
            try:
                with open(self.log_file, 'a', encoding='utf-8') as f:
                    f.write(json.dumps(event) + '\n')
            except Exception as e:
                self.logger.error(f"Ошибка логирования аудита: {e}")
    
    def log_login(self, user_id: str, success: bool, ip_address: str):
        """Логировать попытку входа"""
        self.log_event('login', user_id, {
            'success': success,
            'ip_address': ip_address
        })
    
    def log_command_execution(self, user_id: str, command: str, success: bool):
        """Логировать выполнение команды"""
        self.log_event('command_execution', user_id, {
            'command': command,
            'success': success
        })
    
    def log_access_denied(self, user_id: str, resource: str, reason: str):
        """Логировать отказ в доступе"""
        self.log_event('access_denied', user_id, {
            'resource': resource,
            'reason': reason
        })
    
    def get_recent_events(self, limit: int = 100) -> List[Dict[str, Any]]:
        """Получить последние события"""
        with self.lock:
            return self.events[-limit:]


class SecurityManager:
    """Менеджер безопасности"""
    
    def __init__(self, secret_key: str = None):
        """
        Args:
            secret_key: Секретный ключ
        """
        self.secret_key = secret_key or secrets.token_hex(32)
        self.policy = SecurityPolicy()
        self.password_validator = PasswordValidator(self.policy)
        self.token_manager = TokenManager(self.secret_key)
        self.input_validator = InputValidator(self.policy)
        self.audit_logger = AuditLogger()
        self.logger = logging.getLogger('daur_ai.security_manager')
    
    def require_auth(self, f):
        """Декоратор для проверки аутентификации"""
        @wraps(f)
        def wrapper(*args, **kwargs):
            # Получаем токен из заголовков
            from flask import request
            
            auth_header = request.headers.get('Authorization', '')
            
            if not auth_header.startswith('Bearer '):
                return {'error': 'Требуется аутентификация'}, 401
            
            token = auth_header[7:]  # Удаляем 'Bearer '
            is_valid, token_data = self.token_manager.verify_token(token)
            
            if not is_valid:
                return {'error': 'Недействительный токен'}, 401
            
            # Добавляем данные токена в контекст запроса
            request.user_id = token_data['user_id']
            request.permissions = token_data['permissions']
            
            return f(*args, **kwargs)
        
        return wrapper
    
    def require_permission(self, required_permission: str):
        """Декоратор для проверки прав доступа"""
        def decorator(f):
            @wraps(f)
            def wrapper(*args, **kwargs):
                from flask import request
                
                if not hasattr(request, 'permissions'):
                    return {'error': 'Требуется аутентификация'}, 401
                
                if required_permission not in request.permissions:
                    user_id = getattr(request, 'user_id', 'unknown')
                    self.audit_logger.log_access_denied(
                        user_id,
                        request.path,
                        f"Недостаточно прав для {required_permission}"
                    )
                    return {'error': 'Недостаточно прав доступа'}, 403
                
                return f(*args, **kwargs)
            
            return wrapper
        
        return decorator
    
    def validate_and_sanitize(self, user_input: str, input_type: str = 'command') -> Tuple[bool, str]:
        """
        Валидировать и очистить входные данные
        
        Args:
            user_input: Входные данные
            input_type: Тип входных данных
            
        Returns:
            Tuple: (is_valid, sanitized_input)
        """
        if input_type == 'command':
            is_valid, error = self.input_validator.validate_command(user_input)
            if not is_valid:
                return False, error
        
        elif input_type == 'path':
            is_valid, error = self.input_validator.validate_path(user_input)
            if not is_valid:
                return False, error
        
        sanitized = self.input_validator.sanitize_input(user_input)
        return True, sanitized


# Глобальный менеджер безопасности
_security_manager = None


def get_security_manager(secret_key: str = None) -> SecurityManager:
    """Получить глобальный менеджер безопасности"""
    global _security_manager
    
    if _security_manager is None:
        _security_manager = SecurityManager(secret_key)
    
    return _security_manager

