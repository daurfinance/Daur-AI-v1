#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
Daur-AI: Модуль управления клавиатурой с поддержкой горячих клавиш
Полный контроль над клавиатурой, макросы и горячие клавиши

Версия: 2.0
Дата: 25.10.2025
Автор: Manus AI
"""

import logging
import time
from typing import Dict, List, Any, Optional, Callable, Tuple
from enum import Enum
from dataclasses import dataclass, field
from datetime import datetime


class KeyModifier(Enum):
    """Модификаторы клавиш"""
    CTRL = "ctrl"
    SHIFT = "shift"
    ALT = "alt"
    CMD = "cmd"
    WIN = "win"


@dataclass
class KeyboardEvent:
    """Событие клавиатуры"""
    key: str
    modifiers: List[KeyModifier] = field(default_factory=list)
    event_type: str = "press"  # press, release, hold
    duration: float = 0.0
    timestamp: datetime = field(default_factory=datetime.now)


@dataclass
class Hotkey:
    """Горячая клавиша"""
    hotkey_id: str
    key_combination: str  # например: "ctrl+c"
    callback: Optional[Callable] = None
    description: str = ""
    enabled: bool = True
    created_at: datetime = field(default_factory=datetime.now)


@dataclass
class Macro:
    """Макрос клавиатуры"""
    macro_id: str
    name: str
    keys: List[str] = field(default_factory=list)
    delays: List[float] = field(default_factory=list)  # задержки между нажатиями
    description: str = ""
    created_at: datetime = field(default_factory=datetime.now)


class KeyboardController:
    """Контроллер клавиатуры"""
    
    def __init__(self):
        """Инициализация"""
        self.logger = logging.getLogger('daur_ai.keyboard_controller')
        self.hotkeys: Dict[str, Hotkey] = {}
        self.macros: Dict[str, Macro] = {}
        self.is_recording = False
        self.recorded_keys: List[KeyboardEvent] = []
        self.event_callbacks: Dict[str, List[Callable]] = {}
        self.logger.info("Keyboard controller инициализирован")
    
    def press_key(self, key: str, duration: float = 0.1) -> bool:
        """
        Нажать клавишу
        
        Args:
            key: Название клавиши
            duration: Длительность нажатия
            
        Returns:
            bool: Успешность операции
        """
        try:
            import pyautogui
            
            pyautogui.press(key, interval=duration)
            
            self._trigger_event('press', KeyboardEvent(key, event_type='press'))
            self.logger.info(f"Клавиша нажата: {key}")
            return True
        
        except Exception as e:
            self.logger.error(f"Ошибка нажатия клавиши: {e}")
            return False
    
    def type_text(self, text: str, interval: float = 0.05) -> bool:
        """
        Напечатать текст
        
        Args:
            text: Текст для печати
            interval: Интервал между символами
            
        Returns:
            bool: Успешность операции
        """
        try:
            import pyautogui
            
            pyautogui.typewrite(text, interval=interval)
            
            self._trigger_event('type', KeyboardEvent(text, event_type='type'))
            self.logger.info(f"Текст напечатан: {text[:50]}")
            return True
        
        except Exception as e:
            self.logger.error(f"Ошибка печати текста: {e}")
            return False
    
    def write_text(self, text: str, interval: float = 0.05) -> bool:
        """
        Написать текст (поддерживает Unicode)
        
        Args:
            text: Текст для написания
            interval: Интервал между символами
            
        Returns:
            bool: Успешность операции
        """
        try:
            import pyautogui
            import time
            
            for char in text:
                pyautogui.write(char)
                time.sleep(interval)
            
            self._trigger_event('write', KeyboardEvent(text, event_type='write'))
            self.logger.info(f"Текст написан: {text[:50]}")
            return True
        
        except Exception as e:
            self.logger.error(f"Ошибка написания текста: {e}")
            return False
    
    def key_down(self, key: str) -> bool:
        """
        Нажать клавишу и держать
        
        Args:
            key: Название клавиши
            
        Returns:
            bool: Успешность операции
        """
        try:
            import pyautogui
            
            pyautogui.keyDown(key)
            
            self._trigger_event('down', KeyboardEvent(key, event_type='down'))
            self.logger.info(f"Клавиша нажата (hold): {key}")
            return True
        
        except Exception as e:
            self.logger.error(f"Ошибка нажатия клавиши: {e}")
            return False
    
    def key_up(self, key: str) -> bool:
        """
        Отпустить клавишу
        
        Args:
            key: Название клавиши
            
        Returns:
            bool: Успешность операции
        """
        try:
            import pyautogui
            
            pyautogui.keyUp(key)
            
            self._trigger_event('up', KeyboardEvent(key, event_type='up'))
            self.logger.info(f"Клавиша отпущена: {key}")
            return True
        
        except Exception as e:
            self.logger.error(f"Ошибка отпускания клавиши: {e}")
            return False
    
    def hotkey(self, *keys: str) -> bool:
        """
        Нажать комбинацию клавиш
        
        Args:
            *keys: Клавиши для комбинации (например: 'ctrl', 'c')
            
        Returns:
            bool: Успешность операции
        """
        try:
            import pyautogui
            
            pyautogui.hotkey(*keys)
            
            key_combo = '+'.join(keys)
            self._trigger_event('hotkey', KeyboardEvent(key_combo, event_type='hotkey'))
            self.logger.info(f"Комбинация нажата: {key_combo}")
            return True
        
        except Exception as e:
            self.logger.error(f"Ошибка комбинации клавиш: {e}")
            return False
    
    def register_hotkey(self, hotkey_id: str, key_combination: str,
                       callback: Callable, description: str = "") -> bool:
        """
        Зарегистрировать горячую клавишу
        
        Args:
            hotkey_id: ID горячей клавиши
            key_combination: Комбинация клавиш (например: "ctrl+c")
            callback: Функция callback
            description: Описание
            
        Returns:
            bool: Успешность операции
        """
        hotkey = Hotkey(hotkey_id, key_combination, callback, description)
        self.hotkeys[hotkey_id] = hotkey
        
        self.logger.info(f"Горячая клавиша зарегистрирована: {hotkey_id} ({key_combination})")
        return True
    
    def unregister_hotkey(self, hotkey_id: str) -> bool:
        """
        Отменить регистрацию горячей клавиши
        
        Args:
            hotkey_id: ID горячей клавиши
            
        Returns:
            bool: Успешность операции
        """
        if hotkey_id in self.hotkeys:
            del self.hotkeys[hotkey_id]
            self.logger.info(f"Горячая клавиша удалена: {hotkey_id}")
            return True
        
        return False
    
    def create_macro(self, macro_id: str, name: str, description: str = "") -> Macro:
        """
        Создать макрос
        
        Args:
            macro_id: ID макроса
            name: Имя макроса
            description: Описание
            
        Returns:
            Macro: Объект макроса
        """
        macro = Macro(macro_id, name, description=description)
        self.macros[macro_id] = macro
        self.logger.info(f"Макрос создан: {macro_id}")
        return macro
    
    def add_key_to_macro(self, macro_id: str, key: str, delay: float = 0.1) -> bool:
        """
        Добавить клавишу в макрос
        
        Args:
            macro_id: ID макроса
            key: Клавиша
            delay: Задержка после нажатия
            
        Returns:
            bool: Успешность операции
        """
        if macro_id not in self.macros:
            self.logger.error(f"Макрос не найден: {macro_id}")
            return False
        
        self.macros[macro_id].keys.append(key)
        self.macros[macro_id].delays.append(delay)
        self.logger.info(f"Клавиша добавлена в макрос: {macro_id} <- {key}")
        return True
    
    def execute_macro(self, macro_id: str, repeat: int = 1) -> bool:
        """
        Выполнить макрос
        
        Args:
            macro_id: ID макроса
            repeat: Количество повторений
            
        Returns:
            bool: Успешность операции
        """
        if macro_id not in self.macros:
            self.logger.error(f"Макрос не найден: {macro_id}")
            return False
        
        try:
            macro = self.macros[macro_id]
            
            for _ in range(repeat):
                for key, delay in zip(macro.keys, macro.delays):
                    self.press_key(key, duration=delay)
                    time.sleep(delay)
            
            self.logger.info(f"Макрос выполнен: {macro_id} ({repeat} раз)")
            return True
        
        except Exception as e:
            self.logger.error(f"Ошибка выполнения макроса: {e}")
            return False
    
    def record_macro(self, macro_id: str, duration: float = 10.0) -> Optional[Macro]:
        """
        Записать макрос
        
        Args:
            macro_id: ID макроса
            duration: Длительность записи в секундах
            
        Returns:
            Optional[Macro]: Объект макроса или None
        """
        try:
            from pynput import keyboard
            
            macro = self.create_macro(macro_id, f"Recorded macro {macro_id}")
            
            start_time = time.time()
            last_time = start_time
            
            def on_press(key):
                nonlocal last_time
                current_time = time.time()
                
                if current_time - start_time > duration:
                    return False
                
                delay = current_time - last_time
                
                try:
                    key_str = key.char if hasattr(key, 'char') else key.name
                    macro.keys.append(key_str)
                    macro.delays.append(delay)
                except Exception as e:
                    pass
                
                last_time = current_time
            
            listener = keyboard.Listener(on_press=on_press)
            listener.start()
            listener.join(timeout=duration)
            
            self.logger.info(f"Макрос записан: {macro_id} ({len(macro.keys)} клавиш)")
            return macro
        
        except Exception as e:
            self.logger.error(f"Ошибка записи макроса: {e}")
            return None
    
    def start_recording(self) -> bool:
        """Начать запись событий клавиатуры"""
        self.is_recording = True
        self.recorded_keys = []
        self.logger.info("Запись событий клавиатуры начата")
        return True
    
    def stop_recording(self) -> List[KeyboardEvent]:
        """
        Остановить запись событий клавиатуры
        
        Returns:
            List[KeyboardEvent]: Записанные события
        """
        self.is_recording = False
        self.logger.info(f"Запись событий клавиатуры остановлена ({len(self.recorded_keys)} событий)")
        return self.recorded_keys
    
    def register_event_callback(self, event_type: str, callback: Callable) -> bool:
        """
        Зарегистрировать callback для события клавиатуры
        
        Args:
            event_type: Тип события
            callback: Функция callback
            
        Returns:
            bool: Успешность операции
        """
        if event_type not in self.event_callbacks:
            self.event_callbacks[event_type] = []
        
        self.event_callbacks[event_type].append(callback)
        self.logger.info(f"Callback зарегистрирован: {event_type}")
        return True
    
    def _trigger_event(self, event_type: str, event: KeyboardEvent) -> None:
        """Вызвать callbacks для события"""
        if self.is_recording:
            self.recorded_keys.append(event)
        
        if event_type in self.event_callbacks:
            for callback in self.event_callbacks[event_type]:
                try:
                    callback(event)
                except Exception as e:
                    self.logger.error(f"Ошибка в callback: {e}")
    
    def get_status(self) -> Dict[str, Any]:
        """Получить статус контроллера"""
        return {
            'hotkeys': len(self.hotkeys),
            'macros': len(self.macros),
            'is_recording': self.is_recording,
            'recorded_keys': len(self.recorded_keys),
            'event_callbacks': len(self.event_callbacks)
        }


# Глобальный экземпляр
_keyboard_controller = None


def get_keyboard_controller() -> KeyboardController:
    """Получить контроллер клавиатуры"""
    global _keyboard_controller
    if _keyboard_controller is None:
        _keyboard_controller = KeyboardController()
    return _keyboard_controller

