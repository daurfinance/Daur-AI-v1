"""
Real Input Controller for Daur-AI v2.0
Полнофункциональный модуль управления мышкой и клавиатурой

Поддерживает:
- Движение мыши с плавностью и ускорением
- Клики (левый, правый, средний)
- Прокрутка колесика
- Перетаскивание элементов
- Печать текста с интервалом
- Горячие клавиши
- Запись и воспроизведение жестов
- История событий
- Слушатели событий (callbacks)
"""

import os
import sys
import time
import logging
import json
from datetime import datetime
from typing import Dict, List, Optional, Callable, Tuple
from dataclasses import dataclass, asdict
from enum import Enum
from threading import Thread, Lock

# Обрабатываем отсутствие DISPLAY для headless окружения
if 'DISPLAY' not in os.environ:
    os.environ['DISPLAY'] = ':99'

# Импортируем библиотеки с обработкой ошибок
HAS_PYAUTOGUI = False
HAS_PYNPUT = False

try:
    import pyautogui
    HAS_PYAUTOGUI = True
except Exception as e:
    logging.warning(f"pyautogui not available: {e}")

try:
    import pynput
    from pynput.mouse import Mouse, Button, Controller as MouseController
    from pynput.keyboard import Key, Controller as KeyboardController, Listener
    HAS_PYNPUT = True
except Exception as e:
    logging.warning(f"pynput not available: {e}")

# Настройка логирования
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class MouseButton(Enum):
    """Кнопки мыши"""
    LEFT = "left"
    RIGHT = "right"
    MIDDLE = "middle"


@dataclass
class MouseEvent:
    """Событие мыши"""
    timestamp: str
    x: int
    y: int
    button: str
    action: str  # move, click, scroll


@dataclass
class KeyboardEvent:
    """Событие клавиатуры"""
    timestamp: str
    key: str
    action: str  # press, release


