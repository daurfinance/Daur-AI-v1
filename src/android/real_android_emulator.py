"""
Real Android Emulation with ADB
Полнофункциональная эмуляция Android с реальной интеграцией ADB
"""

import logging
import subprocess
import json
import time
from typing import Dict, List, Optional, Tuple, Any
from enum import Enum
from dataclasses import dataclass
import re

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class DeviceType(Enum):
    """Типы устройств"""
    EMULATOR = "emulator"
    REAL_DEVICE = "device"


class KeyCode(Enum):
    """Коды клавиш Android"""
    HOME = 3
    BACK = 4
    CALL = 5
    ENDCALL = 6
    POWER = 26
    VOLUME_UP = 24
    VOLUME_DOWN = 25
    CAMERA = 27
    MENU = 82
    SEARCH = 84
    ENTER = 66
    DEL = 67
    SPACE = 62
    TAB = 61


@dataclass
class DeviceInfo:
    """Информация об устройстве"""
    device_id: str
    device_type: DeviceType
    model: str
    manufacturer: str
    android_version: str
    api_level: int
    screen_width: int
    screen_height: int
    is_online: bool = True


@dataclass
class AppInfo:
    """Информация о приложении"""
    package_name: str
    app_name: str
    version: str
    version_code: int
    is_system_app: bool = False


@dataclass
class ProcessInfo:
    """Информация о процессе"""
    pid: int
    package_name: str
    memory_mb: float
    cpu_percent: float


