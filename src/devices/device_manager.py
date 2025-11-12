#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
Daur-AI: Интегрированный менеджер управления устройствами
Управление мышкой, клавиатурой, оборудованием и экранным распознаванием

Версия: 2.0
Дата: 25.10.2025
Автор: Manus AI
"""

import logging
from typing import Dict, List, Any, Optional, Tuple
from datetime import datetime
from dataclasses import dataclass, field


@dataclass
class DeviceManagerStatus:
    """Статус менеджера устройств"""
    timestamp: datetime = field(default_factory=datetime.now)
    mouse_active: bool = False
    keyboard_active: bool = False
    hardware_healthy: bool = False
    screen_analyzed: bool = False
    total_devices: int = 0
    active_operations: int = 0


class IntegratedDeviceManager:
    """Интегрированный менеджер управления устройствами"""
    
    def __init__(self):
        """Инициализация"""
        self.logger = logging.getLogger('daur_ai.device_manager')
        
        # Инициализация компонентов
        try:
            from ..input import get_mouse_controller, get_keyboard_controller
            self.mouse = get_mouse_controller()
            self.keyboard = get_keyboard_controller()
        except Exception as e:
            self.logger.warning(f"Ошибка инициализации input модулей: {e}")
            self.mouse = None
            self.keyboard = None
        
        try:
            from ..hardware import get_driver_manager, get_hardware_monitor
            self.driver_manager = get_driver_manager()
            self.hardware_monitor = get_hardware_monitor()
        except Exception as e:
            self.logger.warning(f"Ошибка инициализации hardware модулей: {e}")
            self.driver_manager = None
            self.hardware_monitor = None
        
        try:
            from ..vision import get_screen_analyzer
            self.screen_analyzer = get_screen_analyzer()
        except Exception as e:
            self.logger.warning(f"Ошибка инициализации vision модулей: {e}")
            self.screen_analyzer = None
        
        self.logger.info("Integrated Device Manager инициализирован")
    
    # ==================== УПРАВЛЕНИЕ МЫШКОЙ ====================
    
    def mouse_move(self, x: int, y: int, duration: float = 0.5) -> bool:
        """
        Переместить мышь
        
        Args:
            x: X координата
            y: Y координата
            duration: Длительность движения
            
        Returns:
            bool: Успешность операции
        """
        if not self.mouse:
            self.logger.error("Мышь не инициализирована")
            return False
        
        return self.mouse.move_to(x, y, duration)
    
    def mouse_click(self, x: Optional[int] = None, y: Optional[int] = None,
                   button: str = "left", clicks: int = 1) -> bool:
        """
        Нажать кнопку мыши
        
        Args:
            x: X координата (если None, текущая позиция)
            y: Y координата (если None, текущая позиция)
            button: Кнопка мыши (left, right, middle)
            clicks: Количество нажатий
            
        Returns:
            bool: Успешность операции
        """
        if not self.mouse:
            return False
        
        if x is not None and y is not None:
            self.mouse.move_to(x, y, duration=0.2)
        
        from ..input import MouseButton
        button_map = {
            "left": MouseButton.LEFT,
            "right": MouseButton.RIGHT,
            "middle": MouseButton.MIDDLE
        }
        
        return self.mouse.click(button_map.get(button, MouseButton.LEFT), clicks=clicks)
    
    def mouse_drag(self, start_x: int, start_y: int, end_x: int, end_y: int,
                  duration: float = 0.5) -> bool:
        """
        Перетащить мышь
        
        Args:
            start_x: Начальная X координата
            start_y: Начальная Y координата
            end_x: Конечная X координата
            end_y: Конечная Y координата
            duration: Длительность операции
            
        Returns:
            bool: Успешность операции
        """
        if not self.mouse:
            return False
        
        return self.mouse.drag(start_x, start_y, end_x, end_y, duration)
    
    def mouse_scroll(self, x: int, y: int, direction: str = "down", clicks: int = 3) -> bool:
        """
        Прокрутить колесико мыши
        
        Args:
            x: X координата
            y: Y координата
            direction: Направление (up/down)
            clicks: Количество кликов
            
        Returns:
            bool: Успешность операции
        """
        if not self.mouse:
            return False
        
        return self.mouse.scroll(x, y, clicks, direction)
    
    # ==================== УПРАВЛЕНИЕ КЛАВИАТУРОЙ ====================
    
    def keyboard_press(self, key: str) -> bool:
        """
        Нажать клавишу
        
        Args:
            key: Название клавиши
            
        Returns:
            bool: Успешность операции
        """
        if not self.keyboard:
            return False
        
        return self.keyboard.press_key(key)
    
    def keyboard_type(self, text: str, interval: float = 0.05) -> bool:
        """
        Напечатать текст
        
        Args:
            text: Текст для печати
            interval: Интервал между символами
            
        Returns:
            bool: Успешность операции
        """
        if not self.keyboard:
            return False
        
        return self.keyboard.type_text(text, interval)
    
    def keyboard_hotkey(self, *keys: str) -> bool:
        """
        Нажать комбинацию клавиш
        
        Args:
            *keys: Клавиши для комбинации
            
        Returns:
            bool: Успешность операции
        """
        if not self.keyboard:
            return False
        
        return self.keyboard.hotkey(*keys)
    
    def keyboard_register_hotkey(self, hotkey_id: str, key_combination: str,
                                callback) -> bool:
        """
        Зарегистрировать горячую клавишу
        
        Args:
            hotkey_id: ID горячей клавиши
            key_combination: Комбинация клавиш
            callback: Функция callback
            
        Returns:
            bool: Успешность операции
        """
        if not self.keyboard:
            return False
        
        return self.keyboard.register_hotkey(hotkey_id, key_combination, callback)
    
    # ==================== УПРАВЛЕНИЕ ОБОРУДОВАНИЕМ ====================
    
    def hardware_detect_devices(self) -> List[Dict[str, Any]]:
        """
        Обнаружить устройства
        
        Returns:
            List: Список устройств
        """
        if not self.driver_manager:
            return []
        
        devices = self.driver_manager.detect_devices()
        return [self.driver_manager.get_device_info(d.device_id) for d in devices]
    
    def hardware_get_info(self) -> Dict[str, Any]:
        """
        Получить информацию об оборудовании
        
        Returns:
            Dict: Информация об оборудовании
        """
        if not self.hardware_monitor:
            return {}
        
        info = self.hardware_monitor.get_hardware_info()
        return {
            'cpu_count': info.cpu_count,
            'cpu_percent': info.cpu_percent,
            'ram_total': info.ram_total,
            'ram_used': info.ram_used,
            'ram_percent': info.ram_percent,
            'disk_total': info.disk_total,
            'disk_used': info.disk_used,
            'disk_percent': info.disk_percent
        }
    
    def hardware_check_health(self) -> Dict[str, Any]:
        """
        Проверить здоровье оборудования
        
        Returns:
            Dict: Результаты проверки
        """
        if not self.driver_manager:
            return {}
        
        return self.driver_manager.check_device_health()
    
    # ==================== УПРАВЛЕНИЕ ЭКРАНОМ ====================
    
    def screen_capture(self) -> Optional[Any]:
        """
        Захватить экран
        
        Returns:
            Optional: Изображение экрана
        """
        if not self.screen_analyzer:
            return None
        
        return self.screen_analyzer.screen_capture.capture_screen()
    
    def screen_analyze(self) -> Optional[Dict[str, Any]]:
        """
        Анализировать экран
        
        Returns:
            Optional[Dict]: Результаты анализа
        """
        if not self.screen_analyzer:
            return None
        
        analysis = self.screen_analyzer.analyze_screen()
        if not analysis:
            return None
        
        return {
            'timestamp': analysis.timestamp.isoformat(),
            'objects_count': len(analysis.objects),
            'text_content': analysis.text_content,
            'brightness': analysis.brightness,
            'contrast': analysis.contrast,
            'dominant_colors': analysis.dominant_colors
        }
    
    def screen_find_object(self, text: str) -> Optional[Dict[str, Any]]:
        """
        Найти объект на экране по тексту
        
        Args:
            text: Текст для поиска
            
        Returns:
            Optional[Dict]: Информация об объекте
        """
        if not self.screen_analyzer:
            return None
        
        obj = self.screen_analyzer.find_object_by_text(text)
        if not obj:
            return None
        
        return {
            'object_id': obj.object_id,
            'type': obj.object_type.value,
            'x': obj.x,
            'y': obj.y,
            'width': obj.width,
            'height': obj.height,
            'text': obj.text,
            'confidence': obj.confidence,
            'center': obj.center
        }
    
    def screen_find_button(self, text: str) -> Optional[Dict[str, Any]]:
        """
        Найти кнопку на экране
        
        Args:
            text: Текст кнопки
            
        Returns:
            Optional[Dict]: Информация о кнопке
        """
        if not self.screen_analyzer:
            return None
        
        btn = self.screen_analyzer.find_button(text)
        if not btn:
            return None
        
        return {
            'object_id': btn.object_id,
            'text': btn.text,
            'center': btn.center,
            'bounds': btn.bounds
        }
    
    # ==================== КОМБИНИРОВАННЫЕ ОПЕРАЦИИ ====================
    
    def click_on_text(self, text: str, button: str = "left") -> bool:
        """
        Найти текст на экране и нажать на него
        
        Args:
            text: Текст для поиска
            button: Кнопка мыши
            
        Returns:
            bool: Успешность операции
        """
        obj = self.screen_find_object(text)
        if not obj:
            self.logger.error(f"Объект не найден: {text}")
            return False
        
        center = obj['center']
        return self.mouse_click(center[0], center[1], button)
    
    def click_button(self, text: str) -> bool:
        """
        Найти и нажать кнопку
        
        Args:
            text: Текст кнопки
            
        Returns:
            bool: Успешность операции
        """
        btn = self.screen_find_button(text)
        if not btn:
            self.logger.error(f"Кнопка не найдена: {text}")
            return False
        
        center = btn['center']
        return self.mouse_click(center[0], center[1])
    
    def type_and_press_enter(self, text: str) -> bool:
        """
        Напечатать текст и нажать Enter
        
        Args:
            text: Текст для печати
            
        Returns:
            bool: Успешность операции
        """
        success = self.keyboard_type(text)
        if success:
            success = self.keyboard_press('enter')
        
        return success
    
    # ==================== СТАТУС И ДИАГНОСТИКА ====================
    
    def get_status(self) -> DeviceManagerStatus:
        """
        Получить статус менеджера
        
        Returns:
            DeviceManagerStatus: Статус менеджера
        """
        status = DeviceManagerStatus()
        
        if self.mouse:
            status.mouse_active = True
        
        if self.keyboard:
            status.keyboard_active = True
        
        if self.hardware_monitor:
            health = self.hardware_check_health()
            status.hardware_healthy = health.get('overall_status') == 'healthy'
        
        if self.screen_analyzer:
            status.screen_analyzed = True
        
        return status
    
    def get_full_status(self) -> Dict[str, Any]:
        """
        Получить полный статус системы
        
        Returns:
            Dict: Полный статус
        """
        return {
            'timestamp': datetime.now().isoformat(),
            'device_manager': self.get_status().__dict__,
            'hardware': self.hardware_get_info(),
            'health': self.hardware_check_health()
        }
    
    def health_check(self) -> Dict[str, Any]:
        """
        Проверить здоровье системы
        
        Returns:
            Dict: Результаты проверки
        """
        checks = {
            'timestamp': datetime.now().isoformat(),
            'components': {
                'mouse': self.mouse is not None,
                'keyboard': self.keyboard is not None,
                'hardware': self.hardware_monitor is not None,
                'screen': self.screen_analyzer is not None
            },
            'hardware_health': self.hardware_check_health()
        }
        
        return checks


# Глобальный экземпляр
_device_manager = None


def get_device_manager() -> IntegratedDeviceManager:
    """Получить менеджер устройств"""
    global _device_manager
    if _device_manager is None:
        _device_manager = IntegratedDeviceManager()
    return _device_manager

