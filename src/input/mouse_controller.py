#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
Daur-AI: Модуль управления мышкой с продвинутыми функциями
Полный контроль над мышкой с поддержкой жестов, записи и воспроизведения

Версия: 2.0
Дата: 25.10.2025
Автор: Manus AI
"""

import logging
import time
from typing import Dict, List, Any, Optional, Tuple, Callable
from enum import Enum
from dataclasses import dataclass, field
from datetime import datetime
from pathlib import Path
import json


class MouseButton(Enum):
    """Кнопки мыши"""
    LEFT = "left"
    RIGHT = "right"
    MIDDLE = "middle"
    SCROLL_UP = "scroll_up"
    SCROLL_DOWN = "scroll_down"


class MouseGesture(Enum):
    """Жесты мыши"""
    CLICK = "click"
    DOUBLE_CLICK = "double_click"
    TRIPLE_CLICK = "triple_click"
    DRAG = "drag"
    SWIPE = "swipe"
    CIRCLE = "circle"
    ZIGZAG = "zigzag"


@dataclass
class MousePosition:
    """Позиция мыши"""
    x: int
    y: int
    timestamp: datetime = field(default_factory=datetime.now)
    
    def distance_to(self, other: 'MousePosition') -> float:
        """Расстояние до другой позиции"""
        return ((self.x - other.x) ** 2 + (self.y - other.y) ** 2) ** 0.5


@dataclass
class MouseEvent:
    """Событие мыши"""
    event_type: str
    position: MousePosition
    button: Optional[MouseButton] = None
    gesture: Optional[MouseGesture] = None
    duration: float = 0.0
    timestamp: datetime = field(default_factory=datetime.now)


@dataclass
class MouseGestureRecord:
    """Запись жеста мыши"""
    gesture_id: str
    gesture_type: MouseGesture
    positions: List[MousePosition] = field(default_factory=list)
    duration: float = 0.0
    created_at: datetime = field(default_factory=datetime.now)


class MouseController:
    """Контроллер мыши"""
    
    def __init__(self):
        """Инициализация"""
        self.logger = logging.getLogger('daur_ai.mouse_controller')
        self.current_position = MousePosition(0, 0)
        self.is_recording = False
        self.recorded_events: List[MouseEvent] = []
        self.gesture_records: Dict[str, MouseGestureRecord] = {}
        self.event_callbacks: Dict[str, List[Callable]] = {}
        self.logger.info("Mouse controller инициализирован")
    
    def get_position(self) -> MousePosition:
        """
        Получить текущую позицию мыши
        
        Returns:
            MousePosition: Текущая позиция
        """
        try:
            import pyautogui
            x, y = pyautogui.position()
            self.current_position = MousePosition(x, y)
            return self.current_position
        except Exception as e:
            self.logger.error(f"Ошибка получения позиции: {e}")
            return self.current_position
    
    def move_to(self, x: int, y: int, duration: float = 0.5) -> bool:
        """
        Переместить мышь в позицию
        
        Args:
            x: X координата
            y: Y координата
            duration: Длительность движения в секундах
            
        Returns:
            bool: Успешность операции
        """
        try:
            import pyautogui
            start_pos = self.get_position()
            pyautogui.moveTo(x, y, duration=duration)
            self.current_position = MousePosition(x, y)
            
            self._trigger_event('move', MouseEvent(
                'move',
                self.current_position,
                duration=duration
            ))
            
            self.logger.info(f"Мышь перемещена: ({start_pos.x}, {start_pos.y}) -> ({x}, {y})")
            return True
        
        except Exception as e:
            self.logger.error(f"Ошибка перемещения мыши: {e}")
            return False
    
    def move_relative(self, dx: int, dy: int, duration: float = 0.5) -> bool:
        """
        Переместить мышь относительно текущей позиции
        
        Args:
            dx: Смещение по X
            dy: Смещение по Y
            duration: Длительность движения
            
        Returns:
            bool: Успешность операции
        """
        current = self.get_position()
        return self.move_to(current.x + dx, current.y + dy, duration)
    
    def click(self, button: MouseButton = MouseButton.LEFT, clicks: int = 1,
             interval: float = 0.1) -> bool:
        """
        Нажать на кнопку мыши
        
        Args:
            button: Кнопка мыши
            clicks: Количество нажатий
            interval: Интервал между нажатиями
            
        Returns:
            bool: Успешность операции
        """
        try:
            import pyautogui
            
            button_map = {
                MouseButton.LEFT: 'left',
                MouseButton.RIGHT: 'right',
                MouseButton.MIDDLE: 'middle'
            }
            
            pyautogui.click(button=button_map[button], clicks=clicks, interval=interval)
            
            event_type = 'double_click' if clicks == 2 else 'triple_click' if clicks == 3 else 'click'
            self._trigger_event(event_type, MouseEvent(
                event_type,
                self.get_position(),
                button=button
            ))
            
            self.logger.info(f"Нажата кнопка: {button.value} ({clicks} раз)")
            return True
        
        except Exception as e:
            self.logger.error(f"Ошибка нажатия: {e}")
            return False
    
    def drag(self, start_x: int, start_y: int, end_x: int, end_y: int,
            duration: float = 0.5, button: MouseButton = MouseButton.LEFT) -> bool:
        """
        Перетащить мышь
        
        Args:
            start_x: Начальная X координата
            start_y: Начальная Y координата
            end_x: Конечная X координата
            end_y: Конечная Y координата
            duration: Длительность операции
            button: Кнопка мыши
            
        Returns:
            bool: Успешность операции
        """
        try:
            import pyautogui
            
            button_map = {
                MouseButton.LEFT: 'left',
                MouseButton.RIGHT: 'right',
                MouseButton.MIDDLE: 'middle'
            }
            
            pyautogui.moveTo(start_x, start_y)
            pyautogui.drag(end_x - start_x, end_y - start_y, duration=duration,
                          button=button_map[button])
            
            self._trigger_event('drag', MouseEvent(
                'drag',
                MousePosition(end_x, end_y),
                button=button,
                duration=duration
            ))
            
            self.logger.info(f"Перетаскивание: ({start_x}, {start_y}) -> ({end_x}, {end_y})")
            return True
        
        except Exception as e:
            self.logger.error(f"Ошибка перетаскивания: {e}")
            return False
    
    def scroll(self, x: int, y: int, clicks: int = 3, direction: str = 'down') -> bool:
        """
        Прокрутить колесико мыши
        
        Args:
            x: X координата
            y: Y координата
            clicks: Количество кликов колесика
            direction: Направление (up/down)
            
        Returns:
            bool: Успешность операции
        """
        try:
            import pyautogui
            
            self.move_to(x, y, duration=0.2)
            
            if direction.lower() == 'up':
                pyautogui.scroll(clicks)
            else:
                pyautogui.scroll(-clicks)
            
            button = MouseButton.SCROLL_UP if direction.lower() == 'up' else MouseButton.SCROLL_DOWN
            self._trigger_event('scroll', MouseEvent(
                'scroll',
                MousePosition(x, y),
                button=button
            ))
            
            self.logger.info(f"Прокрутка: {direction} ({clicks} кликов)")
            return True
        
        except Exception as e:
            self.logger.error(f"Ошибка прокрутки: {e}")
            return False
    
    def record_gesture(self, gesture_id: str, duration: float = 5.0) -> Optional[MouseGestureRecord]:
        """
        Записать жест мыши
        
        Args:
            gesture_id: ID жеста
            duration: Длительность записи в секундах
            
        Returns:
            Optional[MouseGestureRecord]: Запись жеста или None
        """
        try:
            import pyautogui
            
            positions = []
            start_time = time.time()
            
            self.logger.info(f"Начало записи жеста: {gesture_id}")
            
            while time.time() - start_time < duration:
                x, y = pyautogui.position()
                positions.append(MousePosition(x, y))
                time.sleep(0.05)
            
            # Определяем тип жеста
            gesture_type = self._detect_gesture_type(positions)
            
            record = MouseGestureRecord(
                gesture_id=gesture_id,
                gesture_type=gesture_type,
                positions=positions,
                duration=time.time() - start_time
            )
            
            self.gesture_records[gesture_id] = record
            self.logger.info(f"Жест записан: {gesture_id} ({gesture_type.value})")
            return record
        
        except Exception as e:
            self.logger.error(f"Ошибка записи жеста: {e}")
            return None
    
    def playback_gesture(self, gesture_id: str, speed: float = 1.0) -> bool:
        """
        Воспроизвести записанный жест
        
        Args:
            gesture_id: ID жеста
            speed: Скорость воспроизведения (1.0 = нормальная)
            
        Returns:
            bool: Успешность операции
        """
        if gesture_id not in self.gesture_records:
            self.logger.error(f"Жест не найден: {gesture_id}")
            return False
        
        try:
            record = self.gesture_records[gesture_id]
            positions = record.positions
            
            if not positions:
                return False
            
            # Начинаем с первой позиции
            self.move_to(positions[0].x, positions[0].y, duration=0.1)
            
            # Воспроизводим остальные позиции
            for i in range(1, len(positions)):
                prev_pos = positions[i-1]
                curr_pos = positions[i]
                
                distance = prev_pos.distance_to(curr_pos)
                
                if distance > 0:
                    duration = (distance / 1000) / speed
                    self.move_to(curr_pos.x, curr_pos.y, duration=max(0.01, duration))
            
            self.logger.info(f"Жест воспроизведен: {gesture_id}")
            return True
        
        except Exception as e:
            self.logger.error(f"Ошибка воспроизведения жеста: {e}")
            return False
    
    def start_recording(self) -> bool:
        """Начать запись событий мыши"""
        self.is_recording = True
        self.recorded_events = []
        self.logger.info("Запись событий мыши начата")
        return True
    
    def stop_recording(self) -> List[MouseEvent]:
        """
        Остановить запись событий мыши
        
        Returns:
            List[MouseEvent]: Записанные события
        """
        self.is_recording = False
        self.logger.info(f"Запись событий мыши остановлена ({len(self.recorded_events)} событий)")
        return self.recorded_events
    
    def save_gesture(self, gesture_id: str, filepath: str) -> bool:
        """
        Сохранить жест в файл
        
        Args:
            gesture_id: ID жеста
            filepath: Путь к файлу
            
        Returns:
            bool: Успешность операции
        """
        if gesture_id not in self.gesture_records:
            return False
        
        try:
            record = self.gesture_records[gesture_id]
            data = {
                'gesture_id': record.gesture_id,
                'gesture_type': record.gesture_type.value,
                'duration': record.duration,
                'positions': [
                    {'x': p.x, 'y': p.y, 'timestamp': p.timestamp.isoformat()}
                    for p in record.positions
                ]
            }
            
            with open(filepath, 'w') as f:
                json.dump(data, f, indent=2)
            
            self.logger.info(f"Жест сохранен: {filepath}")
            return True
        
        except Exception as e:
            self.logger.error(f"Ошибка сохранения жеста: {e}")
            return False
    
    def load_gesture(self, gesture_id: str, filepath: str) -> bool:
        """
        Загрузить жест из файла
        
        Args:
            gesture_id: ID жеста
            filepath: Путь к файлу
            
        Returns:
            bool: Успешность операции
        """
        try:
            with open(filepath, 'r') as f:
                data = json.load(f)
            
            positions = [
                MousePosition(p['x'], p['y'])
                for p in data['positions']
            ]
            
            record = MouseGestureRecord(
                gesture_id=gesture_id,
                gesture_type=MouseGesture[data['gesture_type'].upper()],
                positions=positions,
                duration=data['duration']
            )
            
            self.gesture_records[gesture_id] = record
            self.logger.info(f"Жест загружен: {filepath}")
            return True
        
        except Exception as e:
            self.logger.error(f"Ошибка загрузки жеста: {e}")
            return False
    
    def register_event_callback(self, event_type: str, callback: Callable) -> bool:
        """
        Зарегистрировать callback для события мыши
        
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
    
    def _trigger_event(self, event_type: str, event: MouseEvent) -> None:
        """Вызвать callbacks для события"""
        if self.is_recording:
            self.recorded_events.append(event)
        
        if event_type in self.event_callbacks:
            for callback in self.event_callbacks[event_type]:
                try:
                    callback(event)
                except Exception as e:
                    self.logger.error(f"Ошибка в callback: {e}")
    
    def _detect_gesture_type(self, positions: List[MousePosition]) -> MouseGesture:
        """Определить тип жеста по позициям"""
        if len(positions) < 2:
            return MouseGesture.CLICK
        
        # Простой анализ движения
        total_distance = sum(
            positions[i].distance_to(positions[i+1])
            for i in range(len(positions)-1)
        )
        
        if total_distance < 50:
            return MouseGesture.CLICK
        elif total_distance < 200:
            return MouseGesture.DRAG
        else:
            return MouseGesture.SWIPE
    
    def get_status(self) -> Dict[str, Any]:
        """Получить статус контроллера"""
        return {
            'current_position': {'x': self.current_position.x, 'y': self.current_position.y},
            'is_recording': self.is_recording,
            'recorded_events': len(self.recorded_events),
            'gesture_records': len(self.gesture_records),
            'event_callbacks': len(self.event_callbacks)
        }


# Глобальный экземпляр
_mouse_controller = None


def get_mouse_controller() -> MouseController:
    """Получить контроллер мыши"""
    global _mouse_controller
    if _mouse_controller is None:
        _mouse_controller = MouseController()
    return _mouse_controller

