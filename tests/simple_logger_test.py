import os
import tempfile
import logging
import unittest

class SimpleLoggerTest(unittest.TestCase):
    
    def setUp(self):
        # Создание временного файла для логов
        self.temp_fd, self.log_path = tempfile.mkstemp()
        
        # Настройка логгера
        self.logger = logging.getLogger('test_logger')
        self.logger.setLevel(logging.DEBUG)
        self.logger.handlers = []  # Очистка обработчиков
        
        # Добавление файлового обработчика
        handler = logging.FileHandler(self.log_path)
        formatter = logging.Formatter('%(levelname)s: %(message)s')
        handler.setFormatter(formatter)
        self.logger.addHandler(handler)
    
    def tearDown(self):
        # Закрытие файлов и удаление
        os.close(self.temp_fd)
        os.unlink(self.log_path)
    
    def test_basic_logging(self):
        # Логирование тестового сообщения
        test_message = "Test log message"
        self.logger.info(test_message)
        
        # Проверка, что сообщение записано в лог
        with open(self.log_path, 'r') as f:
            log_content = f.read()
        
        self.assertIn(test_message, log_content)
        print("Basic logging test passed!")

if __name__ == '__main__':
    unittest.main()
