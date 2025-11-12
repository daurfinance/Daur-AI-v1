"""
Production-Grade Input Controller for Daur-AI v2.0
Полнофункциональный контроллер ввода без заглушек и симуляции
"""

import pyautogui
import pynput
from pynput.mouse import Mouse, Button, Controller as MouseController
from pynput.keyboard import Key, Controller as KeyboardController
import time
import threading
import json
import logging
from datetime import datetime
from typing import List, Tuple, Dict, Optional, Callable
from dataclasses import dataclass, asdict
from enum import Enum
import queue
import hashlib

# Настройка логирования
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


class MouseButton(Enum):
    """Кнопки мыши"""
    LEFT = Button.left
    RIGHT = Button.right
    MIDDLE = Button.middle


@dataclass
class MouseEvent:
    """Событие мыши"""
    timestamp: float
    x: int
    y: int
    button: Optional[str] = None
    action: str = "move"  # move, click, scroll
    
    def to_dict(self):
        return asdict(self)


@dataclass
class KeyboardEvent:
    """Событие клавиатуры"""
    timestamp: float
    key: str
    action: str = "press"  # press, release
    
    def to_dict(self):
        return asdict(self)


class ProductionMouseController:
    """Полнофункциональный контроллер мыши"""
    
    def __init__(self, enable_recording: bool = True):
        self.mouse = MouseController()
        self.enable_recording = enable_recording
        self.events: List[MouseEvent] = []
        self.listeners: List[Callable] = []
        self.is_recording = False
        self._listener = None
        self._event_queue = queue.Queue()
        
    def move_to(self, x: int, y: int, duration: float = 0.5) -> bool:
        """Переместить мышь с плавностью"""
        try:
            pyautogui.moveTo(x, y, duration=duration)
            event = MouseEvent(
                timestamp=time.time(),
                x=x,
                y=y,
                action="move"
            )
            self._record_event(event)
            self._notify_listeners(event)
            logger.info(f"Mouse moved to ({x}, {y})")
            return True
        except Exception as e:
            logger.error(f"Error moving mouse: {e}")
            return False
    
    def click(self, x: Optional[int] = None, y: Optional[int] = None, 
              button: str = "left", clicks: int = 1, interval: float = 0.1) -> bool:
        """Нажать кнопку мыши"""
        try:
            if x is not None and y is not None:
                self.move_to(x, y, duration=0.3)
            
            btn = MouseButton[button.upper()].value
            self.mouse.click(btn, clicks, interval)
            
            event = MouseEvent(
                timestamp=time.time(),
                x=x or self.mouse.position[0],
                y=y or self.mouse.position[1],
                button=button,
                action="click"
            )
            self._record_event(event)
            self._notify_listeners(event)
            logger.info(f"Mouse clicked {button} button {clicks} times")
            return True
        except Exception as e:
            logger.error(f"Error clicking mouse: {e}")
            return False
    
    def scroll(self, x: int, y: int, dx: int = 0, dy: int = 5) -> bool:
        """Прокрутить колесико мыши"""
        try:
            self.move_to(x, y, duration=0.2)
            self.mouse.scroll(dx, dy)
            
            event = MouseEvent(
                timestamp=time.time(),
                x=x,
                y=y,
                action="scroll"
            )
            self._record_event(event)
            self._notify_listeners(event)
            logger.info(f"Mouse scrolled by ({dx}, {dy})")
            return True
        except Exception as e:
            logger.error(f"Error scrolling: {e}")
            return False
    
    def drag_to(self, x: int, y: int, duration: float = 0.5, button: str = "left") -> bool:
        """Перетащить мышь"""
        try:
            btn = MouseButton[button.upper()].value
            current_x, current_y = self.mouse.position
            
            self.mouse.press(btn)
            pyautogui.moveTo(x, y, duration=duration)
            self.mouse.release(btn)
            
            event = MouseEvent(
                timestamp=time.time(),
                x=x,
                y=y,
                button=button,
                action="drag"
            )
            self._record_event(event)
            self._notify_listeners(event)
            logger.info(f"Mouse dragged to ({x}, {y})")
            return True
        except Exception as e:
            logger.error(f"Error dragging: {e}")
            return False
    
    def start_recording(self) -> bool:
        """Начать запись событий мыши"""
        try:
            if self.is_recording:
                return False
            
            self.is_recording = True
            self.events = []
            
            def on_move(x, y):
                if self.is_recording:
                    self._event_queue.put(MouseEvent(
                        timestamp=time.time(),
                        x=x,
                        y=y,
                        action="move"
                    ))
            
            def on_click(x, y, button, pressed):
                if self.is_recording:
                    self._event_queue.put(MouseEvent(
                        timestamp=time.time(),
                        x=x,
                        y=y,
                        button=button.name.lower(),
                        action="click" if pressed else "release"
                    ))
            
            def on_scroll(x, y, dx, dy):
                if self.is_recording:
                    self._event_queue.put(MouseEvent(
                        timestamp=time.time(),
                        x=x,
                        y=y,
                        action="scroll"
                    ))
            
            self._listener = pynput.mouse.Listener(
                on_move=on_move,
                on_click=on_click,
                on_scroll=on_scroll
            )
            self._listener.start()
            logger.info("Mouse recording started")
            return True
        except Exception as e:
            logger.error(f"Error starting recording: {e}")
            return False
    
    def stop_recording(self) -> List[MouseEvent]:
        """Остановить запись и вернуть события"""
        try:
            self.is_recording = False
            if self._listener:
                self._listener.stop()
            
            # Собрать все события из очереди
            while not self._event_queue.empty():
                try:
                    event = self._event_queue.get_nowait()
                    self.events.append(event)
                except queue.Empty:
                    break
            
            logger.info(f"Mouse recording stopped. Recorded {len(self.events)} events")
            return self.events
        except Exception as e:
            logger.error(f"Error stopping recording: {e}")
            return []
    
    def playback_events(self, events: List[MouseEvent], speed: float = 1.0) -> bool:
        """Воспроизвести записанные события"""
        try:
            if not events:
                return False
            
            start_time = events[0].timestamp
            
            for event in events:
                # Ожидание между событиями
                wait_time = (event.timestamp - start_time) / speed
                if wait_time > 0:
                    time.sleep(wait_time)
                
                if event.action == "move":
                    self.move_to(event.x, event.y, duration=0.1)
                elif event.action == "click":
                    self.click(event.x, event.y, button=event.button or "left")
                elif event.action == "scroll":
                    self.scroll(event.x, event.y)
                elif event.action == "drag":
                    self.drag_to(event.x, event.y, button=event.button or "left")
            
            logger.info(f"Playback completed: {len(events)} events")
            return True
        except Exception as e:
            logger.error(f"Error during playback: {e}")
            return False
    
    def save_events(self, filepath: str) -> bool:
        """Сохранить события в JSON"""
        try:
            data = {
                "timestamp": datetime.now().isoformat(),
                "event_count": len(self.events),
                "events": [event.to_dict() for event in self.events]
            }
            with open(filepath, 'w') as f:
                json.dump(data, f, indent=2)
            logger.info(f"Events saved to {filepath}")
            return True
        except Exception as e:
            logger.error(f"Error saving events: {e}")
            return False
    
    def load_events(self, filepath: str) -> bool:
        """Загрузить события из JSON"""
        try:
            with open(filepath, 'r') as f:
                data = json.load(f)
            
            self.events = [
                MouseEvent(**event) for event in data.get("events", [])
            ]
            logger.info(f"Loaded {len(self.events)} events from {filepath}")
            return True
        except Exception as e:
            logger.error(f"Error loading events: {e}")
            return False
    
    def add_listener(self, callback: Callable[[MouseEvent], None]):
        """Добавить слушатель событий"""
        self.listeners.append(callback)
    
    def _record_event(self, event: MouseEvent):
        """Записать событие"""
        if self.enable_recording:
            self.events.append(event)
    
    def _notify_listeners(self, event: MouseEvent):
        """Уведомить слушателей"""
        for listener in self.listeners:
            try:
                listener(event)
            except Exception as e:
                logger.error(f"Error in listener: {e}")
    
    def get_position(self) -> Tuple[int, int]:
        """Получить текущую позицию мыши"""
        return self.mouse.position
    
    def get_events_history(self) -> List[Dict]:
        """Получить историю событий"""
        return [event.to_dict() for event in self.events]


