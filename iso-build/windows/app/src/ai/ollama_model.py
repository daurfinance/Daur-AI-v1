#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
Daur-AI: Интеграция с Ollama
Модуль для работы с локальными LLM моделями через Ollama API

Версия: 1.1
Дата: 01.10.2025
"""

import json
import logging
import requests
import time
from typing import Dict, List, Any, Optional, Union
from dataclasses import dataclass


@dataclass
class OllamaConfig:
    """Конфигурация для Ollama"""
    host: str = "http://localhost:11434"
    model: str = "llama3.2"
    timeout: int = 30
    max_tokens: int = 1000
    temperature: float = 0.7
    system_prompt: str = ""


class OllamaModelManager:
    """
    Менеджер для работы с Ollama API
    Обеспечивает интеграцию с локальными LLM моделями
    """
    
    def __init__(self, config: OllamaConfig = None):
        """
        Инициализация менеджера Ollama
        
        Args:
            config (OllamaConfig): Конфигурация подключения
        """
        self.logger = logging.getLogger('daur_ai.ollama')
        self.config = config or OllamaConfig()
        
        # Системный промпт для парсинга команд
        self.system_prompt = """Ты - помощник для парсинга команд пользователя в структурированный JSON формат.

Твоя задача - преобразовать естественную команду пользователя в JSON с действиями для выполнения.

Поддерживаемые типы действий:
- file_create: создание файла
- file_read: чтение файла  
- file_delete: удаление файла
- file_list: список файлов в директории
- file_mkdir: создание папки
- app_open: открытие приложения
- app_close: закрытие приложения
- input_click: клик мышью
- input_type: ввод текста
- input_key: нажатие клавиши

Формат ответа - JSON массив объектов:
[
  {
    "action": "тип_действия",
    "params": {
      "параметр1": "значение1",
      "параметр2": "значение2"
    }
  }
]

Примеры:
Команда: "создай файл test.txt с содержимым привет"
Ответ: [{"action": "file_create", "params": {"filename": "test.txt", "content": "привет"}}]

Команда: "открой браузер"
Ответ: [{"action": "app_open", "params": {"app_name": "firefox"}}]

