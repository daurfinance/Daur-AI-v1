from enum import Enum
from typing import Set, Dict, Optional
from dataclasses import dataclass

class Permission(Enum):
    """Определяет возможные разрешения в системе."""
    
    # Общие разрешения
    VIEW_DASHBOARD = "view_dashboard"
    MANAGE_SETTINGS = "manage_settings"
    
    # Разрешения для AI
    TRAIN_MODELS = "train_models"
    MANAGE_MODELS = "manage_models"
    
    # Системные разрешения
    SYSTEM_CONTROL = "system_control"
    FILE_OPERATIONS = "file_operations"
    
    # Административные разрешения
    MANAGE_USERS = "manage_users"
    VIEW_LOGS = "view_logs"
    
@dataclass
class Role:
    """Представляет роль пользователя в системе."""
    
    name: str
    permissions: Set[Permission]
    description: Optional[str] = None

class RoleManager:
    """Управляет ролями и разрешениями в системе."""
    
    def __init__(self):
        self._roles: Dict[str, Role] = {}
        self._initialize_default_roles()
    
    def _initialize_default_roles(self):
        """Инициализирует стандартные роли."""
        # Администратор
        admin_permissions = set(Permission)
        self._roles["admin"] = Role(
            name="Administrator",
            permissions=admin_permissions,
            description="Полный доступ ко всем функциям системы"
        )
        
        # Оператор
        operator_permissions = {
            Permission.VIEW_DASHBOARD,
            Permission.SYSTEM_CONTROL,
            Permission.FILE_OPERATIONS
        }
        self._roles["operator"] = Role(
            name="Operator",
            permissions=operator_permissions,
            description="Управление системой и файловыми операциями"
        )
        
        # Наблюдатель
        viewer_permissions = {
            Permission.VIEW_DASHBOARD,
            Permission.VIEW_LOGS
        }
        self._roles["viewer"] = Role(
            name="Viewer",
            permissions=viewer_permissions,
            description="Только просмотр дашборда и логов"
        )
    
    def has_permission(self, role_name: str, permission: Permission) -> bool:
        """Проверяет наличие разрешения у роли."""
        role = self._roles.get(role_name)
        return role is not None and permission in role.permissions
    
    def add_role(self, role: Role) -> None:
        """Добавляет новую роль в систему."""
        self._roles[role.name.lower()] = role
    
    def get_role(self, role_name: str) -> Optional[Role]:
        """Возвращает роль по имени."""
        return self._roles.get(role_name.lower())