class ProductionKeyboardController:
    """Полнофункциональный контроллер клавиатуры"""
    
    def __init__(self, enable_recording: bool = True):
        self.keyboard = KeyboardController()
        self.enable_recording = enable_recording
        self.events: List[KeyboardEvent] = []
        self.listeners: List[Callable] = []
        self.is_recording = False
        self._listener = None
        self._event_queue = queue.Queue()
    
    def type_text(self, text: str, interval: float = 0.05) -> bool:
        """Напечатать текст"""
        try:
            for char in text:
                self.keyboard.type(char)
                time.sleep(interval)
            
            event = KeyboardEvent(
                timestamp=time.time(),
                key=text,
                action="type"
            )
            self._record_event(event)
            self._notify_listeners(event)
            logger.info(f"Typed text: {text[:50]}...")
            return True
        except Exception as e:
            logger.error(f"Error typing text: {e}")
            return False
    
    def press_key(self, key: str) -> bool:
        """Нажать клавишу"""
        try:
            key_obj = self._get_key_object(key)
            self.keyboard.press(key_obj)
            
            event = KeyboardEvent(
                timestamp=time.time(),
                key=key,
                action="press"
            )
            self._record_event(event)
            self._notify_listeners(event)
            logger.info(f"Key pressed: {key}")
            return True
        except Exception as e:
            logger.error(f"Error pressing key: {e}")
            return False
    
    def release_key(self, key: str) -> bool:
        """Отпустить клавишу"""
        try:
            key_obj = self._get_key_object(key)
            self.keyboard.release(key_obj)
            
            event = KeyboardEvent(
                timestamp=time.time(),
                key=key,
                action="release"
            )
            self._record_event(event)
            self._notify_listeners(event)
            logger.info(f"Key released: {key}")
            return True
        except Exception as e:
            logger.error(f"Error releasing key: {e}")
            return False
    
    def hotkey(self, *keys: str) -> bool:
        """Нажать комбинацию клавиш"""
        try:
            key_objects = [self._get_key_object(k) for k in keys]
            
            # Нажать все клавиши
            for key_obj in key_objects:
                self.keyboard.press(key_obj)
            
            # Отпустить в обратном порядке
            for key_obj in reversed(key_objects):
                self.keyboard.release(key_obj)
            
            event = KeyboardEvent(
                timestamp=time.time(),
                key="+".join(keys),
                action="hotkey"
            )
            self._record_event(event)
            self._notify_listeners(event)
            logger.info(f"Hotkey pressed: {'+'.join(keys)}")
            return True
        except Exception as e:
            logger.error(f"Error pressing hotkey: {e}")
            return False
    
    def start_recording(self) -> bool:
        """Начать запись событий клавиатуры"""
        try:
            if self.is_recording:
                return False
            
            self.is_recording = True
            self.events = []
            
            def on_press(key):
                if self.is_recording:
                    try:
                        key_name = key.char if hasattr(key, 'char') else key.name
                    except Exception as e:
                        key_name = str(key)
                    
                    self._event_queue.put(KeyboardEvent(
                        timestamp=time.time(),
                        key=key_name,
                        action="press"
                    ))
            
            def on_release(key):
                if self.is_recording:
                    try:
                        key_name = key.char if hasattr(key, 'char') else key.name
                    except Exception as e:
                        key_name = str(key)
                    
                    self._event_queue.put(KeyboardEvent(
                        timestamp=time.time(),
                        key=key_name,
                        action="release"
                    ))
            
            self._listener = pynput.keyboard.Listener(
                on_press=on_press,
                on_release=on_release
            )
            self._listener.start()
            logger.info("Keyboard recording started")
            return True
        except Exception as e:
            logger.error(f"Error starting recording: {e}")
            return False
    
    def stop_recording(self) -> List[KeyboardEvent]:
        """Остановить запись и вернуть события"""
        try:
            self.is_recording = False
            if self._listener:
                self._listener.stop()
            
            # Собрать все события из очереди
            while not self._event_queue.empty():
                try:
                    event = self._event_queue.get_nowait()
                    self.events.append(event)
                except queue.Empty:
                    break
            
            logger.info(f"Keyboard recording stopped. Recorded {len(self.events)} events")
            return self.events
        except Exception as e:
            logger.error(f"Error stopping recording: {e}")
            return []
    
    def add_listener(self, callback: Callable[[KeyboardEvent], None]):
        """Добавить слушатель событий"""
        self.listeners.append(callback)
    
    def _record_event(self, event: KeyboardEvent):
        """Записать событие"""
        if self.enable_recording:
            self.events.append(event)
    
    def _notify_listeners(self, event: KeyboardEvent):
        """Уведомить слушателей"""
        for listener in self.listeners:
            try:
                listener(event)
            except Exception as e:
                logger.error(f"Error in listener: {e}")
    
    def _get_key_object(self, key: str):
        """Получить объект клавиши"""
        key_lower = key.lower()
        
        # Специальные клавиши
        special_keys = {
            'ctrl': Key.ctrl,
            'control': Key.ctrl,
            'alt': Key.alt,
            'shift': Key.shift,
            'enter': Key.enter,
            'return': Key.enter,
            'tab': Key.tab,
            'space': Key.space,
            'backspace': Key.backspace,
            'delete': Key.delete,
            'home': Key.home,
            'end': Key.end,
            'pageup': Key.page_up,
            'pagedown': Key.page_down,
            'up': Key.up,
            'down': Key.down,
            'left': Key.left,
            'right': Key.right,
            'esc': Key.esc,
            'escape': Key.esc,
        }
        
        if key_lower in special_keys:
            return special_keys[key_lower]
        elif len(key) == 1:
            return key
        else:
            return key
    
    def get_events_history(self) -> List[Dict]:
        """Получить историю событий"""
        return [event.to_dict() for event in self.events]


