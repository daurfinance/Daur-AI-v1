#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
Daur-AI: Тесты контроллера ввода
Проверяет функциональность модуля управления вводом

Версия: 1.0
Дата: 09.05.2025
"""

import unittest
from unittest.mock import MagicMock, patch

from tests.base import BaseTestCase
from src.input.controller import InputController, MouseButton, KeyModifier


class TestInputController(BaseTestCase):
    """
    Тесты для проверки работы контроллера ввода
    """
    
    def setUp(self):
        """Инициализация перед каждым тестом"""
        super().setUp()
        
        # Патчим pyautogui для предотвращения реального взаимодействия с системой
        self.mock_pyautogui_patcher = patch('src.input.controller.pyautogui')
        self.mock_pyautogui = self.mock_pyautogui_patcher.start()
        
        # Патчим платформо-зависимые обработчики
        self.mock_platform_handler = MagicMock()
        
        # Создаём контроллер ввода для тестов
        self.controller = InputController(os_platform="Windows")
        self.controller.platform_handler = self.mock_platform_handler
    
    def tearDown(self):
        """Очистка после каждого теста"""
        self.mock_pyautogui_patcher.stop()
        super().tearDown()
    
    def test_controller_initialization(self):
        """Проверка корректной инициализации контроллера ввода"""
        # Проверка для Windows
        with patch('src.input.controller.WindowsInputHandler') as mock_win_handler:
            mock_win_handler.return_value = MagicMock()
            win_controller = InputController(os_platform="Windows")
            self.assertIsNotNone(win_controller.platform_handler)
        
        # Проверка для macOS
        with patch('src.input.controller.MacOSInputHandler') as mock_mac_handler:
            mock_mac_handler.return_value = MagicMock()
            mac_controller = InputController(os_platform="Darwin")
            self.assertIsNotNone(mac_controller.platform_handler)
        
        # Проверка для других платформ
        with patch('src.input.controller.DefaultInputHandler') as mock_default_handler:
            mock_default_handler.return_value = MagicMock()
            other_controller = InputController(os_platform="Linux")
            self.assertIsNotNone(other_controller.platform_handler)
    
    def test_mouse_click(self):
        """Проверка функции клика мыши"""
        # Сброс моков
        self.mock_pyautogui.reset_mock()
        
        # Проверка простого клика
        result = self.controller.mouse_click(x=100, y=200)
        self.assertTrue(result)
        
        # Проверка правильного вызова pyautogui
        self.mock_pyautogui.moveTo.assert_called_once_with(100, 200, duration=0.1)
        self.mock_pyautogui.click.assert_called_once_with(button="left", clicks=1, interval=0.1)
        
        # Сброс моков
        self.mock_pyautogui.reset_mock()
        
        # Проверка двойного клика правой кнопкой
        result = self.controller.mouse_click(x=300, y=400, button="right", clicks=2, interval=0.2)
        self.assertTrue(result)
        
        # Проверка правильного вызова pyautogui
        self.mock_pyautogui.moveTo.assert_called_once_with(300, 400, duration=0.1)
        self.mock_pyautogui.click.assert_called_once_with(button="right", clicks=2, interval=0.2)
        
        # Проверка обработки ошибок
        self.mock_pyautogui.click.side_effect = Exception("Test exception")
        result = self.controller.mouse_click(x=100, y=100)
        self.assertFalse(result)
    
    def test_mouse_move(self):
        """Проверка функции перемещения мыши"""
        # Сброс моков
        self.mock_pyautogui.reset_mock()
        
        # Проверка перемещения
        result = self.controller.mouse_move(x=150, y=250, duration=0.3)
        self.assertTrue(result)
        
        # Проверка правильного вызова pyautogui
        self.mock_pyautogui.moveTo.assert_called_once_with(150, 250, duration=0.3)
        
        # Проверка обработки ошибок
        self.mock_pyautogui.moveTo.side_effect = Exception("Test exception")
        result = self.controller.mouse_move(x=100, y=100)
        self.assertFalse(result)
    
    def test_mouse_drag(self):
        """Проверка функции перетаскивания"""
        # Сброс моков
        self.mock_pyautogui.reset_mock()
        
        # Проверка перетаскивания
        result = self.controller.mouse_drag(
            start_x=100, start_y=100, 
            end_x=200, end_y=200, 
            duration=0.5, button="left"
        )
        self.assertTrue(result)
        
        # Проверка правильного вызова pyautogui
        self.mock_pyautogui.moveTo.assert_called_once_with(100, 100, duration=0.1)
        self.mock_pyautogui.dragTo.assert_called_once_with(200, 200, duration=0.5, button="left")
    
    def test_mouse_scroll(self):
        """Проверка функции прокрутки"""
        # Сброс моков
        self.mock_pyautogui.reset_mock()
        
        # Проверка прокрутки вниз
        result = self.controller.mouse_scroll(clicks=3, direction="down")
        self.assertTrue(result)
        self.mock_pyautogui.scroll.assert_called_once_with(-3)
        
        # Сброс моков
        self.mock_pyautogui.reset_mock()
        
        # Проверка прокрутки вверх
        result = self.controller.mouse_scroll(clicks=2, direction="up")
        self.assertTrue(result)
        self.mock_pyautogui.scroll.assert_called_once_with(2)
        
        # Сброс моков
        self.mock_pyautogui.reset_mock()
        
        # Проверка горизонтальной прокрутки
        result = self.controller.mouse_scroll(clicks=1, direction="right")
        self.assertTrue(result)
        self.mock_pyautogui.hscroll.assert_called_once_with(1)
        
        # Проверка с неверным направлением
        result = self.controller.mouse_scroll(clicks=1, direction="invalid")
        self.assertFalse(result)
    
    def test_key_press(self):
        """Проверка функции нажатия клавиши"""
        # Сброс моков
        self.mock_pyautogui.reset_mock()
        
        # Проверка нажатия простой клавиши
        result = self.controller.key_press(key="a")
        self.assertTrue(result)
        self.mock_pyautogui.press.assert_called_once_with("a")
        
        # Сброс моков
        self.mock_pyautogui.reset_mock()
        
        # Проверка нажатия с модификаторами
        result = self.controller.key_press(key="a", modifiers=["ctrl", "alt"])
        self.assertTrue(result)
        # Должен вызывать платформо-зависимый обработчик
        self.mock_platform_handler.press_hotkey.assert_called_once()
    
    def test_type_text(self):
        """Проверка функции ввода текста"""
        # Сброс моков
        self.mock_pyautogui.reset_mock()
        
        # Проверка ввода обычного текста
        result = self.controller.type_text(text="Hello world", interval=0.1)
        self.assertTrue(result)
        self.mock_pyautogui.typewrite.assert_called_once_with("Hello world", interval=0.1)
        
        # Сброс моков
        self.mock_pyautogui.reset_mock()
        
        # Проверка ввода Unicode текста
        result = self.controller.type_text(text="Привет мир")
        self.assertTrue(result)
        # Должен вызывать платформо-зависимый обработчик
        self.mock_platform_handler.type_text.assert_called_once()
    
    def test_hotkey(self):
        """Проверка функции комбинации клавиш"""
        # Сброс моков
        self.mock_pyautogui.reset_mock()
        
        # Проверка обычной комбинации клавиш
        result = self.controller.hotkey(keys=["ctrl", "s"])
        self.assertTrue(result)
        self.mock_pyautogui.hotkey.assert_called_once_with("ctrl", "s")
        
        # Сброс моков
        self.mock_pyautogui.reset_mock()
        
        # Проверка системной комбинации
        result = self.controller.hotkey(keys=["alt", "tab"])
        self.assertTrue(result)
        # Должен вызывать платформо-зависимый обработчик
        self.mock_platform_handler.press_system_hotkey.assert_called_once()
    
    def test_execute_action(self):
        """Проверка выполнения действий через метод execute_action"""
        # Патчим методы контроллера
        with patch.object(self.controller, 'mouse_click') as mock_click, \
             patch.object(self.controller, 'mouse_move') as mock_move, \
             patch.object(self.controller, 'type_text') as mock_type:
            
            # Настройка мок-методов
            mock_click.return_value = True
            mock_move.return_value = True
            mock_type.return_value = True
            
            # Проверка действия клика мышью
            click_action = {
                "action": "input_mouse_click",
                "x": 100,
                "y": 200,
                "button": "left",
                "clicks": 1
            }
            result = self.controller.execute_action(click_action)
            self.assertTrue(result)
            mock_click.assert_called_once_with(
                x=100, y=200, button="left", clicks=1, interval=0.1
            )
            
            # Проверка действия перемещения мыши
            move_action = {
                "action": "input_mouse_move",
                "x": 300,
                "y": 400,
                "duration": 0.5
            }
            result = self.controller.execute_action(move_action)
            self.assertTrue(result)
            mock_move.assert_called_once_with(x=300, y=400, duration=0.5)
            
            # Проверка действия ввода текста
            type_action = {
                "action": "input_type_text",
                "text": "Test text",
                "interval": 0.02
            }
            result = self.controller.execute_action(type_action)
            self.assertTrue(result)
            mock_type.assert_called_once_with(text="Test text", interval=0.02)
            
            # Проверка неизвестного действия
            unknown_action = {
                "action": "unknown_action"
            }
            result = self.controller.execute_action(unknown_action)
            self.assertFalse(result)


if __name__ == '__main__':
    unittest.main()
