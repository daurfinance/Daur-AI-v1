"""
Input Recorder and Playback Module for Daur-AI v2.0
Полнофункциональная запись и воспроизведение действий пользователя

Поддерживает:
- Запись движений мыши
- Запись кликов мыши
- Запись нажатий клавиш
- Сохранение/загрузка записей
- Воспроизведение с сохранением времени
- Редактирование записей
- Экспорт в JSON
"""

import json
import time
import threading
import logging
from datetime import datetime
from typing import List, Dict, Optional, Callable
from dataclasses import dataclass, asdict, field
from enum import Enum
from pathlib import Path
import pickle

# Настройка логирования
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class ActionType(Enum):
    """Типы действий"""
    MOUSE_MOVE = "mouse_move"
    MOUSE_CLICK = "mouse_click"
    MOUSE_SCROLL = "mouse_scroll"
    KEY_PRESS = "key_press"
    KEY_RELEASE = "key_release"
    PAUSE = "pause"


class MouseButton(Enum):
    """Кнопки мыши"""
    LEFT = "left"
    RIGHT = "right"
    MIDDLE = "middle"


@dataclass
class InputAction:
    """Одно действие пользователя"""
    action_type: ActionType
    timestamp: float  # Время действия в секундах от начала записи
    x: Optional[int] = None  # X координата для mouse_move
    y: Optional[int] = None  # Y координата для mouse_move
    button: Optional[str] = None  # Кнопка мыши
    key: Optional[str] = None  # Клавиша
    dx: Optional[int] = None  # Смещение X для scroll
    dy: Optional[int] = None  # Смещение Y для scroll
    duration: Optional[float] = None  # Длительность паузы
    
    def to_dict(self):
        data = asdict(self)
        data['action_type'] = self.action_type.value
        return data


