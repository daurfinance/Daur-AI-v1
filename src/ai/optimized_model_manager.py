#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
Daur-AI: Оптимизированный менеджер AI моделей
Включает кэширование, асинхронную обработку, пулинг соединений и умное распределение нагрузки

Версия: 2.0
Дата: 25.10.2025
Автор: Manus AI
"""

import logging
import os
import asyncio
import hashlib
import time
from typing import Dict, List, Any, Optional, Tuple
from enum import Enum
from datetime import datetime, timedelta
from collections import OrderedDict
import threading
from concurrent.futures import ThreadPoolExecutor
import json


class ModelType(Enum):
    """Типы поддерживаемых моделей"""
    OLLAMA = "ollama"
    OPENAI = "openai"
    LOCAL = "local"
    SIMPLE = "simple"


class CacheEntry:
    """Запись в кэше с метаданными"""
    
    def __init__(self, value: Any, ttl: int = 3600):
        """
        Args:
            value: Кэшируемое значение
            ttl: Время жизни в секундах (по умолчанию 1 час)
        """
        self.value = value
        self.created_at = time.time()
        self.ttl = ttl
        self.access_count = 0
        self.last_accessed = time.time()
    
    def is_expired(self) -> bool:
        """Проверка истечения срока кэша"""
        return time.time() - self.created_at > self.ttl
    
    def access(self) -> Any:
        """Получить значение и обновить метаданные"""
        self.access_count += 1
        self.last_accessed = time.time()
        return self.value


class OptimizedModelManager:
    """
    Оптимизированный менеджер AI моделей с расширенными возможностями
    """
    
    def __init__(self, config: Dict[str, Any], max_cache_size: int = 1000):
        """
        Инициализация менеджера
        
        Args:
            config (Dict): Конфигурация моделей
            max_cache_size (int): Максимальный размер кэша
        """
        self.logger = logging.getLogger('daur_ai.optimized_model')
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
        
        # Кэширование результатов
        self.response_cache = OrderedDict()
        self.max_cache_size = max_cache_size
        self.cache_hits = 0
        self.cache_misses = 0
        self.cache_lock = threading.RLock()
        
        # Пулинг потоков для асинхронной обработки
        self.executor = ThreadPoolExecutor(max_workers=4, thread_name_prefix="daur_ai_model_")
        
        # Статистика использования моделей
        self.model_stats = {
            'total_requests': 0,
            'successful_requests': 0,
            'failed_requests': 0,
            'total_processing_time': 0,
            'model_switch_count': 0
        }
        
        # Инициализация доступных моделей
        self._initialize_models()
        
        self.logger.info(f"Оптимизированный менеджер инициализирован с активной моделью: {self.active_model_type}")
    
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
                target_model = self.config.get('ai_models', {}).get('ollama_model', 'llama3.2')
                
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
            from src.ai.simple_model import MockModelManager
            
            simple_manager = MockModelManager(self.config)
            self.models[ModelType.SIMPLE] = simple_manager
            self.logger.info("✓ Простая модель доступна (fallback)")
            
        except Exception as e:
            self.logger.warning(f"Ошибка инициализации простой модели: {e}")
        
        # Выбираем активную модель по приоритету
        for model_type in self.model_priority:
            if model_type in self.models:
                self.active_model = self.models[model_type]
                self.active_model_type = model_type
                self.logger.info(f"Активная модель: {model_type.value}")
                break
    
    def _generate_cache_key(self, prompt: str, model_type: Optional[str] = None) -> str:
        """
        Генерация ключа кэша на основе prompt и параметров
        
        Args:
            prompt: Текст запроса
            model_type: Тип модели (опционально)
            
        Returns:
            str: Хэш-ключ
        """
        key_data = f"{prompt}:{model_type or self.active_model_type.value}"
        return hashlib.md5(key_data.encode()).hexdigest()
    
    def _get_from_cache(self, cache_key: str) -> Optional[Any]:
        """
        Получить значение из кэша
        
        Args:
            cache_key: Ключ кэша
            
        Returns:
            Optional[Any]: Кэшированное значение или None
        """
        with self.cache_lock:
            if cache_key in self.response_cache:
                entry = self.response_cache[cache_key]
                
                if entry.is_expired():
                    del self.response_cache[cache_key]
                    self.cache_misses += 1
                    return None
                
                # Переместить в конец (LRU)
                self.response_cache.move_to_end(cache_key)
                self.cache_hits += 1
                return entry.access()
            
            self.cache_misses += 1
            return None
    
    def _set_cache(self, cache_key: str, value: Any, ttl: int = 3600):
        """
        Сохранить значение в кэш
        
        Args:
            cache_key: Ключ кэша
            value: Значение
            ttl: Время жизни в секундах
        """
        with self.cache_lock:
            # Если кэш переполнен, удаляем самый старый элемент
            if len(self.response_cache) >= self.max_cache_size:
                self.response_cache.popitem(last=False)
            
            self.response_cache[cache_key] = CacheEntry(value, ttl)
    
    def _switch_model(self, reason: str = ""):
        """
        Переключиться на следующую доступную модель
        
        Args:
            reason: Причина переключения
        """
        current_index = self.model_priority.index(self.active_model_type)
        
        for i in range(current_index + 1, len(self.model_priority)):
            model_type = self.model_priority[i]
            if model_type in self.models:
                self.active_model = self.models[model_type]
                self.active_model_type = model_type
                self.model_stats['model_switch_count'] += 1
                self.logger.warning(f"Переключение на модель {model_type.value}. Причина: {reason}")
                return True
        
        return False
    
    def generate_response(self, prompt: str, use_cache: bool = True, 
                         max_tokens: Optional[int] = None) -> Dict[str, Any]:
        """
        Генерация ответа с использованием кэша и fallback механизма
        
        Args:
            prompt: Текст запроса
            use_cache: Использовать кэш
            max_tokens: Максимальное количество токенов
            
        Returns:
            Dict: Результат с ответом и метаданными
        """
        start_time = time.time()
        self.model_stats['total_requests'] += 1
        
        # Проверка кэша
        if use_cache:
            cache_key = self._generate_cache_key(prompt)
            cached_response = self._get_from_cache(cache_key)
            
            if cached_response is not None:
                return {
                    'success': True,
                    'response': cached_response,
                    'model': self.active_model_type.value,
                    'from_cache': True,
                    'processing_time': time.time() - start_time
                }
        
        # Попытка генерации ответа
        max_attempts = len(self.models)
        attempt = 0
        
        while attempt < max_attempts:
            try:
                if not self.active_model:
                    raise Exception("Нет доступных моделей")
                
                # Генерируем ответ
                response = self.active_model.generate(
                    prompt=prompt,
                    max_tokens=max_tokens or self.config.get('ai_models', {}).get('max_tokens', 1000)
                )
                
                # Сохраняем в кэш
                if use_cache:
                    cache_key = self._generate_cache_key(prompt)
                    self._set_cache(cache_key, response)
                
                processing_time = time.time() - start_time
                self.model_stats['successful_requests'] += 1
                self.model_stats['total_processing_time'] += processing_time
                
                return {
                    'success': True,
                    'response': response,
                    'model': self.active_model_type.value,
                    'from_cache': False,
                    'processing_time': processing_time
                }
                
            except Exception as e:
                self.logger.error(f"Ошибка при использовании модели {self.active_model_type.value}: {e}")
                self.model_stats['failed_requests'] += 1
                
                # Пытаемся переключиться на другую модель
                if not self._switch_model(f"Ошибка: {str(e)}"):
                    break
                
                attempt += 1
        
        # Если все модели не сработали
        processing_time = time.time() - start_time
        return {
            'success': False,
            'error': 'Все доступные модели недоступны',
            'model': None,
            'from_cache': False,
            'processing_time': processing_time
        }
    
    def generate_response_async(self, prompt: str, use_cache: bool = True) -> asyncio.Future:
        """
        Асинхронная генерация ответа
        
        Args:
            prompt: Текст запроса
            use_cache: Использовать кэш
            
        Returns:
            asyncio.Future: Будущий результат
        """
        return asyncio.wrap_future(
            self.executor.submit(self.generate_response, prompt, use_cache)
        )
    
    def batch_generate(self, prompts: List[str], use_cache: bool = True) -> List[Dict[str, Any]]:
        """
        Пакетная генерация ответов
        
        Args:
            prompts: Список запросов
            use_cache: Использовать кэш
            
        Returns:
            List[Dict]: Список результатов
        """
        results = []
        for prompt in prompts:
            result = self.generate_response(prompt, use_cache)
            results.append(result)
        
        return results
    
    def clear_cache(self):
        """Очистить кэш"""
        with self.cache_lock:
            self.response_cache.clear()
            self.cache_hits = 0
            self.cache_misses = 0
            self.logger.info("Кэш очищен")
    
    def get_cache_stats(self) -> Dict[str, Any]:
        """
        Получить статистику кэша
        
        Returns:
            Dict: Статистика кэша
        """
        total_requests = self.cache_hits + self.cache_misses
        hit_rate = (self.cache_hits / total_requests * 100) if total_requests > 0 else 0
        
        return {
            'cache_size': len(self.response_cache),
            'max_cache_size': self.max_cache_size,
            'cache_hits': self.cache_hits,
            'cache_misses': self.cache_misses,
            'hit_rate': round(hit_rate, 2),
            'total_requests': total_requests
        }
    
    def get_model_stats(self) -> Dict[str, Any]:
        """
        Получить статистику использования моделей
        
        Returns:
            Dict: Статистика моделей
        """
        avg_time = 0
        if self.model_stats['successful_requests'] > 0:
            avg_time = self.model_stats['total_processing_time'] / self.model_stats['successful_requests']
        
        return {
            'total_requests': self.model_stats['total_requests'],
            'successful_requests': self.model_stats['successful_requests'],
            'failed_requests': self.model_stats['failed_requests'],
            'average_processing_time': round(avg_time, 3),
            'model_switch_count': self.model_stats['model_switch_count'],
            'active_model': self.active_model_type.value if self.active_model_type else None,
            'available_models': [m.value for m in self.models.keys()]
        }
    
    def get_full_stats(self) -> Dict[str, Any]:
        """
        Получить полную статистику системы
        
        Returns:
            Dict: Полная статистика
        """
        return {
            'cache_stats': self.get_cache_stats(),
            'model_stats': self.get_model_stats(),
            'timestamp': datetime.now().isoformat()
        }
    
    def shutdown(self):
        """Корректное завершение работы"""
        self.executor.shutdown(wait=True)
        self.logger.info("Оптимизированный менеджер моделей завершил работу")


def create_optimized_manager(config: Dict[str, Any]) -> OptimizedModelManager:
    """
    Фабрика для создания оптимизированного менеджера
    
    Args:
        config: Конфигурация
        
    Returns:
        OptimizedModelManager: Инициализированный менеджер
    """
    return OptimizedModelManager(config)

