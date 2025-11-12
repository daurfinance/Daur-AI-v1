#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
Daur-AI: Модуль экранного распознавания и компьютерного зрения
Анализ экрана, распознавание объектов, OCR и компьютерное зрение

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
import numpy as np
from PIL import Image, ImageDraw, ImageOps
import io


class ObjectType(Enum):
    """Типы объектов на экране"""
    BUTTON = "button"
    TEXT = "text"
    IMAGE = "image"
    WINDOW = "window"
    ICON = "icon"
    MENU = "menu"
    CHECKBOX = "checkbox"
    TEXTFIELD = "textfield"
    DROPDOWN = "dropdown"
    SLIDER = "slider"


@dataclass
class ScreenObject:
    """Объект на экране"""
    object_id: str
    object_type: ObjectType
    x: int
    y: int
    width: int
    height: int
    text: str = ""
    confidence: float = 0.0
    timestamp: datetime = field(default_factory=datetime.now)
    
    @property
    def center(self) -> Tuple[int, int]:
        """Центр объекта"""
        return (self.x + self.width // 2, self.y + self.height // 2)
    
    @property
    def bounds(self) -> Tuple[int, int, int, int]:
        """Границы объекта (x1, y1, x2, y2)"""
        return (self.x, self.y, self.x + self.width, self.y + self.height)


@dataclass
class ScreenAnalysis:
    """Анализ экрана"""
    timestamp: datetime = field(default_factory=datetime.now)
    objects: List[ScreenObject] = field(default_factory=list)
    text_content: str = ""
    dominant_colors: List[Tuple[int, int, int]] = field(default_factory=list)
    brightness: float = 0.0
    contrast: float = 0.0


class ScreenCapture:
    """Захват экрана"""
    
    def __init__(self):
        """Инициализация"""
        self.logger = logging.getLogger('daur_ai.screen_capture')
    
    def capture_screen(self) -> Optional[Image.Image]:
        """
        Захватить экран
        
        Returns:
            Optional[Image.Image]: Изображение экрана
        """
        try:
            import pyautogui
            screenshot = pyautogui.screenshot()
            self.logger.info(f"Экран захвачен: {screenshot.size}")
            return screenshot
        except Exception as e:
            self.logger.error(f"Ошибка захвата экрана: {e}")
            return None
    
    def capture_region(self, x: int, y: int, width: int, height: int) -> Optional[Image.Image]:
        """
        Захватить регион экрана
        
        Args:
            x: X координата
            y: Y координата
            width: Ширина
            height: Высота
            
        Returns:
            Optional[Image.Image]: Изображение региона
        """
        try:
            import pyautogui
            screenshot = pyautogui.screenshot(region=(x, y, width, height))
            self.logger.info(f"Регион захвачен: ({x}, {y}, {width}, {height})")
            return screenshot
        except Exception as e:
            self.logger.error(f"Ошибка захвата региона: {e}")
            return None
    
    def save_screenshot(self, filepath: str) -> bool:
        """
        Сохранить скриншот
        
        Args:
            filepath: Путь к файлу
            
        Returns:
            bool: Успешность операции
        """
        try:
            screenshot = self.capture_screen()
            if screenshot:
                screenshot.save(filepath)
                self.logger.info(f"Скриншот сохранен: {filepath}")
                return True
            return False
        except Exception as e:
            self.logger.error(f"Ошибка сохранения скриншота: {e}")
            return False


class ObjectDetector:
    """Детектор объектов на экране"""
    
    def __init__(self):
        """Инициализация"""
        self.logger = logging.getLogger('daur_ai.object_detector')
    
    def detect_buttons(self, image: Image.Image) -> List[ScreenObject]:
        """
        Обнаружить кнопки на экране
        
        Args:
            image: Изображение
            
        Returns:
            List[ScreenObject]: Обнаруженные кнопки
        """
        buttons = []
        
        try:
            # Простой анализ на основе цвета и формы
            img_array = np.array(image)
            
            # Поиск прямоугольных областей с контрастными границами
            # Это упрощенная версия - в реальности нужно использовать ML модели
            
            self.logger.info(f"Обнаружено кнопок: {len(buttons)}")
            return buttons
        
        except Exception as e:
            self.logger.error(f"Ошибка обнаружения кнопок: {e}")
            return buttons
    
    def detect_text(self, image: Image.Image) -> List[ScreenObject]:
        """
        Обнаружить текст на экране
        
        Args:
            image: Изображение
            
        Returns:
            List[ScreenObject]: Обнаруженный текст
        """
        text_objects = []
        
        try:
            try:
                import pytesseract
                
                # Использование OCR для распознавания текста
                data = pytesseract.image_to_data(image, output_type=pytesseract.Output.DICT)
                
                for i in range(len(data['text'])):
                    if data['text'][i].strip():
                        text_obj = ScreenObject(
                            object_id=f"text_{i}",
                            object_type=ObjectType.TEXT,
                            x=data['left'][i],
                            y=data['top'][i],
                            width=data['width'][i],
                            height=data['height'][i],
                            text=data['text'][i],
                            confidence=data['confidence'][i] / 100.0
                        )
                        text_objects.append(text_obj)
                
                self.logger.info(f"Обнаружено текстовых объектов: {len(text_objects)}")
            
            except ImportError:
                self.logger.warning("pytesseract не установлен, OCR недоступен")
        
        except Exception as e:
            self.logger.error(f"Ошибка обнаружения текста: {e}")
        
        return text_objects
    
    def detect_colors(self, image: Image.Image, num_colors: int = 5) -> List[Tuple[int, int, int]]:
        """
        Обнаружить доминирующие цвета
        
        Args:
            image: Изображение
            num_colors: Количество цветов
            
        Returns:
            List[Tuple]: Доминирующие цвета (RGB)
        """
        try:
            # Уменьшение размера для быстрого анализа
            small_image = image.resize((150, 150))
            pixels = small_image.getdata()
            
            # Простой анализ - получение уникальных цветов
            colors = list(set(pixels))
            colors.sort(key=lambda x: sum(x), reverse=True)
            
            return colors[:num_colors]
        
        except Exception as e:
            self.logger.error(f"Ошибка обнаружения цветов: {e}")
            return []
    
    def find_image(self, haystack: Image.Image, needle: Image.Image,
                  threshold: float = 0.8) -> Optional[Tuple[int, int]]:
        """
        Найти изображение в изображении
        
        Args:
            haystack: Большое изображение
            needle: Маленькое изображение для поиска
            threshold: Порог совпадения (0-1)
            
        Returns:
            Optional[Tuple]: Координаты найденного изображения
        """
        try:
            import pyautogui
            
            # Сохранение временных файлов
            haystack_path = "/tmp/haystack.png"
            needle_path = "/tmp/needle.png"
            
            haystack.save(haystack_path)
            needle.save(needle_path)
            
            # Использование pyautogui для поиска
            location = pyautogui.locateOnScreen(needle_path, confidence=threshold)
            
            if location:
                self.logger.info(f"Изображение найдено: {location}")
                return location
            
            return None
        
        except Exception as e:
            self.logger.error(f"Ошибка поиска изображения: {e}")
            return None


class ScreenAnalyzer:
    """Анализатор экрана"""
    
    def __init__(self):
        """Инициализация"""
        self.logger = logging.getLogger('daur_ai.screen_analyzer')
        self.screen_capture = ScreenCapture()
        self.object_detector = ObjectDetector()
        self.analysis_history: List[ScreenAnalysis] = []
    
    def analyze_screen(self) -> Optional[ScreenAnalysis]:
        """
        Анализировать текущий экран
        
        Returns:
            Optional[ScreenAnalysis]: Результаты анализа
        """
        try:
            screenshot = self.screen_capture.capture_screen()
            if not screenshot:
                return None
            
            analysis = ScreenAnalysis()
            
            # Обнаружение объектов
            text_objects = self.object_detector.detect_text(screenshot)
            buttons = self.object_detector.detect_buttons(screenshot)
            
            analysis.objects = text_objects + buttons
            
            # Анализ цветов
            analysis.dominant_colors = self.object_detector.detect_colors(screenshot)
            
            # Анализ яркости и контраста
            analysis.brightness = self._calculate_brightness(screenshot)
            analysis.contrast = self._calculate_contrast(screenshot)
            
            # Сбор текста
            analysis.text_content = '\n'.join(obj.text for obj in text_objects)
            
            self.analysis_history.append(analysis)
            
            self.logger.info(f"Экран проанализирован: {len(analysis.objects)} объектов")
            return analysis
        
        except Exception as e:
            self.logger.error(f"Ошибка анализа экрана: {e}")
            return None
    
    def find_object_by_text(self, text: str, threshold: float = 0.8) -> Optional[ScreenObject]:
        """
        Найти объект по тексту
        
        Args:
            text: Текст для поиска
            threshold: Порог совпадения
            
        Returns:
            Optional[ScreenObject]: Найденный объект
        """
        analysis = self.analyze_screen()
        if not analysis:
            return None
        
        for obj in analysis.objects:
            if text.lower() in obj.text.lower() and obj.confidence >= threshold:
                return obj
        
        return None
    
    def find_button(self, text: str) -> Optional[ScreenObject]:
        """
        Найти кнопку по тексту
        
        Args:
            text: Текст кнопки
            
        Returns:
            Optional[ScreenObject]: Найденная кнопка
        """
        analysis = self.analyze_screen()
        if not analysis:
            return None
        
        for obj in analysis.objects:
            if obj.object_type == ObjectType.BUTTON and text.lower() in obj.text.lower():
                return obj
        
        return None
    
    def wait_for_object(self, text: str, timeout: float = 10.0) -> Optional[ScreenObject]:
        """
        Ждать появления объекта на экране
        
        Args:
            text: Текст объекта
            timeout: Таймаут в секундах
            
        Returns:
            Optional[ScreenObject]: Найденный объект
        """
        start_time = time.time()
        
        while time.time() - start_time < timeout:
            obj = self.find_object_by_text(text)
            if obj:
                return obj
            time.sleep(0.5)
        
        self.logger.warning(f"Объект не найден за {timeout} секунд: {text}")
        return None
    
    def highlight_object(self, obj: ScreenObject, screenshot: Optional[Image.Image] = None) -> Optional[Image.Image]:
        """
        Выделить объект на скриншоте
        
        Args:
            obj: Объект для выделения
            screenshot: Скриншот (если None, захватывается текущий)
            
        Returns:
            Optional[Image.Image]: Изображение с выделением
        """
        if screenshot is None:
            screenshot = self.screen_capture.capture_screen()
        
        if not screenshot:
            return None
        
        try:
            # Копируем изображение
            highlighted = screenshot.copy()
            draw = ImageDraw.Draw(highlighted)
            
            # Рисуем прямоугольник вокруг объекта
            bounds = obj.bounds
            draw.rectangle(bounds, outline="red", width=3)
            
            # Добавляем текст
            if obj.text:
                draw.text((obj.x, obj.y - 20), obj.text, fill="red")
            
            return highlighted
        
        except Exception as e:
            self.logger.error(f"Ошибка выделения объекта: {e}")
            return None
    
    def _calculate_brightness(self, image: Image.Image) -> float:
        """Рассчитать яркость изображения"""
        try:
            img_array = np.array(image.convert('L'))
            return float(np.mean(img_array)) / 255.0
        except Exception as e:
            return 0.0
    
    def _calculate_contrast(self, image: Image.Image) -> float:
        """Рассчитать контраст изображения"""
        try:
            img_array = np.array(image.convert('L'))
            return float(np.std(img_array)) / 255.0
        except Exception as e:
            return 0.0
    
    def get_status(self) -> Dict[str, Any]:
        """Получить статус анализатора"""
        return {
            'analysis_history': len(self.analysis_history),
            'last_analysis': self.analysis_history[-1].timestamp.isoformat() if self.analysis_history else None
        }


# Глобальный экземпляр
_screen_analyzer = None


def get_screen_analyzer() -> ScreenAnalyzer:
    """Получить анализатор экрана"""
    global _screen_analyzer
    if _screen_analyzer is None:
        _screen_analyzer = ScreenAnalyzer()
    return _screen_analyzer

