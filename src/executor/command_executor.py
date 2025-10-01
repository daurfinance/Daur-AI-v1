#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
Daur-AI: Исполнитель команд
Выполняет распознанные команды через соответствующие компоненты системы

Версия: 1.1
Дата: 01.10.2025
"""

import os
import time
import logging
import subprocess
import platform
from typing import Dict, Any, Optional, List
from pathlib import Path

class CommandExecutor:
    """
    Исполнитель команд для Daur-AI
    """
    
    def __init__(self, input_controller, app_manager, file_manager, sandbox=False):
        """
        Инициализация исполнителя
        
        Args:
            input_controller: Контроллер ввода
            app_manager: Менеджер приложений
            file_manager: Менеджер файлов
            sandbox (bool): Режим песочницы
        """
        self.logger = logging.getLogger('daur_ai.executor')
        self.input_controller = input_controller
        self.app_manager = app_manager
        self.file_manager = file_manager
        self.sandbox = sandbox
        
        # Статистика выполнения
        self.execution_stats = {
            'total_commands': 0,
            'successful_commands': 0,
            'failed_commands': 0,
            'last_execution_time': None
        }
        
        # Безопасные команды для песочницы
        self.safe_commands = {
            'file_operation': ['create', 'read', 'write', 'list'],
            'text_input': ['type'],
            'screenshot': ['take'],
            'help': ['help'],
            'application': ['list', 'status']  # Ограниченный набор
        }
        
        self.logger.info(f"Исполнитель команд инициализирован (песочница: {sandbox})")
    
    def execute(self, parsed_command: Dict[str, Any]) -> Dict[str, Any]:
        """
        Выполнение распознанной команды
        
        Args:
            parsed_command (Dict): Распознанная команда
            
        Returns:
            Dict: Результат выполнения
        """
        start_time = time.time()
        self.execution_stats['total_commands'] += 1
        
        try:
            # Проверка безопасности в песочнице
            if self.sandbox and not self._is_safe_command(parsed_command):
                return self._create_result(
                    success=False,
                    message=f"Команда заблокирована в режиме песочницы: {parsed_command.get('action', 'unknown')}",
                    execution_time=time.time() - start_time
                )
            
            # Маршрутизация команды по типу
            command_type = parsed_command.get('command_type', 'unknown')
            
            if command_type == 'file_operation':
                result = self._execute_file_operation(parsed_command)
            elif command_type == 'application':
                result = self._execute_application_command(parsed_command)
            elif command_type == 'text_input':
                result = self._execute_text_input(parsed_command)
            elif command_type == 'mouse_action':
                result = self._execute_mouse_action(parsed_command)
            elif command_type == 'screenshot':
                result = self._execute_screenshot(parsed_command)
            elif command_type == 'system_control':
                result = self._execute_system_control(parsed_command)
            elif command_type == 'help':
                result = self._execute_help(parsed_command)
            else:
                result = self._create_result(
                    success=False,
                    message=f"Неизвестный тип команды: {command_type}"
                )
            
            # Обновление статистики
            if result.get('success', False):
                self.execution_stats['successful_commands'] += 1
            else:
                self.execution_stats['failed_commands'] += 1
            
            result['execution_time'] = time.time() - start_time
            self.execution_stats['last_execution_time'] = time.time()
            
            return result
            
        except Exception as e:
            self.logger.error(f"Ошибка выполнения команды: {e}", exc_info=True)
            self.execution_stats['failed_commands'] += 1
            
            return self._create_result(
                success=False,
                message=f"Ошибка выполнения: {str(e)}",
                execution_time=time.time() - start_time
            )
    
    def _is_safe_command(self, parsed_command: Dict[str, Any]) -> bool:
        """Проверка безопасности команды в песочнице"""
        
        command_type = parsed_command.get('command_type', 'unknown')
        action = parsed_command.get('action', 'unknown')
        
        if command_type not in self.safe_commands:
            return False
        
        return action in self.safe_commands[command_type]
    
    def _execute_file_operation(self, parsed_command: Dict[str, Any]) -> Dict[str, Any]:
        """Выполнение файловых операций"""
        
        action = parsed_command.get('action', '')
        target = parsed_command.get('target', '')
        parameters = parsed_command.get('parameters', {})
        
        try:
            if action == 'create':
                # Создание файла
                content = parameters.get('content', '')
                
                # Обеспечиваем безопасный путь
                safe_path = self._get_safe_path(target)
                
                # Создаем директорию если нужно
                os.makedirs(os.path.dirname(safe_path), exist_ok=True)
                
                # Записываем файл
                with open(safe_path, 'w', encoding='utf-8') as f:
                    f.write(content)
                
                return self._create_result(
                    success=True,
                    message=f"Файл создан: {safe_path}",
                    data={'file_path': safe_path, 'size': len(content)}
                )
            
            elif action == 'delete':
                safe_path = self._get_safe_path(target)
                
                if os.path.exists(safe_path):
                    os.remove(safe_path)
                    return self._create_result(
                        success=True,
                        message=f"Файл удален: {safe_path}"
                    )
                else:
                    return self._create_result(
                        success=False,
                        message=f"Файл не найден: {safe_path}"
                    )
            
            elif action == 'open':
                safe_path = self._get_safe_path(target)
                
                if os.path.exists(safe_path):
                    # Открываем файл системным приложением
                    if platform.system() == 'Linux':
                        subprocess.run(['xdg-open', safe_path], check=False)
                    elif platform.system() == 'Darwin':
                        subprocess.run(['open', safe_path], check=False)
                    elif platform.system() == 'Windows':
                        os.startfile(safe_path)
                    
                    return self._create_result(
                        success=True,
                        message=f"Файл открыт: {safe_path}"
                    )
                else:
                    return self._create_result(
                        success=False,
                        message=f"Файл не найден: {safe_path}"
                    )
            
            elif action == 'read':
                safe_path = self._get_safe_path(target)
                
                if os.path.exists(safe_path):
                    with open(safe_path, 'r', encoding='utf-8') as f:
                        content = f.read()
                    
                    return self._create_result(
                        success=True,
                        message=f"Файл прочитан: {safe_path}",
                        data={'content': content, 'size': len(content)}
                    )
                else:
                    return self._create_result(
                        success=False,
                        message=f"Файл не найден: {safe_path}"
                    )
            
            elif action == 'list':
                # Список файлов в директории
                directory = target or os.getcwd()
                safe_dir = self._get_safe_path(directory)
                
                if os.path.isdir(safe_dir):
                    files = []
                    for item in os.listdir(safe_dir):
                        item_path = os.path.join(safe_dir, item)
                        files.append({
                            'name': item,
                            'type': 'directory' if os.path.isdir(item_path) else 'file',
                            'size': os.path.getsize(item_path) if os.path.isfile(item_path) else 0
                        })
                    
                    return self._create_result(
                        success=True,
                        message=f"Найдено файлов: {len(files)}",
                        data={'files': files, 'directory': safe_dir}
                    )
                else:
                    return self._create_result(
                        success=False,
                        message=f"Директория не найдена: {safe_dir}"
                    )
            
            else:
                return self._create_result(
                    success=False,
                    message=f"Неизвестное файловое действие: {action}"
                )
                
        except Exception as e:
            return self._create_result(
                success=False,
                message=f"Ошибка файловой операции: {str(e)}"
            )
    
    def _execute_application_command(self, parsed_command: Dict[str, Any]) -> Dict[str, Any]:
        """Выполнение команд приложений"""
        
        action = parsed_command.get('action', '')
        target = parsed_command.get('target', '')
        
        try:
            if action == 'open' or action == 'start':
                # Маппинг популярных приложений
                app_mapping = {
                    'browser': 'firefox',
                    'браузер': 'firefox',
                    'terminal': 'gnome-terminal',
                    'терминал': 'gnome-terminal',
                    'notepad': 'gedit',
                    'блокнот': 'gedit',
                    'calculator': 'gnome-calculator',
                    'калькулятор': 'gnome-calculator',
                    'files': 'nautilus',
                    'файлы': 'nautilus'
                }
                
                app_name = app_mapping.get(target.lower(), target)
                
                if self.sandbox:
                    return self._create_result(
                        success=False,
                        message=f"Запуск приложений заблокирован в песочнице: {app_name}"
                    )
                
                # Пытаемся запустить приложение
                try:
                    subprocess.Popen([app_name], 
                                   stdout=subprocess.DEVNULL, 
                                   stderr=subprocess.DEVNULL)
                    
                    return self._create_result(
                        success=True,
                        message=f"Приложение запущено: {app_name}",
                        data={'application': app_name}
                    )
                    
                except FileNotFoundError:
                    return self._create_result(
                        success=False,
                        message=f"Приложение не найдено: {app_name}"
                    )
            
            elif action == 'list':
                # Список запущенных процессов
                try:
                    import psutil
                    processes = []
                    
                    for proc in psutil.process_iter(['pid', 'name', 'cpu_percent']):
                        try:
                            processes.append({
                                'pid': proc.info['pid'],
                                'name': proc.info['name'],
                                'cpu_percent': proc.info['cpu_percent']
                            })
                        except (psutil.NoSuchProcess, psutil.AccessDenied):
                            pass
                    
                    return self._create_result(
                        success=True,
                        message=f"Найдено процессов: {len(processes)}",
                        data={'processes': processes[:20]}  # Ограничиваем вывод
                    )
                    
                except ImportError:
                    return self._create_result(
                        success=False,
                        message="psutil не установлен для получения списка процессов"
                    )
            
            else:
                return self._create_result(
                    success=False,
                    message=f"Неизвестное действие приложения: {action}"
                )
                
        except Exception as e:
            return self._create_result(
                success=False,
                message=f"Ошибка команды приложения: {str(e)}"
            )
    
    def _execute_text_input(self, parsed_command: Dict[str, Any]) -> Dict[str, Any]:
        """Выполнение ввода текста"""
        
        action = parsed_command.get('action', '')
        target = parsed_command.get('target', '')
        
        if action == 'type':
            if self.sandbox:
                # В песочнице просто логируем
                return self._create_result(
                    success=True,
                    message=f"[ПЕСОЧНИЦА] Ввод текста: '{target}'",
                    data={'text': target, 'length': len(target)}
                )
            
            try:
                # Пытаемся использовать контроллер ввода
                if hasattr(self.input_controller, 'type_text'):
                    self.input_controller.type_text(target)
                    return self._create_result(
                        success=True,
                        message=f"Текст введен: '{target}'",
                        data={'text': target, 'length': len(target)}
                    )
                else:
                    return self._create_result(
                        success=False,
                        message="Контроллер ввода не поддерживает ввод текста"
                    )
                    
            except Exception as e:
                return self._create_result(
                    success=False,
                    message=f"Ошибка ввода текста: {str(e)}"
                )
        
        else:
            return self._create_result(
                success=False,
                message=f"Неизвестное действие ввода: {action}"
            )
    
    def _execute_mouse_action(self, parsed_command: Dict[str, Any]) -> Dict[str, Any]:
        """Выполнение действий мыши"""
        
        action = parsed_command.get('action', '')
        target = parsed_command.get('target', '')
        
        if self.sandbox:
            return self._create_result(
                success=True,
                message=f"[ПЕСОЧНИЦА] Действие мыши: {action} на {target}"
            )
        
        try:
            if action == 'click':
                if hasattr(self.input_controller, 'click'):
                    # Простой клик (нужно будет улучшить для поиска элементов)
                    self.input_controller.click(100, 100)  # Заглушка
                    return self._create_result(
                        success=True,
                        message=f"Клик выполнен: {target}"
                    )
                else:
                    return self._create_result(
                        success=False,
                        message="Контроллер не поддерживает клики мыши"
                    )
            
            elif action == 'scroll':
                if hasattr(self.input_controller, 'scroll'):
                    direction = 'up' if 'вверх' in target else 'down'
                    self.input_controller.scroll(direction)
                    return self._create_result(
                        success=True,
                        message=f"Прокрутка выполнена: {direction}"
                    )
                else:
                    return self._create_result(
                        success=False,
                        message="Контроллер не поддерживает прокрутку"
                    )
            
            else:
                return self._create_result(
                    success=False,
                    message=f"Неизвестное действие мыши: {action}"
                )
                
        except Exception as e:
            return self._create_result(
                success=False,
                message=f"Ошибка действия мыши: {str(e)}"
            )
    
    def _execute_screenshot(self, parsed_command: Dict[str, Any]) -> Dict[str, Any]:
        """Выполнение создания скриншота"""
        
        try:
            if hasattr(self.input_controller, 'take_screenshot'):
                screenshot_path = self.input_controller.take_screenshot()
                
                if screenshot_path and os.path.exists(screenshot_path):
                    return self._create_result(
                        success=True,
                        message=f"Скриншот создан: {screenshot_path}",
                        data={'screenshot_path': screenshot_path}
                    )
                else:
                    return self._create_result(
                        success=False,
                        message="Не удалось создать скриншот"
                    )
            else:
                return self._create_result(
                    success=False,
                    message="Контроллер не поддерживает создание скриншотов"
                )
                
        except Exception as e:
            return self._create_result(
                success=False,
                message=f"Ошибка создания скриншота: {str(e)}"
            )
    
    def _execute_system_control(self, parsed_command: Dict[str, Any]) -> Dict[str, Any]:
        """Выполнение системных команд"""
        
        if self.sandbox:
            return self._create_result(
                success=False,
                message="Системные команды заблокированы в песочнице"
            )
        
        action = parsed_command.get('action', '')
        
        return self._create_result(
            success=False,
            message=f"Системные команды пока не реализованы: {action}"
        )
    
    def _execute_help(self, parsed_command: Dict[str, Any]) -> Dict[str, Any]:
        """Выполнение команды справки"""
        
        help_text = """
