"""
Production-Grade Security Module for Daur-AI v2.0
"""

import jwt
import hashlib
import secrets
import logging
from datetime import datetime, timedelta
from typing import Dict, Optional, Tuple
from functools import wraps
import bcrypt
import json

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class ProductionSecurityManager:
    """Полнофункциональный менеджер безопасности"""
    
    def __init__(self, secret_key: str = None, algorithm: str = "HS256"):
        self.secret_key = secret_key or secrets.token_urlsafe(32)
        self.algorithm = algorithm
        self.users = {}
        self.tokens = {}
        self.audit_log = []
    
    def hash_password(self, password: str) -> str:
        """Хэшировать пароль с bcrypt"""
        salt = bcrypt.gensalt(rounds=12)
        return bcrypt.hashpw(password.encode('utf-8'), salt).decode('utf-8')
    
    def verify_password(self, password: str, hashed: str) -> bool:
        """Проверить пароль"""
        return bcrypt.checkpw(password.encode('utf-8'), hashed.encode('utf-8'))
    
    def create_user(self, username: str, password: str, email: str, role: str = "user") -> bool:
        """Создать пользователя"""
        try:
            if username in self.users:
                logger.warning(f"User already exists: {username}")
                return False
            
            self.users[username] = {
                'password': self.hash_password(password),
                'email': email,
                'role': role,
                'created_at': datetime.now().isoformat(),
                'last_login': None,
                'is_active': True
            }
            
            self._log_audit("create_user", username, "success")
            logger.info(f"User created: {username}")
            return True
        except Exception as e:
            logger.error(f"Error creating user: {e}")
            return False
    
    def authenticate(self, username: str, password: str) -> Optional[str]:
        """Аутентифицировать пользователя и вернуть токен"""
        try:
            if username not in self.users:
                self._log_audit("authenticate", username, "failed - user not found")
                return None
            
            user = self.users[username]
            
            if not user['is_active']:
                self._log_audit("authenticate", username, "failed - user inactive")
                return None
            
            if not self.verify_password(password, user['password']):
                self._log_audit("authenticate", username, "failed - invalid password")
                return None
            
            # Создаем JWT токен
            payload = {
                'username': username,
                'role': user['role'],
                'exp': datetime.utcnow() + timedelta(hours=24),
                'iat': datetime.utcnow()
            }
            
            token = jwt.encode(payload, self.secret_key, algorithm=self.algorithm)
            
            # Сохраняем токен
            self.tokens[token] = {
                'username': username,
                'created_at': datetime.now().isoformat(),
                'expires_at': (datetime.utcnow() + timedelta(hours=24)).isoformat()
            }
            
            # Обновляем last_login
            user['last_login'] = datetime.now().isoformat()
            
            self._log_audit("authenticate", username, "success")
            logger.info(f"User authenticated: {username}")
            return token
        
        except Exception as e:
            logger.error(f"Error authenticating user: {e}")
            return None
    
    def verify_token(self, token: str) -> Optional[Dict]:
        """Проверить JWT токен"""
        try:
            payload = jwt.decode(token, self.secret_key, algorithms=[self.algorithm])
            return payload
        except jwt.ExpiredSignatureError:
            logger.warning("Token expired")
            return None
        except jwt.InvalidTokenError:
            logger.warning("Invalid token")
            return None
    
    def require_auth(self, func):
        """Декоратор для требования аутентификации"""
        @wraps(func)
        def wrapper(*args, **kwargs):
            token = kwargs.get('token')
            if not token or not self.verify_token(token):
                raise PermissionError("Authentication required")
            return func(*args, **kwargs)
        return wrapper
    
    def require_role(self, required_role: str):
        """Декоратор для требования роли"""
        def decorator(func):
            @wraps(func)
            def wrapper(*args, **kwargs):
                token = kwargs.get('token')
                if not token:
                    raise PermissionError("Authentication required")
                
                payload = self.verify_token(token)
                if not payload or payload.get('role') != required_role:
                    raise PermissionError(f"Role '{required_role}' required")
                
                return func(*args, **kwargs)
            return wrapper
        return decorator
    
    def validate_input(self, data: Dict, schema: Dict) -> Tuple[bool, Optional[str]]:
        """Валидировать входные данные"""
        try:
            for field, rules in schema.items():
                if field not in data:
                    if rules.get('required'):
                        return False, f"Field '{field}' is required"
                    continue
                
                value = data[field]
                
                # Проверка типа
                if 'type' in rules:
                    if not isinstance(value, rules['type']):
                        return False, f"Field '{field}' must be {rules['type'].__name__}"
                
                # Проверка длины
                if 'min_length' in rules and len(str(value)) < rules['min_length']:
                    return False, f"Field '{field}' is too short"
                
                if 'max_length' in rules and len(str(value)) > rules['max_length']:
                    return False, f"Field '{field}' is too long"
                
                # Проверка значений
                if 'allowed_values' in rules and value not in rules['allowed_values']:
                    return False, f"Field '{field}' has invalid value"
            
            return True, None
        except Exception as e:
            logger.error(f"Error validating input: {e}")
            return False, str(e)
    
    def encrypt_data(self, data: str) -> str:
        """Шифровать данные"""
        try:
            import base64
            from cryptography.fernet import Fernet
            
            key = Fernet.generate_key()
            cipher = Fernet(key)
            encrypted = cipher.encrypt(data.encode())
            return base64.b64encode(encrypted).decode()
        except Exception as e:
            logger.error(f"Error encrypting data: {e}")
            return data
    
    def _log_audit(self, action: str, user: str, status: str):
        """Логировать аудит"""
        self.audit_log.append({
            'timestamp': datetime.now().isoformat(),
            'action': action,
            'user': user,
            'status': status
        })
    
    def get_audit_log(self) -> list:
        """Получить лог аудита"""
        return self.audit_log
    
    def export_audit_log(self, filepath: str) -> bool:
        """Экспортировать лог аудита"""
        try:
            with open(filepath, 'w') as f:
                json.dump(self.audit_log, f, indent=2)
            logger.info(f"Audit log exported to {filepath}")
            return True
        except Exception as e:
            logger.error(f"Error exporting audit log: {e}")
            return False


__all__ = ['ProductionSecurityManager']

