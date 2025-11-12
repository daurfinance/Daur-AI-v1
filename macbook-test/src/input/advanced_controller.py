#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
Daur-AI: Продвинутый контроллер ввода
Реальное управление мышью, клавиатурой и экраном через pyautogui

Версия: 1.1
Дата: 01.10.2025
"""

import logging
import time
import os
import cv2
import numpy as np
from typing import Dict, List, Any, Optional, Tuple, Union
from dataclasses import dataclass
import threading
import queue

try:
    # Проверяем наличие DISPLAY для GUI приложений
    if os.getenv('DISPLAY') is None:
        # В headless режиме отключаем GUI зависимости
        ADVANCED_AVAILABLE = False
        import_error = "Headless режим: DISPLAY не установлен"
    else:
        import pyautogui
        import pynput
        from pynput import mouse, keyboard
        ADVANCED_AVAILABLE = True
except ImportError as e:
    ADVANCED_AVAILABLE = False
    import_error = str(e)
except Exception as e:
    ADVANCED_AVAILABLE = False
    import_error = f"Ошибка инициализации GUI: {str(e)}"


@dataclass
class ClickTarget:
    """Цель для клика"""
    x: int = 0
    y: int = 0
    button: str = "left"  # left, right, middle
    clicks: int = 1
    interval: float = 0.0


@dataclass
class ScreenRegion:
    """Регион экрана"""
    x: int
    y: int
    width: int
    height: int


class AdvancedInputController:
    """
    Продвинутый контроллер ввода с реальным управлением системой
    """
    
    def __init__(self, platform: str = "Linux"):
        """
        Инициализация контроллера
        
        Args:
            platform (str): Платформа (Linux, Windows, Darwin)
        """
        self.logger = logging.getLogger('daur_ai.advanced_input')
        self.platform = platform
        
        if not ADVANCED_AVAILABLE:
            raise ImportError(f"Продвинутый контроллер недоступен: {import_error}")
        
        # Настройка pyautogui
        pyautogui.FAILSAFE = True  # Защита от случайного управления
        pyautogui.PAUSE = 0.1  # Пауза между действиями
        
        # Отключаем fail-safe для headless режима
        if os.getenv('DISPLAY') is None:
            self.logger.warning("Headless режим обнаружен, отключаю fail-safe")
            pyautogui.FAILSAFE = False
        
        # Получение размеров экрана
        try:
            self.screen_width, self.screen_height = pyautogui.size()
            self.logger.info(f"Размер экрана: {self.screen_width}x{self.screen_height}")
        except Exception as e:
            self.logger.warning(f"Не удалось получить размер экрана: {e}")
            self.screen_width, self.screen_height = 1920, 1080
        
        # Мониторинг событий
        self.monitoring = False
        self.event_queue = queue.Queue()
        self.mouse_listener = None
        self.keyboard_listener = None
        
        # Кэш скриншотов
        self.screenshot_cache = {}
        self.cache_timeout = 5  # секунд
        
        self.logger.info(f"Продвинутый контроллер ввода инициализирован для {platform}")
    
    def get_screen_size(self) -> Tuple[int, int]:
        """
        Получение размера экрана
        
        Returns:
            Tuple[int, int]: Ширина и высота экрана
        """
        return self.screen_width, self.screen_height
    
    def get_mouse_position(self) -> Tuple[int, int]:
        """
        Получение текущей позиции мыши
        
        Returns:
            Tuple[int, int]: Координаты x, y
        """
        try:
            return pyautogui.position()
        except Exception as e:
            self.logger.error(f"Ошибка получения позиции мыши: {e}")
            return (0, 0)
    
    def move_mouse(self, x: int, y: int, duration: float = 0.5) -> bool:
        """
        Перемещение мыши в указанную позицию
        
        Args:
            x (int): Координата X
            y (int): Координата Y
            duration (float): Длительность перемещения в секундах
            
        Returns:
            bool: Успешность операции
        """
        try:
            self.logger.debug(f"Перемещение мыши в ({x}, {y})")
            pyautogui.moveTo(x, y, duration=duration)
            return True
        except Exception as e:
            self.logger.error(f"Ошибка перемещения мыши: {e}")
            return False
    
    def click(self, x: int = None, y: int = None, button: str = "left", 
              clicks: int = 1, interval: float = 0.0) -> bool:
        """
        Клик мышью
        
        Args:
            x (int): Координата X (None для текущей позиции)
            y (int): Координата Y (None для текущей позиции)
            button (str): Кнопка мыши (left, right, middle)
            clicks (int): Количество кликов
            interval (float): Интервал между кликами
            
        Returns:
            bool: Успешность операции
        """
        try:
            if x is not None and y is not None:
                self.logger.debug(f"Клик в ({x}, {y}), кнопка: {button}")
                pyautogui.click(x, y, clicks=clicks, interval=interval, button=button)
            else:
                self.logger.debug(f"Клик в текущей позиции, кнопка: {button}")
                pyautogui.click(clicks=clicks, interval=interval, button=button)
            return True
        except Exception as e:
            self.logger.error(f"Ошибка клика: {e}")
            return False
    
    def drag(self, start_x: int, start_y: int, end_x: int, end_y: int, 
             duration: float = 1.0, button: str = "left") -> bool:
        """
        Перетаскивание мышью
        
        Args:
            start_x (int): Начальная координата X
            start_y (int): Начальная координата Y
            end_x (int): Конечная координата X
            end_y (int): Конечная координата Y
            duration (float): Длительность перетаскивания
            button (str): Кнопка мыши
            
        Returns:
            bool: Успешность операции
        """
        try:
            self.logger.debug(f"Перетаскивание от ({start_x}, {start_y}) до ({end_x}, {end_y})")
            pyautogui.drag(end_x - start_x, end_y - start_y, 
                          duration=duration, button=button)
            return True
        except Exception as e:
            self.logger.error(f"Ошибка перетаскивания: {e}")
            return False
    
    def scroll(self, x: int, y: int, clicks: int) -> bool:
        """
        Прокрутка колесом мыши
        
        Args:
            x (int): Координата X
            y (int): Координата Y
            clicks (int): Количество кликов (положительное - вверх, отрицательное - вниз)
            
        Returns:
            bool: Успешность операции
        """
        try:
            self.logger.debug(f"Прокрутка в ({x}, {y}), кликов: {clicks}")
            pyautogui.scroll(clicks, x=x, y=y)
            return True
        except Exception as e:
            self.logger.error(f"Ошибка прокрутки: {e}")
            return False
    
    def type_text(self, text: str, interval: float = 0.01) -> bool:
        """
        Ввод текста
        
        Args:
            text (str): Текст для ввода
            interval (float): Интервал между символами
            
        Returns:
            bool: Успешность операции
        """
        try:
            self.logger.debug(f"Ввод текста: {text[:50]}...")
            pyautogui.typewrite(text, interval=interval)
            return True
        except Exception as e:
            self.logger.error(f"Ошибка ввода текста: {e}")
            return False
    
    def press_key(self, key: str, presses: int = 1, interval: float = 0.0) -> bool:
        """
        Нажатие клавиши
        
        Args:
            key (str): Название клавиши
            presses (int): Количество нажатий
            interval (float): Интервал между нажатиями
            
        Returns:
            bool: Успешность операции
        """
        try:
            self.logger.debug(f"Нажатие клавиши: {key}")
            pyautogui.press(key, presses=presses, interval=interval)
            return True
        except Exception as e:
            self.logger.error(f"Ошибка нажатия клавиши: {e}")
            return False
    
    def key_combination(self, *keys) -> bool:
        """
        Комбинация клавиш
        
        Args:
            *keys: Список клавиш для одновременного нажатия
            
        Returns:
            bool: Успешность операции
        """
        try:
            self.logger.debug(f"Комбинация клавиш: {'+'.join(keys)}")
            pyautogui.hotkey(*keys)
            return True
        except Exception as e:
            self.logger.error(f"Ошибка комбинации клавиш: {e}")
            return False
    
    def take_screenshot(self, region: ScreenRegion = None) -> Optional[np.ndarray]:
        """
        Создание скриншота
        
        Args:
            region (ScreenRegion): Регион для скриншота (None для всего экрана)
            
        Returns:
            Optional[np.ndarray]: Изображение в формате OpenCV
        """
        try:
            if region:
                self.logger.debug(f"Скриншот региона: {region}")
                screenshot = pyautogui.screenshot(region=(region.x, region.y, 
                                                        region.width, region.height))
            else:
                self.logger.debug("Скриншот всего экрана")
                screenshot = pyautogui.screenshot()
            
            # Конвертация в OpenCV формат
            screenshot_cv = cv2.cvtColor(np.array(screenshot), cv2.COLOR_RGB2BGR)
            return screenshot_cv
            
        except Exception as e:
            self.logger.error(f"Ошибка создания скриншота: {e}")
            return None
    
    def find_image_on_screen(self, template_path: str, confidence: float = 0.8,
                           region: ScreenRegion = None) -> Optional[Tuple[int, int]]:
        """
        Поиск изображения на экране
        
        Args:
            template_path (str): Путь к шаблону изображения
            confidence (float): Уровень совпадения (0.0-1.0)
            region (ScreenRegion): Регион поиска
            
        Returns:
            Optional[Tuple[int, int]]: Координаты центра найденного изображения
        """
        try:
            if region:
                result = pyautogui.locateOnScreen(template_path, confidence=confidence,
                                                region=(region.x, region.y, 
                                                       region.width, region.height))
            else:
                result = pyautogui.locateOnScreen(template_path, confidence=confidence)
            
            if result:
                center = pyautogui.center(result)
                self.logger.debug(f"Изображение найдено в {center}")
                return center
            else:
                self.logger.debug("Изображение не найдено")
                return None
                
        except Exception as e:
            self.logger.error(f"Ошибка поиска изображения: {e}")
            return None
    
    def find_text_on_screen(self, text: str, region: ScreenRegion = None) -> List[Tuple[int, int]]:
        """
        Поиск текста на экране (требует OCR)
        
        Args:
            text (str): Текст для поиска
            region (ScreenRegion): Регион поиска
            
        Returns:
            List[Tuple[int, int]]: Список координат найденного текста
        """
        try:
            # Создаем скриншот
            screenshot = self.take_screenshot(region)
            if screenshot is None:
                return []
            
            # Здесь можно добавить OCR с помощью pytesseract
            # Пока возвращаем пустой список
            self.logger.warning("OCR поиск текста не реализован")
            return []
            
        except Exception as e:
            self.logger.error(f"Ошибка поиска текста: {e}")
            return []
    
    def wait_for_image(self, template_path: str, timeout: float = 10.0,
                      confidence: float = 0.8) -> Optional[Tuple[int, int]]:
        """
        Ожидание появления изображения на экране
        
        Args:
            template_path (str): Путь к шаблону
            timeout (float): Таймаут в секундах
            confidence (float): Уровень совпадения
            
        Returns:
            Optional[Tuple[int, int]]: Координаты найденного изображения
        """
        start_time = time.time()
        
        while time.time() - start_time < timeout:
            result = self.find_image_on_screen(template_path, confidence)
            if result:
                return result
            time.sleep(0.5)
        
        self.logger.warning(f"Изображение не найдено за {timeout} секунд")
        return None
    
    def start_monitoring(self):
        """Запуск мониторинга событий мыши и клавиатуры"""
        if self.monitoring:
            return
        
        self.monitoring = True
        
        def on_mouse_event(x, y, button, pressed):
            if self.monitoring:
                self.event_queue.put({
                    'type': 'mouse',
                    'x': x, 'y': y,
                    'button': str(button),
                    'pressed': pressed,
                    'timestamp': time.time()
                })
        
        def on_keyboard_event(key):
            if self.monitoring:
                try:
                    key_name = key.char
                except AttributeError:
                    key_name = str(key)
                
                self.event_queue.put({
                    'type': 'keyboard',
                    'key': key_name,
                    'timestamp': time.time()
                })
        
        # Запуск слушателей
        self.mouse_listener = mouse.Listener(on_click=on_mouse_event)
        self.keyboard_listener = keyboard.Listener(on_press=on_keyboard_event)
        
        self.mouse_listener.start()
        self.keyboard_listener.start()
        
        self.logger.info("Мониторинг событий запущен")
    
    def stop_monitoring(self):
        """Остановка мониторинга событий"""
        self.monitoring = False
        
        if self.mouse_listener:
            self.mouse_listener.stop()
        if self.keyboard_listener:
            self.keyboard_listener.stop()
        
        self.logger.info("Мониторинг событий остановлен")
    
    def get_events(self) -> List[Dict[str, Any]]:
        """
        Получение накопленных событий
        
        Returns:
            List[Dict]: Список событий
        """
        events = []
        while not self.event_queue.empty():
            try:
                events.append(self.event_queue.get_nowait())
            except queue.Empty:
                break
        return events
    
    def execute_action(self, action: Dict[str, Any]) -> bool:
        """
        Выполнение действия ввода
        
        Args:
            action (Dict): Описание действия
            
        Returns:
            bool: Успешность выполнения
        """
        action_type = action.get('action')
        params = action.get('params', {})
        
        try:
            if action_type == 'input_click':
                x = params.get('x')
                y = params.get('y')
                button = params.get('button', 'left')
                clicks = params.get('clicks', 1)
                
                # Если координаты не указаны, пытаемся найти по описанию
                if x is None or y is None:
                    target = params.get('target', '')
                    if target:
                        # Здесь можно добавить поиск элементов по описанию
                        self.logger.warning(f"Поиск элемента '{target}' не реализован")
                        return False
                
                return self.click(x, y, button, clicks)
            
            elif action_type == 'input_type':
                text = params.get('text', '')
                interval = params.get('interval', 0.01)
                return self.type_text(text, interval)
            
            elif action_type == 'input_key':
                key = params.get('key', '')
                presses = params.get('presses', 1)
                return self.press_key(key, presses)
            
            elif action_type == 'input_hotkey':
                keys = params.get('keys', [])
                return self.key_combination(*keys)
            
            elif action_type == 'input_drag':
                start_x = params.get('start_x', 0)
                start_y = params.get('start_y', 0)
                end_x = params.get('end_x', 0)
                end_y = params.get('end_y', 0)
                duration = params.get('duration', 1.0)
                return self.drag(start_x, start_y, end_x, end_y, duration)
            
            elif action_type == 'input_scroll':
                x = params.get('x', 0)
                y = params.get('y', 0)
                clicks = params.get('clicks', 1)
                return self.scroll(x, y, clicks)
            
            elif action_type == 'input_screenshot':
                region_params = params.get('region')
                region = None
                if region_params:
                    region = ScreenRegion(**region_params)
                
                screenshot = self.take_screenshot(region)
                return screenshot is not None
            
            else:
                self.logger.warning(f"Неизвестный тип действия: {action_type}")
                return False
                
        except Exception as e:
            self.logger.error(f"Ошибка выполнения действия {action_type}: {e}")
            return False
    
    def cleanup(self):
        """Очистка ресурсов"""
        self.logger.info("Очистка продвинутого контроллера ввода")
        self.stop_monitoring()


def create_input_controller(platform: str = "Linux") -> Union['AdvancedInputController', 'SimpleInputController']:
    """
    Фабричная функция для создания контроллера ввода
    
    Args:
        platform (str): Платформа
        
    Returns:
        Union[AdvancedInputController, SimpleInputController]: Экземпляр контроллера
    """
    try:
        if ADVANCED_AVAILABLE:
            return AdvancedInputController(platform)
        else:
            # Fallback к упрощенному контроллеру
            from src.input.simple_controller import SimpleInputController
            return SimpleInputController(platform)
    except Exception as e:
        # Fallback к упрощенному контроллеру
        from src.input.simple_controller import SimpleInputController
        return SimpleInputController(platform)