class ProductionInputManager:
    """Менеджер ввода для управления мышкой и клавиатурой"""
    
    def __init__(self):
        self.mouse = ProductionMouseController()
        self.keyboard = ProductionKeyboardController()
        self.is_active = True
    
    def execute_sequence(self, sequence: List[Dict]) -> bool:
        """Выполнить последовательность действий"""
        try:
            for action in sequence:
                action_type = action.get("type")
                
                if action_type == "mouse_move":
                    self.mouse.move_to(action["x"], action["y"], action.get("duration", 0.5))
                elif action_type == "mouse_click":
                    self.mouse.click(action.get("x"), action.get("y"), 
                                   action.get("button", "left"))
                elif action_type == "mouse_scroll":
                    self.mouse.scroll(action["x"], action["y"], 
                                    action.get("dx", 0), action.get("dy", 5))
                elif action_type == "mouse_drag":
                    self.mouse.drag_to(action["x"], action["y"], 
                                     action.get("duration", 0.5))
                elif action_type == "keyboard_type":
                    self.keyboard.type_text(action["text"], action.get("interval", 0.05))
                elif action_type == "keyboard_hotkey":
                    self.keyboard.hotkey(*action["keys"])
                elif action_type == "wait":
                    time.sleep(action.get("duration", 1))
                
                time.sleep(action.get("wait", 0.1))
            
            logger.info(f"Executed sequence of {len(sequence)} actions")
            return True
        except Exception as e:
            logger.error(f"Error executing sequence: {e}")
            return False
    
    def get_status(self) -> Dict:
        """Получить статус системы ввода"""
        return {
            "active": self.is_active,
            "mouse_position": self.mouse.get_position(),
            "mouse_events": len(self.mouse.events),
            "keyboard_events": len(self.keyboard.events),
            "timestamp": datetime.now().isoformat()
        }


# Экспорт основных классов
__all__ = [
    'ProductionMouseController',
    'ProductionKeyboardController',
    'ProductionInputManager',
    'MouseEvent',
    'KeyboardEvent'
]

