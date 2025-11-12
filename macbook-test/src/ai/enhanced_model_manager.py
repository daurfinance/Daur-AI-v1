#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
Daur-AI: Улучшенный менеджер AI моделей
Объединяет различные источники AI: Ollama, OpenAI API, локальные модели

Версия: 1.1
Дата: 01.10.2025
"""

import logging
import os
from typing import Dict, List, Any, Optional, Union
from enum import Enum


class ModelType(Enum):
    """Типы поддерживаемых моделей"""
    OLLAMA = "ollama"
    OPENAI = "openai"
    LOCAL = "local"
    SIMPLE = "simple"


class EnhancedModelManager:
    """
    Улучшенный менеджер AI моделей с поддержкой множественных источников
    """
    
    def __init__(self, config: Dict[str, Any]):
        """
        Инициализация менеджера
        
        Args:
            config (Dict): Конфигурация моделей
        """
        self.logger = logging.getLogger('daur_ai.enhanced_model')
        self.config = config
        
        # Приоритет моделей (от наиболее предпочтительной к резервной)
        self.model_priority = [
            ModelType.OLLAMA,
            ModelType.OPENAI, 
            ModelType.LOCAL,
            ModelType.SIMPLE
        ]
        
        self.active_model = None
        self.active_model_type = None
        self.models = {}
        
        # Инициализация доступных моделей
        self._initialize_models()
        
        self.logger.info(f"Менеджер инициализирован с активной моделью: {self.active_model_type}")
    
    def _initialize_models(self):
        """Инициализация всех доступных моделей"""
        
        # 1. Попытка инициализации Ollama
        try:
            from src.ai.ollama_model import create_ollama_manager
            
            ollama_manager = create_ollama_manager(self.config)
            if ollama_manager.is_available():
                self.models[ModelType.OLLAMA] = ollama_manager
                self.logger.info("✓ Ollama модель доступна")
                
                # Проверяем наличие нужной модели
                available_models = ollama_manager.list_models()
                target_model = self.config.get('ollama_model', 'llama3.2')
                
                if target_model not in available_models:
                    self.logger.info(f"Модель {target_model} не найдена, пытаюсь загрузить...")
                    if ollama_manager.pull_model(target_model):
                        self.logger.info(f"✓ Модель {target_model} успешно загружена")
                    else:
                        self.logger.warning(f"✗ Не удалось загрузить модель {target_model}")
            else:
                self.logger.info("✗ Ollama недоступна")
                
        except Exception as e:
            self.logger.warning(f"Ошибка инициализации Ollama: {e}")
        
        # 2. Попытка инициализации OpenAI API
        try:
            if os.getenv('OPENAI_API_KEY'):
                from src.ai.openai_model import OpenAIModelManager
                
                openai_manager = OpenAIModelManager(self.config)
                self.models[ModelType.OPENAI] = openai_manager
                self.logger.info("✓ OpenAI API доступен")
            else:
                self.logger.info("✗ OpenAI API ключ не найден")
                
        except Exception as e:
            self.logger.warning(f"Ошибка инициализации OpenAI: {e}")
        
        # 3. Попытка инициализации локальных моделей
        try:
            from src.ai.model_manager import AIModelManager
            
            local_manager = AIModelManager(
                model_path=self.config.get("model_path"),
                timeout=self.config.get("advanced", {}).get("model_inference_timeout", 30)
            )
            self.models[ModelType.LOCAL] = local_manager
            self.logger.info("✓ Локальная модель доступна")
            
        except Exception as e:
            self.logger.warning(f"Ошибка инициализации локальной модели: {e}")
        
        # 4. Резервная упрощенная модель (всегда доступна)
        try:
            from src.ai.simple_model import MockModelManager
            
            simple_manager = MockModelManager()
            self.models[ModelType.SIMPLE] = simple_manager
            self.logger.info("✓ Упрощенная модель доступна")
            
        except Exception as e:
            self.logger.error(f"Критическая ошибка: не удалось загрузить даже упрощенную модель: {e}")
        
        # Выбираем активную модель по приоритету
        self._select_active_model()
    
    def _select_active_model(self):
        """Выбор активной модели по приоритету"""
        for model_type in self.model_priority:
            if model_type in self.models:
                self.active_model = self.models[model_type]
                self.active_model_type = model_type
                self.logger.info(f"Выбрана активная модель: {model_type.value}")
                return
        
        # Если ничего не найдено - критическая ошибка
        raise RuntimeError("Не удалось инициализировать ни одну модель AI")
    
    def parse_command(self, command: str) -> List[Dict[str, Any]]:
        """
        Парсинг команды с использованием активной модели
        
        Args:
            command (str): Команда пользователя
            
        Returns:
            List[Dict]: Список действий
        """
        try:
            if hasattr(self.active_model, 'parse_command'):
                return self.active_model.parse_command(command)
            else:
                # Fallback для моделей без метода parse_command
                response = self.generate_text(f"Parse command: {command}")
                return self._parse_response_to_actions(response)
                
        except Exception as e:
            self.logger.error(f"Ошибка парсинга команды: {e}")
            
            # Пытаемся использовать резервную модель
            if self.active_model_type != ModelType.SIMPLE and ModelType.SIMPLE in self.models:
                try:
                    return self.models[ModelType.SIMPLE].parse_command(command)
                except Exception as fallback_error:
                    self.logger.error(f"Ошибка в резервной модели: {fallback_error}")
            
            return []
    
    def generate_text(self, prompt: str, **kwargs) -> str:
        """
        Генерация текста с использованием активной модели
        
        Args:
            prompt (str): Входной промпт
            **kwargs: Дополнительные параметры
            
        Returns:
            str: Сгенерированный текст
        """
        try:
            if hasattr(self.active_model, 'generate_text'):
                return self.active_model.generate_text(prompt, **kwargs)
            elif hasattr(self.active_model, 'generate'):
                return self.active_model.generate(prompt, **kwargs)
            else:
                return "Метод генерации текста не поддерживается активной моделью"
                
        except Exception as e:
            self.logger.error(f"Ошибка генерации текста: {e}")
            return f"Ошибка генерации: {str(e)}"
    
    def chat(self, message: str, context: List[Dict] = None) -> str:
        """
        Диалоговый режим
        
        Args:
            message (str): Сообщение пользователя
            context (List[Dict]): Контекст диалога
            
        Returns:
            str: Ответ модели
        """
        try:
            if hasattr(self.active_model, 'chat'):
                return self.active_model.chat(message, context)
            else:
                # Fallback через generate_text
                return self.generate_text(message)
                
        except Exception as e:
            self.logger.error(f"Ошибка в диалоговом режиме: {e}")
            return f"Извините, произошла ошибка: {str(e)}"
    
    def _parse_response_to_actions(self, response: str) -> List[Dict[str, Any]]:
        """
        Парсинг ответа модели в список действий
        
        Args:
            response (str): Ответ модели
            
        Returns:
            List[Dict]: Список действий
        """
        try:
            import json
            
            # Попытка парсинга как JSON
            if response.strip().startswith('[') or response.strip().startswith('{'):
                actions = json.loads(response)
                if isinstance(actions, dict):
                    actions = [actions]
                return actions
            
            # Если не JSON, возвращаем как текстовый ответ
            return [{
                "action": "text_response",
                "params": {"text": response}
            }]
            
        except Exception as e:
            self.logger.error(f"Ошибка парсинга ответа: {e}")
            return []
    
    def switch_model(self, model_type: ModelType) -> bool:
        """
        Переключение на другую модель
        
        Args:
            model_type (ModelType): Тип модели для переключения
            
        Returns:
            bool: Успешность переключения
        """
        if model_type in self.models:
            self.active_model = self.models[model_type]
            self.active_model_type = model_type
            self.logger.info(f"Переключено на модель: {model_type.value}")
            return True
        else:
            self.logger.warning(f"Модель {model_type.value} недоступна")
            return False
    
    def get_available_models(self) -> List[str]:
        """
        Получение списка доступных моделей
        
        Returns:
            List[str]: Список типов доступных моделей
        """
        return [model_type.value for model_type in self.models.keys()]
    
    def get_model_info(self) -> Dict[str, Any]:
        """
        Получение информации об активной модели
        
        Returns:
            Dict: Информация о модели
        """
        info = {
            "active_model": self.active_model_type.value if self.active_model_type else None,
            "available_models": self.get_available_models(),
        }
        
        # Дополнительная информация от активной модели
        if hasattr(self.active_model, 'get_model_info'):
            try:
                model_specific_info = self.active_model.get_model_info()
                info.update(model_specific_info)
            except Exception as e:
                info["model_info_error"] = str(e)
        
        return info
    
    def is_loaded(self) -> bool:
        """
        Проверка загрузки модели
        
        Returns:
            bool: True если модель загружена
        """
        return self.active_model is not None
    
    def cleanup(self):
        """Очистка ресурсов всех моделей"""
        self.logger.info("Очистка ресурсов Enhanced Model Manager")
        
        for model_type, model in self.models.items():
            try:
                if hasattr(model, 'cleanup'):
                    model.cleanup()
                    self.logger.debug(f"Очищена модель: {model_type.value}")
            except Exception as e:
                self.logger.error(f"Ошибка очистки модели {model_type.value}: {e}")
        
        self.models.clear()
        self.active_model = None
        self.active_model_type = None
