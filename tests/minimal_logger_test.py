#!/usr/bin/env python3

import os
import sys
import unittest
import tempfile
from pathlib import Path

# Добавляем корень проекта в пути импорта
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

# Указываем возможные причины импорта
try:
    # Импорт модуля логгера
    from src.logger.logger import setup_logger, ActionLogger
    
    # Тестовый класс для логгера
    class MinimalLoggerTest(unittest.TestCase):
        def setUp(self):
            # Создаем временную директорию для лога
            self.temp_dir = tempfile.TemporaryDirectory()
            self.log_file = os.path.join(self.temp_dir.name, "test_log.log")
            
        def tearDown(self):
            # Удаляем временную директорию
            self.temp_dir.cleanup()
        
        def test_setup_logger(self):
            # Проверка инициализации логгера
            logger = setup_logger(log_file=self.log_file)
            self.assertIsNotNone(logger)
            
            # Запись тестового сообщения
            test_msg = "Test message"
            logger.info(test_msg)
            
            # Проверка, что файл создан
            self.assertTrue(os.path.exists(self.log_file))
            
            # Проверка содержимого файла
            with open(self.log_file, 'r') as f:
                content = f.read()
                self.assertIn(test_msg, content)
            
            print("Тест setup_logger выполнен успешно!")

    if __name__ == '__main__':
        unittest.main(verbosity=2)
        
except Exception as e:
    print(f"Произошла ошибка при импорте или выполнении: {e}")
    import traceback
    traceback.print_exc()
