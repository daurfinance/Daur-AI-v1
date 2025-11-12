#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
Daur-AI: Обработчик ввода для macOS
Реализация низкоуровневого управления вводом для macOS

Версия: 1.0
Дата: 09.05.2025
"""

import os
import time
import logging
import pyautogui

# Импорт macOS-специфичных библиотек
try:
    import Quartz
    import AppKit
    from Foundation import NSEvent, NSPoint
    from PyObjCTools import AppHelper
    HAS_PYOBJC = True
except ImportError:
    HAS_PYOBJC = False
    logging.warning("pyobjc не установлен. Некоторые функции будут недоступны.")


class MacOSInputHandler:
    """Обработчик ввода для macOS с использованием Quartz и AppKit"""
    
    def __init__(self):
        """Инициализация обработчика ввода для macOS"""
        self.logger = logging.getLogger('daur_ai.input.macos')
        
        if not HAS_PYOBJC:
            self.logger.warning("Для полной функциональности требуется pyobjc")
            self.logger.warning("Выполните: pip install pyobjc")
        
        # Проверка доступа к Accessibility API
        self._check_accessibility_access()
    
    def _check_accessibility_access(self):
        """Проверка разрешений доступа к Accessibility API"""
        if not HAS_PYOBJC:
            return
        
        try:
            trusted = Quartz.AXIsProcessTrusted()
            if not trusted:
                self.logger.warning(
                    "Программе не предоставлен доступ к Accessibility API. "
                    "Некоторые функции могут быть недоступны."
                )
                self.logger.warning(
                    "Для включения доступа перейдите в System Preferences > "
                    "Security & Privacy > Privacy > Accessibility и добавьте программу в список."
                )
        except Exception as e:
            self.logger.error(f"Ошибка проверки доступа к Accessibility API: {e}")
    
    def _get_key_code(self, key):
        """
        Получение кода клавиши для Quartz Events
        
        Args:
            key (str): Имя клавиши
            
        Returns:
            int: Код клавиши
        """
        if not HAS_PYOBJC:
            return 0
            
        # Маппинг основных клавиш
        key_map = {
            'command': 0x37,
            'cmd': 0x37,
            'shift': 0x38,
            'option': 0x3A,
            'opt': 0x3A,
            'alt': 0x3A,
            'control': 0x3B,
            'ctrl': 0x3B,
            'return': 0x24,
            'enter': 0x24,
            'space': 0x31,
            'tab': 0x30,
            'delete': 0x33,  # Backspace на самом деле
            'escape': 0x35,
            'esc': 0x35,
            'left': 0x7B,
            'right': 0x7C,
            'up': 0x7E,
            'down': 0x7D,
            'home': 0x73,
            'end': 0x77,
            'pageup': 0x74,
            'pagedown': 0x79,
            'f1': 0x7A,
            'f2': 0x78,
            'f3': 0x63,
            'f4': 0x76,
            'f5': 0x60,
            'f6': 0x61,
            'f7': 0x62,
            'f8': 0x64,
            'f9': 0x65,
            'f10': 0x6D,
            'f11': 0x67,
            'f12': 0x6F,
        }
        
        if key.lower() in key_map:
            return key_map[key.lower()]
        
        # Для буквенных клавиш нужно использовать символы
        if len(key) == 1:
            # Получение кода из символа
            try:
                # Это не всегда работает точно, но может помочь
                # для базовых ASCII символов
                char_code = ord(key.lower())
                return char_code
            except Exception:
                pass
        
        # По умолчанию
        return 0
    
    def _get_modifier_flags(self, modifiers):
        """
        Преобразование списка модификаторов в флаги для Quartz
        
        Args:
            modifiers (list): Список названий модификаторов
            
        Returns:
            int: Комбинированный флаг модификаторов
        """
        if not HAS_PYOBJC or not modifiers:
            return 0
            
        flags = 0
        for mod in modifiers:
            mod = mod.lower()
            if mod in ('command', 'cmd'):
                flags |= NSEvent.NSCommandKeyMask
            elif mod in ('shift',):
                flags |= NSEvent.NSShiftKeyMask
            elif mod in ('option', 'opt', 'alt'):
                flags |= NSEvent.NSAlternateKeyMask
            elif mod in ('control', 'ctrl'):
                flags |= NSEvent.NSControlKeyMask
            elif mod in ('fn',):
                flags |= NSEvent.NSFunctionKeyMask
                
        return flags
    
    def type_text(self, text, interval=0.05):
        """
        Ввод текста с поддержкой Unicode
        
        Args:
            text (str): Текст для ввода
            interval (float): Интервал между нажатиями клавиш
            
        Returns:
            bool: Результат выполнения
        """
        if not HAS_PYOBJC:
            # Fallback на PyAutoGUI
            return pyautogui.typewrite(text, interval=interval)
        
        try:
            # Для macOS можно использовать системный метод вставки текста
            # Это работает надежнее для Unicode и разных раскладок
            current_app = AppKit.NSWorkspace.sharedWorkspace().frontmostApplication()
            
            # Сохранение текста в буфер обмена
            pasteboard = AppKit.NSPasteboard.generalPasteboard()
            pasteboard.clearContents()
            pasteboard.setString_forType_(text, AppKit.NSPasteboardTypeString)
            
            # Эмуляция Cmd+V для вставки
            self.press_hotkey(['command', 'v'])
            
            return True
            
        except Exception as e:
            self.logger.error(f"Ошибка при вводе текста через pyobjc: {e}")
            # Fallback на PyAutoGUI
            try:
                pyautogui.typewrite(text, interval=interval)
                return True
            except Exception as e2:
                self.logger.error(f"Резервный метод ввода текста также не удался: {e2}")
                return False
    
    def _post_keyboard_event(self, key_code, down, modifiers=None):
        """
        Отправка события клавиатуры через Quartz
        
        Args:
            key_code (int): Код клавиши
            down (bool): True для нажатия, False для отпускания
            modifiers (list): Список модификаторов
            
        Returns:
            bool: Результат выполнения
        """
        if not HAS_PYOBJC:
            return False
            
        try:
            # Получение флагов модификаторов
            flags = self._get_modifier_flags(modifiers or [])
            
            # Создание и отправка события
            event = Quartz.CGEventCreateKeyboardEvent(None, key_code, down)
            if flags:
                Quartz.CGEventSetFlags(event, flags)
            Quartz.CGEventPost(Quartz.kCGHIDEventTap, event)
            
            # Небольшая задержка для стабильности
            time.sleep(0.01)
            
            return True
            
        except Exception as e:
            self.logger.error(f"Ошибка при отправке события клавиатуры: {e}")
            return False
    
    def press_system_hotkey(self, keys):
        """
        Нажатие системных комбинаций клавиш
        
        Args:
            keys (list): Список клавиш в комбинации
            
        Returns:
            bool: Результат выполнения
        """
        if not HAS_PYOBJC:
            return pyautogui.hotkey(*keys)
        
        try:
            hotkey_str = "+".join(keys).lower()
            
            # Cmd+Space - Spotlight
            if hotkey_str == "cmd+space" or hotkey_str == "command+space":
                cmd_code = self._get_key_code('command')
                space_code = self._get_key_code('space')
                
                # Нажатие
                self._post_keyboard_event(cmd_code, True)
                self._post_keyboard_event(space_code, True)
                
                # Небольшая пауза
                time.sleep(0.1)
                
                # Отпускание
                self._post_keyboard_event(space_code, False)
                self._post_keyboard_event(cmd_code, False)
                
                return True
                
            # Cmd+Tab - переключение между приложениями
            elif hotkey_str == "cmd+tab" or hotkey_str == "command+tab":
                cmd_code = self._get_key_code('command')
                tab_code = self._get_key_code('tab')
                
                # Нажатие
                self._post_keyboard_event(cmd_code, True)
                self._post_keyboard_event(tab_code, True)
                
                # Пауза, чтобы увидеть меню переключения
                time.sleep(0.2)
                
                # Отпускание
                self._post_keyboard_event(tab_code, False)
                self._post_keyboard_event(cmd_code, False)
                
                return True
                
            # Cmd+Q - закрытие приложения
            elif hotkey_str == "cmd+q" or hotkey_str == "command+q":
                cmd_code = self._get_key_code('command')
                q_code = ord('q')
                
                # Нажатие
                self._post_keyboard_event(cmd_code, True)
                self._post_keyboard_event(q_code, True)
                
                # Небольшая пауза
                time.sleep(0.1)
                
                # Отпускание
                self._post_keyboard_event(q_code, False)
                self._post_keyboard_event(cmd_code, False)
                
                return True
                
            # Cmd+Opt+Esc - Force Quit (аналог Ctrl+Alt+Del)
            elif hotkey_str in ["cmd+opt+esc", "command+option+esc", "command+alt+esc"]:
                cmd_code = self._get_key_code('command')
                opt_code = self._get_key_code('option')
                esc_code = self._get_key_code('escape')
                
                # Нажатие
                self._post_keyboard_event(cmd_code, True)
                self._post_keyboard_event(opt_code, True)
                self._post_keyboard_event(esc_code, True)
                
                # Небольшая пауза
                time.sleep(0.1)
                
                # Отпускание
                self._post_keyboard_event(esc_code, False)
                self._post_keyboard_event(opt_code, False)
                self._post_keyboard_event(cmd_code, False)
                
                return True
                
            else:
                # Общий случай для системных комбинаций
                return self.press_hotkey(keys)
            
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
        if not HAS_PYOBJC:
            return pyautogui.hotkey(*keys)
            
        try:
            # Проверка на системные комбинации
            hotkey_str = "+".join(keys).lower()
            if any(system_key in hotkey_str for system_key in ["cmd+space", "command+space", "cmd+tab", "command+tab"]):
                return self.press_system_hotkey(keys)
            
            # Для остальных комбинаций используем Quartz
            # Разделение на модификаторы и основную клавишу
            modifiers = []
            main_keys = []
            
            for key in keys:
                if key.lower() in ['command', 'cmd', 'shift', 'option', 'opt', 'alt', 'control', 'ctrl', 'fn']:
                    modifiers.append(key)
                else:
                    main_keys.append(key)
            
            # Обработка модификаторов
            mod_codes = [self._get_key_code(mod) for mod in modifiers]
            
            # Нажатие модификаторов
            for code in mod_codes:
                self._post_keyboard_event(code, True)
            
            # Нажатие основных клавиш
            for main_key in main_keys:
                key_code = self._get_key_code(main_key)
                self._post_keyboard_event(key_code, True)
                time.sleep(0.05)
                self._post_keyboard_event(key_code, False)
            
            # Отпускание модификаторов
            for code in reversed(mod_codes):
                self._post_keyboard_event(code, False)
            
            return True
            
        except Exception as e:
            self.logger.error(f"Ошибка при нажатии комбинации клавиш: {e}")
            
            # Fallback на PyAutoGUI
            try:
                pyautogui.hotkey(*keys)
                return True
            except Exception:
                return False
    
    def get_screen_info(self):
        """
        Получение информации об экранах
        
        Returns:
            dict: Информация о мониторах
        """
        if not HAS_PYOBJC:
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
            # Получение информации о мониторах через AppKit
            displays = AppKit.NSScreen.screens()
            monitors = []
            
            for i, display in enumerate(displays):
                frame = display.frame()
                
                # В macOS (0,0) находится в левом нижнем углу главного экрана,
                # нужно преобразовать координаты для совместимости
                y_offset = AppKit.NSScreen.mainScreen().frame().size.height - frame.size.height
                
                monitors.append({
                    'left': int(frame.origin.x),
                    'top': int(y_offset - frame.origin.y),
                    'width': int(frame.size.width),
                    'height': int(frame.size.height),
                    'is_primary': (i == 0)  # Главный экран всегда первый в списке
                })
            
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
