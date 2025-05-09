#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
Daur-AI: Тесты парсера команд
Проверяет функциональность парсера команд

Версия: 1.0
Дата: 09.05.2025
"""

import os
import unittest
from unittest.mock import MagicMock, patch

from tests.base import BaseTestCase
from src.parser.command_parser import CommandParser


class TestCommandParser(BaseTestCase):
    """
    Тесты для проверки работы парсера команд
    """
    
    def setUp(self):
        """Инициализация перед каждым тестом"""
        super().setUp()
        
        # Создание мок-объекта для AI модели
        self.mock_ai = MagicMock()
        self.mock_ai.parse_command.return_value = [
            {
                "action": "input_click",
                "params": {"target": "кнопка"}
            }
        ]
        
        # Инициализация парсера команд
        self.parser = CommandParser()
    
    def test_simple_click_command(self):
        """Проверка распознавания простых команд клика"""
        commands = [
            "кликни по кнопке",
            "нажми на кнопку",
            "клик на кнопку",
            "нажать кнопку"
        ]
        
        for cmd in commands:
            with self.subTest(cmd=cmd):
                result = self.parser.parse(cmd)
                self.assertIsNotNone(result)
                self.assertIsInstance(result, list)
                self.assertTrue(len(result) > 0)
                
                # Проверка структуры результата
                action = result[0]
                self.assertIsInstance(action, dict)
                self.assertIn('action', action)
                self.assertEqual(action['action'], 'input_click')
                self.assertIn('params', action)
                self.assertIn('target', action['params'])
    
    def test_app_open_command(self):
        """Проверка распознавания команд открытия приложения"""
        commands = [
            "открой приложение блокнот",
            "запусти программу калькулятор"
        ]
        
        for cmd in commands:
            with self.subTest(cmd=cmd):
                result = self.parser.parse(cmd)
                self.assertIsNotNone(result)
                self.assertIsInstance(result, list)
                self.assertTrue(len(result) > 0)
                
                # Проверка структуры результата
                action = result[0]
                self.assertIsInstance(action, dict)
                self.assertIn('action', action)
                self.assertEqual(action['action'], 'app_open')
                self.assertIn('params', action)
                self.assertIn('app_name', action['params'])
    
    def test_file_operations_commands(self):
        """Проверка распознавания команд для работы с файлами"""
        commands = [
            "создай файл test.txt с содержимым привет мир",
            "прочитай файл document.txt",
            "запиши 'тестовый текст' в файл output.txt"
        ]
        
        expected_actions = [
            'file_create',
            'file_read',
            'file_write'
        ]
        
        for cmd, expected_action in zip(commands, expected_actions):
            with self.subTest(cmd=cmd, action=expected_action):
                result = self.parser.parse(cmd)
                self.assertIsNotNone(result)
                self.assertIsInstance(result, list)
                self.assertTrue(len(result) > 0)
                
                # Проверка структуры результата
                action = result[0]
                self.assertIsInstance(action, dict)
                self.assertIn('action', action)
                self.assertEqual(action['action'], expected_action)
                self.assertIn('params', action)
    
    def test_sequence_commands(self):
        """Проверка распознавания последовательности команд"""
        # Команда с последовательностью действий
        command = "открой блокнот и напечатай 'привет мир'"
        
        result = self.parser.parse(command)
        self.assertIsNotNone(result)
        self.assertIsInstance(result, list)
        self.assertEqual(len(result), 2)
        
        # Проверка первой команды
        self.assertEqual(result[0]['action'], 'app_open')
        self.assertIn('app_name', result[0]['params'])
        
        # Проверка второй команды
        self.assertEqual(result[1]['action'], 'input_type')
        self.assertIn('text', result[1]['params'])
    
    def test_fallback_to_ai(self):
        """Проверка использования AI для неизвестных команд"""
        # Патчим метод парсера для использования мок-объекта AI
        with patch.object(self.parser, '_parse_with_ai', self.mock_ai.parse_command):
            # Неизвестная команда
            command = "выполни какое-то сложное действие"
            
            result = self.parser.parse(command)
            self.assertIsNotNone(result)
            
            # Проверяем, что был вызван AI парсер
            self.mock_ai.parse_command.assert_called_once_with(command)


if __name__ == '__main__':
    unittest.main()
