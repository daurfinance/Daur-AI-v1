#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
Daur-AI: Тесты AI-модуля
Проверяет функциональность модуля для работы с моделями ИИ

Версия: 1.0
Дата: 09.05.2025
"""

import os
import unittest
import json
from unittest.mock import MagicMock, patch

from tests.base import BaseTestCase
from src.ai.model_manager import AIModelManager


class TestAIModelManager(BaseTestCase):
    """
    Тесты для проверки работы менеджера AI-моделей
    """
    
    def setUp(self):
        """Инициализация перед каждым тестом"""
        super().setUp()
        
        # Создание фиктивной модели для тестов
        self.model_path = self.create_test_model()
        
        # Патчинг проверок библиотек
        self.setup_patches()
    
    def create_test_model(self):
        """
        Создание фиктивной модели для тестов
        
        Returns:
            Path: Путь к фиктивному файлу модели
        """
        # Создаем пустой файл .gguf для имитации модели
        model_path = self.test_dir / "test_model.gguf"
        with open(model_path, 'wb') as f:
            # Записываем фиктивные данные, имитирующие заголовок GGUF
            f.write(b'GGUF' + b'\x00' * 100)
        
        # Создаем конфигурационный файл для имитации модели Transformers
        config_dir = self.test_dir / "test_transformers_model"
        os.makedirs(config_dir, exist_ok=True)
        
        with open(config_dir / "config.json", 'w', encoding='utf-8') as f:
            json.dump({
                "model_type": "gpt2",
                "architectures": ["GPT2LMHeadModel"],
                "vocab_size": 100
            }, f)
            
        return model_path
    
    def setup_patches(self):
        """Настройка патчей для тестов"""
        # Патчи для проверки наличия библиотек
        self.torch_patch = patch('src.ai.model_manager.HAS_TORCH', True)
        self.transformers_patch = patch('src.ai.model_manager.HAS_TRANSFORMERS', True)
        self.llama_cpp_patch = patch('src.ai.model_manager.HAS_LLAMA_CPP', True)
        
        # Применение патчей
        self.torch_patch.start()
        self.transformers_patch.start()
        self.llama_cpp_patch.start()
        
        # Создание мок-объектов для библиотек
        self.mock_torch = MagicMock()
        self.mock_transformers = MagicMock()
        self.mock_llama = MagicMock()
        
        # Патчи для библиотек
        self.torch_module_patch = patch('src.ai.model_manager.torch', self.mock_torch)
        self.transformers_module_patch = patch('src.ai.model_manager.AutoModelForCausalLM', self.mock_transformers)
        self.llama_module_patch = patch('src.ai.model_manager.Llama', self.mock_llama)
        
        # Применение патчей для модулей
        self.torch_module_patch.start()
        self.transformers_module_patch.start()
        self.llama_module_patch.start()
        
        # Настройка возвращаемых значений
        self.mock_torch.cuda.is_available.return_value = False
        
    def tearDown(self):
        """Очистка после каждого теста"""
        # Остановка всех патчей
        self.torch_patch.stop()
        self.transformers_patch.stop()
        self.llama_cpp_patch.stop()
        self.torch_module_patch.stop()
        self.transformers_module_patch.stop()
        self.llama_module_patch.stop()
        
        super().tearDown()
    
    def test_initialization(self):
        """Проверка инициализации менеджера моделей"""
        # Создание менеджера моделей
        ai_manager = AIModelManager(
            model_path=str(self.model_path),
            timeout=5,
            context_length=1024,
            use_gpu=False
        )
        
        # Проверка инициализации
        self.assertEqual(ai_manager.model_path, str(self.model_path))
        self.assertEqual(ai_manager.timeout, 5)
        self.assertEqual(ai_manager.context_length, 1024)
        self.assertFalse(ai_manager.use_gpu)
        self.assertEqual(ai_manager.device, "cpu")
        self.assertEqual(ai_manager.model_type, "llama_cpp")  # Должен определить тип по расширению .gguf
    
    def test_model_type_detection(self):
        """Проверка обнаружения типа модели"""
        # Тест для GGUF модели
        ai_manager_gguf = AIModelManager(
            model_path=str(self.model_path),
            use_gpu=False
        )
        self.assertEqual(ai_manager_gguf.model_type, "llama_cpp")
        
        # Тест для Transformers модели
        transformers_path = self.test_dir / "test_transformers_model"
        ai_manager_tf = AIModelManager(
            model_path=str(transformers_path),
            use_gpu=False
        )
        self.assertEqual(ai_manager_tf.model_type, "transformers")
    
    @patch('src.ai.model_manager.Llama')
    def test_load_model_llama_cpp(self, mock_llama):
        """Проверка загрузки llama_cpp модели"""
        # Настройка мока
        mock_llama.return_value = MagicMock()
        
        # Создание менеджера моделей
        ai_manager = AIModelManager(
            model_path=str(self.model_path),
            use_gpu=False
        )
        
        # Проверка загрузки модели
        result = ai_manager.load_model()
        self.assertTrue(result)
        mock_llama.assert_called_once()
        
        # Проверка состояния
        self.assertTrue(ai_manager.is_loaded)
        self.assertIsNotNone(ai_manager.model)
    
    @patch('src.ai.model_manager.AutoModelForCausalLM')
    @patch('src.ai.model_manager.AutoTokenizer')
    def test_load_model_transformers(self, mock_tokenizer, mock_model):
        """Проверка загрузки transformers модели"""
        # Настройка моков
        mock_tokenizer.from_pretrained.return_value = MagicMock()
        mock_model.from_pretrained.return_value = MagicMock()
        
        # Создание менеджера моделей
        transformers_path = self.test_dir / "test_transformers_model"
        ai_manager = AIModelManager(
            model_path=str(transformers_path),
            use_gpu=False
        )
        
        # Проверка загрузки модели
        result = ai_manager.load_model()
        self.assertTrue(result)
        mock_tokenizer.from_pretrained.assert_called_once()
        mock_model.from_pretrained.assert_called_once()
        
        # Проверка состояния
        self.assertTrue(ai_manager.is_loaded)
        self.assertIsNotNone(ai_manager.model)
        self.assertIsNotNone(ai_manager.tokenizer)
    
    def test_generate_text(self):
        """Проверка генерации текста"""
        # Создание мока для модели
        mock_model = MagicMock()
        mock_model.return_value = {
            'choices': [{'text': 'Сгенерированный текст'}]
        }
        
        # Создание менеджера моделей с моком
        ai_manager = AIModelManager(
            model_path=str(self.model_path),
            use_gpu=False
        )
        
        # Замена реальной модели на мок
        ai_manager.is_loaded = True
        ai_manager.model = mock_model
        ai_manager.model_type = "llama_cpp"
        
        # Проверка генерации текста
        text = ai_manager.generate_text("Тестовый запрос")
        self.assertIsNotNone(text)
        mock_model.assert_called_once()
    
    def test_unload_model(self):
        """Проверка выгрузки модели"""
        # Создание менеджера моделей
        ai_manager = AIModelManager(
            model_path=str(self.model_path),
            use_gpu=False
        )
        
        # Искусственное состояние загруженной модели
        ai_manager.is_loaded = True
        ai_manager.model = MagicMock()
        ai_manager.tokenizer = MagicMock()
        
        # Проверка выгрузки
        ai_manager.unload_model()
        self.assertFalse(ai_manager.is_loaded)
        self.assertIsNone(ai_manager.model)
    
    def test_parse_command(self):
        """Проверка парсинга команды пользователя"""
        # Создание мок-модели, возвращающей структурированный JSON
        mock_generate = MagicMock(return_value='''
        [
            {
                "action": "input_click",
                "params": {
                    "target": "кнопка"
                }
            }
        ]
        ''')
        
        # Создание менеджера моделей с моком
        ai_manager = AIModelManager(
            model_path=str(self.model_path),
            use_gpu=False
        )
        
        # Подмена метода генерации текста
        ai_manager.generate_text = mock_generate
        
        # Тестирование парсинга команды
        result = ai_manager.parse_command("кликни на кнопку")
        mock_generate.assert_called_once()
        
        # Проверка результата
        self.assertIsInstance(result, list)
        self.assertEqual(len(result), 1)
        self.assertEqual(result[0]["action"], "input_click")
        self.assertEqual(result[0]["params"]["target"], "кнопка")


if __name__ == '__main__':
    unittest.main()
