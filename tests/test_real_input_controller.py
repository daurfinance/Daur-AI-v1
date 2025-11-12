"""
Unit tests for RealInputController
Полные тесты для модуля управления вводом
"""

import unittest
import os
import sys
import json
import tempfile
from unittest.mock import Mock, patch, MagicMock
import time

# Добавляем путь к src
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

from src.input.real_input_controller import (
    RealMouseController,
    RealKeyboardController,
    RealInputManager,
    MouseEvent,
    KeyboardEvent,
    MouseButton
)


class TestMouseEvent(unittest.TestCase):
    """Тесты для MouseEvent"""
    
    def test_mouse_event_creation(self):
        """Тест создания события мыши"""
        event = MouseEvent(
            timestamp="2025-10-25T10:00:00",
            event_type="click",
            x=100,
            y=200,
            button="left"
        )
        
        self.assertEqual(event.x, 100)
        self.assertEqual(event.y, 200)
        self.assertEqual(event.button, "left")
        self.assertEqual(event.event_type, "click")
    
    def test_mouse_event_to_dict(self):
        """Тест преобразования события в словарь"""
        event = MouseEvent(
            timestamp="2025-10-25T10:00:00",
            event_type="move",
            x=50,
            y=75
        )
        
        event_dict = event.to_dict()
        self.assertIsInstance(event_dict, dict)
        self.assertEqual(event_dict['x'], 50)
        self.assertEqual(event_dict['y'], 75)


class TestKeyboardEvent(unittest.TestCase):
    """Тесты для KeyboardEvent"""
    
    def test_keyboard_event_creation(self):
        """Тест создания события клавиатуры"""
        event = KeyboardEvent(
            timestamp="2025-10-25T10:00:00",
            event_type="press",
            key="a"
        )
        
        self.assertEqual(event.key, "a")
        self.assertEqual(event.event_type, "press")
    
    def test_keyboard_event_to_dict(self):
        """Тест преобразования события в словарь"""
        event = KeyboardEvent(
            timestamp="2025-10-25T10:00:00",
            event_type="type",
            key="hello"
        )
        
        event_dict = event.to_dict()
        self.assertIsInstance(event_dict, dict)
        self.assertEqual(event_dict['key'], "hello")


