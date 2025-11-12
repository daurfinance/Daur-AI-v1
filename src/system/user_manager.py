"""Daur AI User Management System

This module provides comprehensive user management with role-based access control (RBAC).
Supports user authentication, authorization, permissions, and role management.

Version: 2.0
Date: 2025-11-12
"""

from typing import Dict, Any, Optional, List, Set
import logging
from pathlib import Path
import json
from datetime import datetime
from enum import Enum
from .password_utils import hasher

class UserRole(Enum):
    """Роли пользователей в системе."""
    ADMIN = "admin"
    MANAGER = "manager"
    USER = "user"
    GUEST = "guest"

class Permission(Enum):
    """Разрешения в системе."""
    # Административные разрешения
    MANAGE_USERS = "manage_users"
    MANAGE_ROLES = "manage_roles"
    VIEW_LOGS = "view_logs"
    MANAGE_SYSTEM = "manage_system"
    
    # Разрешения для работы с плагинами
    INSTALL_PLUGINS = "install_plugins"
    USE_PLUGINS = "use_plugins"
    PUBLISH_PLUGINS = "publish_plugins"
    
    # Разрешения для AI
    USE_AI = "use_ai"
    TRAIN_MODELS = "train_models"
    MANAGE_MODELS = "manage_models"
    
    # Разрешения для файловой системы
    READ_FILES = "read_files"
    WRITE_FILES = "write_files"
    DELETE_FILES = "delete_files"
    
    # Разрешения для браузера
    USE_BROWSER = "use_browser"
    MANAGE_BROWSER = "manage_browser"

