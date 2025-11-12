#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
Daur-AI: Консольный интерфейс
Модуль реализует текстовый интерфейс для работы с агентом

Версия: 1.0
Дата: 09.05.2025
"""

import os
import sys
import time
import logging
import threading
import readline
from typing import Callable, List, Optional


class ConsoleUI:
    """
    Консольный интерфейс для работы с агентом Daur-AI
    """
    
    def __init__(self, prompt: str = "Daur-AI> ", history_size: int = 100,
                 command_callback: Callable[[str], str] = None):
        """
        Инициализация консольного интерфейса
        
        Args:
            prompt (str): Текст приглашения для ввода команды
            history_size (int): Размер истории команд
            command_callback (Callable): Функция обратного вызова для обработки команд
        """
        self.logger = logging.getLogger('daur_ai.ui.console')
        self.prompt = prompt
        self.history_size = history_size
        self.command_callback = command_callback
        self.is_running = False
        self.history_file = os.path.expanduser('~/.daur_ai_history')
        
        # Настройка readline
        readline.set_history_length(history_size)
        
        # Попытка загрузить историю команд
        try:
            if os.path.exists(self.history_file):
                readline.read_history_file(self.history_file)
                self.logger.debug(f"Загружена история команд из {self.history_file}")
        except Exception as e:
            self.logger.warning(f"Не удалось загрузить историю команд: {e}")
        
        self.logger.info("Консольный интерфейс инициализирован")
    
    def run(self):
        """Запуск консольного интерфейса"""
        self.is_running = True
        self.logger.info("Запуск консольного интерфейса")
        
        self._print_welcome_message()
        
        try:
            while self.is_running:
                try:
                    # Чтение ввода пользователя
                    user_input = input(self.prompt)
                    
                    # Пропуск пустых строк
                    if not user_input.strip():
                        continue
                    
                    # Добавление в историю
                    readline.add_history(user_input)
                    
                    # Обработка выхода
                    if user_input.lower() in ['exit', 'quit']:
                        self.is_running = False
                        self.show_message("До свидания!")
                        
                        # Сохраняем также через обработчик команд для корректного завершения
                        if self.command_callback:
                            self.command_callback(user_input)
                        break
                    
                    # Обработка команды через колбэк
                    if self.command_callback:
                        response = self.command_callback(user_input)
                        if response:
                            print(response)
                    else:
                        print("Обработчик команд не определен")
                
                except KeyboardInterrupt:
                    print("\nПрервано пользователем. Для выхода введите 'exit'.")
                
                except EOFError:
                    # Ctrl+D
                    print("\nКонец ввода. Завершение работы.")
                    self.is_running = False
                    if self.command_callback:
                        self.command_callback("exit")
                    break
                
                except Exception as e:
                    self.logger.error(f"Ошибка при обработке ввода: {e}", exc_info=True)
                    print(f"Произошла ошибка: {str(e)}")
        
        finally:
            # Сохранение истории команд
            try:
                readline.write_history_file(self.history_file)
                self.logger.debug(f"История команд сохранена в {self.history_file}")
            except Exception as e:
                self.logger.warning(f"Не удалось сохранить историю команд: {e}")
            
            self.logger.info("Завершение работы консольного интерфейса")
    
    def _print_welcome_message(self):
        """Вывод приветственного сообщения"""
        welcome_message = [
            "╔════════════════════════════════════════════════════════╗",
            "║                                                        ║",
            "║             Daur-AI - Универсальный ИИ-агент           ║",
            "║                                                        ║",
            "║  Введите команду на естественном языке или 'help'      ║",
            "║  для получения справки. Для выхода введите 'exit'.     ║",
            "║                                                        ║",
            "╚════════════════════════════════════════════════════════╝",
        ]
        
        print("\n".join(welcome_message))
    
    def show_message(self, message: str):
        """
        Вывод сообщения в консоль
        
        Args:
            message (str): Текст для вывода
        """
        # Вывод сообщения, при необходимости с очисткой текущей строки ввода
        print(f"\n{message}")
    
    def show_progress(self, message: str, duration: float = None):
        """
        Отображение индикатора прогресса
        
        Args:
            message (str): Сообщение о прогрессе
            duration (float, optional): Продолжительность индикации в секундах
        """
        stop_event = threading.Event()
        
        def _progress_indicator():
            """Функция для отображения индикатора прогресса"""
            spinner = ['/', '-', '\\', '|']
            i = 0
            while not stop_event.is_set():
                # Отображение спиннера
                print(f"\r{message} {spinner[i % len(spinner)]}", end='', flush=True)
                i += 1
                time.sleep(0.1)
            # Очистка строки по завершении
            print("\r" + " " * (len(message) + 2), end="\r", flush=True)
        
        # Запуск индикатора в отдельном потоке
        progress_thread = threading.Thread(target=_progress_indicator)
        progress_thread.daemon = True
        progress_thread.start()
        
        # Если указана продолжительность, ждём и останавливаем индикатор
        if duration:
            time.sleep(duration)
            stop_event.set()
            progress_thread.join()
        
        return stop_event  # Возвращаем событие для возможности остановки извне


class ColoredConsoleUI(ConsoleUI):
    """
    Расширенный консольный интерфейс с поддержкой цветов
    """
    
    # ANSI цветовые коды
    COLORS = {
        'reset': '\033[0m',
        'bold': '\033[1m',
        'red': '\033[31m',
        'green': '\033[32m',
        'yellow': '\033[33m',
        'blue': '\033[34m',
        'magenta': '\033[35m',
        'cyan': '\033[36m',
        'white': '\033[37m',
        'bg_red': '\033[41m',
        'bg_green': '\033[42m',
        'bg_yellow': '\033[43m',
        'bg_blue': '\033[44m',
    }
    
    def __init__(self, prompt: str = "\033[36mDaur-AI>\033[0m ", 
                 history_size: int = 100,
                 command_callback: Callable[[str], str] = None):
        """
        Инициализация цветного консольного интерфейса
        
        Args:
            prompt (str): Текст приглашения для ввода команды
            history_size (int): Размер истории команд
            command_callback (Callable): Функция обратного вызова для обработки команд
        """
        # Проверка поддержки цветного вывода
        self.has_color_support = (
            sys.platform != "win32" 
            or "ANSICON" in os.environ
            or "WT_SESSION" in os.environ
        )
        
        # Если цвета не поддерживаются, убираем коды ANSI из prompt
        if not self.has_color_support:
            for color in self.COLORS.values():
                prompt = prompt.replace(color, '')
        
        super().__init__(prompt, history_size, command_callback)
        self.logger.info("Инициализирован цветной консольный интерфейс")
    
    def _print_welcome_message(self):
        """Вывод приветственного сообщения с цветами"""
        if not self.has_color_support:
            # Если нет поддержки цветов, используем обычное приветствие
            super()._print_welcome_message()
            return
        
        welcome_message = [
            f"{self.COLORS['cyan']}╔════════════════════════════════════════════════════════╗{self.COLORS['reset']}",
            f"{self.COLORS['cyan']}║{self.COLORS['reset']}                                                        {self.COLORS['cyan']}║{self.COLORS['reset']}",
            f"{self.COLORS['cyan']}║{self.COLORS['reset']}             {self.COLORS['bold']}{self.COLORS['green']}Daur-AI - Универсальный ИИ-агент{self.COLORS['reset']}           {self.COLORS['cyan']}║{self.COLORS['reset']}",
            f"{self.COLORS['cyan']}║{self.COLORS['reset']}                                                        {self.COLORS['cyan']}║{self.COLORS['reset']}",
            f"{self.COLORS['cyan']}║{self.COLORS['reset']}  Введите команду на естественном языке или {self.COLORS['yellow']}'help'{self.COLORS['reset']}      {self.COLORS['cyan']}║{self.COLORS['reset']}",
            f"{self.COLORS['cyan']}║{self.COLORS['reset']}  для получения справки. Для выхода введите {self.COLORS['red']}'exit'{self.COLORS['reset']}.     {self.COLORS['cyan']}║{self.COLORS['reset']}",
            f"{self.COLORS['cyan']}║{self.COLORS['reset']}                                                        {self.COLORS['cyan']}║{self.COLORS['reset']}",
            f"{self.COLORS['cyan']}╚════════════════════════════════════════════════════════╝{self.COLORS['reset']}",
        ]
        
        print("\n".join(welcome_message))

    def show_message(self, message: str, message_type: str = "info"):
        """
        Вывод сообщения в консоль с цветовым оформлением
        
        Args:
            message (str): Текст для вывода
            message_type (str): Тип сообщения (info, success, warning, error)
        """
        if not self.has_color_support:
            # Если нет поддержки цветов, используем обычный вывод
            super().show_message(message)
            return
        
        color = self.COLORS['reset']
        prefix = ""
        
        if message_type == "info":
            color = self.COLORS['blue']
            prefix = "ℹ "
        elif message_type == "success":
            color = self.COLORS['green']
            prefix = "✓ "
        elif message_type == "warning":
            color = self.COLORS['yellow']
            prefix = "⚠ "
        elif message_type == "error":
            color = self.COLORS['red']
            prefix = "✗ "
        
        print(f"\n{color}{prefix}{message}{self.COLORS['reset']}")
    
    def show_progress(self, message: str, duration: float = None):
        """
        Отображение индикатора прогресса с цветами
        
        Args:
            message (str): Сообщение о прогрессе
            duration (float, optional): Продолжительность индикации в секундах
        """
        if not self.has_color_support:
            # Если нет поддержки цветов, используем обычный индикатор
            return super().show_progress(message, duration)
        
        stop_event = threading.Event()
        colored_message = f"{self.COLORS['cyan']}{message}{self.COLORS['reset']}"
        
        def _progress_indicator():
            """Функция для отображения индикатора прогресса с цветами"""
            spinner = ['/', '-', '\\', '|']
            i = 0
            while not stop_event.is_set():
                # Отображение спиннера с цветом
                print(f"\r{colored_message} {self.COLORS['yellow']}{spinner[i % len(spinner)]}{self.COLORS['reset']}", 
                      end='', flush=True)
                i += 1
                time.sleep(0.1)
            # Очистка строки по завершении
            print("\r" + " " * (len(message) + 2), end="\r", flush=True)
        
        # Запуск индикатора в отдельном потоке
        progress_thread = threading.Thread(target=_progress_indicator)
        progress_thread.daemon = True
        progress_thread.start()
        
        # Если указана продолжительность, ждём и останавливаем индикатор
        if duration:
            time.sleep(duration)
            stop_event.set()
            progress_thread.join()
        
        return stop_event  # Возвращаем событие для возможности остановки извне


# Пример использования
if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO)
    
    def command_handler(cmd):
        """Пример обработчика команд"""
        if cmd.lower() in ['exit', 'quit']:
            return "Выход из программы..."
        return f"Обрабатывается команда: {cmd}"
    
    # Использование цветного интерфейса, если поддерживается
    ui = ColoredConsoleUI(command_callback=command_handler)
    ui.run()