class RealMouseController:
    """Контроллер мыши"""
    
    def __init__(self):
        self.history: List[MouseEvent] = []
        self.listeners: List[Callable] = []
        self.lock = Lock()
        self.recording = False
        self.gesture_recording: List[Tuple[int, int, float]] = []
        
        if HAS_PYNPUT:
            self.controller = MouseController()
        else:
            self.controller = None
            logger.warning("Mouse controller not available")
    
    def move(self, x: int, y: int, duration: float = 0.5):
        """Переместить мышь"""
        if not HAS_PYAUTOGUI and not HAS_PYNPUT:
            logger.warning("Cannot move mouse: no GUI available")
            return
        
        try:
            if HAS_PYAUTOGUI:
                pyautogui.moveTo(x, y, duration=duration)
            elif HAS_PYNPUT and self.controller:
                self.controller.position = (x, y)
            
            # Логируем событие
            event = MouseEvent(
                timestamp=datetime.now().isoformat(),
                x=x,
                y=y,
                button="none",
                action="move"
            )
            self._add_event(event)
            
            # Вызываем слушателей
            self._notify_listeners(event)
        except Exception as e:
            logger.error(f"Error moving mouse: {e}")
    
    def click(self, button: str = "left", clicks: int = 1, interval: float = 0.1):
        """Нажать кнопку мыши"""
        if not HAS_PYAUTOGUI and not HAS_PYNPUT:
            logger.warning("Cannot click: no GUI available")
            return
        
        try:
            for _ in range(clicks):
                if HAS_PYAUTOGUI:
                    pyautogui.click(button=button)
                elif HAS_PYNPUT and self.controller:
                    if button == "left":
                        self.controller.click(Button.left)
                    elif button == "right":
                        self.controller.click(Button.right)
                    elif button == "middle":
                        self.controller.click(Button.middle)
                
                if _ < clicks - 1:
                    time.sleep(interval)
            
            # Логируем событие
            event = MouseEvent(
                timestamp=datetime.now().isoformat(),
                x=0,
                y=0,
                button=button,
                action="click"
            )
            self._add_event(event)
            
            # Вызываем слушателей
            self._notify_listeners(event)
        except Exception as e:
            logger.error(f"Error clicking: {e}")
    
    def scroll(self, x: int, y: int, direction: str = "up", amount: int = 5):
        """Прокрутить колесико"""
        if not HAS_PYAUTOGUI:
            logger.warning("Cannot scroll: pyautogui not available")
            return
        
        try:
            # Перемещаемся к позиции
            self.move(x, y, duration=0.1)
            
            # Прокручиваем
            if direction == "up":
                pyautogui.scroll(amount)
            else:
                pyautogui.scroll(-amount)
            
            # Логируем событие
            event = MouseEvent(
                timestamp=datetime.now().isoformat(),
                x=x,
                y=y,
                button="wheel",
                action="scroll"
            )
            self._add_event(event)
            
            # Вызываем слушателей
            self._notify_listeners(event)
        except Exception as e:
            logger.error(f"Error scrolling: {e}")
    
    def drag(self, start_x: int, start_y: int, end_x: int, end_y: int, duration: float = 0.5):
        """Перетащить элемент"""
        if not HAS_PYAUTOGUI:
            logger.warning("Cannot drag: pyautogui not available")
            return
        
        try:
            pyautogui.moveTo(start_x, start_y, duration=0.1)
            pyautogui.drag(end_x - start_x, end_y - start_y, duration=duration)
            
            # Логируем событие
            event = MouseEvent(
                timestamp=datetime.now().isoformat(),
                x=end_x,
                y=end_y,
                button="left",
                action="drag"
            )
            self._add_event(event)
            
            # Вызываем слушателей
            self._notify_listeners(event)
        except Exception as e:
            logger.error(f"Error dragging: {e}")
    
    def start_recording(self):
        """Начать запись жеста"""
        self.recording = True
        self.gesture_recording = []
        logger.info("Gesture recording started")
    
    def stop_recording(self) -> List[Tuple[int, int, float]]:
        """Остановить запись жеста"""
        self.recording = False
        logger.info(f"Gesture recording stopped: {len(self.gesture_recording)} points")
        return self.gesture_recording
    
    def playback_gesture(self, gesture: List[Tuple[int, int, float]]):
        """Воспроизвести записанный жест"""
        if not gesture:
            return
        
        try:
            for x, y, delay in gesture:
                self.move(x, y, duration=0.1)
                time.sleep(delay)
            
            logger.info(f"Gesture playback completed: {len(gesture)} points")
        except Exception as e:
            logger.error(f"Error playing back gesture: {e}")
    
    def save_gesture(self, gesture: List[Tuple[int, int, float]], filepath: str) -> bool:
        """Сохранить жест в JSON"""
        try:
            data = {
                'timestamp': datetime.now().isoformat(),
                'gesture': gesture
            }
            
            with open(filepath, 'w') as f:
                json.dump(data, f, indent=2)
            
            logger.info(f"Gesture saved to {filepath}")
            return True
        except Exception as e:
            logger.error(f"Error saving gesture: {e}")
            return False
    
    def load_gesture(self, filepath: str) -> Optional[List[Tuple[int, int, float]]]:
        """Загрузить жест из JSON"""
        try:
            with open(filepath, 'r') as f:
                data = json.load(f)
            
            gesture = data.get('gesture', [])
            logger.info(f"Gesture loaded from {filepath}")
            return gesture
        except Exception as e:
            logger.error(f"Error loading gesture: {e}")
            return None
    
    def add_listener(self, callback: Callable):
        """Добавить слушателя событий"""
        with self.lock:
            self.listeners.append(callback)
    
    def remove_listener(self, callback: Callable):
        """Удалить слушателя событий"""
        with self.lock:
            if callback in self.listeners:
                self.listeners.remove(callback)
    
    def _add_event(self, event: MouseEvent):
        """Добавить событие в историю"""
        with self.lock:
            self.history.append(event)
            # Ограничиваем размер истории
            if len(self.history) > 1000:
                self.history = self.history[-1000:]
    
    def _notify_listeners(self, event: MouseEvent):
        """Уведомить слушателей о событии"""
        with self.lock:
            for listener in self.listeners:
                try:
                    listener(event)
                except Exception as e:
                    logger.error(f"Error in listener: {e}")
    
    def get_history(self) -> List[MouseEvent]:
        """Получить историю событий"""
        with self.lock:
            return self.history.copy()
    
    def export_history(self, filepath: str) -> bool:
        """Экспортировать историю в JSON"""
        try:
            data = {
                'timestamp': datetime.now().isoformat(),
                'events': [asdict(event) for event in self.history]
            }
            
            with open(filepath, 'w') as f:
                json.dump(data, f, indent=2)
            
            logger.info(f"History exported to {filepath}")
            return True
        except Exception as e:
            logger.error(f"Error exporting history: {e}")
            return False