class InputRecorder:
    """Запись действий пользователя"""
    
    def __init__(self):
        """Инициализация рекордера"""
        self.actions: List[InputAction] = []
        self.is_recording = False
        self.start_time: Optional[float] = None
        self.lock = threading.Lock()
        
        # Попытка импортировать mouse и keyboard
        try:
            import mouse
            self.mouse = mouse
            self.has_mouse = True
        except ImportError:
            logger.warning("mouse library not available. Install with: pip install mouse")
            self.has_mouse = False
            self.mouse = None
        
        try:
            from pynput import keyboard
            self.keyboard = keyboard
            self.has_keyboard = True
        except ImportError:
            logger.warning("pynput library not available. Install with: pip install pynput")
            self.has_keyboard = False
            self.keyboard = None
        
        # Слушатели
        self.mouse_listener = None
        self.keyboard_listener = None
        
        logger.info("Input Recorder initialized")
    
    def start(self) -> bool:
        """Начать запись"""
        if self.is_recording:
            logger.warning("Recording already in progress")
            return False
        
        with self.lock:
            self.actions = []
            self.start_time = time.time()
            self.is_recording = True
        
        # Запустить слушатели мыши
        if self.has_mouse:
            try:
                self.mouse.on_move(self._on_mouse_move)
                self.mouse.on_click(self._on_mouse_click)
                self.mouse.on_scroll(self._on_mouse_scroll)
            except Exception as e:
                logger.warning(f"Could not start mouse listener: {e}")
        
        # Запустить слушатели клавиатуры
        if self.has_keyboard:
            try:
                self.keyboard_listener = self.keyboard.Listener(
                    on_press=self._on_key_press,
                    on_release=self._on_key_release
                )
                self.keyboard_listener.start()
            except Exception as e:
                logger.warning(f"Could not start keyboard listener: {e}")
        
        logger.info("Recording started")
        return True
    
    def stop(self) -> List[InputAction]:
        """Остановить запись"""
        if not self.is_recording:
            logger.warning("Recording not in progress")
            return []
        
        with self.lock:
            self.is_recording = False
        
        # Остановить слушатели
        if self.has_mouse:
            try:
                self.mouse.unhook_all()
            except Exception as e:
                logger.warning(f"Could not stop mouse listener: {e}")
        
        if self.keyboard_listener:
            try:
                self.keyboard_listener.stop()
            except Exception as e:
                logger.warning(f"Could not stop keyboard listener: {e}")
        
        logger.info(f"Recording stopped. Total actions: {len(self.actions)}")
        return self.actions.copy()
    
    def _on_mouse_move(self, event):
        """Обработчик движения мыши"""
        if not self.is_recording:
            return
        
        with self.lock:
            action = InputAction(
                action_type=ActionType.MOUSE_MOVE,
                timestamp=time.time() - self.start_time,
                x=event.x,
                y=event.y
            )
            self.actions.append(action)
    
    def _on_mouse_click(self, x, y, button, pressed):
        """Обработчик клика мыши"""
        if not self.is_recording:
            return
        
        with self.lock:
            action = InputAction(
                action_type=ActionType.MOUSE_CLICK,
                timestamp=time.time() - self.start_time,
                x=x,
                y=y,
                button=button.name.lower() if hasattr(button, 'name') else str(button)
            )
            self.actions.append(action)
    
    def _on_mouse_scroll(self, x, y, dx, dy):
        """Обработчик прокрутки мыши"""
        if not self.is_recording:
            return
        
        with self.lock:
            action = InputAction(
                action_type=ActionType.MOUSE_SCROLL,
                timestamp=time.time() - self.start_time,
                x=x,
                y=y,
                dx=dx,
                dy=dy
            )
            self.actions.append(action)
    
    def _on_key_press(self, key):
        """Обработчик нажатия клавиши"""
        if not self.is_recording:
            return
        
        try:
            key_name = key.char if hasattr(key, 'char') else key.name
        except AttributeError:
            key_name = str(key)
        
        with self.lock:
            action = InputAction(
                action_type=ActionType.KEY_PRESS,
                timestamp=time.time() - self.start_time,
                key=key_name
            )
            self.actions.append(action)
    
    def _on_key_release(self, key):
        """Обработчик отпускания клавиши"""
        if not self.is_recording:
            return
        
        try:
            key_name = key.char if hasattr(key, 'char') else key.name
        except AttributeError:
            key_name = str(key)
        
        with self.lock:
            action = InputAction(
                action_type=ActionType.KEY_RELEASE,
                timestamp=time.time() - self.start_time,
                key=key_name
            )
            self.actions.append(action)
    
    def get_recording(self) -> List[InputAction]:
        """Получить текущую запись"""
        with self.lock:
            return self.actions.copy()
    
    def save_recording(self, filename: str) -> bool:
        """Сохранить запись в файл"""
        try:
            with open(filename, 'w') as f:
                actions_data = [action.to_dict() for action in self.actions]
                json.dump(actions_data, f, indent=2)
            logger.info(f"Recording saved to {filename}")
            return True
        except Exception as e:
            logger.error(f"Error saving recording: {e}")
            return False
    
    def load_recording(self, filename: str) -> bool:
        """Загрузить запись из файла"""
        try:
            with open(filename, 'r') as f:
                actions_data = json.load(f)
            
            self.actions = []
            for action_data in actions_data:
                action_type = ActionType(action_data.pop('action_type'))
                action = InputAction(action_type=action_type, **action_data)
                self.actions.append(action)
            
            logger.info(f"Recording loaded from {filename}. Total actions: {len(self.actions)}")
            return True
        except Exception as e:
            logger.error(f"Error loading recording: {e}")
            return False
    
    def clear_recording(self):
        """Очистить запись"""
        with self.lock:
            self.actions = []
        logger.info("Recording cleared")
    
    def add_pause(self, duration: float):
        """Добавить паузу в запись"""
        with self.lock:
            if self.actions:
                last_timestamp = self.actions[-1].timestamp
            else:
                last_timestamp = 0
            
            action = InputAction(
                action_type=ActionType.PAUSE,
                timestamp=last_timestamp + duration,
                duration=duration
            )
            self.actions.append(action)
        logger.info(f"Pause added: {duration}s")
    
    def get_statistics(self) -> Dict:
        """Получить статистику записи"""
        if not self.actions:
            return {
                'total_actions': 0,
                'duration': 0,
                'action_breakdown': {}
            }
        
        duration = self.actions[-1].timestamp if self.actions else 0
        action_breakdown = {}
        
        for action in self.actions:
            action_type = action.action_type.value
            action_breakdown[action_type] = action_breakdown.get(action_type, 0) + 1
        
        return {
            'total_actions': len(self.actions),
            'duration': duration,
            'action_breakdown': action_breakdown
        }


