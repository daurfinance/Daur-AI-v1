#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
Daur-AI: Стандартный обработчик ввода
Реализация платформенно-независимого управления вводом

Версия: 1.0
Дата: 09.05.2025
"""

import time
import logging
import platform
import pyautogui


class DefaultInputHandler:
    """
    Стандартный обработчик ввода с использованием PyAutoGUI
    Используется как запасной вариант или для не поддерживаемых платформ
    """
    
    def __init__(self):
        """Инициализация стандартного обработчика ввода"""
        self.logger = logging.getLogger('daur_ai.input.default')
        self.os_platform = platform.system()
        
        # Базовые настройки PyAutoGUI
        pyautogui.PAUSE = 0.1  # Пауза между действиями
        pyautogui.FAILSAFE = True  # Безопасный режим (угол экрана)
        
        self.logger.info(f"Инициализирован стандартный обработчик ввода для {self.os_platform}")
    
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
            # Для Unicode символов может не работать корректно
            # в зависимости от операционной системы и языка ввода
            if any(ord(c) > 127 for c in text):
                self.logger.warning("Обнаружены Unicode символы. Ввод может быть некорректным.")
                
                # Обходной путь для некоторых случаев:
                # попытка использовать буфер обмена
                current_clipboard = pyautogui.clipboard()
                pyautogui.clipboard(text)
                
                if self.os_platform == "Darwin":  # macOS
                    pyautogui.hotkey('command', 'v')
                else:
                    pyautogui.hotkey('ctrl', 'v')
                
                # Восстанавливаем буфер обмена
                time.sleep(0.2)
                pyautogui.clipboard(current_clipboard)
                
            else:
                # Для ASCII текста используем стандартный метод
                pyautogui.typewrite(text, interval=interval)
            
            self.logger.debug(f"Введен текст: {text}")
            return True
            
        except Exception as e:
            self.logger.error(f"Ошибка при вводе текста: {e}")
            return False
    
    def press_system_hotkey(self, keys):
        """
        Нажатие системных комбинаций клавиш
        
        Args:
            keys (list): Список клавиш в комбинации
            
        Returns:
            bool: Результат выполнения
        """
        try:
            # Адаптация комбинаций для текущей ОС
            hotkey_str = "+".join(keys).lower()
            
            # Win+R (Windows) -> Cmd+Space (macOS)
            if hotkey_str == "win+r" and self.os_platform == "Darwin":
                pyautogui.hotkey('command', 'space')
                return True
                
            # Alt+Tab (Windows) -> Cmd+Tab (macOS)
            elif hotkey_str == "alt+tab" and self.os_platform == "Darwin":
                pyautogui.hotkey('command', 'tab')
                return True
                
            # Alt+F4 (Windows) -> Cmd+Q (macOS)
            elif hotkey_str == "alt+f4" and self.os_platform == "Darwin":
                pyautogui.hotkey('command', 'q')
                return True
                
            # Ctrl+Alt+Del (Windows) -> Cmd+Opt+Esc (macOS)
            elif hotkey_str == "ctrl+alt+del" and self.os_platform == "Darwin":
                pyautogui.hotkey('command', 'option', 'escape')
                return True
                
            # Если система - macOS, преобразуем Win/Ctrl в Cmd для некоторых команд
            elif self.os_platform == "Darwin" and "win" in hotkey_str:
                new_keys = []
                for key in keys:
                    if key.lower() == "win":
                        new_keys.append("command")
                    else:
                        new_keys.append(key)
                pyautogui.hotkey(*new_keys)
                return True
                
            else:
                # Для остальных комбинаций используем стандартный метод
                pyautogui.hotkey(*keys)
                return True
                
        except Exception as e:
            self.logger.error(f"Ошибка при нажатии системной комбинации клавиш: {e}")
            return False
    
    def press_hotkey(self, keys):
        """
        Нажатие комбинации клавиш
        
        Args:
            keys (list): Список клавиш в комбинации
            
        Returns:
            bool: Результат выполнения
        """
        # Для системных комбинаций используем специальный метод
        hotkey_str = "+".join(keys).lower()
        if any(system_key in hotkey_str for system_key in ["win+", "alt+tab", "ctrl+alt+del", "alt+f4"]):
            return self.press_system_hotkey(keys)
        
        # Для остальных комбинаций используем стандартный метод
        try:
            # Преобразование системных клавиш для macOS
            if self.os_platform == "Darwin":
                new_keys = []
                for key in keys:
                    if key.lower() == "ctrl" and len(keys) > 1 and keys[1].lower() in "vxcazfspo":
                        # Для распространенных сочетаний заменяем Ctrl на Cmd
                        new_keys.append("command")
                    elif key.lower() == "win":
                        new_keys.append("command")
                    else:
                        new_keys.append(key)
                keys = new_keys
            
            pyautogui.hotkey(*keys)
            self.logger.debug(f"Нажата комбинация клавиш: {'+'.join(keys)}")
            return True
            
        except Exception as e:
            self.logger.error(f"Ошибка при нажатии комбинации клавиш: {e}")
            return False
    
    def get_screen_info(self):
        """
        Получение информации об экранах
        
        Returns:
            dict: Информация о мониторах
        """
        try:
            # Базовая информация через PyAutoGUI
            width, height = pyautogui.size()
            
            return {
                'monitors': [{
                    'left': 0,
                    'top': 0,
                    'width': width,
                    'height': height,
                    'is_primary': True
                }]
            }
            
        except Exception as e:
            self.logger.error(f"Ошибка при получении информации о мониторах: {e}")
            
            # Возвращаем значения по умолчанию
            return {
                'monitors': [{
                    'left': 0,
                    'top': 0,
                    'width': 1920,
                    'height': 1080,
                    'is_primary': True
                }]
            }