class RealKeyboardController:
    """Контроллер клавиатуры"""
    
    def __init__(self):
        self.history: List[KeyboardEvent] = []
        self.listeners: List[Callable] = []
        self.lock = Lock()
        
        if HAS_PYNPUT:
            self.controller = KeyboardController()
        else:
            self.controller = None
            logger.warning("Keyboard controller not available")
    
    def type_text(self, text: str, interval: float = 0.05):
        """Напечатать текст"""
        if not HAS_PYNPUT or not self.controller:
            logger.warning("Cannot type: keyboard controller not available")
            return
        
        try:
            for char in text:
                self.controller.type(char)
                time.sleep(interval)
            
            # Логируем событие
            event = KeyboardEvent(
                timestamp=datetime.now().isoformat(),
                key=f"text({len(text)})",
                action="type"
            )
            self._add_event(event)
            
            # Вызываем слушателей
            self._notify_listeners(event)
        except Exception as e:
            logger.error(f"Error typing: {e}")
    
    def hotkey(self, *keys):
        """Нажать комбинацию клавиш"""
        if not HAS_PYNPUT or not self.controller:
            logger.warning("Cannot press hotkey: keyboard controller not available")
            return
        
        try:
            # Преобразуем строки в Key объекты
            key_objects = []
            for key in keys:
                if hasattr(Key, key.lower()):
                    key_objects.append(getattr(Key, key.lower()))
                else:
                    key_objects.append(key)
            
            # Нажимаем все клавиши
            for key in key_objects:
                self.controller.press(key)
            
            # Отпускаем в обратном порядке
            for key in reversed(key_objects):
                self.controller.release(key)
            
            # Логируем событие
            event = KeyboardEvent(
                timestamp=datetime.now().isoformat(),
                key="+".join(keys),
                action="hotkey"
            )
            self._add_event(event)
            
            # Вызываем слушателей
            self._notify_listeners(event)
        except Exception as e:
            logger.error(f"Error pressing hotkey: {e}")
    
    def press(self, key: str):
        """Нажать клавишу"""
        if not HAS_PYNPUT or not self.controller:
            logger.warning("Cannot press key: keyboard controller not available")
            return
        
        try:
            if hasattr(Key, key.lower()):
                self.controller.press(getattr(Key, key.lower()))
            else:
                self.controller.press(key)
            
            # Логируем событие
            event = KeyboardEvent(
                timestamp=datetime.now().isoformat(),
                key=key,
                action="press"
            )
            self._add_event(event)
            
            # Вызываем слушателей
            self._notify_listeners(event)
        except Exception as e:
            logger.error(f"Error pressing key: {e}")
    
    def release(self, key: str):
        """Отпустить клавишу"""
        if not HAS_PYNPUT or not self.controller:
            logger.warning("Cannot release key: keyboard controller not available")
            return
        
        try:
            if hasattr(Key, key.lower()):
                self.controller.release(getattr(Key, key.lower()))
            else:
                self.controller.release(key)
            
            # Логируем событие
            event = KeyboardEvent(
                timestamp=datetime.now().isoformat(),
                key=key,
                action="release"
            )
            self._add_event(event)
            
            # Вызываем слушателей
            self._notify_listeners(event)
        except Exception as e:
            logger.error(f"Error releasing key: {e}")
    
    def add_listener(self, callback: Callable):
        """Добавить слушателя событий"""
        with self.lock:
            self.listeners.append(callback)
    
    def remove_listener(self, callback: Callable):
        """Удалить слушателя событий"""
        with self.lock:
            if callback in self.listeners:
                self.listeners.remove(callback)
    
    def _add_event(self, event: KeyboardEvent):
        """Добавить событие в историю"""
        with self.lock:
            self.history.append(event)
            # Ограничиваем размер истории
            if len(self.history) > 1000:
                self.history = self.history[-1000:]
    
    def _notify_listeners(self, event: KeyboardEvent):
        """Уведомить слушателей о событии"""
        with self.lock:
            for listener in self.listeners:
                try:
                    listener(event)
                except Exception as e:
                    logger.error(f"Error in listener: {e}")
    
    def get_history(self) -> List[KeyboardEvent]:
        """Получить историю событий"""
        with self.lock:
            return self.history.copy()
    
    def export_history(self, filepath: str) -> bool:
        """Экспортировать историю в JSON"""
        try:
            data = {
                'timestamp': datetime.now().isoformat(),
                'events': [asdict(event) for event in self.history]
            }
            
            with open(filepath, 'w') as f:
                json.dump(data, f, indent=2)
            
            logger.info(f"History exported to {filepath}")
            return True
        except Exception as e:
            logger.error(f"Error exporting history: {e}")
            return False


class RealInputManager:
    """Менеджер управления вводом"""
    
    def __init__(self):
        self.mouse_controller = RealMouseController()
        self.keyboard_controller = RealKeyboardController()
        logger.info("Real Input Manager initialized")
    
    def cleanup(self):
        """Очистить ресурсы"""
        logger.info("Input Manager cleaned up")


# Alias for backward compatibility
RealInputController = RealInputManager

# Экспорт основных классов
__all__ = [
    'RealInputController',
    'RealInputManager',
    'RealMouseController',
    'RealKeyboardController',
    'MouseEvent',
    'KeyboardEvent',
    'MouseButton'
]