class UserManager:
    """Система управления пользователями и ролями."""
    
    def __init__(self, data_dir: Path):
        self.data_dir = data_dir
        self.logger = logging.getLogger(__name__)
        
        # Создаем директории для данных
        self.users_dir = data_dir / "users"
        self.roles_dir = data_dir / "roles"
        self.users_dir.mkdir(parents=True, exist_ok=True)
        self.roles_dir.mkdir(parents=True, exist_ok=True)
        
        # Инициализируем базовые роли
        self._initialize_default_roles()
        
    def _initialize_default_roles(self) -> None:
        """Инициализирует стандартные роли."""
        default_roles = {
            UserRole.ADMIN.value: {
                "name": "Administrator",
                "permissions": [p.value for p in Permission],
                "description": "Полный доступ ко всем функциям системы"
            },
            UserRole.MANAGER.value: {
                "name": "Manager",
                "permissions": [
                    Permission.VIEW_LOGS.value,
                    Permission.USE_PLUGINS.value,
                    Permission.USE_AI.value,
                    Permission.MANAGE_MODELS.value,
                    Permission.READ_FILES.value,
                    Permission.WRITE_FILES.value,
                    Permission.USE_BROWSER.value
                ],
                "description": "Управление системой без административных функций"
            },
            UserRole.USER.value: {
                "name": "User",
                "permissions": [
                    Permission.USE_PLUGINS.value,
                    Permission.USE_AI.value,
                    Permission.READ_FILES.value,
                    Permission.USE_BROWSER.value
                ],
                "description": "Базовый доступ к функциям системы"
            },
            UserRole.GUEST.value: {
                "name": "Guest",
                "permissions": [
                    Permission.USE_AI.value,
                    Permission.USE_BROWSER.value
                ],
                "description": "Ограниченный доступ к базовым функциям"
            }
        }
        
        for role_id, role_data in default_roles.items():
            role_file = self.roles_dir / f"{role_id}.json"
            if not role_file.exists():
                with open(role_file, 'w') as f:
                    json.dump(role_data, f, indent=2)
                    
    def create_user(self,
                    username: str,
                    password: str,
                    email: str,
                    role: UserRole = UserRole.USER,
                    extra_data: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        """Создает нового пользователя.
        
        Args:
            username: Имя пользователя
            password: Пароль
            email: Email
            role: Роль пользователя
            extra_data: Дополнительные данные
            
        Returns:
            Данные созданного пользователя
        """
        user_file = self.users_dir / f"{username}.json"
        
        if user_file.exists():
            raise ValueError(f"User {username} already exists")
            
        # Хэшируем пароль
        hashed = hasher.hashpw(password.encode())
        
        user_data = {
            "username": username,
            "email": email,
            "password_hash": hashed.decode(),
            "role": role.value,
            "created_at": datetime.now().isoformat(),
            "last_login": None,
            "is_active": True,
            "extra_data": extra_data or {}
        }
        
        with open(user_file, 'w') as f:
            json.dump(user_data, f, indent=2)
            
        return user_data
        
    def get_user(self, username: str) -> Optional[Dict[str, Any]]:
        """Получает данные пользователя."""
        user_file = self.users_dir / f"{username}.json"
        
        if not user_file.exists():
            return None
            
        with open(user_file, 'r') as f:
            return json.load(f)
            
    def update_user(self,
                    username: str,
                    data: Dict[str, Any]) -> bool:
        """Обновляет данные пользователя."""
        user_data = self.get_user(username)
        if not user_data:
            return False
            
        # Обновляем данные
        user_data.update(data)
        
        user_file = self.users_dir / f"{username}.json"
        with open(user_file, 'w') as f:
            json.dump(user_data, f, indent=2)
            
        return True
        
    def delete_user(self, username: str) -> bool:
        """Удаляет пользователя."""
        user_file = self.users_dir / f"{username}.json"
        
        if not user_file.exists():
            return False
            
        user_file.unlink()
        return True
        
    def authenticate(self, username: str, password: str) -> bool:
        """Аутентифицирует пользователя.
        
        Args:
            username: Имя пользователя
            password: Пароль
            
        Returns:
            True если аутентификация успешна
        """
        user_data = self.get_user(username)
        if not user_data:
            return False
            
        try:
            stored_hash = user_data["password_hash"].encode()
            return hasher.checkpw(password.encode(), stored_hash)
        except Exception as e:
            return False
            
    def get_user_permissions(self, username: str) -> Set[str]:
        """Получает разрешения пользователя."""
        user_data = self.get_user(username)
        if not user_data:
            return set()
            
        role_file = self.roles_dir / f"{user_data['role']}.json"
        if not role_file.exists():
            return set()
            
        with open(role_file, 'r') as f:
            role_data = json.load(f)
            
        return set(role_data.get("permissions", []))
        
    def has_permission(self, username: str, permission: Permission) -> bool:
        """Проверяет наличие разрешения у пользователя."""
        return permission.value in self.get_user_permissions(username)
        
    def list_users(self,
                   role: Optional[UserRole] = None,
                   active_only: bool = True) -> List[Dict[str, Any]]:
        """Получает список пользователей."""
        users = []
        
        for user_file in self.users_dir.glob("*.json"):
            with open(user_file, 'r') as f:
                user_data = json.load(f)
                
            if role and user_data["role"] != role.value:
                continue
                
            if active_only and not user_data.get("is_active", True):
                continue
                
            users.append(user_data)
            
        return users
        
    def create_role(self,
                    role_id: str,
                    name: str,
                    permissions: List[Permission],
                    description: Optional[str] = None) -> Dict[str, Any]:
        """Создает новую роль."""
        role_file = self.roles_dir / f"{role_id}.json"
        
        if role_file.exists():
            raise ValueError(f"Role {role_id} already exists")
            
        role_data = {
            "name": name,
            "permissions": [p.value for p in permissions],
            "description": description or ""
        }
        
        with open(role_file, 'w') as f:
            json.dump(role_data, f, indent=2)
            
        return role_data
        
    def get_role(self, role_id: str) -> Optional[Dict[str, Any]]:
        """Получает данные роли."""
        role_file = self.roles_dir / f"{role_id}.json"
        
        if not role_file.exists():
            return None
            
        with open(role_file, 'r') as f:
            return json.load(f)
            
    def update_role(self,
                    role_id: str,
                    data: Dict[str, Any]) -> bool:
        """Обновляет данные роли."""
        role_data = self.get_role(role_id)
        if not role_data:
            return False
            
        # Обновляем данные
        role_data.update(data)
        
        role_file = self.roles_dir / f"{role_id}.json"
        with open(role_file, 'w') as f:
            json.dump(role_data, f, indent=2)
            
        return True
        
    def delete_role(self, role_id: str) -> bool:
        """Удаляет роль."""
        role_file = self.roles_dir / f"{role_id}.json"
        
        if not role_file.exists():
            return False
            
        # Проверяем, есть ли пользователи с этой ролью
        for user_file in self.users_dir.glob("*.json"):
            with open(user_file, 'r') as f:
                user_data = json.load(f)
                if user_data["role"] == role_id:
                    return False
                    
        role_file.unlink()
        return True