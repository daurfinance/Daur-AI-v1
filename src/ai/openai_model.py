#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
Daur-AI: Интеграция с OpenAI API
Модуль для работы с моделями OpenAI (GPT-3.5, GPT-4)

Версия: 1.1
Дата: 01.10.2025
"""

import json
import logging
import os
import requests
import time
from typing import Dict, List, Any, Optional
from dataclasses import dataclass


@dataclass
class OpenAIConfig:
    """Конфигурация для OpenAI API"""
    api_key: str = ""
    model: str = "gpt-3.5-turbo"
    max_tokens: int = 1000
    temperature: float = 0.7
    timeout: int = 30
    base_url: str = "https://api.openai.com/v1"


class OpenAIModelManager:
    """
    Менеджер для работы с OpenAI API
    """
    
    def __init__(self, config_dict: Dict[str, Any] = None):
        """
        Инициализация OpenAI менеджера
        
        Args:
            config_dict (Dict): Словарь конфигурации
        """
        self.logger = logging.getLogger('daur_ai.openai')
        
        # Настройка конфигурации
        self.config = OpenAIConfig(
            api_key=os.getenv('OPENAI_API_KEY', ''),
            model=config_dict.get('openai_model', 'gpt-3.5-turbo') if config_dict else 'gpt-3.5-turbo',
            max_tokens=config_dict.get('max_tokens', 1000) if config_dict else 1000,
            temperature=config_dict.get('temperature', 0.7) if config_dict else 0.7,
            timeout=config_dict.get('openai_timeout', 30) if config_dict else 30
        )
        
        if not self.config.api_key:
            raise ValueError("OpenAI API ключ не найден в переменных окружения")
        
        # Системный промпт для парсинга команд
        self.system_prompt = """Ты - помощник для парсинга команд пользователя в структурированный JSON формат.

Твоя задача - преобразовать естественную команду пользователя в JSON с действиями для выполнения.

Поддерживаемые типы действий:
- file_create: создание файла (params: filename, content)
- file_read: чтение файла (params: filename)
- file_delete: удаление файла (params: filename)
- file_list: список файлов в директории (params: directory)
- file_mkdir: создание папки (params: dirname)
- app_open: открытие приложения (params: app_name)
- app_close: закрытие приложения (params: app_name)
- input_click: клик мышью (params: target, x, y)
- input_type: ввод текста (params: text)
- input_key: нажатие клавиши (params: key)

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

