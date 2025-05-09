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
from queue import Queue
from threading import Thread

# Импорты компонентов системы
from src.input.controller import InputController
from src.apps.manager import AppManager
from src.files.manager import FileManager
from src.parser.command_parser import CommandParser
from src.ai.model_manager import AIModelManager
from src.logger.logger import ActionLogger


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
            
            # Инициализация контроллера ввода (мышь, клавиатура)
            self.input_controller = InputController(self.os_platform)
            
            # Инициализация менеджера приложений
            self.app_manager = AppManager(self.os_platform, self.input_controller)
            
            # Инициализация менеджера файлов
            self.file_manager = FileManager(
                allowed_extensions=config["file_operations"]["allowed_extensions"],
                restricted_paths=config["file_operations"]["restricted_paths"]
            )
            
            # Инициализация AI-модели
            self.ai_manager = AIModelManager(
                model_path=config["model_path"],
                timeout=config["advanced"]["model_inference_timeout"]
            )
            
            # Инициализация парсера команд
            self.command_parser = CommandParser(self.ai_manager)
            
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
            actions = self.command_parser.parse(command)
            
            if not actions:
                self.logger.warning(f"Не удалось распознать команду: {command}")
                self.action_logger.log_action(
                    command=command,
                    action="parse_failed",
                    result="failure",
                    error="Не удалось распознать команду"
                )
                self.ui.show_message("Не удалось распознать команду")
                return
            
            # Выполнение каждого действия из списка
            for idx, action in enumerate(actions):
                self.logger.debug(f"Выполнение действия {idx+1}/{len(actions)}: {action}")
                
                try:
                    # Определение типа действия
                    action_type = action.get("action")
                    
                    # Выполнение действия в зависимости от типа
                    if action_type.startswith("input_"):
                        # Действия с вводом (мышь, клавиатура)
                        result = self.input_controller.execute_action(action)
                    
                    elif action_type.startswith("app_"):
                        # Действия с приложениями
                        result = self.app_manager.execute_action(action)
                    
                    elif action_type.startswith("file_"):
                        # Действия с файлами
                        result = self.file_manager.execute_action(action)
                    
                    else:
                        # Неизвестное действие
                        self.logger.warning(f"Неизвестный тип действия: {action_type}")
                        result = False
                        error = f"Неизвестный тип действия: {action_type}"
                    
                    # Логирование результата
                    if result:
                        self.action_logger.log_action(
                            command=command,
                            action=action,
                            result="success"
                        )
                    else:
                        self.action_logger.log_action(
                            command=command,
                            action=action,
                            result="failure",
                            error=error if 'error' in locals() else "Сбой выполнения"
                        )
                    
                    # Пауза между действиями
                    time.sleep(0.1)
                
                except Exception as e:
                    self.logger.error(f"Ошибка при выполнении действия: {e}", exc_info=True)
                    self.action_logger.log_action(
                        command=command,
                        action=action,
                        result="failure",
                        error=str(e)
                    )
                    self.ui.show_message(f"Ошибка: {str(e)}")
            
            self.logger.info(f"Команда выполнена: {command}")
            self.ui.show_message("Команда выполнена")
            
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
                
            except Queue.Empty:
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