class TestRealMouseController(unittest.TestCase):
    """Тесты для RealMouseController"""
    
    def setUp(self):
        """Подготовка к тестам"""
        self.mouse = RealMouseController()
    
    def tearDown(self):
        """Очистка после тестов"""
        self.mouse.cleanup()
    
    @patch('pyautogui.moveTo')
    def test_move_to(self, mock_move):
        """Тест движения мыши"""
        result = self.mouse.move_to(100, 200, duration=0.5)
        
        self.assertTrue(result)
        mock_move.assert_called_once_with(100, 200, duration=0.5)
        self.assertEqual(len(self.mouse.history), 1)
        self.assertEqual(self.mouse.history[0].event_type, "move")
    
    @patch('pyautogui.click')
    @patch('pyautogui.moveTo')
    def test_click(self, mock_move, mock_click):
        """Тест клика мыши"""
        result = self.mouse.click(100, 200, button="left")
        
        self.assertTrue(result)
        mock_move.assert_called()
        mock_click.assert_called()
        self.assertEqual(len(self.mouse.history), 2)  # move + click
    
    @patch('pyautogui.click')
    @patch('pyautogui.moveTo')
    def test_double_click(self, mock_move, mock_click):
        """Тест двойного клика"""
        result = self.mouse.double_click(100, 200)
        
        self.assertTrue(result)
        self.assertEqual(mock_click.call_count, 2)
    
    @patch('pyautogui.click')
    @patch('pyautogui.moveTo')
    def test_right_click(self, mock_move, mock_click):
        """Тест правого клика"""
        result = self.mouse.right_click(100, 200)
        
        self.assertTrue(result)
        mock_click.assert_called()
    
    @patch('pyautogui.scroll')
    @patch('pyautogui.moveTo')
    def test_scroll(self, mock_move, mock_scroll):
        """Тест прокрутки колесика"""
        result = self.mouse.scroll(100, 200, direction="down", amount=3)
        
        self.assertTrue(result)
        mock_scroll.assert_called()
        self.assertEqual(len(self.mouse.history), 2)  # move + scroll
    
    @patch('pyautogui.drag')
    @patch('pyautogui.moveTo')
    def test_drag(self, mock_move, mock_drag):
        """Тест перетаскивания"""
        result = self.mouse.drag(100, 200, 300, 400, duration=0.5)
        
        self.assertTrue(result)
        mock_move.assert_called()
        mock_drag.assert_called()
        self.assertEqual(len(self.mouse.history), 1)
    
    @patch('pyautogui.position', return_value=(100, 200))
    def test_get_position(self, mock_position):
        """Тест получения позиции мыши"""
        pos = self.mouse.get_position()
        
        self.assertEqual(pos, (100, 200))
    
    def test_recording(self):
        """Тест записи жестов"""
        self.mouse.start_recording()
        self.assertTrue(self.mouse.recording)
        
        # Добавляем событие вручную
        event = MouseEvent(
            timestamp="2025-10-25T10:00:00",
            event_type="click",
            x=100,
            y=200
        )
        self.mouse._emit_event(event)
        
        events = self.mouse.stop_recording()
        self.assertFalse(self.mouse.recording)
        self.assertEqual(len(events), 1)
    
    def test_save_and_load_events(self):
        """Тест сохранения и загрузки событий"""
        # Добавляем события
        event1 = MouseEvent(
            timestamp="2025-10-25T10:00:00",
            event_type="move",
            x=100,
            y=200
        )
        event2 = MouseEvent(
            timestamp="2025-10-25T10:00:01",
            event_type="click",
            x=100,
            y=200,
            button="left"
        )
        
        self.mouse.history = [event1, event2]
        
        # Сохраняем в временный файл
        with tempfile.NamedTemporaryFile(mode='w', delete=False, suffix='.json') as f:
            temp_file = f.name
        
        try:
            # Сохраняем
            result = self.mouse.save_events(temp_file)
            self.assertTrue(result)
            self.assertTrue(os.path.exists(temp_file))
            
            # Загружаем
            loaded_events = self.mouse.load_events(temp_file)
            self.assertEqual(len(loaded_events), 2)
            self.assertEqual(loaded_events[0].event_type, "move")
            self.assertEqual(loaded_events[1].event_type, "click")
        finally:
            if os.path.exists(temp_file):
                os.remove(temp_file)
    
    def test_listeners(self):
        """Тест слушателей событий"""
        callback = Mock()
        self.mouse.add_listener(callback)
        
        event = MouseEvent(
            timestamp="2025-10-25T10:00:00",
            event_type="click",
            x=100,
            y=200
        )
        
        self.mouse._emit_event(event)
        callback.assert_called_once()
    
    def test_get_history(self):
        """Тест получения истории"""
        # Добавляем события
        for i in range(10):
            event = MouseEvent(
                timestamp=f"2025-10-25T10:00:{i:02d}",
                event_type="move",
                x=i * 10,
                y=i * 10
            )
            self.mouse.history.append(event)
        
        # Получаем последние 5
        history = self.mouse.get_history(limit=5)
        self.assertEqual(len(history), 5)
        self.assertEqual(history[0].x, 50)
    
    def test_clear_history(self):
        """Тест очистки истории"""
        event = MouseEvent(
            timestamp="2025-10-25T10:00:00",
            event_type="move",
            x=100,
            y=200
        )
        self.mouse.history.append(event)
        
        self.assertEqual(len(self.mouse.history), 1)
        self.mouse.clear_history()
        self.assertEqual(len(self.mouse.history), 0)


