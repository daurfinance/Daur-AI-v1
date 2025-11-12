#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
Daur-AI: Обработчик ввода для Windows
Реализация низкоуровневого управления вводом для Windows

Версия: 1.0
Дата: 09.05.2025
"""

import os
import time
import logging
import pyautogui

# Импорт Windows-специфичных библиотек
try:
    import win32api
    import win32con
    import win32gui
    import ctypes
    from ctypes import wintypes
    HAS_WIN32_API = True
except ImportError:
    HAS_WIN32_API = False
    logging.warning("win32api не установлен. Некоторые функции будут недоступны.")


class WindowsInputHandler:
    """Обработчик ввода для Windows с использованием Win32 API"""
    
    def __init__(self):
        """Инициализация обработчика ввода для Windows"""
        self.logger = logging.getLogger('daur_ai.input.windows')
        
        if not HAS_WIN32_API:
            self.logger.warning("Для полной функциональности требуется pywin32")
            self.logger.warning("Выполните: pip install pywin32")
        
        # Настройка масштабирования DPI
        self._setup_dpi_awareness()
    
    def _setup_dpi_awareness(self):
        """Настройка осведомленности о DPI для корректного позиционирования"""
        if HAS_WIN32_API:
            try:
                # Для Windows 8.1+
                # Это предотвращает автоматическое масштабирование координат Windows
                process_dpi_awareness = ctypes.windll.shcore.SetProcessDpiAwareness
                process_dpi_awareness(2)  # PROCESS_PER_MONITOR_DPI_AWARE
                self.logger.debug("DPI awareness настроена")
            except Exception as e:
                self.logger.debug(f"Ошибка настройки DPI awareness: {e}")
                # Для Windows Vista - Windows 8
                try:
                    ctypes.windll.user32.SetProcessDPIAware()
                except Exception:
                    self.logger.warning("Не удалось настроить DPI awareness")
    
    def _get_virtual_key_code(self, key):
        """
        Получение виртуального кода клавиши для Win32 API
        
        Args:
            key (str): Имя клавиши
            
        Returns:
            int: Виртуальный код клавиши
        """
        # Маппинг основных клавиш
        key_map = {
            'alt': win32con.VK_MENU,
            'ctrl': win32con.VK_CONTROL,
            'shift': win32con.VK_SHIFT,
            'win': win32con.VK_LWIN,
            'enter': win32con.VK_RETURN,
            'space': win32con.VK_SPACE,
            'tab': win32con.VK_TAB,
            'esc': win32con.VK_ESCAPE,
            'up': win32con.VK_UP,
            'down': win32con.VK_DOWN,
            'left': win32con.VK_LEFT,
            'right': win32con.VK_RIGHT,
            'backspace': win32con.VK_BACK,
            'delete': win32con.VK_DELETE,
            'home': win32con.VK_HOME,
            'end': win32con.VK_END,
            'pageup': win32con.VK_PRIOR,
            'pagedown': win32con.VK_NEXT,
            'insert': win32con.VK_INSERT,
            'f1': win32con.VK_F1,
            'f2': win32con.VK_F2,
            'f3': win32con.VK_F3,
            'f4': win32con.VK_F4,
            'f5': win32con.VK_F5,
            'f6': win32con.VK_F6,
            'f7': win32con.VK_F7,
            'f8': win32con.VK_F8,
            'f9': win32con.VK_F9,
            'f10': win32con.VK_F10,
            'f11': win32con.VK_F11,
            'f12': win32con.VK_F12,
        }
        
        if key.lower() in key_map:
            return key_map[key.lower()]
        
        # Для однобуквенных клавиш (a-z, 0-9)
        if len(key) == 1:
            # Преобразование в верхний регистр для Win32 API
            return ord(key.upper())
        
        # По умолчанию
        return 0
    
    def type_text(self, text, interval=0.05):
        """
        Ввод текста с поддержкой Unicode
        
        Args:
            text (str): Текст для ввода
            interval (float): Интервал между нажатиями клавиш
            
        Returns:
            bool: Результат выполнения
        """
        if not HAS_WIN32_API:
            # Fallback на PyAutoGUI, если win32api отсутствует
            return pyautogui.typewrite(text, interval=interval)
        
        try:
            # Получение текущей раскладки клавиатуры
            layout_id = win32api.GetKeyboardLayout(0) & 0xFFFF
            
            # Если текст содержит кириллицу, может потребоваться переключение раскладки
            has_cyrillic = any(ord('а') <= ord(c) <= ord('я') or ord('А') <= ord(c) <= ord('Я') for c in text)
            
            # Переключение раскладки для русского текста (если текущая не русская)
            # 0x0419 - русская раскладка
            if has_cyrillic and layout_id != 0x0419:
                self.logger.debug("Обнаружен кириллический текст. Требуется русская раскладка.")
                # TODO: Переключение раскладки через Win32 API
            
            # Ввод каждого символа
            for char in text:
                # Для сложных символов (не ASCII) используем SendInput с Unicode
                if ord(char) > 127:
                    # Эмуляция нажатия ALT+CODE для Unicode символа
                    # Это может работать не во всех приложениях
                    pyautogui.keyDown('alt')
                    numpad_sequence = [ord(d) for d in str(ord(char))]
                    for num in numpad_sequence:
                        num_to_key = {
                            ord('0'): win32con.VK_NUMPAD0,
                            ord('1'): win32con.VK_NUMPAD1,
                            ord('2'): win32con.VK_NUMPAD2,
                            ord('3'): win32con.VK_NUMPAD3,
                            ord('4'): win32con.VK_NUMPAD4,
                            ord('5'): win32con.VK_NUMPAD5,
                            ord('6'): win32con.VK_NUMPAD6,
                            ord('7'): win32con.VK_NUMPAD7,
                            ord('8'): win32con.VK_NUMPAD8,
                            ord('9'): win32con.VK_NUMPAD9,
                        }
                        win32api.keybd_event(num_to_key[num], 0, 0, 0)
                        win32api.keybd_event(num_to_key[num], 0, win32con.KEYEVENTF_KEYUP, 0)
                    pyautogui.keyUp('alt')
                else:
                    # Для ASCII символов используем стандартный метод
                    pyautogui.press(char)
                
                # Пауза между символами
                time.sleep(interval)
            
            return True
            
        except Exception as e:
            self.logger.error(f"Ошибка при вводе текста через Win32 API: {e}")
            # Fallback на PyAutoGUI
            try:
                pyautogui.typewrite(text, interval=interval)
                return True
            except Exception as e2:
                self.logger.error(f"Резервный метод ввода текста также не удался: {e2}")
                return False
    
    def press_system_hotkey(self, keys):
        """
        Нажатие системных комбинаций клавиш
        
        Args:
            keys (list): Список клавиш в комбинации
        
        Returns:
            bool: Результат выполнения
        """
        if not HAS_WIN32_API:
            return pyautogui.hotkey(*keys)
        
        try:
            # Специальная обработка для особых комбинаций
            hotkey_str = "+".join(keys).lower()
            
            # Win+R - запуск команды
            if hotkey_str == "win+r":
                # Нажатие клавиш через Win32 API
                win32api.keybd_event(win32con.VK_LWIN, 0, 0, 0)
                win32api.keybd_event(ord('R'), 0, 0, 0)
                time.sleep(0.1)
                win32api.keybd_event(ord('R'), 0, win32con.KEYEVENTF_KEYUP, 0)
                win32api.keybd_event(win32con.VK_LWIN, 0, win32con.KEYEVENTF_KEYUP, 0)
                return True
            
            # Alt+Tab - переключение между окнами
            elif hotkey_str == "alt+tab":
                win32api.keybd_event(win32con.VK_MENU, 0, 0, 0)
                win32api.keybd_event(win32con.VK_TAB, 0, 0, 0)
                time.sleep(0.2)  # Пауза, чтобы увидеть меню переключения
                win32api.keybd_event(win32con.VK_TAB, 0, win32con.KEYEVENTF_KEYUP, 0)
                win32api.keybd_event(win32con.VK_MENU, 0, win32con.KEYEVENTF_KEYUP, 0)
                return True
            
            # Alt+F4 - закрытие окна
            elif hotkey_str == "alt+f4":
                win32api.keybd_event(win32con.VK_MENU, 0, 0, 0)
                win32api.keybd_event(win32con.VK_F4, 0, 0, 0)
                time.sleep(0.1)
                win32api.keybd_event(win32con.VK_F4, 0, win32con.KEYEVENTF_KEYUP, 0)
                win32api.keybd_event(win32con.VK_MENU, 0, win32con.KEYEVENTF_KEYUP, 0)
                return True
            
            # Ctrl+Alt+Del - специальное системное меню
            elif hotkey_str == "ctrl+alt+del":
                self.logger.warning("Комбинация Ctrl+Alt+Del не может быть эмулирована из-за ограничений безопасности")
                return False
            
            # Общий случай - преобразование клавиш в виртуальные коды
            else:
                # Нажатие клавиш
                for key in keys:
                    vk_code = self._get_virtual_key_code(key)
                    if vk_code:
                        win32api.keybd_event(vk_code, 0, 0, 0)
                
                # Небольшая пауза
                time.sleep(0.1)
                
                # Отпускание клавиш в обратном порядке
                for key in reversed(keys):
                    vk_code = self._get_virtual_key_code(key)
                    if vk_code:
                        win32api.keybd_event(vk_code, 0, win32con.KEYEVENTF_KEYUP, 0)
                
                return True
            
        except Exception as e:
            self.logger.error(f"Ошибка при нажатии системной комбинации клавиш: {e}")
            # Fallback на PyAutoGUI
            try:
                pyautogui.hotkey(*keys)
                return True
            except Exception:
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
        
        # Для остальных комбинаций используем PyAutoGUI
        try:
            pyautogui.hotkey(*keys)
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
        if not HAS_WIN32_API:
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
        
        try:
            # Получение информации о мониторах через Win32 API
            monitors = []
            def callback(monitor, dc, rect, data):
                rct = rect.contents
                monitors.append({
                    'left': rct.left,
                    'top': rct.top,
                    'width': rct.right - rct.left,
                    'height': rct.bottom - rct.top,
                    'is_primary': bool(monitor and (monitorenumproc(monitor, 0, 0, 0) & 
                                                   win32con.MONITORINFOF_PRIMARY))
                })
                return True
            
            MONITORENUMPROC = ctypes.WINFUNCTYPE(
                ctypes.c_bool,
                ctypes.c_ulong,
                ctypes.c_ulong,
                ctypes.POINTER(wintypes.RECT),
                ctypes.c_double
            )
            monitorenumproc = MONITORENUMPROC(callback)
            ctypes.windll.user32.EnumDisplayMonitors(0, 0, monitorenumproc, 0)
            
            return {'monitors': monitors}
            
        except Exception as e:
            self.logger.error(f"Ошибка при получении информации о мониторах: {e}")
            # Fallback на базовую информацию
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
