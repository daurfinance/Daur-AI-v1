#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
Daur-AI: Ядро агента
Основной класс агента, отвечающий за координацию всех компонентов системы

Версия: 1.0
Дата: 09.05.2025
"""

import os
import sys
import time
import logging
import platform
import queue
from queue import Queue, Empty
from threading import Thread

# Импорты компонентов системы
try:
    from src.input.advanced_controller import create_input_controller
    InputController = create_input_controller
except ImportError:
    try:
        from src.input.controller import InputController
    except ImportError:
        # Используем упрощенную версию если основная недоступна
        from src.input.simple_controller import SimpleInputController as InputController
from src.apps.manager import AppManager
from src.files.manager import FileManager
try:
    from src.parser.enhanced_command_parser import create_enhanced_parser
    CommandParser = create_enhanced_parser
except ImportError:
    from src.parser.command_parser import CommandParser
try:
    from src.ai.enhanced_model_manager import EnhancedModelManager as AIModelManager
except ImportError:
    try:
        from src.ai.model_manager import AIModelManager
    except ImportError:
        # Используем упрощенную модель если основная недоступна
        from src.ai.simple_model import MockModelManager as AIModelManager
from src.logger.logger import ActionLogger
from src.executor.command_executor import CommandExecutor


class DaurAgent:
    """
    Основной класс агента Daur-AI
    Координирует работу всех компонентов системы и обрабатывает команды пользователя
    """
    
    def __init__(self, config, ui_mode="console", sandbox=False):
        """
        Инициализация агента
        
        Args:
            config (dict): Конфигурация агента
            ui_mode (str): Режим интерфейса (console или gui)
            sandbox (bool): Запуск в песочнице
        """
        self.logger = logging.getLogger('daur_ai')
        self.logger.info("Инициализация Daur-AI агента")
        
        # Сохранение конфигурации
        self.config = config
        self.ui_mode = ui_mode
        self.sandbox_mode = sandbox
        
        # Определение ОС
        self.os_platform = platform.system()
        self.logger.info(f"Определена ОС: {self.os_platform}")
        
        # Инициализация компонентов
        try:
            # Инициализация логгера действий
            self.action_logger = ActionLogger(
                log_path=config["log_path"], 
                encrypt=config.get("encrypt_logs", False)
            )
            
            # Инициализация контроллера ввода
            if callable(InputController):
                # Новый интерфейс с фабричной функцией
                self.input_controller = InputController(self.os_platform)
            else:
                # Старый интерфейс с классом
                self.input_controller = InputController(self.os_platform)
            
            # Инициализация менеджера приложений
            self.app_manager = AppManager(self.os_platform, self.input_controller)
            
            # Инициализация менеджера файлов
            self.file_manager = FileManager(
                allowed_extensions=config["file_operations"]["allowed_extensions"],
                restricted_paths=config["file_operations"]["restricted_paths"]
            )
            
            # Инициализация AI-модели
            try:
                # Проверяем, используется ли EnhancedModelManager
                if AIModelManager.__name__ == 'EnhancedModelManager':
                    self.ai_manager = AIModelManager(config)
                else:
                    # Старый интерфейс
                    self.ai_manager = AIModelManager(
                        model_path=config["model_path"],
                        timeout=config["advanced"]["model_inference_timeout"]
                    )
            except (FileNotFoundError, ImportError) as e:
                self.logger.warning(f"Не удалось загрузить основную AI-модель ({e}), используется упрощенная версия")
                from src.ai.simple_model import MockModelManager
                self.ai_manager = MockModelManager()
            
            # Инициализация парсера команд
            if callable(CommandParser):
                # Новый улучшенный парсер
                self.command_parser = CommandParser(self.ai_manager)
            else:
                # Старый парсер
                self.command_parser = CommandParser(self.ai_manager)
            
            # Инициализация исполнителя команд
            self.command_executor = CommandExecutor(
                input_controller=self.input_controller,
                app_manager=self.app_manager,
                file_manager=self.file_manager,
                sandbox=sandbox
            )
            
            # Очередь команд
            self.command_queue = Queue()
            
            # Флаг работы агента
            self.running = False
            
            # Инициализация UI в зависимости от режима
            self._init_ui(ui_mode)
            
            # Песочница
            if sandbox:
                self.logger.warning("Запуск в песочнице! Некоторые функции могут быть ограничены")
                self._setup_sandbox()
                
            self.logger.info("Инициализация агента успешно завершена")
            
        except Exception as e:
            self.logger.error(f"Ошибка инициализации агента: {e}", exc_info=True)
            raise
    
    def _init_ui(self, ui_mode):
        """Инициализация пользовательского интерфейса"""
        self.logger.info(f"Инициализация интерфейса: {ui_mode}")
        
        if ui_mode == "console":
            from src.ui.console import ConsoleUI
            ui_config = self.config["ui_settings"]["console"]
            self.ui = ConsoleUI(
                prompt=ui_config["prompt"],
                history_size=ui_config["history_size"],
                command_callback=self.handle_command
            )
        
        elif ui_mode == "gui":
            from src.ui.gui import GraphicalUI
            ui_config = self.config["ui_settings"]["gui"]
            self.ui = GraphicalUI(
                theme=ui_config["theme"],
                window_size=ui_config["window_size"],
                command_callback=self.handle_command
            )
        
        else:
            raise ValueError(f"Неподдерживаемый режим интерфейса: {ui_mode}")
    
    def _setup_sandbox(self):
        """Настройка режима песочницы"""
        if self.sandbox_mode:
            # Здесь может быть инициализация Docker-контейнера или другие ограничения
            self.logger.info("Настройка песочницы")
            # TODO: Реализация песочницы (Docker, chroot и т.д.)
    
    def handle_command(self, command):
        """
        Обработка команды пользователя
        
        Args:
            command (str): Команда от пользователя
        
        Returns:
            str: Ответ агента
        """
        self.logger.debug(f"Получена команда: {command}")
        
        # Команды управления агентом
        if command.lower() == "exit" or command.lower() == "quit":
            self.running = False
            return "До свидания!"
            
        if command.lower() == "help":
            return self._get_help_text()
        
        # Добавление команды в очередь
        self.command_queue.put(command)
        
        # Ответ пользователю
        return "Команда принята к исполнению"
    
    def _get_help_text(self):
        """Получение текста помощи"""
        help_text = [
            "Daur-AI - Универсальный автономный ИИ-агент",
            "---------------------------------------------",
            "Доступные команды:",
            "  help - Показать эту справку",
            "  exit, quit - Выйти из программы",
            "",
            "Примеры команд:",
            "  создай веб-приложение на Flask",
            "  открой браузер и перейди на google.com",
            "  создай файл hello.py с функцией приветствия",
        ]
        
        return "\n".join(help_text)
    
    def _process_command(self, command):
        """
        Обработка команды в отдельном потоке
        
        Args:
            command (str): Команда пользователя
        """
        self.logger.info(f"Обработка команды: {command}")
        
        try:
            # Парсинг команды
            parsed_command = self.command_parser.parse(command)
            
            if not parsed_command or parsed_command.get('command_type') == 'unknown':
                error_msg = parsed_command.get('parameters', {}).get('error', 'Не удалось распознать команду')
                self.logger.warning(f"Не удалось распознать команду: {command}")
                self.action_logger.log_action(
                    command=command,
                    action="parse_failed",
                    result="failure",
                    error=error_msg
                )
                self.ui.show_message(f"❌ {error_msg}")
                return
            
            # Выполнение команды через исполнителя
            self.logger.debug(f"Выполнение команды: {parsed_command}")
            
            try:
                # Выполняем команду
                execution_result = self.command_executor.execute(parsed_command)
                
                # Обработка результата
                if execution_result.get('success', False):
                    message = execution_result.get('message', 'Команда выполнена')
                    self.logger.info(f"Команда выполнена успешно: {message}")
                    
                    # Логирование успешного выполнения
                    self.action_logger.log_action(
                        command=command,
                        action=parsed_command.get('action', 'unknown'),
                        result="success",
                        details=execution_result.get('data', {})
                    )
                    
                    # Показываем результат пользователю
                    if execution_result.get('data', {}).get('help_text'):
                        # Специальная обработка справки
                        self.ui.show_message(execution_result['data']['help_text'])
                    else:
                        self.ui.show_message(f"✅ {message}")
                        
                        # Дополнительная информация если есть
                        if 'data' in execution_result:
                            data = execution_result['data']
                            if 'file_path' in data:
                                self.ui.show_message(f"📁 Путь: {data['file_path']}")
                            elif 'files' in data:
                                files_info = f"📂 Файлов: {len(data['files'])}"
                                self.ui.show_message(files_info)
                
                else:
                    error_msg = execution_result.get('message', 'Ошибка выполнения команды')
                    self.logger.error(f"Ошибка выполнения команды: {error_msg}")
                    
                    # Логирование ошибки
                    self.action_logger.log_action(
                        command=command,
                        action=parsed_command.get('action', 'unknown'),
                        result="failure",
                        error=error_msg
                    )
                    
            except Exception as e:
                self.logger.error(f"Ошибка при выполнении команды: {e}", exc_info=True)
                self.action_logger.log_action(
                    command=command,
                    action=parsed_command.get('action', 'unknown'),
                    result="failure",
                    error=str(e)
                )
                self.ui.show_message(f"❌ Ошибка выполнения: {str(e)}")
            
            self.logger.info(f"Команда обработана: {command}")
            
        except Exception as e:
            self.logger.error(f"Ошибка обработки команды: {e}", exc_info=True)
            self.ui.show_message(f"Ошибка обработки команды: {str(e)}")
    
    def _command_worker(self):
        """Рабочий поток для обработки команд из очереди"""
        self.logger.debug("Запуск рабочего потока команд")
        
        while self.running:
            try:
                # Получение команды из очереди
                command = self.command_queue.get(timeout=1)
                
                # Обработка команды
                self._process_command(command)
                
                # Пометка задачи как выполненной
                self.command_queue.task_done()
                
            except Empty:
                # Очередь пуста, ожидание
                pass
            except Exception as e:
                self.logger.error(f"Ошибка в рабочем потоке: {e}", exc_info=True)
    
    def run(self):
        """Запуск агента"""
        self.logger.info("Запуск Daur-AI агента")
        self.running = True
        
        try:
            # Запуск рабочего потока команд
            worker_thread = Thread(target=self._command_worker, daemon=True)
            worker_thread.start()
            
            # Запуск пользовательского интерфейса
            self.ui.run()
            
            # Завершение рабочего потока после закрытия UI
            self.running = False
            worker_thread.join(timeout=5)
            
        except KeyboardInterrupt:
            self.logger.info("Принудительное завершение работы")
            self.running = False
        
        except Exception as e:
            self.logger.error(f"Критическая ошибка при работе агента: {e}", exc_info=True)
            self.running = False
        
        finally:
            self.logger.info("Завершение работы Daur-AI агента")
    
    def cleanup(self):
        """Очистка ресурсов при завершении работы"""
        self.logger.info("Очистка ресурсов")
        
        # Закрытие моделей ИИ
        if hasattr(self, 'ai_manager'):
            self.ai_manager.cleanup()
        
        # Очистка в менеджере приложений
        if hasattr(self, 'app_manager'):
            self.app_manager.cleanup()
        
        # Отключение песочницы
        if self.sandbox_mode:
            self._cleanup_sandbox()
    
    def _cleanup_sandbox(self):
        """Очистка песочницы при завершении работы"""
        if self.sandbox_mode:
            self.logger.info("Очистка песочницы")
            # TODO: Реализация очистки песочницы (остановка Docker-контейнера и т.д.)
