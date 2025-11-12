#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
Daur-AI: Графический интерфейс
Модуль реализует графический интерфейс для работы с агентом

Версия: 1.0
Дата: 09.05.2025
"""

import os
import sys
import time
import logging
import threading
from typing import Callable, Dict, List, Tuple, Union, Optional
from datetime import datetime

# Проверка и импорт библиотек для графического интерфейса
try:
    import tkinter as tk
    from tkinter import ttk, scrolledtext, filedialog, messagebox
    from tkinter.font import Font
    HAS_TKINTER = True
except ImportError:
    HAS_TKINTER = False
    logging.error("Библиотека tkinter не установлена, графический интерфейс недоступен")


class GraphicalUI:
    """
    Графический интерфейс для работы с агентом Daur-AI
    """
    
    # Определение темы по умолчанию
    DEFAULT_THEME = {
        "bg_main": "#2E3440",
        "bg_secondary": "#3B4252",
        "fg_main": "#ECEFF4",
        "fg_secondary": "#D8DEE9",
        "accent": "#88C0D0",
        "accent_hover": "#81A1C1",
        "success": "#A3BE8C",
        "error": "#BF616A",
        "warning": "#EBCB8B"
    }
    
    def __init__(self, theme: Dict[str, str] = None, 
                 window_size: Tuple[int, int] = (800, 600),
                 command_callback: Callable[[str], str] = None):
        """
        Инициализация графического интерфейса
        
        Args:
            theme (Dict[str, str], optional): Тема оформления (цвета) интерфейса
            window_size (Tuple[int, int]): Размер окна в пикселях (ширина, высота)
            command_callback (Callable): Функция обратного вызова для обработки команд
        """
        self.logger = logging.getLogger('daur_ai.ui.gui')
        
        # Проверка наличия библиотеки tkinter
        if not HAS_TKINTER:
            self.logger.error("Не удалось инициализировать графический интерфейс: библиотека tkinter не установлена")
            raise ImportError("Для графического интерфейса требуется библиотека tkinter")
        
        # Инициализация параметров
        self.theme = theme or self.DEFAULT_THEME
        self.window_size = window_size
        self.command_callback = command_callback
        self.is_running = False
        
        # История команд
        self.command_history = []
        self.history_position = 0
        
        # Thread для обновления интерфейса
        self.update_queue = []
        self.update_lock = threading.Lock()
        
        self.logger.info("Графический интерфейс инициализирован")
    
    def _setup_ui(self):
        """Настройка элементов интерфейса"""
        self.logger.debug("Настройка элементов интерфейса")
        
        # Настройка окна
        self.root = tk.Tk()
        self.root.title("Daur-AI - Универсальный автономный ИИ-агент")
        self.root.geometry(f"{self.window_size[0]}x{self.window_size[1]}")
        self.root.minsize(640, 480)
        self.root.configure(background=self.theme["bg_main"])
        
        # Значок приложения (если доступен)
        try:
            icon_path = os.path.join(os.path.dirname(__file__), '..', '..', 'resources', 'icon.png')
            if os.path.exists(icon_path):
                icon = tk.PhotoImage(file=icon_path)
                self.root.iconphoto(True, icon)
        except Exception as e:
            self.logger.warning(f"Не удалось загрузить значок: {e}")
        
        # Создание стилей
        self.style = ttk.Style()
        self.style.theme_use('clam')  # Базовая тема
        
        # Настройка стилей для виджетов ttk
        self.style.configure(
            "TButton", 
            background=self.theme["accent"],
            foreground=self.theme["fg_main"],
            borderwidth=0,
            focusthickness=3,
            focuscolor=self.theme["accent_hover"]
        )
        
        self.style.map(
            "TButton",
            background=[("active", self.theme["accent_hover"])]
        )
        
        # Определение шрифтов
        self.default_font = Font(family="Arial", size=10)
        self.monospace_font = Font(family="Courier New", size=10)
        self.title_font = Font(family="Arial", size=14, weight="bold")
        
        # Главные фреймы
        self.main_frame = tk.Frame(
            self.root,
            bg=self.theme["bg_main"],
            padx=10,
            pady=10
        )
        self.main_frame.pack(fill=tk.BOTH, expand=True)
        
        # Верхняя панель с логотипом и статусом
        self.header_frame = tk.Frame(
            self.main_frame,
            bg=self.theme["bg_main"],
            height=50
        )
        self.header_frame.pack(fill=tk.X, pady=(0, 10))
        
        # Логотип и заголовок
        self.title_label = tk.Label(
            self.header_frame,
            text="Daur-AI",
            font=self.title_font,
            bg=self.theme["bg_main"],
            fg=self.theme["accent"]
        )
        self.title_label.pack(side=tk.LEFT)
        
        # Индикатор статуса
        self.status_frame = tk.Frame(
            self.header_frame,
            bg=self.theme["bg_main"]
        )
        self.status_frame.pack(side=tk.RIGHT)
        
        self.status_indicator = tk.Canvas(
            self.status_frame,
            width=15,
            height=15,
            bg=self.theme["bg_main"],
            highlightthickness=0
        )
        self.status_indicator.pack(side=tk.LEFT, padx=(0, 5))
        self.status_indicator.create_oval(2, 2, 13, 13, fill=self.theme["success"], outline="")
        
        self.status_label = tk.Label(
            self.status_frame,
            text="Готов",
            bg=self.theme["bg_main"],
            fg=self.theme["fg_secondary"]
        )
        self.status_label.pack(side=tk.LEFT)
        
        # Основное содержимое
        self.content_frame = tk.Frame(
            self.main_frame,
            bg=self.theme["bg_main"]
        )
        self.content_frame.pack(fill=tk.BOTH, expand=True)
        
        # Область вывода
        self.output_frame = tk.Frame(
            self.content_frame,
            bg=self.theme["bg_secondary"],
            padx=5,
            pady=5
        )
        self.output_frame.pack(fill=tk.BOTH, expand=True, pady=(0, 10))
        
        self.output_text = scrolledtext.ScrolledText(
            self.output_frame,
            bg=self.theme["bg_secondary"],
            fg=self.theme["fg_main"],
            font=self.monospace_font,
            wrap=tk.WORD,
            padx=10,
            pady=10,
            state=tk.DISABLED
        )
        self.output_text.pack(fill=tk.BOTH, expand=True)
        
        # Панель ввода
        self.input_frame = tk.Frame(
            self.content_frame,
            bg=self.theme["bg_main"],
            height=50
        )
        self.input_frame.pack(fill=tk.X)
        
        self.input_entry = tk.Entry(
            self.input_frame,
            bg=self.theme["bg_secondary"],
            fg=self.theme["fg_main"],
            insertbackground=self.theme["fg_main"],
            font=self.default_font,
            relief=tk.FLAT,
            bd=0,
        )
        self.input_entry.pack(side=tk.LEFT, fill=tk.X, expand=True, ipady=10, padx=(0, 10))
        
        self.send_button = ttk.Button(
            self.input_frame,
            text="Отправить",
            style="TButton",
            command=self._handle_input
        )
        self.send_button.pack(side=tk.RIGHT, ipadx=10, ipady=5)
        
        # Bind для обработки клавиш
        self.input_entry.bind("<Return>", lambda event: self._handle_input())
        self.input_entry.bind("<Up>", self._history_up)
        self.input_entry.bind("<Down>", self._history_down)
        
        # Установка фокуса на поле ввода
        self.input_entry.focus_set()
        
        # Обработчик закрытия окна
        self.root.protocol("WM_DELETE_WINDOW", self._on_closing)
        
        # Настройка периодического обновления интерфейса
        self._setup_updater()
    
    def _setup_updater(self):
        """Настройка обновления интерфейса"""
        def update_ui():
            if not self.is_running:
                return
            
            # Обработка очереди обновлений
            with self.update_lock:
                updates = list(self.update_queue)
                self.update_queue.clear()
            
            for update_func, args, kwargs in updates:
                try:
                    update_func(*args, **kwargs)
                except Exception as e:
                    self.logger.error(f"Ошибка при обновлении интерфейса: {e}", exc_info=True)
            
            # Запланировать следующее обновление
            if self.is_running:
                self.root.after(100, update_ui)
        
        # Запуск первого обновления
        self.root.after(100, update_ui)
    
    def _handle_input(self):
        """Обработка ввода пользователя"""
        command = self.input_entry.get().strip()
        if not command:
            return
        
        # Очистка поля ввода
        self.input_entry.delete(0, tk.END)
        
        # Добавление в историю команд
        if not self.command_history or self.command_history[-1] != command:
            self.command_history.append(command)
            if len(self.command_history) > 100:  # Ограничение истории
                self.command_history.pop(0)
        self.history_position = len(self.command_history)
        
        # Отображение команды в выводе
        timestamp = datetime.now().strftime("%H:%M:%S")
        self._add_to_output(f"[{timestamp}] > {command}", tag="command")
        
        # Обработка выхода
        if command.lower() in ['exit', 'quit']:
            if self.command_callback:
                self.command_callback(command)
            self.root.after(500, self.root.destroy)
            return
        
        # Обработка команды через колбэк
        if self.command_callback:
            # Установка статуса "обработка"
            self._update_status("Обработка...", "processing")
            
            # Запуск обработки в отдельном потоке
            def process_command():
                try:
                    response = self.command_callback(command)
                    if response:
                        # Добавление ответа в очередь обновлений
                        with self.update_lock:
                            self.update_queue.append(
                                (self._add_to_output, (response, "response"), {})
                            )
                        
                    # Восстановление статуса
                    with self.update_lock:
                        self.update_queue.append(
                            (self._update_status, ("Готов", "ready"), {})
                        )
                except Exception as e:
                    self.logger.error(f"Ошибка при обработке команды: {e}", exc_info=True)
                    # Добавление сообщения об ошибке
                    with self.update_lock:
                        self.update_queue.append(
                            (self._add_to_output, (f"Ошибка: {str(e)}", "error"), {})
                        )
                        self.update_queue.append(
                            (self._update_status, ("Готов", "ready"), {})
                        )
            
            threading.Thread(target=process_command, daemon=True).start()
        else:
            self._add_to_output("Обработчик команд не определен", "error")
    
    def _add_to_output(self, text, tag=None):
        """Добавление текста в область вывода"""
        self.output_text.configure(state=tk.NORMAL)
        
        # Добавление текста с тегами для оформления
        end_position = self.output_text.index(tk.END)
        self.output_text.insert(tk.END, text + "\n")
        
        # Настройка тегов для стилизации
        if tag == "command":
            self.output_text.tag_add(tag, f"{float(end_position) - 1.0}", end_position)
            self.output_text.tag_config(tag, foreground=self.theme["accent"])
        elif tag == "response":
            self.output_text.tag_add(tag, f"{float(end_position) - 1.0}", end_position)
            self.output_text.tag_config(tag, foreground=self.theme["fg_main"])
        elif tag == "error":
            self.output_text.tag_add(tag, f"{float(end_position) - 1.0}", end_position)
            self.output_text.tag_config(tag, foreground=self.theme["error"])
        elif tag == "success":
            self.output_text.tag_add(tag, f"{float(end_position) - 1.0}", end_position)
            self.output_text.tag_config(tag, foreground=self.theme["success"])
        elif tag == "warning":
            self.output_text.tag_add(tag, f"{float(end_position) - 1.0}", end_position)
            self.output_text.tag_config(tag, foreground=self.theme["warning"])
        
        # Прокрутка до конца
        self.output_text.see(tk.END)
        self.output_text.configure(state=tk.DISABLED)
    
    def _update_status(self, text, status="ready"):
        """Обновление статуса"""
        self.status_label.config(text=text)
        
        # Обновление индикатора
        if status == "ready":
            fill_color = self.theme["success"]
        elif status == "processing":
            fill_color = self.theme["accent"]
        elif status == "error":
            fill_color = self.theme["error"]
        elif status == "warning":
            fill_color = self.theme["warning"]
        else:
            fill_color = self.theme["fg_secondary"]
        
        self.status_indicator.itemconfig(1, fill=fill_color)
    
    def _history_up(self, event=None):
        """Навигация по истории команд вверх"""
        if not self.command_history:
            return
        
        if self.history_position > 0:
            self.history_position -= 1
            self.input_entry.delete(0, tk.END)
            self.input_entry.insert(0, self.command_history[self.history_position])
    
    def _history_down(self, event=None):
        """Навигация по истории команд вниз"""
        if not self.command_history:
            return
        
        if self.history_position < len(self.command_history) - 1:
            self.history_position += 1
            self.input_entry.delete(0, tk.END)
            self.input_entry.insert(0, self.command_history[self.history_position])
        elif self.history_position == len(self.command_history) - 1:
            # Если достигли конца истории, очищаем поле ввода
            self.history_position = len(self.command_history)
            self.input_entry.delete(0, tk.END)
    
    def _on_closing(self):
        """Обработка закрытия окна"""
        if messagebox.askokcancel("Выход", "Вы действительно хотите завершить работу?"):
            self.is_running = False
            if self.command_callback:
                self.command_callback("exit")
            self.root.destroy()
    
    def run(self):
        """Запуск графического интерфейса"""
        self.is_running = True
        self.logger.info("Запуск графического интерфейса")
        
        try:
            # Инициализация UI
            self._setup_ui()
            
            # Приветственное сообщение
            self._add_to_output("Daur-AI - Универсальный автономный ИИ-агент", "success")
            self._add_to_output("Введите команду на естественном языке или 'help' для справки")
            
            # Запуск главного цикла
            self.root.mainloop()
            
        except Exception as e:
            self.logger.error(f"Ошибка при запуске графического интерфейса: {e}", exc_info=True)
            raise
        finally:
            self.is_running = False
            self.logger.info("Завершение работы графического интерфейса")
    
    def show_message(self, message: str, message_type: str = "info"):
        """
        Отображение сообщения
        
        Args:
            message (str): Текст сообщения
            message_type (str): Тип сообщения (info, success, warning, error)
        """
        # Добавление в очередь обновлений для потокобезопасности
        with self.update_lock:
            self.update_queue.append(
                (self._add_to_output, (message, message_type), {})
            )
    
    def show_progress(self, message: str, duration: float = None):
        """
        Отображение индикатора прогресса
        
        Args:
            message (str): Сообщение о прогрессе
            duration (float, optional): Продолжительность индикации в секундах
        """
        stop_event = threading.Event()
        progress_id = f"progress_{int(time.time() * 1000)}"
        
        # Добавление сообщения о начале операции
        with self.update_lock:
            self.update_queue.append(
                (self._add_to_output, (f"{message}...", "info"), {})
            )
            self.update_queue.append(
                (self._update_status, (f"{message}...", "processing"), {})
            )
        
        # Если указана продолжительность, запускаем таймер для остановки
        if duration:
            def stop_after_duration():
                time.sleep(duration)
                if not stop_event.is_set():
                    stop_event.set()
                    with self.update_lock:
                        self.update_queue.append(
                            (self._update_status, ("Готов", "ready"), {})
                        )
            
            threading.Thread(target=stop_after_duration, daemon=True).start()
        
        return stop_event  # Возвращаем событие для возможности остановки извне


# Пример использования
if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO)
    
    def command_handler(cmd):
        """Пример обработчика команд"""
        if cmd.lower() in ['exit', 'quit']:
            return "Выход из программы..."
        
        # Имитация задержки обработки
        time.sleep(1)
        return f"Обрабатывается команда: {cmd}"
    
    # Проверка наличия tkinter
    if HAS_TKINTER:
        ui = GraphicalUI(command_callback=command_handler)
        ui.run()
    else:
        print("Графический интерфейс недоступен: не установлена библиотека tkinter")
