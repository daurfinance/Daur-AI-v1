#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
Daur-AI: Контроллер сенсорного ввода
Поддержка сенсорных жестов (tap, swipe, pinch, rotate)

Версия: 2.0
Дата: 25.10.2025
Автор: Manus AI
"""

import logging
import time
import math
from typing import Tuple, List, Optional, Dict, Any
from dataclasses import dataclass
from enum import Enum
from datetime import datetime

try:
    import pyautogui
except (ImportError, Exception) as e:
    logging.warning(f"pyautogui not available in touch_controller: {e}")
    # Create mock pyautogui for headless environments
    class MockPyautogui:
        @staticmethod
        def moveTo(x, y, duration=0):
            pass
        @staticmethod
        def click(x, y, clicks=1, button='left'):
            pass
    pyautogui = MockPyautogui()


class TouchGestureType(Enum):
    """Типы сенсорных жестов"""
    TAP = "tap"
    LONG_PRESS = "long_press"
    SWIPE = "swipe"
    PINCH = "pinch"
    ROTATE = "rotate"
    MULTI_TOUCH = "multi_touch"


@dataclass
class TouchPoint:
    """Точка касания"""
    x: int
    y: int
    pressure: float = 1.0
    timestamp: datetime = None
    
    def __post_init__(self):
        if self.timestamp is None:
            self.timestamp = datetime.now()


@dataclass
class TouchGesture:
    """Сенсорный жест"""
    gesture_type: TouchGestureType
    points: List[TouchPoint]
    duration: float = 0.0
    timestamp: datetime = None
    
    def __post_init__(self):
        if self.timestamp is None:
            self.timestamp = datetime.now()


class TouchController:
    """Контроллер сенсорного ввода"""
    
    def __init__(self):
        """Инициализация"""
        self.logger = logging.getLogger('daur_ai.touch_controller')
        self.gesture_history: List[TouchGesture] = []
        self.logger.info("Touch Controller инициализирован")
    
    # ==================== БАЗОВЫЕ ЖЕСТЫ ====================
    
    def tap(self, x: int, y: int, duration: float = 0.1) -> bool:
        """
        Одиночное касание (tap)
        
        Args:
            x: X координата
            y: Y координата
            duration: Длительность касания
            
        Returns:
            bool: Успешность операции
        """
        try:
            pyautogui.moveTo(x, y, duration=0.1)
            pyautogui.mouseDown()
            time.sleep(duration)
            pyautogui.mouseUp()
            
            gesture = TouchGesture(
                TouchGestureType.TAP,
                [TouchPoint(x, y)],
                duration
            )
            self.gesture_history.append(gesture)
            
            self.logger.info(f"Tap в ({x}, {y})")
            return True
        
        except Exception as e:
            self.logger.error(f"Ошибка tap: {e}")
            return False
    
    def long_press(self, x: int, y: int, duration: float = 1.0) -> bool:
        """
        Длительное нажатие (long press)
        
        Args:
            x: X координата
            y: Y координата
            duration: Длительность нажатия
            
        Returns:
            bool: Успешность операции
        """
        try:
            pyautogui.moveTo(x, y, duration=0.1)
            pyautogui.mouseDown()
            time.sleep(duration)
            pyautogui.mouseUp()
            
            gesture = TouchGesture(
                TouchGestureType.LONG_PRESS,
                [TouchPoint(x, y)],
                duration
            )
            self.gesture_history.append(gesture)
            
            self.logger.info(f"Long press в ({x}, {y}) на {duration}с")
            return True
        
        except Exception as e:
            self.logger.error(f"Ошибка long press: {e}")
            return False
    
    # ==================== СВАЙП ====================
    
    def swipe(self, start_x: int, start_y: int, end_x: int, end_y: int,
             duration: float = 0.5) -> bool:
        """
        Свайп (свайп пальцем)
        
        Args:
            start_x: Начальная X координата
            start_y: Начальная Y координата
            end_x: Конечная X координата
            end_y: Конечная Y координата
            duration: Длительность свайпа
            
        Returns:
            bool: Успешность операции
        """
        try:
            pyautogui.moveTo(start_x, start_y, duration=0.1)
            pyautogui.mouseDown()
            pyautogui.moveTo(end_x, end_y, duration=duration)
            pyautogui.mouseUp()
            
            gesture = TouchGesture(
                TouchGestureType.SWIPE,
                [TouchPoint(start_x, start_y), TouchPoint(end_x, end_y)],
                duration
            )
            self.gesture_history.append(gesture)
            
            self.logger.info(f"Свайп от ({start_x}, {start_y}) к ({end_x}, {end_y})")
            return True
        
        except Exception as e:
            self.logger.error(f"Ошибка свайпа: {e}")
            return False
    
    def swipe_up(self, x: int, y: int, distance: int = 100, duration: float = 0.5) -> bool:
        """
        Свайп вверх
        
        Args:
            x: X координата начала
            y: Y координата начала
            distance: Расстояние свайпа
            duration: Длительность
            
        Returns:
            bool: Успешность операции
        """
        return self.swipe(x, y, x, y - distance, duration)
    
    def swipe_down(self, x: int, y: int, distance: int = 100, duration: float = 0.5) -> bool:
        """
        Свайп вниз
        
        Args:
            x: X координата начала
            y: Y координата начала
            distance: Расстояние свайпа
            duration: Длительность
            
        Returns:
            bool: Успешность операции
        """
        return self.swipe(x, y, x, y + distance, duration)
    
    def swipe_left(self, x: int, y: int, distance: int = 100, duration: float = 0.5) -> bool:
        """
        Свайп влево
        
        Args:
            x: X координата начала
            y: Y координата начала
            distance: Расстояние свайпа
            duration: Длительность
            
        Returns:
            bool: Успешность операции
        """
        return self.swipe(x, y, x - distance, y, duration)
    
    def swipe_right(self, x: int, y: int, distance: int = 100, duration: float = 0.5) -> bool:
        """
        Свайп вправо
        
        Args:
            x: X координата начала
            y: Y координата начала
            distance: Расстояние свайпа
            duration: Длительность
            
        Returns:
            bool: Успешность операции
        """
        return self.swipe(x, y, x + distance, y, duration)
    
    # ==================== PINCH ====================
    
    def pinch(self, center_x: int, center_y: int, scale: float = 0.5,
             duration: float = 0.5) -> bool:
        """
        Жест pinch (сжатие двумя пальцами)
        
        Args:
            center_x: X центра pinch
            center_y: Y центра pinch
            scale: Масштаб (0.5 = сжатие вполовину)
            duration: Длительность
            
        Returns:
            bool: Успешность операции
        """
        try:
            # Имитируем pinch через движение мыши
            # Начальные точки (два пальца)
            radius = 50
            
            # Первый палец
            x1_start = center_x - radius
            y1_start = center_y
            x1_end = center_x - int(radius * scale)
            y1_end = center_y
            
            # Второй палец
            x2_start = center_x + radius
            y2_start = center_y
            x2_end = center_x + int(radius * scale)
            y2_end = center_y
            
            # Имитируем pinch движением мыши
            pyautogui.moveTo(x1_start, y1_start, duration=0.1)
            pyautogui.mouseDown()
            
            steps = 10
            for i in range(steps + 1):
                progress = i / steps
                x = x1_start + (x1_end - x1_start) * progress
                y = y1_start + (y1_end - y1_start) * progress
                pyautogui.moveTo(int(x), int(y), duration=duration/steps)
            
            pyautogui.mouseUp()
            
            gesture = TouchGesture(
                TouchGestureType.PINCH,
                [
                    TouchPoint(x1_start, y1_start),
                    TouchPoint(x2_start, y2_start),
                    TouchPoint(x1_end, y1_end),
                    TouchPoint(x2_end, y2_end)
                ],
                duration
            )
            self.gesture_history.append(gesture)
            
            self.logger.info(f"Pinch в ({center_x}, {center_y}) с масштабом {scale}")
            return True
        
        except Exception as e:
            self.logger.error(f"Ошибка pinch: {e}")
            return False
    
    def pinch_in(self, center_x: int, center_y: int, duration: float = 0.5) -> bool:
        """
        Pinch in (сжатие)
        
        Args:
            center_x: X центра
            center_y: Y центра
            duration: Длительность
            
        Returns:
            bool: Успешность операции
        """
        return self.pinch(center_x, center_y, scale=0.3, duration=duration)
    
    def pinch_out(self, center_x: int, center_y: int, duration: float = 0.5) -> bool:
        """
        Pinch out (растягивание)
        
        Args:
            center_x: X центра
            center_y: Y центра
            duration: Длительность
            
        Returns:
            bool: Успешность операции
        """
        return self.pinch(center_x, center_y, scale=1.5, duration=duration)
    
    # ==================== ROTATE ====================
    
    def rotate(self, center_x: int, center_y: int, angle: float = 45,
              duration: float = 0.5) -> bool:
        """
        Жест поворота (rotate)
        
        Args:
            center_x: X центра поворота
            center_y: Y центра поворота
            angle: Угол поворота в градусах
            duration: Длительность
            
        Returns:
            bool: Успешность операции
        """
        try:
            radius = 50
            start_angle = 0
            end_angle = math.radians(angle)
            
            # Начальная позиция
            x_start = center_x + int(radius * math.cos(start_angle))
            y_start = center_y + int(radius * math.sin(start_angle))
            
            pyautogui.moveTo(x_start, y_start, duration=0.1)
            pyautogui.mouseDown()
            
            # Движение по дуге
            steps = 20
            for i in range(steps + 1):
                progress = i / steps
                current_angle = start_angle + (end_angle - start_angle) * progress
                
                x = center_x + int(radius * math.cos(current_angle))
                y = center_y + int(radius * math.sin(current_angle))
                
                pyautogui.moveTo(x, y, duration=duration/steps)
            
            pyautogui.mouseUp()
            
            gesture = TouchGesture(
                TouchGestureType.ROTATE,
                [TouchPoint(x_start, y_start)],
                duration
            )
            self.gesture_history.append(gesture)
            
            self.logger.info(f"Rotate в ({center_x}, {center_y}) на {angle}°")
            return True
        
        except Exception as e:
            self.logger.error(f"Ошибка rotate: {e}")
            return False
    
    # ==================== МУЛЬТИТАЧ ====================
    
    def multi_touch(self, points: List[Tuple[int, int]], duration: float = 0.5) -> bool:
        """
        Мультитач (несколько точек касания)
        
        Args:
            points: Список точек (x, y)
            duration: Длительность
            
        Returns:
            bool: Успешность операции
        """
        try:
            if not points:
                return False
            
            # Имитируем мультитач через движение мыши к каждой точке
            for x, y in points:
                pyautogui.moveTo(x, y, duration=0.1)
                pyautogui.mouseDown()
                time.sleep(duration / len(points))
                pyautogui.mouseUp()
            
            touch_points = [TouchPoint(x, y) for x, y in points]
            gesture = TouchGesture(
                TouchGestureType.MULTI_TOUCH,
                touch_points,
                duration
            )
            self.gesture_history.append(gesture)
            
            self.logger.info(f"Multi-touch с {len(points)} точками")
            return True
        
        except Exception as e:
            self.logger.error(f"Ошибка multi-touch: {e}")
            return False
    
    # ==================== ИСТОРИЯ И СТАТУС ====================
    
    def get_gesture_history(self) -> List[Dict[str, Any]]:
        """Получить историю жестов"""
        return [
            {
                'type': g.gesture_type.value,
                'points': [(p.x, p.y) for p in g.points],
                'duration': g.duration,
                'timestamp': g.timestamp.isoformat()
            }
            for g in self.gesture_history
        ]
    
    def clear_gesture_history(self):
        """Очистить историю жестов"""
        self.gesture_history.clear()
        self.logger.info("История жестов очищена")
    
    def get_status(self) -> Dict[str, Any]:
        """Получить статус контроллера"""
        return {
            'gesture_count': len(self.gesture_history),
            'last_gesture': self.gesture_history[-1].gesture_type.value if self.gesture_history else None,
            'timestamp': datetime.now().isoformat()
        }


# Глобальный экземпляр
_touch_controller = None


def get_touch_controller() -> TouchController:
    """Получить контроллер сенсорного ввода"""
    global _touch_controller
    if _touch_controller is None:
        _touch_controller = TouchController()
    return _touch_controller