class RealAndroidEmulator:
    """Реальная эмуляция Android с ADB"""
    
    def __init__(self, device_id: Optional[str] = None):
        """
        Инициализация эмулятора
        
        Args:
            device_id: ID устройства (если None, используется первое доступное)
        """
        self.logger = logging.getLogger(__name__)
        self.device_id = device_id
        self.connected = False
        
        # Проверяем наличие ADB
        if not self._check_adb():
            raise RuntimeError("ADB not found. Install Android SDK Platform Tools")
        
        # Получаем список доступных устройств
        devices = self.get_devices()
        
        if not devices:
            self.logger.warning("No Android devices found")
        elif not device_id:
            # Используем первое доступное устройство
            self.device_id = devices[0].device_id
            self.connected = True
            self.logger.info(f"Connected to device: {self.device_id}")
        else:
            # Проверяем наличие указанного устройства
            if any(d.device_id == device_id for d in devices):
                self.connected = True
                self.logger.info(f"Connected to device: {device_id}")
            else:
                self.logger.error(f"Device not found: {device_id}")
    
    def _check_adb(self) -> bool:
        """Проверить наличие ADB"""
        try:
            subprocess.run(['adb', 'version'], capture_output=True, check=True)
            return True
        except (subprocess.CalledProcessError, FileNotFoundError):
            return False
    
    def _run_adb_command(self, *args, device_specific: bool = True) -> Tuple[bool, str]:
        """
        Выполнить команду ADB
        
        Args:
            *args: Аргументы команды
            device_specific: Добавить ли -s device_id
        
        Returns:
            Tuple[bool, str]: (Успешность, Вывод)
        """
        try:
            cmd = ['adb']
            
            if device_specific and self.device_id:
                cmd.extend(['-s', self.device_id])
            
            cmd.extend(args)
            
            result = subprocess.run(cmd, capture_output=True, text=True, timeout=30)
            
            if result.returncode == 0:
                return True, result.stdout.strip()
            else:
                self.logger.error(f"ADB command failed: {' '.join(cmd)}")
                return False, result.stderr.strip()
        
        except subprocess.TimeoutExpired:
            self.logger.error(f"ADB command timeout: {' '.join(args)}")
            return False, "Timeout"
        except Exception as e:
            self.logger.error(f"Error running ADB command: {e}")
            return False, str(e)
    
    # ===== DEVICE MANAGEMENT =====
    
    def get_devices(self) -> List[DeviceInfo]:
        """Получить список подключённых устройств"""
        try:
            success, output = self._run_adb_command('devices', '-l', device_specific=False)
            
            if not success:
                return []
            
            devices = []
            for line in output.split('\n')[1:]:  # Пропускаем первую строку
                if not line.strip():
                    continue
                
                parts = line.split()
                if len(parts) < 2:
                    continue
                
                device_id = parts[0]
                device_type = DeviceType.EMULATOR if 'emulator' in device_id else DeviceType.REAL_DEVICE
                
                # Получаем информацию об устройстве
                device_info = self._get_device_info(device_id)
                if device_info:
                    devices.append(device_info)
            
            return devices
        except Exception as e:
            self.logger.error(f"Error getting devices: {e}")
            return []
    
    def _get_device_info(self, device_id: str) -> Optional[DeviceInfo]:
        """Получить информацию об устройстве"""
        try:
            # Получаем свойства устройства
            success, model = self._run_adb_command('-s', device_id, 'shell', 'getprop', 'ro.product.model', device_specific=False)
            success, manufacturer = self._run_adb_command('-s', device_id, 'shell', 'getprop', 'ro.product.manufacturer', device_specific=False)
            success, android_version = self._run_adb_command('-s', device_id, 'shell', 'getprop', 'ro.build.version.release', device_specific=False)
            success, api_level = self._run_adb_command('-s', device_id, 'shell', 'getprop', 'ro.build.version.sdk', device_specific=False)
            success, screen_size = self._run_adb_command('-s', device_id, 'shell', 'wm', 'size', device_specific=False)
            
            # Парсим размер экрана
            width, height = 1080, 1920
            if 'x' in screen_size:
                match = re.search(r'(\d+)x(\d+)', screen_size)
                if match:
                    width, height = int(match.group(1)), int(match.group(2))
            
            device_type = DeviceType.EMULATOR if 'emulator' in device_id else DeviceType.REAL_DEVICE
            
            return DeviceInfo(
                device_id=device_id,
                device_type=device_type,
                model=model or "Unknown",
                manufacturer=manufacturer or "Unknown",
                android_version=android_version or "Unknown",
                api_level=int(api_level) if api_level else 0,
                screen_width=width,
                screen_height=height,
                is_online=True
            )
        except Exception as e:
            self.logger.error(f"Error getting device info: {e}")
            return None
    
    def is_connected(self) -> bool:
        """Проверить подключение к устройству"""
        if not self.device_id:
            return False
        
        success, output = self._run_adb_command('shell', 'echo', 'test')
        return success
    
    # ===== APP MANAGEMENT =====
    
    def install_app(self, apk_path: str) -> bool:
        """
        Установить приложение
        
        Args:
            apk_path: Путь к APK файлу
        
        Returns:
            bool: Успешность установки
        """
        try:
            success, output = self._run_adb_command('install', apk_path)
            
            if success and 'Success' in output:
                self.logger.info(f"App installed: {apk_path}")
                return True
            else:
                self.logger.error(f"Failed to install app: {output}")
                return False
        except Exception as e:
            self.logger.error(f"Error installing app: {e}")
            return False
    
    def uninstall_app(self, package_name: str) -> bool:
        """
        Удалить приложение
        
        Args:
            package_name: Имя пакета приложения
        
        Returns:
            bool: Успешность удаления
        """
        try:
            success, output = self._run_adb_command('uninstall', package_name)
            
            if success and 'Success' in output:
                self.logger.info(f"App uninstalled: {package_name}")
                return True
            else:
                self.logger.error(f"Failed to uninstall app: {output}")
                return False
        except Exception as e:
            self.logger.error(f"Error uninstalling app: {e}")
            return False
    
    def get_installed_apps(self) -> List[AppInfo]:
        """Получить список установленных приложений"""
        try:
            success, output = self._run_adb_command('shell', 'pm', 'list', 'packages', '-3')
            
            if not success:
                return []
            
            apps = []
            for line in output.split('\n'):
                if line.startswith('package:'):
                    package_name = line.replace('package:', '').strip()
                    
                    # Получаем информацию о приложении
                    success, app_info = self._run_adb_command(
                        'shell', 'dumpsys', 'package', package_name
                    )
                    
                    if success:
                        # Парсим информацию
                        app_name = self._parse_app_name(app_info)
                        version = self._parse_version(app_info)
                        
                        apps.append(AppInfo(
                            package_name=package_name,
                            app_name=app_name,
                            version=version,
                            version_code=0,
                            is_system_app=False
                        ))
            
            return apps
        except Exception as e:
            self.logger.error(f"Error getting installed apps: {e}")
            return []
    
    def _parse_app_name(self, dumpsys_output: str) -> str:
        """Парсить имя приложения из dumpsys"""
        match = re.search(r'label=([^\n]+)', dumpsys_output)
        return match.group(1) if match else "Unknown"
    
    def _parse_version(self, dumpsys_output: str) -> str:
        """Парсить версию из dumpsys"""
        match = re.search(r'versionName=([^\n]+)', dumpsys_output)
        return match.group(1) if match else "Unknown"
    
    def launch_app(self, package_name: str, activity: str = None) -> bool:
        """
        Запустить приложение
        
        Args:
            package_name: Имя пакета
            activity: Имя активности (если None, используется главная)
        
        Returns:
            bool: Успешность запуска
        """
        try:
            if activity:
                component = f"{package_name}/{activity}"
            else:
                component = package_name
            
            success, output = self._run_adb_command('shell', 'am', 'start', '-n', component)
            
            if success:
                self.logger.info(f"App launched: {package_name}")
                return True
            else:
                self.logger.error(f"Failed to launch app: {output}")
                return False
        except Exception as e:
            self.logger.error(f"Error launching app: {e}")
            return False
    
    def stop_app(self, package_name: str) -> bool:
        """
        Остановить приложение
        
        Args:
            package_name: Имя пакета
        
        Returns:
            bool: Успешность остановки
        """
        try:
            success, output = self._run_adb_command('shell', 'am', 'force-stop', package_name)
            
            if success:
                self.logger.info(f"App stopped: {package_name}")
                return True
            else:
                self.logger.error(f"Failed to stop app: {output}")
                return False
        except Exception as e:
            self.logger.error(f"Error stopping app: {e}")
            return False
    
    def clear_app_data(self, package_name: str) -> bool:
        """
        Очистить данные приложения
        
        Args:
            package_name: Имя пакета
        
        Returns:
            bool: Успешность очистки
        """
        try:
            success, output = self._run_adb_command('shell', 'pm', 'clear', package_name)
            
            if success:
                self.logger.info(f"App data cleared: {package_name}")
                return True
            else:
                self.logger.error(f"Failed to clear app data: {output}")
                return False
        except Exception as e:
            self.logger.error(f"Error clearing app data: {e}")
            return False
    
    # ===== INPUT CONTROL =====
    
    def tap(self, x: int, y: int) -> bool:
        """
        Нажать на экран
        
        Args:
            x: X координата
            y: Y координата
        
        Returns:
            bool: Успешность операции
        """
        try:
            success, _ = self._run_adb_command('shell', 'input', 'tap', str(x), str(y))
            
            if success:
                self.logger.info(f"Tapped at ({x}, {y})")
                return True
            else:
                return False
        except Exception as e:
            self.logger.error(f"Error tapping: {e}")
            return False
    
    def swipe(self, x1: int, y1: int, x2: int, y2: int, duration: int = 500) -> bool:
        """
        Свайп по экрану
        
        Args:
            x1: Начальная X координата
            y1: Начальная Y координата
            x2: Конечная X координата
            y2: Конечная Y координата
            duration: Длительность в миллисекундах
        
        Returns:
            bool: Успешность операции
        """
        try:
            success, _ = self._run_adb_command(
                'shell', 'input', 'swipe', 
                str(x1), str(y1), str(x2), str(y2), str(duration)
            )
            
            if success:
                self.logger.info(f"Swiped from ({x1}, {y1}) to ({x2}, {y2})")
                return True
            else:
                return False
        except Exception as e:
            self.logger.error(f"Error swiping: {e}")
            return False
    
    def type_text(self, text: str) -> bool:
        """
        Напечатать текст
        
        Args:
            text: Текст для печати
        
        Returns:
            bool: Успешность операции
        """
        try:
            # Экранируем специальные символы
            escaped_text = text.replace(' ', '%s').replace('&', '\\&')
            success, _ = self._run_adb_command('shell', 'input', 'text', escaped_text)
            
            if success:
                self.logger.info(f"Typed text: {text}")
                return True
            else:
                return False
        except Exception as e:
            self.logger.error(f"Error typing text: {e}")
            return False
    
    def press_key(self, key_code: int) -> bool:
        """
        Нажать клавишу
        
        Args:
            key_code: Код клавиши
        
        Returns:
            bool: Успешность операции
        """
        try:
            success, _ = self._run_adb_command('shell', 'input', 'keyevent', str(key_code))
            
            if success:
                self.logger.info(f"Pressed key: {key_code}")
                return True
            else:
                return False
        except Exception as e:
            self.logger.error(f"Error pressing key: {e}")
            return False
    
    def press_home(self) -> bool:
        """Нажать Home"""
        return self.press_key(KeyCode.HOME.value)
    
    def press_back(self) -> bool:
        """Нажать Back"""
        return self.press_key(KeyCode.BACK.value)
    
    def press_power(self) -> bool:
        """Нажать Power"""
        return self.press_key(KeyCode.POWER.value)
    
    # ===== SCREEN OPERATIONS =====
    
    def take_screenshot(self, filepath: str) -> bool:
        """
        Сделать скриншот
        
        Args:
            filepath: Путь для сохранения скриншота
        
        Returns:
            bool: Успешность операции
        """
        try:
            success, _ = self._run_adb_command('shell', 'screencap', '-p', '/sdcard/screenshot.png')
            
            if success:
                success, _ = self._run_adb_command('pull', '/sdcard/screenshot.png', filepath)
                
                if success:
                    self.logger.info(f"Screenshot saved: {filepath}")
                    return True
            
            return False
        except Exception as e:
            self.logger.error(f"Error taking screenshot: {e}")
            return False
    
    def get_screen_size(self) -> Tuple[int, int]:
        """Получить размер экрана"""
        try:
            success, output = self._run_adb_command('shell', 'wm', 'size')
            
            if success and 'x' in output:
                match = re.search(r'(\d+)x(\d+)', output)
                if match:
                    return int(match.group(1)), int(match.group(2))
            
            return 1080, 1920
        except Exception as e:
            self.logger.error(f"Error getting screen size: {e}")
            return 1080, 1920
    
    # ===== SYSTEM OPERATIONS =====
    
    def get_logcat(self, lines: int = 100) -> str:
        """
        Получить логи
        
        Args:
            lines: Количество строк логов
        
        Returns:
            str: Логи устройства
        """
        try:
            success, output = self._run_adb_command('logcat', '-d', '-n', str(lines))
            
            if success:
                return output
            else:
                return ""
        except Exception as e:
            self.logger.error(f"Error getting logcat: {e}")
            return ""
    
    def clear_logcat(self) -> bool:
        """Очистить логи"""
        try:
            success, _ = self._run_adb_command('logcat', '-c')
            
            if success:
                self.logger.info("Logcat cleared")
                return True
            else:
                return False
        except Exception as e:
            self.logger.error(f"Error clearing logcat: {e}")
            return False
    
    def reboot(self) -> bool:
        """Перезагрузить устройство"""
        try:
            success, _ = self._run_adb_command('reboot')
            
            if success:
                self.logger.info("Device rebooting")
                return True
            else:
                return False
        except Exception as e:
            self.logger.error(f"Error rebooting device: {e}")
            return False
    
    def get_battery_info(self) -> Dict[str, Any]:
        """Получить информацию о батарее"""
        try:
            success, output = self._run_adb_command('shell', 'dumpsys', 'batterymanager')
            
            if not success:
                return {}
            
            info = {}
            for line in output.split('\n'):
                if ':' in line:
                    key, value = line.split(':', 1)
                    info[key.strip()] = value.strip()
            
            return info
        except Exception as e:
            self.logger.error(f"Error getting battery info: {e}")
            return {}
    
    def push_file(self, local_path: str, remote_path: str) -> bool:
        """
        Загрузить файл на устройство
        
        Args:
            local_path: Локальный путь
            remote_path: Путь на устройстве
        
        Returns:
            bool: Успешность операции
        """
        try:
            success, _ = self._run_adb_command('push', local_path, remote_path)
            
            if success:
                self.logger.info(f"File pushed: {local_path} -> {remote_path}")
                return True
            else:
                return False
        except Exception as e:
            self.logger.error(f"Error pushing file: {e}")
            return False
    
    def pull_file(self, remote_path: str, local_path: str) -> bool:
        """
        Скачать файл с устройства
        
        Args:
            remote_path: Путь на устройстве
            local_path: Локальный путь
        
        Returns:
            bool: Успешность операции
        """
        try:
            success, _ = self._run_adb_command('pull', remote_path, local_path)
            
            if success:
                self.logger.info(f"File pulled: {remote_path} -> {local_path}")
                return True
            else:
                return False
        except Exception as e:
            self.logger.error(f"Error pulling file: {e}")
            return False