class TestRealKeyboardController(unittest.TestCase):
    """Тесты для RealKeyboardController"""
    
    def setUp(self):
        """Подготовка к тестам"""
        self.keyboard = RealKeyboardController()
    
    def tearDown(self):
        """Очистка после тестов"""
        self.keyboard.cleanup()
    
    @patch('pynput.keyboard.Controller.type')
    def test_type_text(self, mock_type):
        """Тест печати текста"""
        result = self.keyboard.type_text("hello", interval=0.05)
        
        self.assertTrue(result)
        self.assertEqual(mock_type.call_count, 5)  # 5 символов
        self.assertEqual(len(self.keyboard.history), 1)
    
    @patch('pynput.keyboard.Controller.press')
    @patch('pynput.keyboard.Controller.release')
    def test_press_key(self, mock_release, mock_press):
        """Тест нажатия клавиши"""
        result = self.keyboard.press_key("enter")
        
        self.assertTrue(result)
        mock_press.assert_called()
        mock_release.assert_called()
        self.assertEqual(len(self.keyboard.history), 1)
    
    @patch('pynput.keyboard.Controller.press')
    @patch('pynput.keyboard.Controller.release')
    def test_hotkey(self, mock_release, mock_press):
        """Тест комбинации клавиш"""
        result = self.keyboard.hotkey("ctrl", "c")
        
        self.assertTrue(result)
        self.assertEqual(mock_press.call_count, 2)
        self.assertEqual(mock_release.call_count, 2)
        self.assertEqual(len(self.keyboard.history), 1)
    
    def test_recording(self):
        """Тест записи нажатий"""
        self.keyboard.start_recording()
        self.assertTrue(self.keyboard.recording)
        
        event = KeyboardEvent(
            timestamp="2025-10-25T10:00:00",
            event_type="press",
            key="a"
        )
        self.keyboard._emit_event(event)
        
        events = self.keyboard.stop_recording()
        self.assertFalse(self.keyboard.recording)
        self.assertEqual(len(events), 1)
    
    def test_save_and_load_events(self):
        """Тест сохранения и загрузки событий"""
        event1 = KeyboardEvent(
            timestamp="2025-10-25T10:00:00",
            event_type="press",
            key="a"
        )
        event2 = KeyboardEvent(
            timestamp="2025-10-25T10:00:01",
            event_type="type",
            key="hello"
        )
        
        self.keyboard.history = [event1, event2]
        
        with tempfile.NamedTemporaryFile(mode='w', delete=False, suffix='.json') as f:
            temp_file = f.name
        
        try:
            result = self.keyboard.save_events(temp_file)
            self.assertTrue(result)
            
            loaded_events = self.keyboard.load_events(temp_file)
            self.assertEqual(len(loaded_events), 2)
            self.assertEqual(loaded_events[0].key, "a")
            self.assertEqual(loaded_events[1].key, "hello")
        finally:
            if os.path.exists(temp_file):
                os.remove(temp_file)
    
    def test_get_history(self):
        """Тест получения истории"""
        for i in range(10):
            event = KeyboardEvent(
                timestamp=f"2025-10-25T10:00:{i:02d}",
                event_type="press",
                key=chr(97 + i)  # a, b, c, ...
            )
            self.keyboard.history.append(event)
        
        history = self.keyboard.get_history(limit=5)
        self.assertEqual(len(history), 5)
    
    def test_clear_history(self):
        """Тест очистки истории"""
        event = KeyboardEvent(
            timestamp="2025-10-25T10:00:00",
            event_type="press",
            key="a"
        )
        self.keyboard.history.append(event)
        
        self.assertEqual(len(self.keyboard.history), 1)
        self.keyboard.clear_history()
        self.assertEqual(len(self.keyboard.history), 0)


class TestRealInputManager(unittest.TestCase):
    """Тесты для RealInputManager"""
    
    def setUp(self):
        """Подготовка к тестам"""
        self.manager = RealInputManager()
    
    def tearDown(self):
        """Очистка после тестов"""
        self.manager.cleanup()
    
    def test_initialization(self):
        """Тест инициализации менеджера"""
        self.assertIsNotNone(self.manager.mouse)
        self.assertIsNotNone(self.manager.keyboard)
        self.assertIsInstance(self.manager.mouse, RealMouseController)
        self.assertIsInstance(self.manager.keyboard, RealKeyboardController)
    
    def test_cleanup(self):
        """Тест очистки ресурсов"""
        # Просто проверяем, что cleanup не вызывает ошибок
        self.manager.cleanup()


class TestMouseButton(unittest.TestCase):
    """Тесты для MouseButton enum"""
    
    def test_mouse_button_values(self):
        """Тест значений кнопок мыши"""
        self.assertEqual(MouseButton.LEFT.value, "left")
        self.assertEqual(MouseButton.RIGHT.value, "right")
        self.assertEqual(MouseButton.MIDDLE.value, "middle")
        self.assertEqual(MouseButton.SCROLL_UP.value, "scroll_up")
        self.assertEqual(MouseButton.SCROLL_DOWN.value, "scroll_down")


if __name__ == '__main__':
    unittest.main()

