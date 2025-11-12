#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
Daur-AI: Продвинутый менеджер приложений
Реальное управление приложениями через системные API и автоматизацию

Версия: 1.1
Дата: 01.10.2025
"""

import logging
import subprocess
import psutil
import time
import os
import signal
from typing import Dict, List, Any, Optional, Tuple
from dataclasses import dataclass

try:
    import pygetwindow as gw
    WINDOW_MANAGEMENT_AVAILABLE = True
except (ImportError, NotImplementedError):
    WINDOW_MANAGEMENT_AVAILABLE = False


@dataclass
class AppInfo:
    """Информация о приложении"""
    name: str
    pid: int
    status: str
    memory_mb: float
    cpu_percent: float
    window_title: str = ""
    window_id: Optional[int] = None


@dataclass
class WindowInfo:
    """Информация об окне"""
    title: str
    pid: int
    x: int
    y: int
    width: int
    height: int
    is_active: bool
    is_minimized: bool


class AdvancedAppManager:
    """
    Продвинутый менеджер приложений с реальным управлением
    """
    
    def __init__(self, platform: str = "Linux", input_controller=None):
        """
        Инициализация менеджера
        
        Args:
            platform (str): Платформа (Linux, Windows, Darwin)
            input_controller: Контроллер ввода для автоматизации
        """
        self.logger = logging.getLogger('daur_ai.advanced_apps')
        self.platform = platform
        self.input_controller = input_controller
        
        # Словарь команд запуска приложений для разных платформ
        self.app_commands = {
            "Linux": {
                "firefox": ["firefox"],
                "chrome": ["google-chrome"],
                "chromium": ["chromium-browser"],
                "gedit": ["gedit"],
                "notepad": ["gedit"],  # Аналог для Linux
                "calculator": ["gnome-calculator"],
                "terminal": ["gnome-terminal"],
                "file_manager": ["nautilus"],
                "text_editor": ["gedit"],
                "browser": ["firefox"],
                "code": ["code"],
                "vscode": ["code"],
                "libreoffice": ["libreoffice"],
                "writer": ["libreoffice", "--writer"],
                "calc": ["libreoffice", "--calc"],
                "impress": ["libreoffice", "--impress"]
            },
            "Windows": {
                "notepad": ["notepad.exe"],
                "calculator": ["calc.exe"],
                "chrome": ["chrome.exe"],
                "firefox": ["firefox.exe"],
                "explorer": ["explorer.exe"],
                "cmd": ["cmd.exe"],
                "powershell": ["powershell.exe"],
                "browser": ["chrome.exe"],
                "text_editor": ["notepad.exe"]
            },
            "Darwin": {  # macOS
                "safari": ["open", "-a", "Safari"],
                "chrome": ["open", "-a", "Google Chrome"],
                "firefox": ["open", "-a", "Firefox"],
                "textedit": ["open", "-a", "TextEdit"],
                "calculator": ["open", "-a", "Calculator"],
                "terminal": ["open", "-a", "Terminal"],
                "finder": ["open", "-a", "Finder"],
                "browser": ["open", "-a", "Safari"],
                "text_editor": ["open", "-a", "TextEdit"]
            }
        }
        
        # Кэш процессов
        self.process_cache = {}
        self.cache_timeout = 5  # секунд
        self.last_cache_update = 0
        
        self.logger.info(f"Продвинутый менеджер приложений инициализирован для {platform}")
    
    def _update_process_cache(self):
        """Обновление кэша процессов"""
        current_time = time.time()
        if current_time - self.last_cache_update < self.cache_timeout:
            return
        
        try:
            self.process_cache.clear()
            for proc in psutil.process_iter(['pid', 'name', 'status', 'memory_info', 'cpu_percent']):
                try:
                    info = proc.info
                    self.process_cache[info['pid']] = {
                        'name': info['name'],
                        'status': info['status'],
                        'memory_mb': info['memory_info'].rss / 1024 / 1024 if info['memory_info'] else 0,
                        'cpu_percent': info['cpu_percent'] or 0
                    }
                except (psutil.NoSuchProcess, psutil.AccessDenied):
                    continue
            
            self.last_cache_update = current_time
            self.logger.debug(f"Кэш процессов обновлен: {len(self.process_cache)} процессов")
            
        except Exception as e:
            self.logger.error(f"Ошибка обновления кэша процессов: {e}")
    
    def get_running_apps(self) -> List[AppInfo]:
        """
        Получение списка запущенных приложений
        
        Returns:
            List[AppInfo]: Список информации о приложениях
        """
        self._update_process_cache()
        apps = []
        
        try:
            # Получаем информацию об окнах если доступно
            windows = {}
            if WINDOW_MANAGEMENT_AVAILABLE:
                try:
                    for window in gw.getAllWindows():
                        if window.title.strip():
                            windows[window.title] = {
                                'x': window.left,
                                'y': window.top,
                                'width': window.width,
                                'height': window.height,
                                'is_active': window.isActive,
                                'is_minimized': window.isMinimized
                            }
                except Exception as e:
                    self.logger.debug(f"Ошибка получения информации об окнах: {e}")
            
            # Создаем список приложений
            for pid, proc_info in self.process_cache.items():
                app_info = AppInfo(
                    name=proc_info['name'],
                    pid=pid,
                    status=proc_info['status'],
                    memory_mb=proc_info['memory_mb'],
                    cpu_percent=proc_info['cpu_percent']
                )
                
                # Пытаемся найти соответствующее окно
                for title, window_info in windows.items():
                    if proc_info['name'].lower() in title.lower():
                        app_info.window_title = title
                        break
                
                apps.append(app_info)
            
            return apps
            
        except Exception as e:
            self.logger.error(f"Ошибка получения списка приложений: {e}")
            return []
    
    def find_app_by_name(self, app_name: str) -> List[AppInfo]:
        """
        Поиск приложения по имени
        
        Args:
            app_name (str): Имя приложения
            
        Returns:
            List[AppInfo]: Список найденных приложений
        """
        apps = self.get_running_apps()
        found_apps = []
        
        app_name_lower = app_name.lower()
        
        for app in apps:
            if (app_name_lower in app.name.lower() or 
                app_name_lower in app.window_title.lower()):
                found_apps.append(app)
        
        return found_apps
    
    def launch_app(self, app_name: str, args: List[str] = None) -> bool:
        """
        Запуск приложения
        
        Args:
            app_name (str): Имя приложения
            args (List[str]): Дополнительные аргументы
            
        Returns:
            bool: Успешность запуска
        """
        try:
            # Нормализуем имя приложения
            app_name_normalized = app_name.lower().strip()
            
            # Получаем команду для запуска
            platform_commands = self.app_commands.get(self.platform, {})
            command = platform_commands.get(app_name_normalized)
            
            if not command:
                # Пытаемся запустить как есть
                command = [app_name]
            
            # Добавляем аргументы если есть
            if args:
                command.extend(args)
            
            self.logger.info(f"Запуск приложения: {' '.join(command)}")
            
            # Запускаем процесс
            if self.platform == "Windows":
                process = subprocess.Popen(command, shell=True, 
                                         creationflags=subprocess.CREATE_NEW_PROCESS_GROUP)
            else:
                process = subprocess.Popen(command, 
                                         start_new_session=True,
                                         stdout=subprocess.DEVNULL,
                                         stderr=subprocess.DEVNULL)
            
            # Ждем немного чтобы процесс запустился
            time.sleep(1)
            
            # Проверяем что процесс запустился
            if process.poll() is None:
                self.logger.info(f"Приложение {app_name} запущено успешно (PID: {process.pid})")
                return True
            else:
                self.logger.error(f"Приложение {app_name} завершилось сразу после запуска")
                return False
                
        except FileNotFoundError:
            self.logger.error(f"Приложение {app_name} не найдено")
            return False
        except Exception as e:
            self.logger.error(f"Ошибка запуска приложения {app_name}: {e}")
            return False
    
    def close_app(self, app_name: str, force: bool = False) -> bool:
        """
        Закрытие приложения
        
        Args:
            app_name (str): Имя приложения
            force (bool): Принудительное закрытие
            
        Returns:
            bool: Успешность закрытия
        """
        try:
            # Находим приложение
            apps = self.find_app_by_name(app_name)
            
            if not apps:
                self.logger.warning(f"Приложение {app_name} не найдено")
                return False
            
            success_count = 0
            
            for app in apps:
                try:
                    process = psutil.Process(app.pid)
                    
                    if force:
                        # Принудительное завершение
                        process.kill()
                        self.logger.info(f"Приложение {app.name} (PID: {app.pid}) принудительно завершено")
                    else:
                        # Мягкое завершение
                        process.terminate()
                        
                        # Ждем завершения
                        try:
                            process.wait(timeout=5)
                            self.logger.info(f"Приложение {app.name} (PID: {app.pid}) завершено")
                        except psutil.TimeoutExpired:
                            # Если не завершилось, принудительно
                            process.kill()
                            self.logger.info(f"Приложение {app.name} (PID: {app.pid}) принудительно завершено после таймаута")
                    
                    success_count += 1
                    
                except (psutil.NoSuchProcess, psutil.AccessDenied) as e:
                    self.logger.error(f"Ошибка завершения процесса {app.pid}: {e}")
            
            return success_count > 0
            
        except Exception as e:
            self.logger.error(f"Ошибка закрытия приложения {app_name}: {e}")
            return False
    
    def focus_app(self, app_name: str) -> bool:
        """
        Фокусировка на приложении
        
        Args:
            app_name (str): Имя приложения
            
        Returns:
            bool: Успешность фокусировки
        """
        if not WINDOW_MANAGEMENT_AVAILABLE:
            self.logger.warning("Управление окнами недоступно")
            return False
        
        try:
            # Находим окна приложения
            windows = gw.getWindowsWithTitle(app_name)
            
            if not windows:
                # Пытаемся найти по частичному совпадению
                all_windows = gw.getAllWindows()
                windows = [w for w in all_windows if app_name.lower() in w.title.lower()]
            
            if not windows:
                self.logger.warning(f"Окна приложения {app_name} не найдены")
                return False
            
            # Фокусируемся на первом найденном окне
            window = windows[0]
            
            if window.isMinimized:
                window.restore()
            
            window.activate()
            
            self.logger.info(f"Фокус установлен на окно: {window.title}")
            return True
            
        except Exception as e:
            self.logger.error(f"Ошибка фокусировки на приложении {app_name}: {e}")
            return False
    
    def minimize_app(self, app_name: str) -> bool:
        """
        Минимизация приложения
        
        Args:
            app_name (str): Имя приложения
            
        Returns:
            bool: Успешность минимизации
        """
        if not WINDOW_MANAGEMENT_AVAILABLE:
            self.logger.warning("Управление окнами недоступно")
            return False
        
        try:
            windows = gw.getWindowsWithTitle(app_name)
            
            if not windows:
                all_windows = gw.getAllWindows()
                windows = [w for w in all_windows if app_name.lower() in w.title.lower()]
            
            if not windows:
                self.logger.warning(f"Окна приложения {app_name} не найдены")
                return False
            
            success_count = 0
            for window in windows:
                try:
                    window.minimize()
                    success_count += 1
                    self.logger.info(f"Окно минимизировано: {window.title}")
                except Exception as e:
                    self.logger.error(f"Ошибка минимизации окна {window.title}: {e}")
            
            return success_count > 0
            
        except Exception as e:
            self.logger.error(f"Ошибка минимизации приложения {app_name}: {e}")
            return False
    
    def maximize_app(self, app_name: str) -> bool:
        """
        Максимизация приложения
        
        Args:
            app_name (str): Имя приложения
            
        Returns:
            bool: Успешность максимизации
        """
        if not WINDOW_MANAGEMENT_AVAILABLE:
            self.logger.warning("Управление окнами недоступно")
            return False
        
        try:
            windows = gw.getWindowsWithTitle(app_name)
            
            if not windows:
                all_windows = gw.getAllWindows()
                windows = [w for w in all_windows if app_name.lower() in w.title.lower()]
            
            if not windows:
                self.logger.warning(f"Окна приложения {app_name} не найдены")
                return False
            
            success_count = 0
            for window in windows:
                try:
                    if window.isMinimized:
                        window.restore()
                    window.maximize()
                    success_count += 1
                    self.logger.info(f"Окно максимизировано: {window.title}")
                except Exception as e:
                    self.logger.error(f"Ошибка максимизации окна {window.title}: {e}")
            
            return success_count > 0
            
        except Exception as e:
            self.logger.error(f"Ошибка максимизации приложения {app_name}: {e}")
            return False
    
    def get_window_info(self, app_name: str) -> List[WindowInfo]:
        """
        Получение информации об окнах приложения
        
        Args:
            app_name (str): Имя приложения
            
        Returns:
            List[WindowInfo]: Список информации об окнах
        """
        if not WINDOW_MANAGEMENT_AVAILABLE:
            return []
        
        try:
            windows = gw.getWindowsWithTitle(app_name)
            
            if not windows:
                all_windows = gw.getAllWindows()
                windows = [w for w in all_windows if app_name.lower() in w.title.lower()]
            
            window_infos = []
            for window in windows:
                try:
                    info = WindowInfo(
                        title=window.title,
                        pid=0,  # pygetwindow не предоставляет PID
                        x=window.left,
                        y=window.top,
                        width=window.width,
                        height=window.height,
                        is_active=window.isActive,
                        is_minimized=window.isMinimized
                    )
                    window_infos.append(info)
                except Exception as e:
                    self.logger.error(f"Ошибка получения информации об окне: {e}")
            
            return window_infos
            
        except Exception as e:
            self.logger.error(f"Ошибка получения информации об окнах {app_name}: {e}")
            return []
    
    def execute_action(self, action: Dict[str, Any]) -> bool:
        """
        Выполнение действия с приложением
        
        Args:
            action (Dict): Описание действия
            
        Returns:
            bool: Успешность выполнения
        """
        action_type = action.get('action')
        params = action.get('params', {})
        
        try:
            if action_type == 'app_open':
                app_name = params.get('app_name', '')
                args = params.get('args', [])
                return self.launch_app(app_name, args)
            
            elif action_type == 'app_close':
                app_name = params.get('app_name', '')
                force = params.get('force', False)
                return self.close_app(app_name, force)
            
            elif action_type == 'app_focus':
                app_name = params.get('app_name', '')
                return self.focus_app(app_name)
            
            elif action_type == 'app_minimize':
                app_name = params.get('app_name', '')
                return self.minimize_app(app_name)
            
            elif action_type == 'app_maximize':
                app_name = params.get('app_name', '')
                return self.maximize_app(app_name)
            
            elif action_type == 'app_list':
                apps = self.get_running_apps()
                self.logger.info(f"Найдено {len(apps)} запущенных приложений")
                return True
            
            else:
                self.logger.warning(f"Неизвестный тип действия: {action_type}")
                return False
                
        except Exception as e:
            self.logger.error(f"Ошибка выполнения действия {action_type}: {e}")
            return False
    
    def cleanup(self):
        """Очистка ресурсов"""
        self.logger.info("Очистка продвинутого менеджера приложений")
        self.process_cache.clear()


def create_app_manager(platform: str = "Linux", input_controller=None) -> 'AdvancedAppManager':
    """
    Фабричная функция для создания менеджера приложений
    
    Args:
        platform (str): Платформа
        input_controller: Контроллер ввода
        
    Returns:
        AdvancedAppManager: Экземпляр менеджера
    """
    return AdvancedAppManager(platform, input_controller)