Отвечай ТОЛЬКО JSON, без дополнительных объяснений."""

        self.available_models = []
        self.current_model = None
        
        # Проверка доступности Ollama
        self._check_ollama_availability()
        
        self.logger.info(f"Ollama менеджер инициализирован для {self.config.host}")
    
    def _check_ollama_availability(self) -> bool:
        """
        Проверка доступности Ollama сервера
        
        Returns:
            bool: True если Ollama доступна
        """
        try:
            response = requests.get(f"{self.config.host}/api/tags", timeout=5)
            if response.status_code == 200:
                data = response.json()
                self.available_models = [model['name'] for model in data.get('models', [])]
                self.logger.info(f"Ollama доступна. Модели: {self.available_models}")
                return True
            else:
                self.logger.warning(f"Ollama недоступна: HTTP {response.status_code}")
                return False
        except requests.exceptions.RequestException as e:
            self.logger.warning(f"Ollama недоступна: {e}")
            return False
    
    def list_models(self) -> List[str]:
        """
        Получение списка доступных моделей
        
        Returns:
            List[str]: Список названий моделей
        """
        try:
            response = requests.get(f"{self.config.host}/api/tags", timeout=self.config.timeout)
            if response.status_code == 200:
                data = response.json()
                models = [model['name'] for model in data.get('models', [])]
                self.available_models = models
                return models
            else:
                self.logger.error(f"Ошибка получения списка моделей: HTTP {response.status_code}")
                return []
        except Exception as e:
            self.logger.error(f"Ошибка при получении списка моделей: {e}")
            return []
    
    def pull_model(self, model_name: str) -> bool:
        """
        Загрузка модели в Ollama
        
        Args:
            model_name (str): Название модели для загрузки
            
        Returns:
            bool: Успешность загрузки
        """
        try:
            self.logger.info(f"Начинаю загрузку модели: {model_name}")
            
            payload = {"name": model_name}
            response = requests.post(
                f"{self.config.host}/api/pull",
                json=payload,
                timeout=300,  # 5 минут на загрузку
                stream=True
            )
            
            if response.status_code == 200:
                # Обработка потокового ответа
                for line in response.iter_lines():
                    if line:
                        try:
                            data = json.loads(line.decode('utf-8'))
                            if 'status' in data:
                                self.logger.info(f"Загрузка {model_name}: {data['status']}")
                            if data.get('status') == 'success':
                                self.logger.info(f"Модель {model_name} успешно загружена")
                                return True
                        except json.JSONDecodeError:
                            continue
                return True
            else:
                self.logger.error(f"Ошибка загрузки модели: HTTP {response.status_code}")
                return False
                
        except Exception as e:
            self.logger.error(f"Ошибка при загрузке модели {model_name}: {e}")
            return False
    
    def generate_text(self, prompt: str, model: str = None, **kwargs) -> str:
        """
        Генерация текста через Ollama API
        
        Args:
            prompt (str): Входной промпт
            model (str): Название модели (по умолчанию из конфига)
            **kwargs: Дополнительные параметры
            
        Returns:
            str: Сгенерированный текст
        """
        model = model or self.config.model
        
        try:
            payload = {
                "model": model,
                "prompt": prompt,
                "system": self.system_prompt,
                "stream": False,
                "options": {
                    "temperature": kwargs.get('temperature', self.config.temperature),
                    "num_predict": kwargs.get('max_tokens', self.config.max_tokens),
                }
            }
            
            self.logger.debug(f"Отправка запроса к Ollama: модель={model}")
            
            response = requests.post(
                f"{self.config.host}/api/generate",
                json=payload,
                timeout=self.config.timeout
            )
            
            if response.status_code == 200:
                data = response.json()
                generated_text = data.get('response', '')
                self.logger.debug(f"Получен ответ от Ollama: {len(generated_text)} символов")
                return generated_text
            else:
                self.logger.error(f"Ошибка генерации: HTTP {response.status_code}")
                return f"Ошибка: {response.status_code}"
                
        except Exception as e:
            self.logger.error(f"Ошибка при генерации текста: {e}")
            return f"Ошибка: {str(e)}"
    
    def parse_command(self, command: str) -> List[Dict[str, Any]]:
        """
        Парсинг команды пользователя с помощью LLM
        
        Args:
            command (str): Команда пользователя
            
        Returns:
            List[Dict]: Список действий для выполнения
        """
        try:
            # Формируем промпт для парсинга
            prompt = f"Команда пользователя: {command}"
            
            # Получаем ответ от модели
            response = self.generate_text(prompt)
            
            # Пытаемся распарсить JSON
            try:
                # Очищаем ответ от лишних символов
                response = response.strip()
                if response.startswith('```json'):
                    response = response[7:]
                if response.endswith('```'):
                    response = response[:-3]
                response = response.strip()
                
                actions = json.loads(response)
                
                # Проверяем что это список
                if not isinstance(actions, list):
                    actions = [actions]
                
                self.logger.info(f"Команда '{command}' распознана как {len(actions)} действий")
                return actions
                
            except json.JSONDecodeError as e:
                self.logger.error(f"Ошибка парсинга JSON ответа: {e}")
                self.logger.debug(f"Ответ модели: {response}")
                
                # Fallback к простому парсингу
                return self._fallback_parsing(command)
                
        except Exception as e:
            self.logger.error(f"Ошибка при парсинге команды: {e}")
            return self._fallback_parsing(command)
    
    def _fallback_parsing(self, command: str) -> List[Dict[str, Any]]:
        """
        Резервный парсинг команд без LLM
        
        Args:
            command (str): Команда пользователя
            
        Returns:
            List[Dict]: Список действий
        """
        # Импортируем упрощенную модель для fallback
        from src.ai.simple_model import SimpleAIModel
        
        simple_model = SimpleAIModel()
        return simple_model.parse_command(command)
    
    def chat(self, message: str, context: List[Dict] = None) -> str:
        """
        Диалоговый режим с моделью
        
        Args:
            message (str): Сообщение пользователя
            context (List[Dict]): Контекст диалога
            
        Returns:
            str: Ответ модели
        """
        try:
            # Формируем контекст если есть
            full_prompt = message
            if context:
                context_text = "\n".join([f"User: {msg.get('user', '')}\nAssistant: {msg.get('assistant', '')}" 
                                        for msg in context[-5:]])  # Последние 5 сообщений
                full_prompt = f"Контекст:\n{context_text}\n\nТекущий вопрос: {message}"
            
            return self.generate_text(full_prompt)
            
        except Exception as e:
            self.logger.error(f"Ошибка в диалоговом режиме: {e}")
            return f"Извините, произошла ошибка: {str(e)}"
    
    def is_available(self) -> bool:
        """
        Проверка доступности Ollama
        
        Returns:
            bool: True если Ollama доступна
        """
        return self._check_ollama_availability()
    
    def get_model_info(self, model_name: str = None) -> Dict[str, Any]:
        """
        Получение информации о модели
        
        Args:
            model_name (str): Название модели
            
        Returns:
            Dict: Информация о модели
        """
        model_name = model_name or self.config.model
        
        try:
            response = requests.post(
                f"{self.config.host}/api/show",
                json={"name": model_name},
                timeout=self.config.timeout
            )
            
            if response.status_code == 200:
                return response.json()
            else:
                return {"error": f"HTTP {response.status_code}"}
                
        except Exception as e:
            return {"error": str(e)}
    
    def cleanup(self):
        """Очистка ресурсов"""
        self.logger.info("Очистка Ollama менеджера")
        pass


def create_ollama_manager(config_dict: Dict[str, Any] = None) -> OllamaModelManager:
    """
    Фабричная функция для создания Ollama менеджера
    
    Args:
        config_dict (Dict): Словарь конфигурации
        
    Returns:
        OllamaModelManager: Экземпляр менеджера
    """
    if config_dict:
        config = OllamaConfig(
            host=config_dict.get('ollama_host', 'http://localhost:11434'),
            model=config_dict.get('ollama_model', 'llama3.2'),
            timeout=config_dict.get('ollama_timeout', 30),
            max_tokens=config_dict.get('max_tokens', 1000),
            temperature=config_dict.get('temperature', 0.7)
        )
    else:
        config = OllamaConfig()
    
    return OllamaModelManager(config)
