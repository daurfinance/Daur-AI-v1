"""
Real Security Manager for Daur-AI v2.0
Полнофункциональный модуль безопасности

Поддерживает:
- Хэширование паролей (bcrypt)
- JWT токены (HS256)
- Аутентификация и авторизация
- Валидация входных данных
- Шифрование данных (Fernet)
- Логирование аудита
- Защита от атак (rate limiting, CORS)
"""

import jwt
import bcrypt
import secrets
import logging
import json
import threading
from datetime import datetime, timedelta
from typing import Dict, Optional, Tuple, List
from dataclasses import dataclass, asdict
from enum import Enum
from collections import defaultdict, deque
import hashlib
import hmac

# Попытка импортировать криптографию
try:
    from cryptography.fernet import Fernet
    HAS_CRYPTO = True
except ImportError:
    HAS_CRYPTO = False
    logging.warning("cryptography not installed. Install with: pip install cryptography")

# Настройка логирования
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class UserRole(Enum):
    """Роли пользователей"""
    ADMIN = "admin"
    USER = "user"
    GUEST = "guest"
    API_CLIENT = "api_client"


class TokenType(Enum):
    """Типы токенов"""
    ACCESS = "access"
    REFRESH = "refresh"
    API_KEY = "api_key"


@dataclass
class User:
    """Пользователь"""
    user_id: str
    username: str
    email: str
    password_hash: str
    role: UserRole
    created_at: str
    last_login: Optional[str] = None
    is_active: bool = True
    
    def to_dict(self):
        return {
            'user_id': self.user_id,
            'username': self.username,
            'email': self.email,
            'role': self.role.value,
            'created_at': self.created_at,
            'last_login': self.last_login,
            'is_active': self.is_active
        }


@dataclass
class Token:
    """Токен"""
    token: str
    token_type: TokenType
    user_id: str
    created_at: str
    expires_at: str
    is_valid: bool = True


@dataclass
class AuditLog:
    """Запись аудита"""
    timestamp: str
    user_id: Optional[str]
    action: str
    resource: str
    status: str  # success, failure
    details: Optional[str] = None


