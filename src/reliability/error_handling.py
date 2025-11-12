#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
Daur-AI: Модуль надежности и обработки ошибок
Включает retry механизмы, circuit breaker, graceful degradation и recovery strategies

Версия: 2.0
Дата: 25.10.2025
Автор: Manus AI
"""

import logging
import time
import threading
from typing import Callable, Any, Optional, Dict, List
from functools import wraps
from enum import Enum
from datetime import datetime, timedelta
import random


class RetryStrategy(Enum):
    """Стратегии повторных попыток"""
    LINEAR = "linear"
    EXPONENTIAL = "exponential"
    FIBONACCI = "fibonacci"
    RANDOM = "random"


class CircuitBreakerState(Enum):
    """Состояния circuit breaker"""
    CLOSED = "closed"  # Нормальное состояние
    OPEN = "open"      # Блокирует запросы
    HALF_OPEN = "half_open"  # Тестирует восстановление


class RetryConfig:
    """Конфигурация для повторных попыток"""
    
    def __init__(self, max_attempts: int = 3, initial_delay: float = 1.0,
                 max_delay: float = 60.0, strategy: RetryStrategy = RetryStrategy.EXPONENTIAL):
        """
        Args:
            max_attempts: Максимальное количество попыток
            initial_delay: Начальная задержка в секундах
            max_delay: Максимальная задержка в секундах
            strategy: Стратегия повторных попыток
        """
        self.max_attempts = max_attempts
        self.initial_delay = initial_delay
        self.max_delay = max_delay
        self.strategy = strategy
    
    def get_delay(self, attempt: int) -> float:
        """
        Получить задержку для попытки
        
        Args:
            attempt: Номер попытки (начиная с 0)
            
        Returns:
            float: Задержка в секундах
        """
        if self.strategy == RetryStrategy.LINEAR:
            delay = self.initial_delay * (attempt + 1)
        
        elif self.strategy == RetryStrategy.EXPONENTIAL:
            delay = self.initial_delay * (2 ** attempt)
        
        elif self.strategy == RetryStrategy.FIBONACCI:
            # Упрощенная последовательность Фибоначчи
            fib = [1, 1]
            for _ in range(attempt - 1):
                fib.append(fib[-1] + fib[-2])
            delay = self.initial_delay * fib[min(attempt, len(fib) - 1)]
        
        elif self.strategy == RetryStrategy.RANDOM:
            delay = random.uniform(self.initial_delay, self.max_delay)
        
        else:
            delay = self.initial_delay
        
        # Ограничиваем максимальной задержкой
        return min(delay, self.max_delay)


class CircuitBreaker:
    """Паттерн Circuit Breaker для предотвращения каскадных отказов"""
    
    def __init__(self, failure_threshold: int = 5, recovery_timeout: int = 60):
        """
        Args:
            failure_threshold: Количество ошибок перед открытием
            recovery_timeout: Время ожидания перед попыткой восстановления (сек)
        """
        self.failure_threshold = failure_threshold
        self.recovery_timeout = recovery_timeout
        
        self.state = CircuitBreakerState.CLOSED
        self.failure_count = 0
        self.last_failure_time = None
        self.lock = threading.RLock()
        self.logger = logging.getLogger('daur_ai.circuit_breaker')
    
    def call(self, func: Callable, *args, **kwargs) -> Any:
        """
        Выполнить функцию через circuit breaker
        
        Args:
            func: Функция для выполнения
            *args: Позиционные аргументы
            **kwargs: Именованные аргументы
            
        Returns:
            Any: Результат функции
            
        Raises:
            Exception: Если circuit breaker открыт или функция вызывает исключение
        """
        with self.lock:
            # Проверяем состояние
            if self.state == CircuitBreakerState.OPEN:
                # Проверяем, прошло ли время восстановления
                if self.last_failure_time and \
                   time.time() - self.last_failure_time > self.recovery_timeout:
                    self.state = CircuitBreakerState.HALF_OPEN
                    self.logger.info("Circuit breaker переходит в HALF_OPEN")
                else:
                    raise Exception("Circuit breaker открыт - сервис недоступен")
            
            try:
                # Выполняем функцию
                result = func(*args, **kwargs)
                
                # Если успешно и был HALF_OPEN, закрываем
                if self.state == CircuitBreakerState.HALF_OPEN:
                    self.state = CircuitBreakerState.CLOSED
                    self.failure_count = 0
                    self.logger.info("Circuit breaker закрыт - сервис восстановлен")
                
                return result
            
            except Exception as e:
                self.failure_count += 1
                self.last_failure_time = time.time()
                
                # Если превышен порог, открываем
                if self.failure_count >= self.failure_threshold:
                    self.state = CircuitBreakerState.OPEN
                    self.logger.error(f"Circuit breaker открыт после {self.failure_count} ошибок")
                
                raise
    
    def reset(self):
        """Сбросить circuit breaker"""
        with self.lock:
            self.state = CircuitBreakerState.CLOSED
            self.failure_count = 0
            self.last_failure_time = None
            self.logger.info("Circuit breaker сброшен")
    
    def get_state(self) -> Dict[str, Any]:
        """Получить состояние circuit breaker"""
        with self.lock:
            return {
                'state': self.state.value,
                'failure_count': self.failure_count,
                'last_failure_time': self.last_failure_time.isoformat() if self.last_failure_time else None
            }


class ResilientExecutor:
    """Исполнитель с встроенной надежностью"""
    
    def __init__(self, retry_config: Optional[RetryConfig] = None,
                 circuit_breaker_enabled: bool = True):
        """
        Args:
            retry_config: Конфигурация повторных попыток
            circuit_breaker_enabled: Включить circuit breaker
        """
        self.retry_config = retry_config or RetryConfig()
        self.circuit_breaker = CircuitBreaker() if circuit_breaker_enabled else None
        self.logger = logging.getLogger('daur_ai.resilient_executor')
    
    def execute(self, func: Callable, *args, **kwargs) -> Dict[str, Any]:
        """
        Выполнить функцию с надежностью
        
        Args:
            func: Функция для выполнения
            *args: Позиционные аргументы
            **kwargs: Именованные аргументы
            
        Returns:
            Dict: Результат выполнения с метаданными
        """
        start_time = time.time()
        last_error = None
        
        for attempt in range(self.retry_config.max_attempts):
            try:
                # Используем circuit breaker если включен
                if self.circuit_breaker:
                    result = self.circuit_breaker.call(func, *args, **kwargs)
                else:
                    result = func(*args, **kwargs)
                
                execution_time = time.time() - start_time
                
                return {
                    'success': True,
                    'result': result,
                    'attempts': attempt + 1,
                    'execution_time': execution_time,
                    'error': None
                }
            
            except Exception as e:
                last_error = e
                
                if attempt < self.retry_config.max_attempts - 1:
                    delay = self.retry_config.get_delay(attempt)
                    self.logger.warning(
                        f"Попытка {attempt + 1} не удалась: {str(e)}. "
                        f"Повтор через {delay:.2f} сек..."
                    )
                    time.sleep(delay)
                else:
                    self.logger.error(
                        f"Все {self.retry_config.max_attempts} попытки исчерпаны: {str(e)}"
                    )
        
        execution_time = time.time() - start_time
        
        return {
            'success': False,
            'result': None,
            'attempts': self.retry_config.max_attempts,
            'execution_time': execution_time,
            'error': str(last_error)
        }


def retry(max_attempts: int = 3, delay: float = 1.0, 
          strategy: RetryStrategy = RetryStrategy.EXPONENTIAL,
          exceptions: tuple = (Exception,)):
    """
    Декоратор для автоматических повторных попыток
    
    Args:
        max_attempts: Максимальное количество попыток
        delay: Начальная задержка
        strategy: Стратегия повторных попыток
        exceptions: Типы исключений для перехвата
    """
    def decorator(func):
        @wraps(func)
        def wrapper(*args, **kwargs):
            config = RetryConfig(
                max_attempts=max_attempts,
                initial_delay=delay,
                strategy=strategy
            )
            
            last_error = None
            
            for attempt in range(config.max_attempts):
                try:
                    return func(*args, **kwargs)
                
                except exceptions as e:
                    last_error = e
                    
                    if attempt < config.max_attempts - 1:
                        wait_time = config.get_delay(attempt)
                        time.sleep(wait_time)
            
            raise last_error
        
        return wrapper
    
    return decorator


def circuit_breaker(failure_threshold: int = 5, recovery_timeout: int = 60):
    """
    Декоратор circuit breaker
    
    Args:
        failure_threshold: Количество ошибок перед открытием
        recovery_timeout: Время ожидания перед восстановлением
    """
    breaker = CircuitBreaker(failure_threshold, recovery_timeout)
    
    def decorator(func):
        @wraps(func)
        def wrapper(*args, **kwargs):
            return breaker.call(func, *args, **kwargs)
        
        wrapper.circuit_breaker = breaker
        return wrapper
    
    return decorator


class FallbackHandler:
    """Обработчик fallback значений"""
    
    def __init__(self):
        """Инициализация"""
        self.fallbacks = {}
        self.logger = logging.getLogger('daur_ai.fallback_handler')
    
    def register_fallback(self, func_name: str, fallback_func: Callable):
        """
        Зарегистрировать fallback функцию
        
        Args:
            func_name: Имя функции
            fallback_func: Fallback функция
        """
        self.fallbacks[func_name] = fallback_func
        self.logger.info(f"Fallback зарегистрирован для {func_name}")
    
    def execute_with_fallback(self, func: Callable, func_name: str, 
                            *args, **kwargs) -> Any:
        """
        Выполнить функцию с fallback
        
        Args:
            func: Основная функция
            func_name: Имя функции (для поиска fallback)
            *args: Позиционные аргументы
            **kwargs: Именованные аргументы
            
        Returns:
            Any: Результат основной функции или fallback
        """
        try:
            return func(*args, **kwargs)
        
        except Exception as e:
            self.logger.warning(f"Ошибка в {func_name}: {str(e)}. Используем fallback...")
            
            if func_name in self.fallbacks:
                try:
                    return self.fallbacks[func_name](*args, **kwargs)
                except Exception as fallback_error:
                    self.logger.error(f"Fallback также не сработал: {str(fallback_error)}")
                    raise
            else:
                self.logger.error(f"Fallback не зарегистрирован для {func_name}")
                raise


class HealthChecker:
    """Проверка здоровья компонентов"""
    
    def __init__(self):
        """Инициализация"""
        self.checks = {}
        self.results = {}
        self.lock = threading.RLock()
        self.logger = logging.getLogger('daur_ai.health_checker')
    
    def register_check(self, component_name: str, check_func: Callable):
        """
        Зарегистрировать проверку здоровья
        
        Args:
            component_name: Имя компонента
            check_func: Функция проверки (должна возвращать bool)
        """
        self.checks[component_name] = check_func
        self.logger.info(f"Проверка здоровья зарегистрирована для {component_name}")
    
    def run_checks(self) -> Dict[str, Dict[str, Any]]:
        """
        Запустить все проверки
        
        Returns:
            Dict: Результаты проверок
        """
        with self.lock:
            results = {}
            
            for component_name, check_func in self.checks.items():
                try:
                    is_healthy = check_func()
                    results[component_name] = {
                        'healthy': is_healthy,
                        'timestamp': datetime.now().isoformat(),
                        'error': None
                    }
                
                except Exception as e:
                    results[component_name] = {
                        'healthy': False,
                        'timestamp': datetime.now().isoformat(),
                        'error': str(e)
                    }
                    self.logger.error(f"Ошибка проверки {component_name}: {str(e)}")
            
            self.results = results
            return results
    
    def is_healthy(self) -> bool:
        """Проверить, здоровы ли все компоненты"""
        with self.lock:
            return all(result.get('healthy', False) for result in self.results.values())
    
    def get_status(self) -> Dict[str, Any]:
        """Получить статус здоровья"""
        with self.lock:
            healthy_count = sum(1 for r in self.results.values() if r.get('healthy'))
            total_count = len(self.results)
            
            return {
                'overall_healthy': self.is_healthy(),
                'healthy_components': healthy_count,
                'total_components': total_count,
                'components': self.results,
                'timestamp': datetime.now().isoformat()
            }


# Глобальные экземпляры
_resilient_executor = None
_fallback_handler = None
_health_checker = None


def get_resilient_executor() -> ResilientExecutor:
    """Получить глобальный исполнитель"""
    global _resilient_executor
    if _resilient_executor is None:
        _resilient_executor = ResilientExecutor()
    return _resilient_executor


def get_fallback_handler() -> FallbackHandler:
    """Получить глобальный обработчик fallback"""
    global _fallback_handler
    if _fallback_handler is None:
        _fallback_handler = FallbackHandler()
    return _fallback_handler


def get_health_checker() -> HealthChecker:
    """Получить глобальный проверщик здоровья"""
    global _health_checker
    if _health_checker is None:
        _health_checker = HealthChecker()
    return _health_checker

