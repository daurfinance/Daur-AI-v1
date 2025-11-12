#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
Daur-AI: Расширенный контроллер мыши
Поддержка паттернов, поиска изображений и продвинутых жестов

Версия: 2.0
Дата: 25.10.2025
Автор: Manus AI
"""

import logging
import math
import time
from typing import List, Tuple, Optional, Dict, Any
from dataclasses import dataclass
from enum import Enum
from datetime import datetime

import os
import sys

# Обработка DISPLAY переменной для headless окружения
if not os.environ.get('DISPLAY') and sys.platform != 'win32' and sys.platform != 'darwin':
    try:
        # Попытка использовать виртуальный дисплей
        from pyvirtualdisplay import Display
        _display = Display(visible=0, size=(1920, 1080))
        _display.start()
    except ImportError:
        # Если pyvirtualdisplay недоступен, продолжаем без него
        pass

try:
    import pyautogui
    from PIL import Image
    import numpy as np
    PYAUTOGUI_AVAILABLE = True
except (ImportError, KeyError, Exception) as e:
    PYAUTOGUI_AVAILABLE = False
    logging.warning(f"pyautogui not available: {e}")
    # Для headless окружения создаем mock объекты
    class MockPyautogui:
        @staticmethod
        def moveTo(x, y, duration=0):
            pass
        @staticmethod
        def click(x, y, clicks=1, button='left'):
            pass
        @staticmethod
        def position():
            return (0, 0)
    pyautogui = MockPyautogui()


class PatternType(Enum):
    """Типы паттернов"""
    CIRCLE = "circle"
    SQUARE = "square"
    TRIANGLE = "triangle"
    DIAGONAL = "diagonal"
    ZIGZAG = "zigzag"
    SPIRAL = "spiral"


@dataclass
class MousePattern:
    """Паттерн движения мыши"""
    pattern_type: PatternType
    center_x: int
    center_y: int
    size: int = 100
    duration: float = 1.0
    timestamp: datetime = None
    
    def __post_init__(self):
        if self.timestamp is None:
            self.timestamp = datetime.now()


class AdvancedMouseController:
    """Расширенный контроллер мыши с паттернами и поиском"""
    
    def __init__(self):
        """Инициализация"""
        self.logger = logging.getLogger('daur_ai.advanced_mouse_controller')
        self.pattern_history: List[MousePattern] = []
        self.logger.info("Advanced Mouse Controller инициализирован")
    
    # ==================== ПАТТЕРНЫ ====================
    
    def draw_circle(self, center_x: int, center_y: int, radius: int = 100,
                   duration: float = 1.0) -> bool:
        """
        Нарисовать круг мышкой
        
        Args:
            center_x: X центра круга
            center_y: Y центра круга
            radius: Радиус круга
            duration: Длительность рисования
            
        Returns:
            bool: Успешность операции
        """
        try:
            steps = 36
            step_duration = duration / steps
            
            for i in range(steps + 1):
                angle = (i / steps) * 2 * math.pi
                x = center_x + int(radius * math.cos(angle))
                y = center_y + int(radius * math.sin(angle))
                
                pyautogui.moveTo(x, y, duration=step_duration)
            
            pattern = MousePattern(PatternType.CIRCLE, center_x, center_y, radius, duration)
            self.pattern_history.append(pattern)
            
            self.logger.info(f"Круг нарисован: центр ({center_x}, {center_y}), радиус {radius}")
            return True
        
        except Exception as e:
            self.logger.error(f"Ошибка рисования круга: {e}")
            return False
    
    def draw_square(self, center_x: int, center_y: int, size: int = 100,
                   duration: float = 1.0) -> bool:
        """
        Нарисовать квадрат мышкой
        
        Args:
            center_x: X центра квадрата
            center_y: Y центра квадрата
            size: Размер квадрата
            duration: Длительность рисования
            
        Returns:
            bool: Успешность операции
        """
        try:
            half_size = size // 2
            points = [
                (center_x - half_size, center_y - half_size),
                (center_x + half_size, center_y - half_size),
                (center_x + half_size, center_y + half_size),
                (center_x - half_size, center_y + half_size),
                (center_x - half_size, center_y - half_size)
            ]
            
            step_duration = duration / len(points)
            
            for x, y in points:
                pyautogui.moveTo(x, y, duration=step_duration)
            
            pattern = MousePattern(PatternType.SQUARE, center_x, center_y, size, duration)
            self.pattern_history.append(pattern)
            
            self.logger.info(f"Квадрат нарисован: центр ({center_x}, {center_y}), размер {size}")
            return True
        
        except Exception as e:
            self.logger.error(f"Ошибка рисования квадрата: {e}")
            return False
    
    def draw_triangle(self, center_x: int, center_y: int, size: int = 100,
                     duration: float = 1.0) -> bool:
        """
        Нарисовать треугольник мышкой
        
        Args:
            center_x: X центра треугольника
            center_y: Y центра треугольника
            size: Размер треугольника
            duration: Длительность рисования
            
        Returns:
            bool: Успешность операции
        """
        try:
            # Вершины треугольника
            height = size * math.sqrt(3) / 2
            points = [
                (center_x, center_y - height / 2),  # Верхняя вершина
                (center_x + size / 2, center_y + height / 2),  # Нижняя правая
                (center_x - size / 2, center_y + height / 2),  # Нижняя левая
                (center_x, center_y - height / 2)  # Замыкаем треугольник
            ]
            
            step_duration = duration / len(points)
            
            for x, y in points:
                pyautogui.moveTo(int(x), int(y), duration=step_duration)
            
            pattern = MousePattern(PatternType.TRIANGLE, center_x, center_y, size, duration)
            self.pattern_history.append(pattern)
            
            self.logger.info(f"Треугольник нарисован: центр ({center_x}, {center_y}), размер {size}")
            return True
        
        except Exception as e:
            self.logger.error(f"Ошибка рисования треугольника: {e}")
            return False
    
    def draw_diagonal(self, start_x: int, start_y: int, end_x: int, end_y: int,
                     duration: float = 1.0) -> bool:
        """
        Нарисовать диагональ мышкой
        
        Args:
            start_x: Начальная X координата
            start_y: Начальная Y координата
            end_x: Конечная X координата
            end_y: Конечная Y координата
            duration: Длительность рисования
            
        Returns:
            bool: Успешность операции
        """
        try:
            center_x = (start_x + end_x) // 2
            center_y = (start_y + end_y) // 2
            size = int(math.sqrt((end_x - start_x)**2 + (end_y - start_y)**2))
            
            pyautogui.moveTo(start_x, start_y, duration=0.1)
            pyautogui.moveTo(end_x, end_y, duration=duration)
            
            pattern = MousePattern(PatternType.DIAGONAL, center_x, center_y, size, duration)
            self.pattern_history.append(pattern)
            
            self.logger.info(f"Диагональ нарисована: от ({start_x}, {start_y}) к ({end_x}, {end_y})")
            return True
        
        except Exception as e:
            self.logger.error(f"Ошибка рисования диагонали: {e}")
            return False
    
    def draw_zigzag(self, center_x: int, center_y: int, width: int = 100,
                   height: int = 100, waves: int = 3, duration: float = 1.0) -> bool:
        """
        Нарисовать зигзаг мышкой
        
        Args:
            center_x: X центра зигзага
            center_y: Y центра зигзага
            width: Ширина зигзага
            height: Высота зигзага
            waves: Количество волн
            duration: Длительность рисования
            
        Returns:
            bool: Успешность операции
        """
        try:
            points = []
            step_x = width / (waves * 2)
            
            for i in range(waves * 2 + 1):
                x = center_x - width / 2 + i * step_x
                y = center_y - height / 2 if i % 2 == 0 else center_y + height / 2
                points.append((int(x), int(y)))
            
            step_duration = duration / len(points)
            
            for x, y in points:
                pyautogui.moveTo(x, y, duration=step_duration)
            
            pattern = MousePattern(PatternType.ZIGZAG, center_x, center_y, width, duration)
            self.pattern_history.append(pattern)
            
            self.logger.info(f"Зигзаг нарисован: центр ({center_x}, {center_y}), волн {waves}")
            return True
        
        except Exception as e:
            self.logger.error(f"Ошибка рисования зигзага: {e}")
            return False
    
    def draw_spiral(self, center_x: int, center_y: int, max_radius: int = 100,
                   turns: int = 3, duration: float = 1.0) -> bool:
        """
        Нарисовать спираль мышкой
        
        Args:
            center_x: X центра спирали
            center_y: Y центра спирали
            max_radius: Максимальный радиус спирали
            turns: Количество оборотов
            duration: Длительность рисования
            
        Returns:
            bool: Успешность операции
        """
        try:
            steps = turns * 36
            step_duration = duration / steps
            
            for i in range(steps + 1):
                angle = (i / 36) * 2 * math.pi
                radius = (i / steps) * max_radius
                
                x = center_x + int(radius * math.cos(angle))
                y = center_y + int(radius * math.sin(angle))
                
                pyautogui.moveTo(x, y, duration=step_duration)
            
            pattern = MousePattern(PatternType.SPIRAL, center_x, center_y, max_radius, duration)
            self.pattern_history.append(pattern)
            
            self.logger.info(f"Спираль нарисована: центр ({center_x}, {center_y}), оборотов {turns}")
            return True
        
        except Exception as e:
            self.logger.error(f"Ошибка рисования спирали: {e}")
            return False
    
    # ==================== ПОИСК ИЗОБРАЖЕНИЙ ====================
    
    def find_image_on_screen(self, image_path: str, confidence: float = 0.8) -> Optional[Tuple[int, int]]:
        """
        Найти изображение на экране
        
        Args:
            image_path: Путь к изображению
            confidence: Уровень уверенности (0.0-1.0)
            
        Returns:
            Optional[Tuple]: (x, y) координаты центра найденного изображения
        """
        try:
            location = pyautogui.locateOnScreen(image_path, confidence=confidence)
            
            if location:
                # location = (left, top, width, height)
                center_x = location[0] + location[2] // 2
                center_y = location[1] + location[3] // 2
                
                self.logger.info(f"Изображение найдено: {image_path} на ({center_x}, {center_y})")
                return (center_x, center_y)
            
            self.logger.warning(f"Изображение не найдено: {image_path}")
            return None
        
        except Exception as e:
            self.logger.error(f"Ошибка поиска изображения: {e}")
            return None
    
    def find_and_click_image(self, image_path: str, confidence: float = 0.8,
                            button: str = 'left', clicks: int = 1) -> bool:
        """
        Найти изображение и нажать на него
        
        Args:
            image_path: Путь к изображению
            confidence: Уровень уверенности
            button: Кнопка мыши (left, right, middle)
            clicks: Количество кликов
            
        Returns:
            bool: Успешность операции
        """
        try:
            location = self.find_image_on_screen(image_path, confidence)
            
            if location:
                x, y = location
                pyautogui.moveTo(x, y, duration=0.3)
                pyautogui.click(x, y, clicks=clicks, button=button)
                
                self.logger.info(f"Клик по изображению: {image_path}")
                return True
            
            return False
        
        except Exception as e:
            self.logger.error(f"Ошибка клика по изображению: {e}")
            return False
    
    def find_multiple_images(self, image_path: str, confidence: float = 0.8,
                            limit: int = 5) -> List[Tuple[int, int]]:
        """
        Найти все вхождения изображения на экране
        
        Args:
            image_path: Путь к изображению
            confidence: Уровень уверенности
            limit: Максимальное количество результатов
            
        Returns:
            List: Список координат найденных изображений
        """
        try:
            locations = list(pyautogui.locateAllOnScreen(image_path, confidence=confidence))
            
            results = []
            for location in locations[:limit]:
                center_x = location[0] + location[2] // 2
                center_y = location[1] + location[3] // 2
                results.append((center_x, center_y))
            
            self.logger.info(f"Найдено {len(results)} вхождений изображения: {image_path}")
            return results
        
        except Exception as e:
            self.logger.error(f"Ошибка поиска множественных изображений: {e}")
            return []
    
    def wait_for_image(self, image_path: str, timeout: float = 10.0,
                      confidence: float = 0.8) -> Optional[Tuple[int, int]]:
        """
        Ждать появления изображения на экране
        
        Args:
            image_path: Путь к изображению
            timeout: Таймаут в секундах
            confidence: Уровень уверенности
            
        Returns:
            Optional[Tuple]: Координаты найденного изображения
        """
        try:
            start_time = time.time()
            
            while time.time() - start_time < timeout:
                location = self.find_image_on_screen(image_path, confidence)
                
                if location:
                    self.logger.info(f"Изображение появилось: {image_path}")
                    return location
                
                time.sleep(0.5)
            
            self.logger.warning(f"Таймаут ожидания изображения: {image_path}")
            return None
        
        except Exception as e:
            self.logger.error(f"Ошибка ожидания изображения: {e}")
            return None
    
    # ==================== ПРОДВИНУТЫЕ ЖЕСТЫ ====================
    
    def double_click(self, x: int, y: int, interval: float = 0.1) -> bool:
        """
        Двойной клик
        
        Args:
            x: X координата
            y: Y координата
            interval: Интервал между кликами
            
        Returns:
            bool: Успешность операции
        """
        try:
            pyautogui.moveTo(x, y, duration=0.2)
            pyautogui.click(x, y)
            time.sleep(interval)
            pyautogui.click(x, y)
            
            self.logger.info(f"Двойной клик в ({x}, {y})")
            return True
        
        except Exception as e:
            self.logger.error(f"Ошибка двойного клика: {e}")
            return False
    
    def triple_click(self, x: int, y: int, interval: float = 0.1) -> bool:
        """
        Тройной клик
        
        Args:
            x: X координата
            y: Y координата
            interval: Интервал между кликами
            
        Returns:
            bool: Успешность операции
        """
        try:
            pyautogui.moveTo(x, y, duration=0.2)
            for _ in range(3):
                pyautogui.click(x, y)
                time.sleep(interval)
            
            self.logger.info(f"Тройной клик в ({x}, {y})")
            return True
        
        except Exception as e:
            self.logger.error(f"Ошибка тройного клика: {e}")
            return False
    
    def right_click(self, x: int, y: int) -> bool:
        """
        Правый клик
        
        Args:
            x: X координата
            y: Y координата
            
        Returns:
            bool: Успешность операции
        """
        try:
            pyautogui.moveTo(x, y, duration=0.2)
            pyautogui.click(x, y, button='right')
            
            self.logger.info(f"Правый клик в ({x}, {y})")
            return True
        
        except Exception as e:
            self.logger.error(f"Ошибка правого клика: {e}")
            return False
    
    def middle_click(self, x: int, y: int) -> bool:
        """
        Клик средней кнопкой
        
        Args:
            x: X координата
            y: Y координата
            
        Returns:
            bool: Успешность операции
        """
        try:
            pyautogui.moveTo(x, y, duration=0.2)
            pyautogui.click(x, y, button='middle')
            
            self.logger.info(f"Клик средней кнопкой в ({x}, {y})")
            return True
        
        except Exception as e:
            self.logger.error(f"Ошибка клика средней кнопкой: {e}")
            return False
    
    def get_pattern_history(self) -> List[Dict[str, Any]]:
        """Получить историю паттернов"""
        return [
            {
                'type': p.pattern_type.value,
                'center': (p.center_x, p.center_y),
                'size': p.size,
                'duration': p.duration,
                'timestamp': p.timestamp.isoformat()
            }
            for p in self.pattern_history
        ]
    
    def clear_pattern_history(self):
        """Очистить историю паттернов"""
        self.pattern_history.clear()
        self.logger.info("История паттернов очищена")


# Глобальный экземпляр
_advanced_mouse_controller = None


def get_advanced_mouse_controller() -> AdvancedMouseController:
    """Получить расширенный контроллер мыши"""
    global _advanced_mouse_controller
    if _advanced_mouse_controller is None:
        _advanced_mouse_controller = AdvancedMouseController()
    return _advanced_mouse_controller