class InputPlayer:
    """Воспроизведение записанных действий"""
    
    def __init__(self):
        """Инициализация плеера"""
        from src.input.real_input_controller import RealMouseController, RealKeyboardController
        
        self.mouse = RealMouseController()
        self.keyboard = RealKeyboardController()
        self.is_playing = False
        self.lock = threading.Lock()
        
        logger.info("Input Player initialized")
    
    def play(self, actions: List[InputAction], speed: float = 1.0, 
             on_action: Optional[Callable] = None) -> bool:
        """
        Воспроизвести действия
        
        Args:
            actions: Список действий для воспроизведения
            speed: Скорость воспроизведения (1.0 = нормальная)
            on_action: Callback при каждом действии
        
        Returns:
            True если успешно, False если ошибка
        """
        if self.is_playing:
            logger.warning("Playback already in progress")
            return False
        
        if not actions:
            logger.warning("No actions to play")
            return False
        
        with self.lock:
            self.is_playing = True
        
        try:
            start_time = time.time()
            
            for i, action in enumerate(actions):
                if not self.is_playing:
                    break
                
                # Ждём до нужного времени
                target_time = action.timestamp / speed
                current_time = time.time() - start_time
                
                if current_time < target_time:
                    time.sleep(target_time - current_time)
                
                # Выполняем действие
                self._execute_action(action)
                
                # Callback
                if on_action:
                    on_action(action, i, len(actions))
            
            logger.info(f"Playback completed. Actions: {len(actions)}")
            return True
        
        except Exception as e:
            logger.error(f"Error during playback: {e}")
            return False
        
        finally:
            with self.lock:
                self.is_playing = False
    
    def _execute_action(self, action: InputAction):
        """Выполнить одно действие"""
        try:
            if action.action_type == ActionType.MOUSE_MOVE:
                self.mouse.move(action.x, action.y)
            
            elif action.action_type == ActionType.MOUSE_CLICK:
                self.mouse.click(button=action.button or 'left')
            
            elif action.action_type == ActionType.MOUSE_SCROLL:
                self.mouse.scroll(action.dx or 0, action.dy or 0)
            
            elif action.action_type == ActionType.KEY_PRESS:
                self.keyboard.type(action.key)
            
            elif action.action_type == ActionType.PAUSE:
                time.sleep(action.duration or 0)
        
        except Exception as e:
            logger.warning(f"Error executing action {action.action_type}: {e}")
    
    def stop(self):
        """Остановить воспроизведение"""
        with self.lock:
            self.is_playing = False
        logger.info("Playback stopped")
    
    def play_from_file(self, filename: str, speed: float = 1.0, 
                       on_action: Optional[Callable] = None) -> bool:
        """Воспроизвести из файла"""
        try:
            with open(filename, 'r') as f:
                actions_data = json.load(f)
            
            actions = []
            for action_data in actions_data:
                action_type = ActionType(action_data.pop('action_type'))
                action = InputAction(action_type=action_type, **action_data)
                actions.append(action)
            
            return self.play(actions, speed, on_action)
        
        except Exception as e:
            logger.error(f"Error loading and playing file: {e}")
            return False


class MacroManager:
    """Управление макросами"""
    
    def __init__(self, macros_dir: str = './macros'):
        """Инициализация менеджера макросов"""
        self.macros_dir = Path(macros_dir)
        self.macros_dir.mkdir(exist_ok=True)
        self.macros: Dict[str, List[InputAction]] = {}
        self.player = InputPlayer()
        
        logger.info(f"Macro Manager initialized. Directory: {macros_dir}")
    
    def record_macro(self, name: str) -> List[InputAction]:
        """Записать макрос"""
        logger.info(f"Recording macro: {name}")
        
        recorder = InputRecorder()
        recorder.start()
        
        input("Press Enter when ready to start recording...")
        input("Press Enter when done recording...")
        
        actions = recorder.stop()
        self.macros[name] = actions
        
        # Сохранить на диск
        self.save_macro(name)
        
        logger.info(f"Macro recorded: {name}. Actions: {len(actions)}")
        return actions
    
    def play_macro(self, name: str, speed: float = 1.0) -> bool:
        """Воспроизвести макрос"""
        if name not in self.macros:
            if not self.load_macro(name):
                logger.error(f"Macro not found: {name}")
                return False
        
        logger.info(f"Playing macro: {name}")
        return self.player.play(self.macros[name], speed)
    
    def save_macro(self, name: str) -> bool:
        """Сохранить макрос"""
        if name not in self.macros:
            logger.error(f"Macro not found: {name}")
            return False
        
        filename = self.macros_dir / f"{name}.json"
        try:
            with open(filename, 'w') as f:
                actions_data = [action.to_dict() for action in self.macros[name]]
                json.dump(actions_data, f, indent=2)
            logger.info(f"Macro saved: {name}")
            return True
        except Exception as e:
            logger.error(f"Error saving macro: {e}")
            return False
    
    def load_macro(self, name: str) -> bool:
        """Загрузить макрос"""
        filename = self.macros_dir / f"{name}.json"
        
        if not filename.exists():
            logger.error(f"Macro file not found: {filename}")
            return False
        
        try:
            with open(filename, 'r') as f:
                actions_data = json.load(f)
            
            actions = []
            for action_data in actions_data:
                action_type = ActionType(action_data.pop('action_type'))
                action = InputAction(action_type=action_type, **action_data)
                actions.append(action)
            
            self.macros[name] = actions
            logger.info(f"Macro loaded: {name}. Actions: {len(actions)}")
            return True
        
        except Exception as e:
            logger.error(f"Error loading macro: {e}")
            return False
    
    def list_macros(self) -> List[str]:
        """Список всех макросов"""
        macros = [f.stem for f in self.macros_dir.glob('*.json')]
        return sorted(macros)
    
    def delete_macro(self, name: str) -> bool:
        """Удалить макрос"""
        filename = self.macros_dir / f"{name}.json"
        
        try:
            if filename.exists():
                filename.unlink()
            if name in self.macros:
                del self.macros[name]
            logger.info(f"Macro deleted: {name}")
            return True
        except Exception as e:
            logger.error(f"Error deleting macro: {e}")
            return False
