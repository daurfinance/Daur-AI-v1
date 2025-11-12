#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
Daur-AI: Модуль расширенных функций
Включает кэширование результатов, планирование задач, уведомления и аналитику

Версия: 2.0
Дата: 25.10.2025
Автор: Manus AI
"""

import logging
import threading
import time
import json
from typing import Dict, List, Any, Optional, Callable
from datetime import datetime, timedelta
from enum import Enum
from collections import defaultdict
import sqlite3
from pathlib import Path


class TaskPriority(Enum):
    """Приоритеты задач"""
    LOW = 1
    NORMAL = 2
    HIGH = 3
    CRITICAL = 4


class TaskStatus(Enum):
    """Статусы задач"""
    PENDING = "pending"
    RUNNING = "running"
    COMPLETED = "completed"
    FAILED = "failed"
    CANCELLED = "cancelled"


class ResultCache:
    """Кэш результатов выполнения команд"""
    
    def __init__(self, db_path: str = None, ttl: int = 3600):
        """
        Args:
            db_path: Путь к базе данных SQLite
            ttl: Время жизни кэша в секундах
        """
        self.db_path = db_path or str(Path.home() / '.daur_ai' / 'cache.db')
        self.ttl = ttl
        self.lock = threading.RLock()
        self.logger = logging.getLogger('daur_ai.result_cache')
        
        # Инициализируем БД
        self._init_db()
    
    def _init_db(self):
        """Инициализировать базу данных"""
        Path(self.db_path).parent.mkdir(parents=True, exist_ok=True)
        
        with sqlite3.connect(self.db_path) as conn:
            conn.execute('''
                CREATE TABLE IF NOT EXISTS cache (
                    id INTEGER PRIMARY KEY,
                    command_hash TEXT UNIQUE,
                    command TEXT,
                    result TEXT,
                    timestamp REAL,
                    hits INTEGER DEFAULT 0
                )
            ''')
            conn.commit()
    
    def get(self, command: str) -> Optional[Any]:
        """
        Получить результат из кэша
        
        Args:
            command: Команда
            
        Returns:
            Any: Результат или None
        """
        import hashlib
        
        command_hash = hashlib.sha256(command.encode()).hexdigest()
        
        with self.lock:
            try:
                with sqlite3.connect(self.db_path) as conn:
                    cursor = conn.execute(
                        'SELECT result, timestamp, hits FROM cache WHERE command_hash = ?',
                        (command_hash,)
                    )
                    row = cursor.fetchone()
                    
                    if row:
                        result, timestamp, hits = row
                        
                        # Проверяем TTL
                        if time.time() - timestamp > self.ttl:
                            conn.execute('DELETE FROM cache WHERE command_hash = ?', (command_hash,))
                            conn.commit()
                            return None
                        
                        # Обновляем счетчик попаданий
                        conn.execute(
                            'UPDATE cache SET hits = ? WHERE command_hash = ?',
                            (hits + 1, command_hash)
                        )
                        conn.commit()
                        
                        return json.loads(result)
                    
                    return None
            
            except Exception as e:
                self.logger.error(f"Ошибка чтения кэша: {e}")
                return None
    
    def set(self, command: str, result: Any):
        """
        Сохранить результат в кэш
        
        Args:
            command: Команда
            result: Результат
        """
        import hashlib
        
        command_hash = hashlib.sha256(command.encode()).hexdigest()
        
        with self.lock:
            try:
                with sqlite3.connect(self.db_path) as conn:
                    conn.execute(
                        '''INSERT OR REPLACE INTO cache 
                           (command_hash, command, result, timestamp) 
                           VALUES (?, ?, ?, ?)''',
                        (command_hash, command, json.dumps(result), time.time())
                    )
                    conn.commit()
            
            except Exception as e:
                self.logger.error(f"Ошибка сохранения в кэш: {e}")
    
    def clear(self):
        """Очистить кэш"""
        with self.lock:
            try:
                with sqlite3.connect(self.db_path) as conn:
                    conn.execute('DELETE FROM cache')
                    conn.commit()
            except Exception as e:
                self.logger.error(f"Ошибка очистки кэша: {e}")
    
    def get_stats(self) -> Dict[str, Any]:
        """Получить статистику кэша"""
        with self.lock:
            try:
                with sqlite3.connect(self.db_path) as conn:
                    cursor = conn.execute('SELECT COUNT(*), SUM(hits) FROM cache')
                    count, total_hits = cursor.fetchone()
                    
                    return {
                        'cached_items': count or 0,
                        'total_hits': total_hits or 0,
                        'average_hits': (total_hits or 0) / (count or 1)
                    }
            
            except Exception as e:
                self.logger.error(f"Ошибка получения статистики: {e}")
                return {}


class TaskScheduler:
    """Планировщик задач"""
    
    def __init__(self):
        """Инициализация"""
        self.tasks = {}
        self.task_id_counter = 0
        self.lock = threading.RLock()
        self.logger = logging.getLogger('daur_ai.task_scheduler')
        self.running = False
        self.scheduler_thread = None
    
    def schedule_task(self, func: Callable, delay: float = 0, 
                     priority: TaskPriority = TaskPriority.NORMAL,
                     repeat: bool = False, interval: float = None) -> str:
        """
        Запланировать задачу
        
        Args:
            func: Функция для выполнения
            delay: Задержка перед выполнением в секундах
            priority: Приоритет задачи
            repeat: Повторять ли задачу
            interval: Интервал повторения в секундах
            
        Returns:
            str: ID задачи
        """
        with self.lock:
            self.task_id_counter += 1
            task_id = f"task_{self.task_id_counter}"
            
            self.tasks[task_id] = {
                'func': func,
                'delay': delay,
                'priority': priority,
                'repeat': repeat,
                'interval': interval or delay,
                'status': TaskStatus.PENDING,
                'created_at': time.time(),
                'scheduled_at': time.time() + delay,
                'last_run': None,
                'next_run': time.time() + delay
            }
            
            self.logger.info(f"Задача {task_id} запланирована")
            return task_id
    
    def cancel_task(self, task_id: str):
        """Отменить задачу"""
        with self.lock:
            if task_id in self.tasks:
                self.tasks[task_id]['status'] = TaskStatus.CANCELLED
                self.logger.info(f"Задача {task_id} отменена")
    
    def start(self):
        """Запустить планировщик"""
        if self.running:
            return
        
        self.running = True
        self.scheduler_thread = threading.Thread(target=self._scheduler_loop, daemon=True)
        self.scheduler_thread.start()
        self.logger.info("Планировщик задач запущен")
    
    def stop(self):
        """Остановить планировщик"""
        self.running = False
        if self.scheduler_thread:
            self.scheduler_thread.join(timeout=5)
        self.logger.info("Планировщик задач остановлен")
    
    def _scheduler_loop(self):
        """Основной цикл планировщика"""
        while self.running:
            current_time = time.time()
            
            with self.lock:
                for task_id, task in list(self.tasks.items()):
                    if task['status'] == TaskStatus.CANCELLED:
                        continue
                    
                    if current_time >= task['next_run']:
                        try:
                            task['status'] = TaskStatus.RUNNING
                            task['func']()
                            task['status'] = TaskStatus.COMPLETED
                            task['last_run'] = current_time
                            
                            if task['repeat']:
                                task['next_run'] = current_time + task['interval']
                            else:
                                task['status'] = TaskStatus.COMPLETED
                        
                        except Exception as e:
                            task['status'] = TaskStatus.FAILED
                            self.logger.error(f"Ошибка в задаче {task_id}: {e}")
            
            time.sleep(1)
    
    def get_task_status(self, task_id: str) -> Optional[Dict[str, Any]]:
        """Получить статус задачи"""
        with self.lock:
            if task_id in self.tasks:
                task = self.tasks[task_id]
                return {
                    'id': task_id,
                    'status': task['status'].value,
                    'created_at': task['created_at'],
                    'last_run': task['last_run'],
                    'next_run': task['next_run']
                }
            return None


class NotificationManager:
    """Менеджер уведомлений"""
    
    def __init__(self):
        """Инициализация"""
        self.notifications = []
        self.subscribers = defaultdict(list)
        self.lock = threading.RLock()
        self.logger = logging.getLogger('daur_ai.notification_manager')
    
    def subscribe(self, event_type: str, callback: Callable):
        """
        Подписаться на события
        
        Args:
            event_type: Тип события
            callback: Функция обратного вызова
        """
        with self.lock:
            self.subscribers[event_type].append(callback)
            self.logger.info(f"Подписка на событие {event_type}")
    
    def unsubscribe(self, event_type: str, callback: Callable):
        """Отписаться от событий"""
        with self.lock:
            if event_type in self.subscribers:
                self.subscribers[event_type].remove(callback)
    
    def notify(self, event_type: str, data: Dict[str, Any]):
        """
        Отправить уведомление
        
        Args:
            event_type: Тип события
            data: Данные события
        """
        notification = {
            'type': event_type,
            'data': data,
            'timestamp': datetime.now().isoformat()
        }
        
        with self.lock:
            self.notifications.append(notification)
            
            # Вызываем подписчиков
            for callback in self.subscribers.get(event_type, []):
                try:
                    callback(notification)
                except Exception as e:
                    self.logger.error(f"Ошибка в callback: {e}")
    
    def get_notifications(self, event_type: str = None, limit: int = 100) -> List[Dict[str, Any]]:
        """Получить уведомления"""
        with self.lock:
            if event_type:
                notifications = [n for n in self.notifications if n['type'] == event_type]
            else:
                notifications = self.notifications
            
            return notifications[-limit:]


class AnalyticsCollector:
    """Сборщик аналитики"""
    
    def __init__(self):
        """Инициализация"""
        self.events = []
        self.metrics = defaultdict(list)
        self.lock = threading.RLock()
        self.logger = logging.getLogger('daur_ai.analytics')
    
    def track_event(self, event_name: str, properties: Dict[str, Any] = None):
        """
        Отследить событие
        
        Args:
            event_name: Имя события
            properties: Свойства события
        """
        event = {
            'name': event_name,
            'properties': properties or {},
            'timestamp': datetime.now().isoformat()
        }
        
        with self.lock:
            self.events.append(event)
    
    def track_metric(self, metric_name: str, value: float):
        """
        Отследить метрику
        
        Args:
            metric_name: Имя метрики
            value: Значение метрики
        """
        with self.lock:
            self.metrics[metric_name].append({
                'value': value,
                'timestamp': time.time()
            })
    
    def get_event_count(self, event_name: str) -> int:
        """Получить количество событий"""
        with self.lock:
            return sum(1 for e in self.events if e['name'] == event_name)
    
    def get_metric_stats(self, metric_name: str) -> Dict[str, Any]:
        """Получить статистику метрики"""
        with self.lock:
            if metric_name not in self.metrics or len(self.metrics[metric_name]) == 0:
                return {}
            
            values = [m['value'] for m in self.metrics[metric_name]]
            
            return {
                'count': len(values),
                'min': min(values),
                'max': max(values),
                'avg': sum(values) / len(values),
                'total': sum(values)
            }
    
    def get_report(self) -> Dict[str, Any]:
        """Получить отчет аналитики"""
        with self.lock:
            return {
                'total_events': len(self.events),
                'event_types': len(set(e['name'] for e in self.events)),
                'metrics': {
                    name: self.get_metric_stats(name)
                    for name in self.metrics.keys()
                }
            }


# Глобальные экземпляры
_result_cache = None
_task_scheduler = None
_notification_manager = None
_analytics_collector = None


def get_result_cache() -> ResultCache:
    """Получить глобальный кэш результатов"""
    global _result_cache
    if _result_cache is None:
        _result_cache = ResultCache()
    return _result_cache


def get_task_scheduler() -> TaskScheduler:
    """Получить глобальный планировщик задач"""
    global _task_scheduler
    if _task_scheduler is None:
        _task_scheduler = TaskScheduler()
    return _task_scheduler


def get_notification_manager() -> NotificationManager:
    """Получить глобальный менеджер уведомлений"""
    global _notification_manager
    if _notification_manager is None:
        _notification_manager = NotificationManager()
    return _notification_manager


def get_analytics_collector() -> AnalyticsCollector:
    """Получить глобальный сборщик аналитики"""
    global _analytics_collector
    if _analytics_collector is None:
        _analytics_collector = AnalyticsCollector()
    return _analytics_collector

