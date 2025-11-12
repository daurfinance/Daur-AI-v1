#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
Daur-AI: Модуль Android эмулятора BlueStacks
Управление BlueStacks, приложениями и взаимодействием с Android

Версия: 2.0
Дата: 25.10.2025
Автор: Manus AI
"""

import logging
import subprocess
import os
import time
import json
from typing import Dict, List, Any, Optional, Tuple
from pathlib import Path
from enum import Enum
from dataclasses import dataclass
from datetime import datetime


class BlueStacksVersion(Enum):
    """Версии BlueStacks"""
    V4 = "4"
    V5 = "5"
    V10 = "10"
    V11 = "11"


class AppType(Enum):
    """Типы приложений"""
    SYSTEM = "system"
    USER = "user"
    GAME = "game"
    UTILITY = "utility"


@dataclass
class AndroidApp:
    """Android приложение"""
    package_name: str
    app_name: str
    version: str = "1.0"
    app_type: AppType = AppType.USER
    installed: bool = False
    version_code: int = 1
    permissions: List[str] = None
    
    def __post_init__(self):
        if self.permissions is None:
            self.permissions = []


@dataclass
class AndroidDevice:
    """Android устройство (BlueStacks)"""
    name: str
    version: str = "11"
    resolution: Tuple[int, int] = (1920, 1080)
    dpi: int = 240
    ram: int = 4096
    storage: int = 51200
    is_running: bool = False


class BlueStacksManager:
    """Менеджер BlueStacks"""
    
    def __init__(self, bluestacks_path: Optional[str] = None):
        """
        Args:
            bluestacks_path: Путь к BlueStacks
        """
        self.bluestacks_path = bluestacks_path or self._find_bluestacks()
        self.logger = logging.getLogger('daur_ai.bluestacks_manager')
        self.devices: Dict[str, AndroidDevice] = {}
        self.apps: Dict[str, AndroidApp] = {}
        self.current_device: Optional[str] = None
    
    def _find_bluestacks(self) -> Optional[str]:
        """Найти BlueStacks в системе"""
        common_paths = [
            '/opt/bluestacks/bluestacks',
            '/Applications/BlueStacks.app/Contents/MacOS/BlueStacks',
            'C:\\Program Files\\BlueStacks\\bluestacks.exe',
            'C:\\Program Files (x86)\\BlueStacks\\bluestacks.exe'
        ]
        
        for path in common_paths:
            if os.path.exists(path):
                return path
        
        return None
    
    def is_available(self) -> bool:
        """Проверить доступность BlueStacks"""
        return self.bluestacks_path is not None and os.path.exists(self.bluestacks_path)
    
    def create_device(self, name: str, version: str = "11",
                     resolution: Tuple[int, int] = (1920, 1080)) -> AndroidDevice:
        """
        Создать новое устройство
        
        Args:
            name: Имя устройства
            version: Версия Android
            resolution: Разрешение экрана
            
        Returns:
            AndroidDevice: Объект устройства
        """
        device = AndroidDevice(name, version, resolution)
        self.devices[name] = device
        self.logger.info(f"Устройство создано: {name}")
        return device
    
    def start_device(self, device_name: str) -> bool:
        """
        Запустить устройство
        
        Args:
            device_name: Имя устройства
            
        Returns:
            bool: Успешность запуска
        """
        if not self.is_available():
            self.logger.error("BlueStacks не доступен")
            return False
        
        try:
            if device_name in self.devices:
                self.devices[device_name].is_running = True
                self.current_device = device_name
                self.logger.info(f"Устройство запущено: {device_name}")
                return True
            
            return False
        
        except Exception as e:
            self.logger.error(f"Ошибка запуска устройства: {e}")
            return False
    
    def stop_device(self, device_name: str) -> bool:
        """
        Остановить устройство
        
        Args:
            device_name: Имя устройства
            
        Returns:
            bool: Успешность операции
        """
        try:
            if device_name in self.devices:
                self.devices[device_name].is_running = False
                if self.current_device == device_name:
                    self.current_device = None
                self.logger.info(f"Устройство остановлено: {device_name}")
                return True
            
            return False
        
        except Exception as e:
            self.logger.error(f"Ошибка остановки устройства: {e}")
            return False
    
    def install_app(self, app_path: str, device_name: str = None) -> bool:
        """
        Установить приложение
        
        Args:
            app_path: Путь к APK файлу
            device_name: Имя устройства
            
        Returns:
            bool: Успешность установки
        """
        device_name = device_name or self.current_device
        
        if not device_name or device_name not in self.devices:
            self.logger.error("Устройство не выбрано")
            return False
        
        if not os.path.exists(app_path):
            self.logger.error(f"Файл не найден: {app_path}")
            return False
        
        try:
            # Используем adb для установки
            cmd = ['adb', 'install', app_path]
            subprocess.run(cmd, check=True, capture_output=True)
            self.logger.info(f"Приложение установлено: {app_path}")
            return True
        
        except Exception as e:
            self.logger.error(f"Ошибка установки приложения: {e}")
            return False
    
    def uninstall_app(self, package_name: str, device_name: str = None) -> bool:
        """
        Удалить приложение
        
        Args:
            package_name: Имя пакета
            device_name: Имя устройства
            
        Returns:
            bool: Успешность удаления
        """
        device_name = device_name or self.current_device
        
        if not device_name or device_name not in self.devices:
            self.logger.error("Устройство не выбрано")
            return False
        
        try:
            cmd = ['adb', 'uninstall', package_name]
            subprocess.run(cmd, check=True, capture_output=True)
            self.logger.info(f"Приложение удалено: {package_name}")
            return True
        
        except Exception as e:
            self.logger.error(f"Ошибка удаления приложения: {e}")
            return False
    
    def launch_app(self, package_name: str, device_name: str = None) -> bool:
        """
        Запустить приложение
        
        Args:
            package_name: Имя пакета
            device_name: Имя устройства
            
        Returns:
            bool: Успешность запуска
        """
        device_name = device_name or self.current_device
        
        if not device_name or device_name not in self.devices:
            self.logger.error("Устройство не выбрано")
            return False
        
        try:
            cmd = ['adb', 'shell', 'am', 'start', '-n', f'{package_name}/.MainActivity']
            subprocess.run(cmd, check=True, capture_output=True)
            self.logger.info(f"Приложение запущено: {package_name}")
            return True
        
        except Exception as e:
            self.logger.error(f"Ошибка запуска приложения: {e}")
            return False
    
    def close_app(self, package_name: str, device_name: str = None) -> bool:
        """
        Закрыть приложение
        
        Args:
            package_name: Имя пакета
            device_name: Имя устройства
            
        Returns:
            bool: Успешность операции
        """
        device_name = device_name or self.current_device
        
        if not device_name or device_name not in self.devices:
            self.logger.error("Устройство не выбрано")
            return False
        
        try:
            cmd = ['adb', 'shell', 'am', 'force-stop', package_name]
            subprocess.run(cmd, check=True, capture_output=True)
            self.logger.info(f"Приложение закрыто: {package_name}")
            return True
        
        except Exception as e:
            self.logger.error(f"Ошибка закрытия приложения: {e}")
            return False
    
    def get_installed_apps(self, device_name: str = None) -> List[str]:
        """
        Получить список установленных приложений
        
        Args:
            device_name: Имя устройства
            
        Returns:
            List[str]: Список пакетов
        """
        device_name = device_name or self.current_device
        
        if not device_name or device_name not in self.devices:
            self.logger.error("Устройство не выбрано")
            return []
        
        try:
            cmd = ['adb', 'shell', 'pm', 'list', 'packages']
            result = subprocess.run(cmd, capture_output=True, text=True, check=True)
            packages = [line.replace('package:', '').strip() for line in result.stdout.split('\n') if line.strip()]
            self.logger.info(f"Получено {len(packages)} приложений")
            return packages
        
        except Exception as e:
            self.logger.error(f"Ошибка получения списка приложений: {e}")
            return []
    
    def push_file(self, local_path: str, remote_path: str, device_name: str = None) -> bool:
        """
        Отправить файл на устройство
        
        Args:
            local_path: Локальный путь
            remote_path: Путь на устройстве
            device_name: Имя устройства
            
        Returns:
            bool: Успешность операции
        """
        device_name = device_name or self.current_device
        
        if not device_name or device_name not in self.devices:
            self.logger.error("Устройство не выбрано")
            return False
        
        if not os.path.exists(local_path):
            self.logger.error(f"Файл не найден: {local_path}")
            return False
        
        try:
            cmd = ['adb', 'push', local_path, remote_path]
            subprocess.run(cmd, check=True, capture_output=True)
            self.logger.info(f"Файл отправлен: {local_path} -> {remote_path}")
            return True
        
        except Exception as e:
            self.logger.error(f"Ошибка отправки файла: {e}")
            return False
    
    def pull_file(self, remote_path: str, local_path: str, device_name: str = None) -> bool:
        """
        Получить файл с устройства
        
        Args:
            remote_path: Путь на устройстве
            local_path: Локальный путь
            device_name: Имя устройства
            
        Returns:
            bool: Успешность операции
        """
        device_name = device_name or self.current_device
        
        if not device_name or device_name not in self.devices:
            self.logger.error("Устройство не выбрано")
            return False
        
        try:
            Path(local_path).parent.mkdir(parents=True, exist_ok=True)
            cmd = ['adb', 'pull', remote_path, local_path]
            subprocess.run(cmd, check=True, capture_output=True)
            self.logger.info(f"Файл получен: {remote_path} -> {local_path}")
            return True
        
        except Exception as e:
            self.logger.error(f"Ошибка получения файла: {e}")
            return False
    
    def execute_shell_command(self, command: str, device_name: str = None) -> Optional[str]:
        """
        Выполнить команду в shell
        
        Args:
            command: Команда
            device_name: Имя устройства
            
        Returns:
            Optional[str]: Результат команды
        """
        device_name = device_name or self.current_device
        
        if not device_name or device_name not in self.devices:
            self.logger.error("Устройство не выбрано")
            return None
        
        try:
            cmd = ['adb', 'shell', command]
            result = subprocess.run(cmd, capture_output=True, text=True, check=True)
            self.logger.info(f"Команда выполнена: {command}")
            return result.stdout
        
        except Exception as e:
            self.logger.error(f"Ошибка выполнения команды: {e}")
            return None
    
    def take_screenshot(self, filepath: str, device_name: str = None) -> bool:
        """
        Сделать скриншот
        
        Args:
            filepath: Путь к файлу
            device_name: Имя устройства
            
        Returns:
            bool: Успешность операции
        """
        device_name = device_name or self.current_device
        
        if not device_name or device_name not in self.devices:
            self.logger.error("Устройство не выбрано")
            return False
        
        try:
            Path(filepath).parent.mkdir(parents=True, exist_ok=True)
            cmd = ['adb', 'shell', 'screencap', '-p', '/sdcard/screenshot.png']
            subprocess.run(cmd, check=True, capture_output=True)
            
            cmd = ['adb', 'pull', '/sdcard/screenshot.png', filepath]
            subprocess.run(cmd, check=True, capture_output=True)
            
            self.logger.info(f"Скриншот сохранен: {filepath}")
            return True
        
        except Exception as e:
            self.logger.error(f"Ошибка создания скриншота: {e}")
            return False
    
    def get_device_info(self, device_name: str = None) -> Dict[str, Any]:
        """
        Получить информацию об устройстве
        
        Args:
            device_name: Имя устройства
            
        Returns:
            Dict: Информация об устройстве
        """
        device_name = device_name or self.current_device
        
        if not device_name or device_name not in self.devices:
            return {}
        
        device = self.devices[device_name]
        return {
            'name': device.name,
            'version': device.version,
            'resolution': device.resolution,
            'dpi': device.dpi,
            'ram': device.ram,
            'storage': device.storage,
            'is_running': device.is_running
        }
    
    def get_status(self) -> Dict[str, Any]:
        """Получить статус менеджера"""
        return {
            'available': self.is_available(),
            'devices': len(self.devices),
            'current_device': self.current_device,
            'running_devices': sum(1 for d in self.devices.values() if d.is_running)
        }


# Глобальный экземпляр
_bluestacks_manager = None


def get_bluestacks_manager() -> BlueStacksManager:
    """Получить менеджер BlueStacks"""
    global _bluestacks_manager
    if _bluestacks_manager is None:
        _bluestacks_manager = BlueStacksManager()
    return _bluestacks_manager