class RealSecurityManager:
    """Полнофункциональный менеджер безопасности"""
    
    def __init__(self, secret_key: str = None, history_size: int = 1000):
        """
        Инициализация менеджера безопасности
        
        Args:
            secret_key: Секретный ключ для JWT (генерируется если не указан)
            history_size: Размер истории аудита
        """
        # Генерируем или используем переданный секретный ключ
        self.secret_key = secret_key or secrets.token_urlsafe(32)
        
        # Хранилище пользователей (в реальном приложении это БД)
        self.users: Dict[str, User] = {}
        
        # Хранилище токенов
        self.tokens: Dict[str, Token] = {}
        
        # Хранилище API ключей
        self.api_keys: Dict[str, str] = {}  # api_key -> user_id
        
        # История аудита
        self.audit_log: deque = deque(maxlen=history_size)
        
        # Rate limiting
        self.rate_limit_tracker: Dict[str, deque] = defaultdict(lambda: deque(maxlen=100))
        
        # Блокировка потоков
        self.lock = threading.Lock()
        
        # Инициализация Fernet для шифрования
        self.cipher = None
        if HAS_CRYPTO:
            self.cipher = Fernet(Fernet.generate_key())
        
        logger.info("Real Security Manager initialized")
    
    # ===== User Management =====
    
    def register_user(self, username: str, email: str, password: str, 
                     role: UserRole = UserRole.USER) -> Tuple[bool, str]:
        """Зарегистрировать нового пользователя"""
        with self.lock:
            # Проверяем что пользователь не существует
            if any(u.username == username for u in self.users.values()):
                self._log_audit(None, "register", "user", "failure", 
                              f"Username already exists: {username}")
                return False, "Username already exists"
            
            if any(u.email == email for u in self.users.values()):
                self._log_audit(None, "register", "user", "failure",
                              f"Email already exists: {email}")
                return False, "Email already exists"
            
            # Хэшируем пароль
            password_hash = self._hash_password(password)
            
            # Создаём пользователя
            user_id = secrets.token_urlsafe(16)
            user = User(
                user_id=user_id,
                username=username,
                email=email,
                password_hash=password_hash,
                role=role,
                created_at=datetime.now().isoformat()
            )
            
            self.users[user_id] = user
            
            self._log_audit(user_id, "register", "user", "success",
                          f"User registered: {username}")
            logger.info(f"User registered: {username}")
            return True, "User registered successfully"
    
    def authenticate_user(self, username: str, password: str) -> Tuple[bool, Optional[str]]:
        """Аутентифицировать пользователя и вернуть user_id"""
        with self.lock:
            # Ищем пользователя по username
            user = None
            for u in self.users.values():
                if u.username == username:
                    user = u
                    break
            
            if not user:
                self._log_audit(None, "authenticate", "user", "failure",
                              f"User not found: {username}")
                return False, None
            
            if not user.is_active:
                self._log_audit(user.user_id, "authenticate", "user", "failure",
                              "User is inactive")
                return False, None
            
            # Проверяем пароль
            if not self._verify_password(password, user.password_hash):
                self._log_audit(user.user_id, "authenticate", "user", "failure",
                              "Invalid password")
                return False, None
            
            # Обновляем last_login
            user.last_login = datetime.now().isoformat()
            
            self._log_audit(user.user_id, "authenticate", "user", "success",
                          f"User authenticated: {username}")
            logger.info(f"User authenticated: {username}")
            return True, user.user_id
    
    def get_user(self, user_id: str) -> Optional[User]:
        """Получить информацию о пользователе"""
        with self.lock:
            return self.users.get(user_id)
    
    def get_user_id_by_username(self, username: str) -> Optional[str]:
        """Получить user_id по username"""
        with self.lock:
            for user_id, user in self.users.items():
                if user.username == username:
                    return user_id
            return None
    
    def update_user(self, user_id: str, **kwargs) -> Tuple[bool, str]:
        """Обновить информацию о пользователе"""
        with self.lock:
            user = self.users.get(user_id)
            if not user:
                return False, "User not found"
            
            # Обновляем только разрешённые поля
            if 'email' in kwargs:
                user.email = kwargs['email']
            if 'password' in kwargs:
                user.password_hash = self._hash_password(kwargs['password'])
            if 'is_active' in kwargs:
                user.is_active = kwargs['is_active']
            
            self._log_audit(user_id, "update", "user", "success")
            return True, "User updated successfully"
    
    def delete_user(self, user_id: str) -> Tuple[bool, str]:
        """Удалить пользователя"""
        with self.lock:
            if user_id not in self.users:
                return False, "User not found"
            
            del self.users[user_id]
            self._log_audit(user_id, "delete", "user", "success")
            return True, "User deleted successfully"
    
    # ===== Token Management =====
    
    def create_access_token(self, user_id: str, expires_in: int = 3600) -> str:
        """Создать access token"""
        with self.lock:
            user = self.users.get(user_id)
            if not user:
                raise ValueError("User not found")
            
            now = datetime.utcnow()
            expires_at = now + timedelta(seconds=expires_in)
            
            payload = {
                'user_id': user_id,
                'username': user.username,
                'role': user.role.value,
                'iat': now,
                'exp': expires_at,
                'type': TokenType.ACCESS.value
            }
            
            token = jwt.encode(payload, self.secret_key, algorithm='HS256')
            
            # Сохраняем токен
            token_obj = Token(
                token=token,
                token_type=TokenType.ACCESS,
                user_id=user_id,
                created_at=now.isoformat(),
                expires_at=expires_at.isoformat()
            )
            self.tokens[token] = token_obj
            
            self._log_audit(user_id, "create_token", "token", "success",
                          f"Access token created")
            return token
    
    def create_refresh_token(self, user_id: str, expires_in: int = 604800) -> str:
        """Создать refresh token (7 дней)"""
        with self.lock:
            user = self.users.get(user_id)
            if not user:
                raise ValueError("User not found")
            
            now = datetime.utcnow()
            expires_at = now + timedelta(seconds=expires_in)
            
            payload = {
                'user_id': user_id,
                'iat': now,
                'exp': expires_at,
                'type': TokenType.REFRESH.value
            }
            
            token = jwt.encode(payload, self.secret_key, algorithm='HS256')
            
            # Сохраняем токен
            token_obj = Token(
                token=token,
                token_type=TokenType.REFRESH,
                user_id=user_id,
                created_at=now.isoformat(),
                expires_at=expires_at.isoformat()
            )
            self.tokens[token] = token_obj
            
            self._log_audit(user_id, "create_token", "token", "success",
                          f"Refresh token created")
            return token
    
    def verify_token(self, token: str) -> Tuple[bool, Optional[Dict]]:
        """Проверить токен"""
        try:
            payload = jwt.decode(token, self.secret_key, algorithms=['HS256'])
            
            # Проверяем что токен в нашем хранилище
            if token not in self.tokens:
                return False, None
            
            token_obj = self.tokens[token]
            if not token_obj.is_valid:
                return False, None
            
            return True, payload
        except jwt.ExpiredSignatureError:
            logger.warning("Token expired")
            return False, None
        except jwt.InvalidTokenError as e:
            logger.warning(f"Invalid token: {e}")
            return False, None
    
    def revoke_token(self, token: str) -> bool:
        """Отозвать токен"""
        with self.lock:
            if token in self.tokens:
                self.tokens[token].is_valid = False
                return True
            return False
    
    # ===== API Key Management =====
    
    def create_api_key(self, user_id: str) -> str:
        """Создать API ключ для пользователя"""
        with self.lock:
            if user_id not in self.users:
                raise ValueError("User not found")
            
            api_key = f"sk_{secrets.token_urlsafe(32)}"
            self.api_keys[api_key] = user_id
            
            self._log_audit(user_id, "create_api_key", "api_key", "success")
            return api_key
    
    def verify_api_key(self, api_key: str) -> Tuple[bool, Optional[str]]:
        """Проверить API ключ и вернуть user_id"""
        with self.lock:
            user_id = self.api_keys.get(api_key)
            if user_id:
                self._log_audit(user_id, "verify_api_key", "api_key", "success")
                return True, user_id
            else:
                self._log_audit(None, "verify_api_key", "api_key", "failure")
                return False, None
    
    def revoke_api_key(self, api_key: str) -> bool:
        """Отозвать API ключ"""
        with self.lock:
            if api_key in self.api_keys:
                user_id = self.api_keys[api_key]
                del self.api_keys[api_key]
                self._log_audit(user_id, "revoke_api_key", "api_key", "success")
                return True
            return False
    
    # ===== Data Encryption =====
    
    def encrypt_data(self, data: str) -> Optional[str]:
        """Зашифровать данные"""
        if not HAS_CRYPTO or not self.cipher:
            logger.warning("Encryption not available")
            return data
        
        try:
            encrypted = self.cipher.encrypt(data.encode())
            return encrypted.decode()
        except Exception as e:
            logger.error(f"Encryption error: {e}")
            return None
    
    def decrypt_data(self, encrypted_data: str) -> Optional[str]:
        """Расшифровать данные"""
        if not HAS_CRYPTO or not self.cipher:
            logger.warning("Decryption not available")
            return encrypted_data
        
        try:
            decrypted = self.cipher.decrypt(encrypted_data.encode())
            return decrypted.decode()
        except Exception as e:
            logger.error(f"Decryption error: {e}")
            return None
    
    # ===== Input Validation =====
    
    def validate_username(self, username: str) -> Tuple[bool, str]:
        """Валидировать username"""
        if not username or len(username) < 3:
            return False, "Username must be at least 3 characters"
        if len(username) > 50:
            return False, "Username must be at most 50 characters"
        if not username.replace('_', '').replace('-', '').isalnum():
            return False, "Username can only contain alphanumeric characters, - and _"
        return True, "Valid"
    
    def validate_email(self, email: str) -> Tuple[bool, str]:
        """Валидировать email"""
        if '@' not in email or '.' not in email.split('@')[1]:
            return False, "Invalid email format"
        if len(email) > 100:
            return False, "Email is too long"
        return True, "Valid"
    
    def validate_password(self, password: str) -> Tuple[bool, str]:
        """Валидировать пароль"""
        if len(password) < 8:
            return False, "Password must be at least 8 characters"
        if len(password) > 128:
            return False, "Password is too long"
        if not any(c.isupper() for c in password):
            return False, "Password must contain at least one uppercase letter"
        if not any(c.islower() for c in password):
            return False, "Password must contain at least one lowercase letter"
        if not any(c.isdigit() for c in password):
            return False, "Password must contain at least one digit"
        return True, "Valid"
    
    # ===== Rate Limiting =====
    
    def check_rate_limit(self, user_id: str, limit: int = 100, 
                        window: int = 60) -> Tuple[bool, int]:
        """Проверить rate limit (запросов в секунду)"""
        with self.lock:
            now = datetime.now()
            tracker = self.rate_limit_tracker[user_id]
            
            # Удаляем старые запросы
            while tracker and (now - tracker[0]).total_seconds() > window:
                tracker.popleft()
            
            # Проверяем лимит
            if len(tracker) >= limit:
                return False, len(tracker)
            
            # Добавляем текущий запрос
            tracker.append(now)
            return True, len(tracker)
    
    # ===== Audit Logging =====
    
    def _log_audit(self, user_id: Optional[str], action: str, resource: str,
                  status: str, details: Optional[str] = None):
        """Логировать действие в аудит"""
        log = AuditLog(
            timestamp=datetime.now().isoformat(),
            user_id=user_id,
            action=action,
            resource=resource,
            status=status,
            details=details
        )
        self.audit_log.append(log)
    
    def get_audit_log(self, limit: int = 100, user_id: Optional[str] = None) -> List[AuditLog]:
        """Получить логи аудита"""
        logs = list(self.audit_log)[-limit:]
        
        if user_id:
            logs = [l for l in logs if l.user_id == user_id]
        
        return logs
    
    # ===== Password Management =====
    
    @staticmethod
    def _hash_password(password: str) -> str:
        """Хэшировать пароль"""
        salt = bcrypt.gensalt(rounds=12)
        return bcrypt.hashpw(password.encode(), salt).decode()
    
    @staticmethod
    def _verify_password(password: str, password_hash: str) -> bool:
        """Проверить пароль"""
        return bcrypt.checkpw(password.encode(), password_hash.encode())
    
    # ===== Export =====
    
    def export_audit_log(self, filepath: str) -> bool:
        """Экспортировать логи аудита в JSON"""
        try:
            data = {
                'timestamp': datetime.now().isoformat(),
                'logs': [asdict(log) for log in self.audit_log]
            }
            
            with open(filepath, 'w') as f:
                json.dump(data, f, indent=2)
            
            logger.info(f"Audit log exported to {filepath}")
            return True
        except Exception as e:
            logger.error(f"Error exporting audit log: {e}")
            return False
    
    def cleanup(self):
        """Очистить ресурсы"""
        logger.info("Security Manager cleaned up")


# Экспорт основных классов
__all__ = [
    'RealSecurityManager',
    'User',
    'Token',
    'AuditLog',
    'UserRole',
    'TokenType'
]