🤖 Daur-AI - Доступные команды:

📁 ФАЙЛЫ:
• создай файл <имя> - создать файл
• удали файл <имя> - удалить файл  
• открой файл <имя> - открыть файл
• покажи файлы - список файлов

🚀 ПРИЛОЖЕНИЯ:
• открой браузер - запустить браузер
• открой терминал - запустить терминал
• покажи процессы - список процессов

⌨️ ТЕКСТ:
• напечатай <текст> - ввести текст

📸 СКРИНШОТ:
• сделай скриншот - создать снимок экрана

❓ СПРАВКА:
• помощь - показать эту справку

Примеры:
• "создай файл test.txt"
• "открой браузер"  
• "напечатай привет мир"
• "сделай скриншот"
        """
        
        return self._create_result(
            success=True,
            message="Справка по командам",
            data={'help_text': help_text.strip()}
        )
    
    def _get_safe_path(self, path: str) -> str:
        """Получение безопасного пути к файлу"""
        
        # Базовая директория для файлов
        base_dir = os.path.expanduser("~/daur_ai_files")
        os.makedirs(base_dir, exist_ok=True)
        
        # Очищаем путь от опасных символов
        safe_name = "".join(c for c in path if c.isalnum() or c in "._-")
        
        # Если нет расширения, добавляем .txt
        if '.' not in safe_name:
            safe_name += '.txt'
        
        return os.path.join(base_dir, safe_name)
    
    def _create_result(self, success: bool, message: str, data: Optional[Dict] = None, execution_time: Optional[float] = None) -> Dict[str, Any]:
        """Создание результата выполнения"""
        
        result = {
            'success': success,
            'message': message,
            'timestamp': time.time()
        }
        
        if data:
            result['data'] = data
        
        if execution_time is not None:
            result['execution_time'] = execution_time
        
        return result
    
    def get_stats(self) -> Dict[str, Any]:
        """Получение статистики выполнения"""
        
        success_rate = 0
        if self.execution_stats['total_commands'] > 0:
            success_rate = (self.execution_stats['successful_commands'] / 
                          self.execution_stats['total_commands']) * 100
        
        return {
            **self.execution_stats,
            'success_rate': round(success_rate, 2)
        }
