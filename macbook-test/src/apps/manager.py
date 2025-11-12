#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
Daur-AI: Менеджер приложений
Отвечает за запуск и взаимодействие с внешними приложениями

Версия: 1.0
Дата: 09.05.2025
"""

import os
import sys
import time
import logging
import platform
import subprocess
from typing import Dict, Union, List, Optional

# Импорт платформо-зависимых модулей
if platform.system() == "Windows":
    from src.platforms.windows.apps import WindowsAppHandler
elif platform.system() == "Darwin":  # macOS
    from src.platforms.macos.apps import MacOSAppHandler
else:
    from src.platforms.common.apps import DefaultAppHandler


class AppManager:
    """
    Менеджер приложений
    Отвечает за запуск и взаимодействие с внешними программами
    """
    
    def __init__(self, os_platform, input_controller):
        """
        Инициализация менеджера приложений
        
        Args:
            os_platform (str): Операционная система ('Windows', 'Darwin', 'Linux')
            input_controller: Контроллер ввода для взаимодействия с приложениями
        """
        self.logger = logging.getLogger('daur_ai.apps')
        self.os_platform = os_platform
        self.input_controller = input_controller
        
        # Инициализация платформо-зависимого обработчика
        if os_platform == "Windows":
            self.platform_handler = WindowsAppHandler()
            self.logger.info("Инициализирован обработчик приложений для Windows")
        
        elif os_platform == "Darwin":
            self.platform_handler = MacOSAppHandler()
            self.logger.info("Инициализирован обработчик приложений для macOS")
        
        else:
            self.platform_handler = DefaultAppHandler()
            self.logger.info(f"Для платформы {os_platform} используется стандартный обработчик приложений")
        
        # Словарь запущенных процессов
        self.active_processes = {}
    
    def execute_action(self, action: Dict) -> Union[bool, Dict]:
        """
        Выполнение действия с приложениями
        
        Args:
            action (dict): Словарь с описанием действия
                {
                    "action": "app_launch",
                    "name": "chrome",
                    "arguments": ["https://google.com"]
                }
        
        Returns:
            bool or dict: Результат выполнения (True - успешно, False - ошибка)
                        или словарь с дополнительной информацией
        """
        action_type = action.get("action", "").lower()
        
        try:
            # Запуск приложения
            if action_type == "app_launch":
                return self.launch_app(
                    name=action.get("name"),
                    arguments=action.get("arguments", []),
                    wait=action.get("wait", False)
                )
            
            # Закрытие приложения
            elif action_type == "app_close":
                return self.close_app(
                    name=action.get("name"),
                    force=action.get("force", False)
                )
            
            # Переключение на приложение
            elif action_type == "app_focus":
                return self.focus_app(
                    name=action.get("name")
                )
            
            # Запуск команды в терминале
            elif action_type == "app_command":
                return self.run_command(
                    command=action.get("command"),
                    wait=action.get("wait", True)
                )
            
            # Получение списка запущенных приложений
            elif action_type == "app_list":
                return self.list_running_apps()
            
            # Проверка, запущено ли приложение
            elif action_type == "app_check":
                return self.is_app_running(
                    name=action.get("name")
                )
            
            # Неизвестное действие
            else:
                self.logger.warning(f"Неизвестное действие с приложениями: {action_type}")
                return False
            
        except Exception as e:
            self.logger.error(f"Ошибка при выполнении действия {action_type}: {e}", exc_info=True)
            return False
    
    def launch_app(self, name: str, arguments: List[str] = None, wait: bool = False) -> Union[bool, Dict]:
        """
        Запуск приложения
        
        Args:
            name (str): Имя приложения или путь к исполняемому файлу
            arguments (list): Список аргументов командной строки
            wait (bool): Ожидать завершения приложения
            
        Returns:
            bool or dict: Результат запуска
        """
        if arguments is None:
            arguments = []
            
        try:
            # Использование специфичного для платформы запуска
            result = self.platform_handler.launch_app(name, arguments, wait)
            
            if not result:
                self.logger.warning(f"Не удалось запустить приложение {name} через платформенный обработчик")
                
                # Fallback: запуск через subprocess
                if self.os_platform == "Windows":
                    cmd = ["start", name] + arguments
                    shell = True
                elif self.os_platform == "Darwin":
                    cmd = ["open", "-a", name, *arguments]
                    shell = False
                else:
                    cmd = [name] + arguments
                    shell = False
                
                proc = subprocess.Popen(
                    cmd, 
                    shell=shell, 
                    stdout=subprocess.PIPE if wait else None,
                    stderr=subprocess.PIPE if wait else None
                )
                
                if wait:
                    stdout, stderr = proc.communicate()
                    return {
                        "pid": proc.pid,
                        "returncode": proc.returncode,
                        "stdout": stdout.decode('utf-8', errors='ignore') if stdout else "",
                        "stderr": stderr.decode('utf-8', errors='ignore') if stderr else ""
                    }
                else:
                    # Сохранение процесса для дальнейшего использования
                    self.active_processes[name] = proc
                    return {
                        "pid": proc.pid,
                        "name": name,
                        "running": True
                    }
            
            return result
            
        except Exception as e:
            self.logger.error(f"Ошибка при запуске приложения {name}: {e}")
            return False
    
    def close_app(self, name: str, force: bool = False) -> bool:
        """
        Закрытие приложения
        
        Args:
            name (str): Имя приложения или ID процесса
            force (bool): Принудительное завершение
            
        Returns:
            bool: Результат закрытия
        """
        try:
            # Проверка, запущен ли процесс через наш менеджер
            if name in self.active_processes:
                proc = self.active_processes[name]
                
                # Закрытие процесса
                if force:
                    proc.kill()
                else:
                    proc.terminate()
                
                # Ожидание завершения
                try:
                    proc.wait(timeout=5)  # Ожидание до 5 секунд
                    del self.active_processes[name]  # Удаление из словаря
                    return True
                except subprocess.TimeoutExpired:
                    # Если процесс не завершился, принудительное завершение
                    proc.kill()
                    proc.wait()
                    del self.active_processes[name]
                    return True
            
            # Использование платформенного обработчика
            return self.platform_handler.close_app(name, force)
            
        except Exception as e:
            self.logger.error(f"Ошибка при закрытии приложения {name}: {e}")
            return False
    
    def focus_app(self, name: str) -> bool:
        """
        Переключение на приложение
        
        Args:
            name (str): Имя приложения или ID окна
            
        Returns:
            bool: Результат переключения
        """
        try:
            # Использование платформенного обработчика
            result = self.platform_handler.focus_app(name)
            
            if not result:
                self.logger.warning(f"Не удалось переключиться на приложение {name} через платформенный обработчик")
                
                # Fallback: использование Alt+Tab (или Cmd+Tab)
                if self.os_platform == "Windows":
                    self.input_controller.hotkey(["alt", "tab"])
                elif self.os_platform == "Darwin":
                    self.input_controller.hotkey(["command", "tab"])
                else:
                    self.input_controller.hotkey(["alt", "tab"])
                
                # Подождать немного для переключения
                time.sleep(0.5)
                
                # Отсутствие возможности проверить, что переключились на нужное приложение
                self.logger.warning("Использован fallback метод переключения, нет гарантий точности")
                return True
            
            return result
            
        except Exception as e:
            self.logger.error(f"Ошибка при переключении на приложение {name}: {e}")
            return False
    
    def run_command(self, command: str, wait: bool = True) -> Union[bool, Dict]:
        """
        Выполнение команды в терминале
        
        Args:
            command (str): Команда для выполнения
            wait (bool): Ожидать завершения команды
            
        Returns:
            bool or dict: Результат выполнения
        """
        try:
            # Определение shell в зависимости от ОС
            use_shell = True
            
            # Выполнение команды
            if wait:
                proc = subprocess.run(
                    command,
                    shell=use_shell,
                    stdout=subprocess.PIPE,
                    stderr=subprocess.PIPE,
                    text=True
                )
                
                return {
                    "returncode": proc.returncode,
                    "stdout": proc.stdout,
                    "stderr": proc.stderr,
                    "success": proc.returncode == 0
                }
            else:
                proc = subprocess.Popen(
                    command,
                    shell=use_shell,
                    stdout=subprocess.PIPE,
                    stderr=subprocess.PIPE,
                    text=True
                )
                
                # Генерируем уникальный идентификатор для команды
                cmd_id = f"cmd_{proc.pid}"
                self.active_processes[cmd_id] = proc
                
                return {
                    "pid": proc.pid,
                    "cmd_id": cmd_id,
                    "running": True
                }
                
        except Exception as e:
            self.logger.error(f"Ошибка при выполнении команды: {e}")
            return False
    
    def list_running_apps(self) -> Union[List, bool]:
        """
        Получение списка запущенных приложений
        
        Returns:
            list or bool: Список приложений или False в случае ошибки
        """
        try:
            # Список процессов, запущенных через менеджер
            own_processes = [
                {
                    "name": name,
                    "pid": proc.pid,
                    "status": "running" if proc.poll() is None else "finished",
                    "source": "managed"
                }
                for name, proc in self.active_processes.items()
            ]
            
            # Использование платформенного обработчика для получения всех процессов
            platform_processes = self.platform_handler.list_running_apps()
            
            if platform_processes:
                # Объединение списков
                return own_processes + platform_processes
            else:
                return own_processes
                
        except Exception as e:
            self.logger.error(f"Ошибка при получении списка приложений: {e}")
            return False
    
    def is_app_running(self, name: str) -> Union[bool, Dict]:
        """
        Проверка, запущено ли приложение
        
        Args:
            name (str): Имя приложения
            
        Returns:
            bool or dict: Результат проверки
        """
        try:
            # Проверка в собственных процессах
            if name in self.active_processes:
                proc = self.active_processes[name]
                is_running = proc.poll() is None
                
                if is_running:
                    return {
                        "running": True,
                        "pid": proc.pid,
                        "name": name,
                        "source": "managed"
                    }
            
            # Использование платформенного обработчика
            result = self.platform_handler.is_app_running(name)
            
            if result is False:
                return {"running": False}
                
            return result
            
        except Exception as e:
            self.logger.error(f"Ошибка при проверке приложения {name}: {e}")
            return {"running": False, "error": str(e)}
    
    def cleanup(self):
        """Очистка ресурсов при завершении работы"""
        self.logger.info("Очистка ресурсов менеджера приложений")
        
        # Завершение запущенных процессов
        for name, proc in list(self.active_processes.items()):
            try:
                if proc.poll() is None:  # Процесс все еще работает
                    self.logger.debug(f"Завершение процесса: {name}")
                    proc.terminate()
                    try:
                        proc.wait(timeout=2)
                    except subprocess.TimeoutExpired:
                        proc.kill()
                        proc.wait()
                
                del self.active_processes[name]
                
            except Exception as e:
                self.logger.error(f"Ошибка при завершении процесса {name}: {e}")
        
        # Очистка платформенного обработчика
        self.platform_handler.cleanup()
