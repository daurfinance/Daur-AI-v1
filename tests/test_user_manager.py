import pytest
import json
from pathlib import Path
from unittest.mock import MagicMock, patch
from src.system.user_manager import UserManager, UserRole, Permission

@pytest.fixture
def test_data_dir(tmp_path):
    return tmp_path / "test_data"

@pytest.fixture
def user_manager(test_data_dir):
    return UserManager(test_data_dir)

def test_create_user(user_manager):
    """Тест создания пользователя."""
    user = user_manager.create_user(
        username="test_user",
        password="test_password",
        email="test@example.com"
    )
    
    assert user["username"] == "test_user"
    assert user["email"] == "test@example.com"
    assert user["role"] == UserRole.USER.value
    assert user["is_active"] is True
    
def test_authenticate_user(user_manager):
    """Тест аутентификации пользователя."""
    user_manager.create_user(
        username="auth_test",
        password="test_password",
        email="auth@example.com"
    )
    
    assert user_manager.authenticate("auth_test", "test_password") is True
    assert user_manager.authenticate("auth_test", "wrong_password") is False
    assert user_manager.authenticate("nonexistent", "test_password") is False
    
def test_user_permissions(user_manager):
    """Тест проверки разрешений пользователя."""
    # Создаем администратора
    user_manager.create_user(
        username="admin_test",
        password="admin_password",
        email="admin@example.com",
        role=UserRole.ADMIN
    )
    
    # Создаем обычного пользователя
    user_manager.create_user(
        username="user_test",
        password="user_password",
        email="user@example.com",
        role=UserRole.USER
    )
    
    # Проверяем разрешения администратора
    assert user_manager.has_permission("admin_test", Permission.MANAGE_USERS) is True
    assert user_manager.has_permission("admin_test", Permission.MANAGE_SYSTEM) is True
    
    # Проверяем разрешения пользователя
    assert user_manager.has_permission("user_test", Permission.USE_AI) is True
    assert user_manager.has_permission("user_test", Permission.MANAGE_USERS) is False
    
def test_update_user(user_manager):
    """Тест обновления данных пользователя."""
    user_manager.create_user(
        username="update_test",
        password="test_password",
        email="update@example.com"
    )
    
    # Обновляем данные
    success = user_manager.update_user("update_test", {
        "email": "new_email@example.com",
        "is_active": False
    })
    
    assert success is True
    
    # Проверяем обновленные данные
    user = user_manager.get_user("update_test")
    assert user["email"] == "new_email@example.com"
    assert user["is_active"] is False
    
def test_delete_user(user_manager):
    """Тест удаления пользователя."""
    user_manager.create_user(
        username="delete_test",
        password="test_password",
        email="delete@example.com"
    )
    
    assert user_manager.delete_user("delete_test") is True
    assert user_manager.get_user("delete_test") is None
    
def test_list_users(user_manager):
    """Тест получения списка пользователей."""
    # Создаем тестовых пользователей
    user_manager.create_user(
        username="user1",
        password="pass1",
        email="user1@example.com",
        role=UserRole.USER
    )
    
    user_manager.create_user(
        username="user2",
        password="pass2",
        email="user2@example.com",
        role=UserRole.MANAGER
    )
    
    user_manager.create_user(
        username="user3",
        password="pass3",
        email="user3@example.com",
        role=UserRole.USER,
    )
    
    # Деактивируем одного пользователя
    user_manager.update_user("user3", {"is_active": False})
    
    # Получаем всех активных пользователей
    active_users = user_manager.list_users(active_only=True)
    assert len(active_users) == 2
    
    # Получаем всех пользователей с ролью USER
    user_role_users = user_manager.list_users(role=UserRole.USER)
    assert len(user_role_users) == 2
    
    # Получаем всех пользователей
    all_users = user_manager.list_users(active_only=False)
    assert len(all_users) == 3