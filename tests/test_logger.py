#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
Daur-AI: Тесты модуля логирования
Проверяет функциональность логгера и экспортера логов

Версия: 1.0
Дата: 09.05.2025
"""

import os
import re
import sys
import csv
import unittest
from unittest.mock import MagicMock, patch
from datetime import datetime
from pathlib import Path

# Добавление пути к родительскому каталогу для импорта модулей
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from tests.base import BaseTestCase
from src.logger.logger import setup_logger, ActionLogger, SecureHandler
from src.logger.exporter import export_logs_to_csv


class TestLogger(BaseTestCase):
    """
    Тесты для проверки работы модуля логирования
    """
    
    def setUp(self):
        """Инициализация перед каждым тестом"""
        super().setUp()
        
        # Создание тестовой директории для логов
        self.log_dir = self.test_dir / "logs"
        os.makedirs(self.log_dir, exist_ok=True)
        
        # Создание тестового лог-файла
        date_str = datetime.now().strftime('%Y%m%d')
        self.log_file = self.log_dir / f"daur_ai_log_{date_str}.log"
    
    def test_setup_logger_basic(self):
        """Проверка базовой инициализации логгера"""
        # Использование пути к временному файлу
        logger = setup_logger(log_file=str(self.log_file))
        
        # Проверка корректной настройки
        self.assertEqual(logger.name, "daur_ai")
        self.assertEqual(len(logger.handlers), 2)  # Консольный и файловый обработчики
        
        # Проверка записи лога
        test_message = "Тестовое сообщение"
        logger.info(test_message)
        
        # Чтение файла лога и проверка наличия сообщения
        with open(self.log_file, 'r', encoding='utf-8') as f:
            log_content = f.read()
        
        self.assertIn(test_message, log_content)
    
    def test_setup_logger_with_encryption(self):
        """Проверка инициализации логгера с шифрованием"""
        # Использование пути к временному файлу
        logger = setup_logger(log_file=str(self.log_file), encrypt_logs=True)
        
        # Проверка корректной настройки
        self.assertEqual(logger.name, "daur_ai")
        self.assertEqual(len(logger.handlers), 3)  # Консольный, файловый и защищённый обработчики
        
        # Проверка наличия защищенного обработчика
        has_secure_handler = any(isinstance(h, SecureHandler) for h in logger.handlers)
        self.assertTrue(has_secure_handler)
        
        # Проверка записи лога
        test_message = "Секретное сообщение"
        logger.info(test_message)
        
        # Проверка наличия ключа шифрования
        key_file = os.path.join(os.path.dirname(str(self.log_file)), 'log_key')
        self.assertTrue(os.path.exists(key_file))
    
    def test_action_logger(self):
        """Проверка функциональности логгера действий"""
        # Создание экземпляра логгера действий
        action_logger = ActionLogger(log_path=str(self.log_dir))
        
        # Запись тестового действия
        test_command = "тестовая команда"
        test_action = {"action": "test_action", "params": {"key": "value"}}
        test_result = "success"
        
        success = action_logger.log_action(test_command, test_action, test_result)
        self.assertTrue(success)
        
        # Проверка содержимого лог-файла
        with open(action_logger.log_file, 'r', encoding='utf-8') as f:
            log_content = f.read()
        
        # Сообщение должно содержать информацию о команде и действии
        self.assertIn("Команда: тестовая команда", log_content)
        self.assertIn("Действие:", log_content)
        self.assertIn("Результат: success", log_content)
    
    def test_action_logger_with_error(self):
        """Проверка записи ошибок в логгер действий"""
        # Создание экземпляра логгера действий
        action_logger = ActionLogger(log_path=str(self.log_dir))
        
        # Запись тестового действия с ошибкой
        test_command = "тестовая команда с ошибкой"
        test_action = "test_action_error"
        test_result = "failure"
        test_error = "Тестовая ошибка"
        
        success = action_logger.log_action(
            test_command, test_action, test_result, error=test_error
        )
        self.assertTrue(success)
        
        # Проверка содержимого лог-файла
        with open(action_logger.log_file, 'r', encoding='utf-8') as f:
            log_content = f.read()
        
        # Сообщение должно содержать информацию об ошибке
        self.assertIn("Команда: тестовая команда с ошибкой", log_content)
        self.assertIn("Действие: test_action_error", log_content)
        self.assertIn("Результат: failure", log_content)
        self.assertIn("Ошибка: Тестовая ошибка", log_content)


class TestLogExporter(BaseTestCase):
    """
    Тесты для проверки работы экспортера логов
    """
    
    def setUp(self):
        """Инициализация перед каждым тестом"""
        super().setUp()
        
        # Создание тестовой директории для логов
        self.log_dir = self.test_dir / "logs"
        os.makedirs(self.log_dir, exist_ok=True)
        
        # Создание тестового лог-файла
        self.log_file = self.log_dir / "daur_ai_log_20250509.log"
        
        # Запись тестовых логов
        log_entries = [
            "[2025-05-09 10:00:00] Команда: тест1 | Действие: action1 | Результат: success",
            "[2025-05-09 10:01:00] Команда: тест2 | Действие: action2 | Результат: failure | Ошибка: Test Error",
            "[2025-05-09 10:02:00] Команда: тест3 | Действие: action3 | Результат: success"
        ]
        
        with open(self.log_file, 'w', encoding='utf-8') as f:
            for entry in log_entries:
                f.write(entry + "\n")
        
        # Путь к CSV файлу для экспорта
        self.csv_file = self.test_dir / "test_export.csv"
    
    def test_export_logs_to_csv(self):
        """Проверка экспорта логов в CSV"""
        # Экспорт логов
        result = export_logs_to_csv(str(self.log_dir), str(self.csv_file))
        self.assertTrue(result)
        
        # Проверка существования CSV файла
        self.assertTrue(self.csv_file.exists())
        
        # Проверка содержимого CSV файла
        with open(self.csv_file, 'r', encoding='utf-8') as f:
            csv_reader = csv.reader(f)
            rows = list(csv_reader)
        
        # Проверка заголовка
        self.assertEqual(rows[0], ['timestamp', 'command', 'action', 'result', 'error'])
        
        # Проверка данных (3 записи + 1 заголовок = 4 строки)
        self.assertEqual(len(rows), 4)
        
        # Проверка содержимого строк
        self.assertEqual(rows[1][1], "тест1")
        self.assertEqual(rows[1][2], "action1")
        self.assertEqual(rows[1][3], "success")
        self.assertEqual(rows[1][4], "")  # Нет ошибки
        
        self.assertEqual(rows[2][1], "тест2")
        self.assertEqual(rows[2][2], "action2")
        self.assertEqual(rows[2][3], "failure")
        self.assertEqual(rows[2][4], "Test Error")  # Есть ошибка
    
    def test_export_logs_no_files(self):
        """Проверка поведения при отсутствии лог-файлов"""
        # Создание пустой директории
        empty_log_dir = self.test_dir / "empty_logs"
        os.makedirs(empty_log_dir, exist_ok=True)
        
        # Экспорт логов из пустой директории
        result = export_logs_to_csv(str(empty_log_dir), str(self.csv_file))
        self.assertFalse(result)  # Экспорт должен завершиться с ошибкой
    
    def test_export_logs_invalid_dir(self):
        """Проверка поведения при недействительном пути к логам"""
        # Экспорт логов из несуществующей директории
        result = export_logs_to_csv(str(self.test_dir / "nonexistent"), str(self.csv_file))
        self.assertFalse(result)  # Экспорт должен завершиться с ошибкой


if __name__ == '__main__':
    # При запуске файла напрямую
    print("Запуск тестов логгера...")
    unittest.main(verbosity=2)
