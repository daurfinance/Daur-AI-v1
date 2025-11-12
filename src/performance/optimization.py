#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
Daur-AI: Модуль оптимизации производительности
Включает пулинг потоков, асинхронную обработку, кэширование и оптимизацию памяти

Версия: 2.0
Дата: 25.10.2025
Автор: Manus AI
"""

import logging
import threading
import queue
import time
import gc
import sys
from typing import Callable, Any, Dict, List, Optional
from concurrent.futures import ThreadPoolExecutor, ProcessPoolExecutor
from functools import wraps, lru_cache
from collections import OrderedDict
import psutil


class ThreadPool:
    """Оптимизированный пул потоков"""
    
    def __init__(self, max_workers: int = 4, queue_size: int = 100):
        """
        Args:
            max_workers: Максимальное количество рабочих потоков
            queue_size: Размер очереди задач
        """
        self.max_workers = max_workers
        self.executor = ThreadPoolExecutor(
            max_workers=max_workers,
            thread_name_prefix="daur_ai_worker_"
        )
        self.task_queue = queue.Queue(maxsize=queue_size)
        self.logger = logging.getLogger('daur_ai.thread_pool')
    
    def submit(self, func: Callable, *args, **kwargs):
        """
        Отправить задачу в пул
        
        Args:
            func: Функция для выполнения
            *args: Позиционные аргументы
            **kwargs: Именованные аргументы
            
        Returns:
            Future: Будущий результат
        """
        return self.executor.submit(func, *args, **kwargs)
    
    def submit_async(self, func: Callable, callback: Optional[Callable] = None, 
                    error_callback: Optional[Callable] = None, *args, **kwargs):
        """
        Отправить задачу с callback
        
        Args:
            func: Функция для выполнения
            callback: Функция обратного вызова при успехе
            error_callback: Функция обратного вызова при ошибке
            *args: Позиционные аргументы
            **kwargs: Именованные аргументы
        """
        future = self.executor.submit(func, *args, **kwargs)
        
        if callback or error_callback:
            def done_callback(f):
                try:
                    result = f.result()
                    if callback:
                        callback(result)
                except Exception as e:
                    if error_callback:
                        error_callback(e)
                    else:
                        self.logger.error(f"Ошибка в асинхронной задаче: {e}")
            
            future.add_done_callback(done_callback)
        
        return future
    
    def shutdown(self, wait: bool = True):
        """Завершить пул"""
        self.executor.shutdown(wait=wait)
        self.logger.info("Пул потоков завершен")


class MemoryOptimizer:
    """Оптимизатор использования памяти"""
    
    def __init__(self, max_memory_percent: float = 80.0):
        """
        Args:
            max_memory_percent: Максимальный процент использования памяти
        """
        self.max_memory_percent = max_memory_percent
        self.logger = logging.getLogger('daur_ai.memory_optimizer')
    
    def get_memory_usage(self) -> Dict[str, Any]:
        """Получить информацию об использовании памяти"""
        process = psutil.Process()
        memory_info = process.memory_info()
        memory_percent = process.memory_percent()
        
        return {
            'rss_mb': memory_info.rss / (1024 * 1024),
            'vms_mb': memory_info.vms / (1024 * 1024),
            'percent': memory_percent
        }
    
    def is_memory_critical(self) -> bool:
        """Проверить, критично ли использование памяти"""
        memory_info = self.get_memory_usage()
        return memory_info['percent'] > self.max_memory_percent
    
    def optimize(self):
        """Оптимизировать использование памяти"""
        if self.is_memory_critical():
            self.logger.warning("Критическое использование памяти, запускаем сборку мусора...")
            gc.collect()
            
            memory_info = self.get_memory_usage()
            self.logger.info(f"Память после оптимизации: {memory_info['percent']:.1f}%")
    
    def monitor(self, interval: int = 60):
        """
        Мониторить использование памяти
        
        Args:
            interval: Интервал проверки в секундах
        """
        def monitor_loop():
            while True:
                try:
                    self.optimize()
                    time.sleep(interval)
                except Exception as e:
                    self.logger.error(f"Ошибка мониторинга памяти: {e}")
                    time.sleep(interval)
        
        monitor_thread = threading.Thread(target=monitor_loop, daemon=True)
        monitor_thread.start()
        self.logger.info("Мониторинг памяти запущен")


class SmartCache:
    """Интеллектуальный кэш с автоматической очисткой"""
    
    def __init__(self, max_size: int = 1000, ttl: int = 3600):
        """
        Args:
            max_size: Максимальный размер кэша
            ttl: Время жизни записей в секундах
        """
        self.max_size = max_size
        self.ttl = ttl
        self.cache = OrderedDict()
        self.access_times = {}
        self.lock = threading.RLock()
        self.logger = logging.getLogger('daur_ai.smart_cache')
    
    def get(self, key: str) -> Optional[Any]:
        """Получить значение из кэша"""
        with self.lock:
            if key in self.cache:
                # Проверяем TTL
                if time.time() - self.access_times[key] > self.ttl:
                    del self.cache[key]
                    del self.access_times[key]
                    return None
                
                # Обновляем время доступа и перемещаем в конец (LRU)
                self.access_times[key] = time.time()
                self.cache.move_to_end(key)
                return self.cache[key]
            
            return None
    
    def set(self, key: str, value: Any):
        """Сохранить значение в кэш"""
        with self.lock:
            # Если кэш переполнен, удаляем самый старый элемент
            if len(self.cache) >= self.max_size:
                oldest_key = next(iter(self.cache))
                del self.cache[oldest_key]
                del self.access_times[oldest_key]
            
            self.cache[key] = value
            self.access_times[key] = time.time()
    
    def clear(self):
        """Очистить кэш"""
        with self.lock:
            self.cache.clear()
            self.access_times.clear()
    
    def get_stats(self) -> Dict[str, Any]:
        """Получить статистику кэша"""
        with self.lock:
            return {
                'size': len(self.cache),
                'max_size': self.max_size,
                'ttl': self.ttl
            }


class LoadBalancer:
    """Балансировщик нагрузки"""
    
    def __init__(self, num_workers: int = 4):
        """
        Args:
            num_workers: Количество рабочих потоков
        """
        self.num_workers = num_workers
        self.worker_queues = [queue.Queue() for _ in range(num_workers)]
        self.worker_loads = [0] * num_workers
        self.lock = threading.RLock()
        self.logger = logging.getLogger('daur_ai.load_balancer')
    
    def get_least_loaded_worker(self) -> int:
        """Получить индекс наименее загруженного рабочего"""
        with self.lock:
            return self.worker_loads.index(min(self.worker_loads))
    
    def submit_task(self, task: Any) -> int:
        """
        Отправить задачу на наименее загруженного рабочего
        
        Args:
            task: Задача для выполнения
            
        Returns:
            int: Индекс рабочего
        """
        with self.lock:
            worker_idx = self.get_least_loaded_worker()
            self.worker_queues[worker_idx].put(task)
            self.worker_loads[worker_idx] += 1
            
            return worker_idx
    
    def complete_task(self, worker_idx: int):
        """Отметить задачу как завершенную"""
        with self.lock:
            if self.worker_loads[worker_idx] > 0:
                self.worker_loads[worker_idx] -= 1
    
    def get_loads(self) -> List[int]:
        """Получить текущие нагрузки рабочих"""
        with self.lock:
            return self.worker_loads.copy()


class BatchProcessor:
    """Обработчик пакетных операций"""
    
    def __init__(self, batch_size: int = 10, timeout: float = 5.0):
        """
        Args:
            batch_size: Размер пакета
            timeout: Таймаут ожидания пакета в секундах
        """
        self.batch_size = batch_size
        self.timeout = timeout
        self.batch = []
        self.lock = threading.RLock()
        self.logger = logging.getLogger('daur_ai.batch_processor')
    
    def add_item(self, item: Any) -> Optional[List[Any]]:
        """
        Добавить элемент в пакет
        
        Args:
            item: Элемент для добавления
            
        Returns:
            Optional[List]: Полный пакет если достигнут размер, иначе None
        """
        with self.lock:
            self.batch.append(item)
            
            if len(self.batch) >= self.batch_size:
                batch = self.batch.copy()
                self.batch.clear()
                return batch
            
            return None
    
    def get_batch(self, force: bool = False) -> Optional[List[Any]]:
        """
        Получить пакет
        
        Args:
            force: Вернуть пакет даже если он неполный
            
        Returns:
            Optional[List]: Пакет или None
        """
        with self.lock:
            if force or len(self.batch) >= self.batch_size:
                batch = self.batch.copy()
                self.batch.clear()
                return batch if batch else None
            
            return None


def memoize(maxsize: int = 128):
    """
    Декоратор мемоизации с ограничением размера
    
    Args:
        maxsize: Максимальный размер кэша
    """
    def decorator(func):
        cached_func = lru_cache(maxsize=maxsize)(func)
        
        @wraps(func)
        def wrapper(*args, **kwargs):
            return cached_func(*args, **kwargs)
        
        wrapper.cache_clear = cached_func.cache_clear
        wrapper.cache_info = cached_func.cache_info
        
        return wrapper
    
    return decorator


def parallelize(num_workers: int = 4):
    """
    Декоратор для параллелизации обработки списков
    
    Args:
        num_workers: Количество рабочих потоков
    """
    def decorator(func):
        pool = ThreadPool(max_workers=num_workers)
        
        @wraps(func)
        def wrapper(items: List[Any], *args, **kwargs):
            futures = []
            
            for item in items:
                future = pool.submit(func, item, *args, **kwargs)
                futures.append(future)
            
            results = []
            for future in futures:
                try:
                    results.append(future.result())
                except Exception as e:
                    results.append(None)
            
            return results
        
        return wrapper
    
    return decorator


class PerformanceMonitor:
    """Мониторинг производительности"""
    
    def __init__(self):
        """Инициализация"""
        self.metrics = {}
        self.lock = threading.RLock()
        self.logger = logging.getLogger('daur_ai.performance_monitor')
    
    def measure_time(self, operation_name: str):
        """
        Декоратор для измерения времени операции
        
        Args:
            operation_name: Имя операции
        """
        def decorator(func):
            @wraps(func)
            def wrapper(*args, **kwargs):
                start_time = time.time()
                
                try:
                    result = func(*args, **kwargs)
                    return result
                
                finally:
                    duration = time.time() - start_time
                    
                    with self.lock:
                        if operation_name not in self.metrics:
                            self.metrics[operation_name] = []
                        
                        self.metrics[operation_name].append(duration)
                        
                        # Ограничиваем размер истории
                        if len(self.metrics[operation_name]) > 1000:
                            self.metrics[operation_name] = self.metrics[operation_name][-500:]
            
            return wrapper
        
        return decorator
    
    def get_stats(self, operation_name: str) -> Dict[str, Any]:
        """Получить статистику операции"""
        with self.lock:
            if operation_name not in self.metrics or len(self.metrics[operation_name]) == 0:
                return {
                    'count': 0,
                    'min': None,
                    'max': None,
                    'avg': None
                }
            
            durations = self.metrics[operation_name]
            
            return {
                'count': len(durations),
                'min': round(min(durations), 4),
                'max': round(max(durations), 4),
                'avg': round(sum(durations) / len(durations), 4),
                'total': round(sum(durations), 4)
            }
    
    def get_all_stats(self) -> Dict[str, Dict[str, Any]]:
        """Получить статистику всех операций"""
        result = {}
        for operation_name in self.metrics.keys():
            result[operation_name] = self.get_stats(operation_name)
        return result


# Глобальные экземпляры
_thread_pool = None
_memory_optimizer = None
_smart_cache = None
_load_balancer = None
_performance_monitor = None


def get_thread_pool(max_workers: int = 4) -> ThreadPool:
    """Получить глобальный пул потоков"""
    global _thread_pool
    if _thread_pool is None:
        _thread_pool = ThreadPool(max_workers=max_workers)
    return _thread_pool


def get_memory_optimizer() -> MemoryOptimizer:
    """Получить глобальный оптимизатор памяти"""
    global _memory_optimizer
    if _memory_optimizer is None:
        _memory_optimizer = MemoryOptimizer()
    return _memory_optimizer


def get_smart_cache(max_size: int = 1000) -> SmartCache:
    """Получить глобальный интеллектуальный кэш"""
    global _smart_cache
    if _smart_cache is None:
        _smart_cache = SmartCache(max_size=max_size)
    return _smart_cache


def get_load_balancer(num_workers: int = 4) -> LoadBalancer:
    """Получить глобальный балансировщик нагрузки"""
    global _load_balancer
    if _load_balancer is None:
        _load_balancer = LoadBalancer(num_workers=num_workers)
    return _load_balancer


def get_performance_monitor() -> PerformanceMonitor:
    """Получить глобальный монитор производительности"""
    global _performance_monitor
    if _performance_monitor is None:
        _performance_monitor = PerformanceMonitor()
    return _performance_monitor

