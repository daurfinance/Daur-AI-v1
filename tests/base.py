#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
Daur-AI: Базовый класс для тестов
Содержит общие функции и настройки для тестирования компонентов Daur-AI

Версия: 1.0
Дата: 09.05.2025
"""

import os
import sys
import unittest
import logging
import tempfile
import json
from pathlib import Path

# Добавление корневой директории проекта в пути импорта
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))


class BaseTestCase(unittest.TestCase):
    """
    Базовый класс для всех тестов Daur-AI
    """
    
    @classmethod
    def setUpClass(cls):
        """Инициализация класса тестирования"""
        # Настройка логгирования
        logging.basicConfig(
            level=logging.INFO,
            format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
            handlers=[
                logging.StreamHandler()
            ]
        )
        cls.logger = logging.getLogger('daur_ai.test')
        cls.logger.info(f"Инициализация тестового класса {cls.__name__}")
        
        # Создание временной директории для тестов
        cls.temp_dir = tempfile.TemporaryDirectory()
        cls.test_dir = Path(cls.temp_dir.name)
        
        # Создание тестовой конфигурации
        cls.create_test_config()
    
    @classmethod
    def tearDownClass(cls):
        """Очистка после тестов"""
        cls.logger.info(f"Завершение тестового класса {cls.__name__}")
        cls.temp_dir.cleanup()
    
    @classmethod
    def create_test_config(cls):
        """Создание тестовой конфигурации"""
        cls.test_config = {
            "app_name": "Daur-AI-Test",
            "version": "1.0",
            "description": "Тестовая конфигурация",
            "model_path": str(cls.test_dir / "test_model.gguf"),
            "log_path": str(cls.test_dir / "logs"),
            "encrypt_logs": False,
            "ui_settings": {
                "console": {
                    "prompt": "Test> ",
                    "history_size": 10,
                    "use_colors": False
                },
                "gui": {
                    "theme": "light",
                    "window_size": [640, 480]
                }
            },
            "file_operations": {
                "allowed_extensions": ["txt", "py", "md", "json"],
                "restricted_paths": ["/", "C:\\"]
            },
            "input_control": {
                "mouse_speed": 0.5,
                "keyboard_delay": 0.01,
                "safe_mode": True
            },
            "app_control": {
                "allowed_apps": ["test_app"],
                "restricted_apps": []
            },
            "advanced": {
                "sandbox_mode": True,
                "model_inference_timeout": 5,
                "max_tokens_response": 50,
                "temperature": 0.1,
                "debug_mode": True
            }
        }
        
        # Создание директорий
        os.makedirs(cls.test_dir / "logs", exist_ok=True)
        os.makedirs(cls.test_dir / "models", exist_ok=True)
        
        # Сохранение конфигурации
        with open(cls.test_dir / "test_config.json", 'w', encoding='utf-8') as f:
            json.dump(cls.test_config, f, indent=4, ensure_ascii=False)
        
        cls.config_path = cls.test_dir / "test_config.json"
    
    def setUp(self):
        """Подготовка перед каждым тестом"""
        self.logger.info(f"Запуск теста: {self._testMethodName}")
    
    def tearDown(self):
        """Очистка после каждого теста"""
        self.logger.info(f"Завершение теста: {self._testMethodName}")
    
    def create_test_file(self, filename, content):
        """
        Создание тестового файла
        
        Args:
            filename (str): Имя файла
            content (str): Содержимое файла
            
        Returns:
            Path: Путь к созданному файлу
        """
        file_path = self.test_dir / filename
        with open(file_path, 'w', encoding='utf-8') as f:
            f.write(content)
        return file_path
    
    def load_test_config(self):
        """
        Загрузка тестовой конфигурации
        
        Returns:
            dict: Конфигурационный словарь
        """
        with open(self.config_path, 'r', encoding='utf-8') as f:
            return json.load(f)
