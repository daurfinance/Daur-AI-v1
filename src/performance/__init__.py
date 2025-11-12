#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
Daur-AI: Модуль оптимизации производительности
"""

from .optimization import (
    ThreadPool,
    MemoryOptimizer,
    SmartCache,
    LoadBalancer,
    BatchProcessor,
    PerformanceMonitor,
    memoize,
    parallelize,
    get_thread_pool,
    get_memory_optimizer,
    get_smart_cache,
    get_load_balancer,
    get_performance_monitor
)

__all__ = [
    'ThreadPool',
    'MemoryOptimizer',
    'SmartCache',
    'LoadBalancer',
    'BatchProcessor',
    'PerformanceMonitor',
    'memoize',
    'parallelize',
    'get_thread_pool',
    'get_memory_optimizer',
    'get_smart_cache',
    'get_load_balancer',
    'get_performance_monitor'
]

