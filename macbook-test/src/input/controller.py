#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
Daur-AI: Модуль управления вводом
Отвечает за эмуляцию мыши, клавиатуры и другие взаимодействия с системой

Версия: 1.0
Дата: 09.05.2025
"""

import time
import logging
import platform
from enum import Enum
import pyautogui

# Импорт платформо-зависимых модулей
if platform.system() == "Windows":
    from src.platforms.windows.input import WindowsInputHandler
elif platform.system() == "Darwin":  # macOS
    from src.platforms.macos.input import MacOSInputHandler
else:
    from src.platforms.common.input import DefaultInputHandler


class MouseButton(Enum):
    """Перечисление кнопок мыши"""
    LEFT = "left"
    RIGHT = "right"
    MIDDLE = "middle"


class KeyModifier(Enum):
    """Перечисление модификаторов клавиш"""
    CTRL = "ctrl"
    ALT = "alt"
    SHIFT = "shift"
    WIN = "win"  # Windows
    CMD = "command"  # macOS


class InputController:
    """
    Контроллер ввода для эмуляции мыши и клавиатуры
    с учетом различий между платформами
    """
    
    def __init__(self, os_platform):
        """
        Инициализация контроллера ввода
        
        Args:
            os_platform (str): Текущая операционная система 
                              ('Windows', 'Darwin', 'Linux')
        """
        self.logger = logging.getLogger('daur_ai.input')
        self.os_platform = os_platform
        
        # Базовые настройки PyAutoGUI
        pyautogui.PAUSE = 0.1  # Пауза между действиями
        pyautogui.FAILSAFE = True  # Безопасный режим (угол экрана)
        
        # Инициализация платформо-зависимого обработчика
        if os_platform == "Windows":
            self.platform_handler = WindowsInputHandler()
            self.logger.info("Инициализирован обработчик ввода для Windows")
        
        elif os_platform == "Darwin":
            self.platform_handler = MacOSInputHandler()
            self.logger.info("Инициализирован обработчик ввода для macOS")
        
        else:
            self.platform_handler = DefaultInputHandler()
            self.logger.warning(f"Для платформы {os_platform} используется стандартный обработчик ввода")
    
    def execute_action(self, action):
        """
        Выполнение действия ввода
        
        Args:
            action (dict): Словарь с описанием действия ввода
                {
                    "action": "input_mouse_click",
                    "x": 100,
                    "y": 200,
                    "button": "left",
                    "clicks": 1,
                    "interval": 0.1
                }
        
        Returns:
            bool: Результат выполнения (True - успешно, False - ошибка)
        """
        action_type = action.get("action", "").lower()
        
        try:
            # Обработка действий с мышью
            if action_type == "input_mouse_click":
                return self.mouse_click(
                    x=action.get("x"),
                    y=action.get("y"),
                    button=action.get("button", "left"),
                    clicks=action.get("clicks", 1),
                    interval=action.get("interval", 0.1)
                )
            
            elif action_type == "input_mouse_move":
                return self.mouse_move(
                    x=action.get("x"),
                    y=action.get("y"),
                    duration=action.get("duration", 0.2)
                )
            
            elif action_type == "input_mouse_drag":
                return self.mouse_drag(
                    start_x=action.get("start_x"),
                    start_y=action.get("start_y"),
                    end_x=action.get("end_x"),
                    end_y=action.get("end_y"),
                    duration=action.get("duration", 0.5),
                    button=action.get("button", "left")
                )
            
            elif action_type == "input_mouse_scroll":
                return self.mouse_scroll(
                    clicks=action.get("clicks", 1),
                    direction=action.get("direction", "down"),
                    x=action.get("x"),
                    y=action.get("y")
                )
            
            # Обработка действий с клавиатурой
            elif action_type == "input_key_press":
                return self.key_press(
                    key=action.get("key"),
                    modifiers=action.get("modifiers", [])
                )
            
            elif action_type == "input_key_down":
                return self.key_down(
                    key=action.get("key")
                )
            
            elif action_type == "input_key_up":
                return self.key_up(
                    key=action.get("key")
                )
            
            elif action_type == "input_type_text":
                return self.type_text(
                    text=action.get("text"),
                    interval=action.get("interval", 0.05)
                )
            
            elif action_type == "input_hotkey":
                return self.hotkey(
                    keys=action.get("keys", [])
                )
            
            else:
                self.logger.warning(f"Неизвестное действие ввода: {action_type}")
                return False
            
        except Exception as e:
            self.logger.error(f"Ошибка при выполнении действия {action_type}: {e}", exc_info=True)
            return False
    
    def mouse_click(self, x=None, y=None, button="left", clicks=1, interval=0.1):
        """
        Клик мышью по координатам
        
        Args:
            x (int): X-координата (если None - текущая позиция)
            y (int): Y-координата (если None - текущая позиция)
            button (str): Кнопка мыши ('left', 'right', 'middle')
            clicks (int): Количество кликов (1 - одинарный, 2 - двойной)
            interval (float): Интервал между кликами
        
        Returns:
            bool: Результат выполнения
        """
        try:
            # Перемещение к координатам, если указаны
            if x is not None and y is not None:
                pyautogui.moveTo(x, y, duration=0.1)
            
            # Выполнение клика
            pyautogui.click(button=button, clicks=clicks, interval=interval)
            
            self.logger.debug(f"Выполнен клик {button}x{clicks} по координатам ({x}, {y})")
            return True
            
        except Exception as e:
            self.logger.error(f"Ошибка при выполнении клика: {e}")
            return False
    
    def mouse_move(self, x, y, duration=0.2):
        """
        Перемещение курсора мыши
        
        Args:
            x (int): X-координата
            y (int): Y-координата
            duration (float): Продолжительность перемещения
        
        Returns:
            bool: Результат выполнения
        """
        try:
            pyautogui.moveTo(x, y, duration=duration)
            self.logger.debug(f"Курсор перемещен к координатам ({x}, {y})")
            return True
            
        except Exception as e:
            self.logger.error(f"Ошибка при перемещении курсора: {e}")
            return False
    
    def mouse_drag(self, start_x, start_y, end_x, end_y, duration=0.5, button="left"):
        """
        Перетаскивание (drag-and-drop)
        
        Args:
            start_x, start_y (int): Начальные координаты
            end_x, end_y (int): Конечные координаты
            duration (float): Продолжительность перетаскивания
            button (str): Кнопка мыши ('left', 'right', 'middle')
        
        Returns:
            bool: Результат выполнения
        """
        try:
            pyautogui.moveTo(start_x, start_y, duration=0.1)
            pyautogui.dragTo(end_x, end_y, duration=duration, button=button)
            
            self.logger.debug(f"Перетаскивание от ({start_x}, {start_y}) к ({end_x}, {end_y})")
            return True
            
        except Exception as e:
            self.logger.error(f"Ошибка при перетаскивании: {e}")
            return False
    
    def mouse_scroll(self, clicks=1, direction="down", x=None, y=None):
        """
        Прокрутка колесика мыши
        
        Args:
            clicks (int): Количество "щелчков" колесика
            direction (str): Направление ('up', 'down', 'left', 'right')
            x, y (int): Координаты для позиционирования (опционально)
        
        Returns:
            bool: Результат выполнения
        """
        try:
            # Перемещение мыши, если указаны координаты
            if x is not None and y is not None:
                pyautogui.moveTo(x, y, duration=0.1)
            
            # Определение направления прокрутки
            if direction.lower() == "up":
                pyautogui.scroll(clicks)
            elif direction.lower() == "down":
                pyautogui.scroll(-clicks)
            elif direction.lower() == "left":
                pyautogui.hscroll(-clicks)
            elif direction.lower() == "right":
                pyautogui.hscroll(clicks)
            else:
                self.logger.warning(f"Неизвестное направление скролла: {direction}")
                return False
            
            self.logger.debug(f"Выполнен скролл в направлении {direction} на {clicks} щелчков")
            return True
            
        except Exception as e:
            self.logger.error(f"Ошибка при скролле: {e}")
            return False
    
    def key_press(self, key, modifiers=None):
        """
        Нажатие клавиши с модификаторами
        
        Args:
            key (str): Клавиша
            modifiers (list): Список модификаторов ('ctrl', 'alt', 'shift' и т.д.)
        
        Returns:
            bool: Результат выполнения
        """
        if modifiers is None:
            modifiers = []
        
        try:
            # Преобразование системных модификаторов
            mod_keys = []
            for mod in modifiers:
                # Для macOS заменяем win/ctrl на cmd там, где это имеет смысл
                if self.os_platform == "Darwin" and mod.lower() in ['win', 'ctrl']:
                    if mod.lower() == 'win':
                        mod_keys.append('command')
                    else:
                        # На macOS некоторые сочетания используют cmd вместо ctrl
                        if key in ['c', 'v', 'x', 'a', 'z', 'f', 'o', 's', 'p']:
                            mod_keys.append('command')
                        else:
                            mod_keys.append('ctrl')
                else:
                    mod_keys.append(mod)
            
            # Добавляем основную клавишу
            all_keys = mod_keys + [key]
            
            # Использование платформенно-зависимого обработчика для сложных случаев
            if len(all_keys) > 1:
                return self.platform_handler.press_hotkey(all_keys)
            else:
                pyautogui.press(key)
            
            self.logger.debug(f"Нажата клавиша {key} с модификаторами {mod_keys}")
            return True
            
        except Exception as e:
            self.logger.error(f"Ошибка при нажатии клавиши: {e}")
            return False
    
    def key_down(self, key):
        """
        Нажатие и удерживание клавиши
        
        Args:
            key (str): Клавиша
        
        Returns:
            bool: Результат выполнения
        """
        try:
            pyautogui.keyDown(key)
            self.logger.debug(f"Клавиша {key} нажата и удерживается")
            return True
            
        except Exception as e:
            self.logger.error(f"Ошибка при нажатии клавиши {key}: {e}")
            return False
    
    def key_up(self, key):
        """
        Отпускание клавиши
        
        Args:
            key (str): Клавиша
        
        Returns:
            bool: Результат выполнения
        """
        try:
            pyautogui.keyUp(key)
            self.logger.debug(f"Клавиша {key} отпущена")
            return True
            
        except Exception as e:
            self.logger.error(f"Ошибка при отпускании клавиши {key}: {e}")
            return False
    
    def type_text(self, text, interval=0.05):
        """
        Ввод текста
        
        Args:
            text (str): Текст для ввода
            interval (float): Интервал между нажатиями клавиш
        
        Returns:
            bool: Результат выполнения
        """
        try:
            # Для Unicode символов используем платформенно-зависимый метод
            if any(ord(c) > 127 for c in text):
                return self.platform_handler.type_text(text, interval)
            else:
                pyautogui.typewrite(text, interval=interval)
            
            self.logger.debug(f"Введен текст: {text}")
            return True
            
        except Exception as e:
            self.logger.error(f"Ошибка при вводе текста: {e}")
            return False
    
    def hotkey(self, keys):
        """
        Нажатие комбинации клавиш
        
        Args:
            keys (list): Список клавиш в комбинации
        
        Returns:
            bool: Результат выполнения
        """
        try:
            # Проверка на системные сочетания, требующие особой обработки
            system_hotkeys = {
                # Windows
                "win+r", "alt+tab", "alt+f4", "ctrl+alt+del",
                # macOS
                "cmd+space", "cmd+tab", "cmd+q", "cmd+opt+esc"
            }
            
            # Преобразование списка клавиш в строку для проверки
            hotkey_str = "+".join(keys).lower()
            
            # Для системных сочетаний используем платформенно-зависимый метод
            if hotkey_str in system_hotkeys:
                return self.platform_handler.press_system_hotkey(keys)
            else:
                pyautogui.hotkey(*keys)
            
            self.logger.debug(f"Нажата комбинация клавиш: {'+'.join(keys)}")
            return True
            
        except Exception as e:
            self.logger.error(f"Ошибка при нажатии комбинации клавиш: {e}")
            return False