Отвечай ТОЛЬКО валидным JSON массивом, без дополнительных объяснений."""

        self.headers = {
            "Authorization": f"Bearer {self.config.api_key}",
            "Content-Type": "application/json"
        }
        
        # Проверка доступности API
        self._check_api_availability()
        
        self.logger.info("OpenAI менеджер инициализирован")
    
    def _check_api_availability(self) -> bool:
        """
        Проверка доступности OpenAI API
        
        Returns:
            bool: True если API доступно
        """
        try:
            response = requests.get(
                f"{self.config.base_url}/models",
                headers=self.headers,
                timeout=5
            )
            
            if response.status_code == 200:
                self.logger.info("OpenAI API доступно")
                return True
            else:
                self.logger.warning(f"OpenAI API недоступно: HTTP {response.status_code}")
                return False
                
        except requests.exceptions.RequestException as e:
            self.logger.warning(f"OpenAI API недоступно: {e}")
            return False
    
    def generate_text(self, prompt: str, **kwargs) -> str:
        """
        Генерация текста через OpenAI API
        
        Args:
            prompt (str): Входной промпт
            **kwargs: Дополнительные параметры
            
        Returns:
            str: Сгенерированный текст
        """
        try:
            payload = {
                "model": kwargs.get('model', self.config.model),
                "messages": [
                    {"role": "system", "content": self.system_prompt},
                    {"role": "user", "content": prompt}
                ],
                "max_tokens": kwargs.get('max_tokens', self.config.max_tokens),
                "temperature": kwargs.get('temperature', self.config.temperature),
                "stream": False
            }
            
            self.logger.debug(f"Отправка запроса к OpenAI: модель={payload['model']}")
            
            response = requests.post(
                f"{self.config.base_url}/chat/completions",
                headers=self.headers,
                json=payload,
                timeout=self.config.timeout
            )
            
            if response.status_code == 200:
                data = response.json()
                generated_text = data['choices'][0]['message']['content']
                self.logger.debug(f"Получен ответ от OpenAI: {len(generated_text)} символов")
                return generated_text
            else:
                error_msg = f"Ошибка OpenAI API: HTTP {response.status_code}"
                try:
                    error_data = response.json()
                    error_msg += f" - {error_data.get('error', {}).get('message', '')}"
                except Exception as e:
                    pass
                self.logger.error(error_msg)
                return error_msg
                
        except Exception as e:
            self.logger.error(f"Ошибка при генерации текста: {e}")
            return f"Ошибка: {str(e)}"
    
    def parse_command(self, command: str) -> List[Dict[str, Any]]:
        """
        Парсинг команды пользователя с помощью OpenAI
        
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
        Резервный парсинг команд без OpenAI
        
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
        Диалоговый режим с OpenAI
        
        Args:
            message (str): Сообщение пользователя
            context (List[Dict]): Контекст диалога
            
        Returns:
            str: Ответ модели
        """
        try:
            messages = [{"role": "system", "content": "Ты - полезный AI-помощник."}]
            
            # Добавляем контекст если есть
            if context:
                for msg in context[-10:]:  # Последние 10 сообщений
                    if 'user' in msg:
                        messages.append({"role": "user", "content": msg['user']})
                    if 'assistant' in msg:
                        messages.append({"role": "assistant", "content": msg['assistant']})
            
            # Добавляем текущее сообщение
            messages.append({"role": "user", "content": message})
            
            payload = {
                "model": self.config.model,
                "messages": messages,
                "max_tokens": self.config.max_tokens,
                "temperature": self.config.temperature
            }
            
            response = requests.post(
                f"{self.config.base_url}/chat/completions",
                headers=self.headers,
                json=payload,
                timeout=self.config.timeout
            )
            
            if response.status_code == 200:
                data = response.json()
                return data['choices'][0]['message']['content']
            else:
                return f"Ошибка API: {response.status_code}"
                
        except Exception as e:
            self.logger.error(f"Ошибка в диалоговом режиме: {e}")
            return f"Извините, произошла ошибка: {str(e)}"
    
    def list_models(self) -> List[str]:
        """
        Получение списка доступных моделей OpenAI
        
        Returns:
            List[str]: Список названий моделей
        """
        try:
            response = requests.get(
                f"{self.config.base_url}/models",
                headers=self.headers,
                timeout=self.config.timeout
            )
            
            if response.status_code == 200:
                data = response.json()
                models = [model['id'] for model in data['data'] 
                         if model['id'].startswith(('gpt-', 'text-', 'davinci', 'curie', 'babbage', 'ada'))]
                return sorted(models)
            else:
                self.logger.error(f"Ошибка получения списка моделей: HTTP {response.status_code}")
                return []
                
        except Exception as e:
            self.logger.error(f"Ошибка при получении списка моделей: {e}")
            return []
    
    def get_model_info(self) -> Dict[str, Any]:
        """
        Получение информации о текущей модели
        
        Returns:
            Dict: Информация о модели
        """
        return {
            "provider": "OpenAI",
            "model": self.config.model,
            "max_tokens": self.config.max_tokens,
            "temperature": self.config.temperature,
            "api_available": self._check_api_availability()
        }
    
    def is_available(self) -> bool:
        """
        Проверка доступности OpenAI API
        
        Returns:
            bool: True если API доступно
        """
        return self._check_api_availability()
    
    def cleanup(self):
        """Очистка ресурсов"""
        self.logger.info("Очистка OpenAI менеджера")
        pass
