#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
Daur-AI: Расширенная система мониторинга и логирования
Включает метрики производительности, отслеживание ошибок, аналитику и алерты

Версия: 2.0
Дата: 25.10.2025
Автор: Manus AI
"""

import logging
import logging.handlers
import os
import json
import time
import threading
from typing import Dict, List, Any, Optional, Tuple
from datetime import datetime, timedelta
from collections import deque, defaultdict
import psutil
from pathlib import Path


class MetricsCollector:
    """Сборщик метрик производительности"""
    
    def __init__(self, max_samples: int = 1000):
        """
        Args:
            max_samples: Максимальное количество сохраняемых образцов
        """
        self.max_samples = max_samples
        self.metrics = defaultdict(lambda: deque(maxlen=max_samples))
        self.lock = threading.RLock()
    
    def record(self, metric_name: str, value: float, timestamp: Optional[float] = None):
        """
        Записать метрику
        
        Args:
            metric_name: Имя метрики
            value: Значение метрики
            timestamp: Временная метка (по умолчанию текущее время)
        """
        if timestamp is None:
            timestamp = time.time()
        
        with self.lock:
            self.metrics[metric_name].append({
                'value': value,
                'timestamp': timestamp
            })
    
    def get_stats(self, metric_name: str) -> Dict[str, Any]:
        """
        Получить статистику по метрике
        
        Args:
            metric_name: Имя метрики
            
        Returns:
            Dict: Статистика (min, max, avg, count)
        """
        with self.lock:
            if metric_name not in self.metrics or len(self.metrics[metric_name]) == 0:
                return {
                    'count': 0,
                    'min': None,
                    'max': None,
                    'avg': None
                }
            
            values = [m['value'] for m in self.metrics[metric_name]]
            
            return {
                'count': len(values),
                'min': min(values),
                'max': max(values),
                'avg': sum(values) / len(values),
                'latest': values[-1]
            }
    
    def get_all_metrics(self) -> Dict[str, Dict[str, Any]]:
        """Получить все метрики"""
        result = {}
        for metric_name in self.metrics.keys():
            result[metric_name] = self.get_stats(metric_name)
        return result
    
    def clear(self):
        """Очистить все метрики"""
        with self.lock:
            self.metrics.clear()


class SystemMonitor:
    """Мониторинг системных ресурсов"""
    
    def __init__(self, interval: int = 5):
        """
        Args:
            interval: Интервал сбора метрик в секундах
        """
        self.interval = interval
        self.metrics_collector = MetricsCollector()
        self.monitoring = False
        self.monitor_thread = None
        self.logger = logging.getLogger('daur_ai.system_monitor')
    
    def start(self):
        """Запустить мониторинг"""
        if self.monitoring:
            return
        
        self.monitoring = True
        self.monitor_thread = threading.Thread(target=self._monitor_loop, daemon=True)
        self.monitor_thread.start()
        self.logger.info("Системный мониторинг запущен")
    
    def stop(self):
        """Остановить мониторинг"""
        self.monitoring = False
        if self.monitor_thread:
            self.monitor_thread.join(timeout=5)
        self.logger.info("Системный мониторинг остановлен")
    
    def _monitor_loop(self):
        """Основной цикл мониторинга"""
        while self.monitoring:
            try:
                # CPU
                cpu_percent = psutil.cpu_percent(interval=0.5)
                self.metrics_collector.record('cpu_percent', cpu_percent)
                
                # Память
                memory = psutil.virtual_memory()
                self.metrics_collector.record('memory_percent', memory.percent)
                self.metrics_collector.record('memory_used_mb', memory.used / (1024 * 1024))
                
                # Диск
                disk = psutil.disk_usage('/')
                self.metrics_collector.record('disk_percent', (disk.used / disk.total) * 100)
                
                # Процессы
                process_count = len(psutil.pids())
                self.metrics_collector.record('process_count', process_count)
                
                time.sleep(self.interval)
                
            except Exception as e:
                self.logger.error(f"Ошибка мониторинга: {e}")
                time.sleep(self.interval)
    
    def get_current_status(self) -> Dict[str, Any]:
        """Получить текущий статус системы"""
        try:
            cpu_percent = psutil.cpu_percent(interval=0.1)
            memory = psutil.virtual_memory()
            disk = psutil.disk_usage('/')
            
            return {
                'cpu_percent': round(cpu_percent, 1),
                'memory_percent': round(memory.percent, 1),
                'memory_available_mb': round(memory.available / (1024 * 1024), 1),
                'disk_percent': round((disk.used / disk.total) * 100, 1),
                'process_count': len(psutil.pids()),
                'timestamp': datetime.now().isoformat()
            }
        except Exception as e:
            self.logger.error(f"Ошибка получения статуса: {e}")
            return {}
    
    def get_metrics_stats(self) -> Dict[str, Any]:
        """Получить статистику собранных метрик"""
        return self.metrics_collector.get_all_metrics()


class AdvancedLogger:
    """Продвинутая система логирования"""
    
    def __init__(self, log_dir: str = None, max_bytes: int = 10485760, backup_count: int = 5):
        """
        Args:
            log_dir: Директория для логов
            max_bytes: Максимальный размер файла лога
            backup_count: Количество резервных копий
        """
        self.log_dir = log_dir or os.path.expanduser('~/.daur_ai/logs')
        self.max_bytes = max_bytes
        self.backup_count = backup_count
        
        # Создаем директорию логов
        os.makedirs(self.log_dir, exist_ok=True)
        
        # Инициализируем логгеры
        self.loggers = {}
        self._setup_root_logger()
    
    def _setup_root_logger(self):
        """Настройка корневого логгера"""
        root_logger = logging.getLogger('daur_ai')
        root_logger.setLevel(logging.DEBUG)
        
        # Формат логов
        formatter = logging.Formatter(
            '%(asctime)s - %(name)s - %(levelname)s - %(message)s',
            datefmt='%Y-%m-%d %H:%M:%S'
        )
        
        # Файловый обработчик (ротирующийся)
        log_file = os.path.join(self.log_dir, 'daur_ai.log')
        file_handler = logging.handlers.RotatingFileHandler(
            log_file,
            maxBytes=self.max_bytes,
            backupCount=self.backup_count
        )
        file_handler.setLevel(logging.DEBUG)
        file_handler.setFormatter(formatter)
        root_logger.addHandler(file_handler)
        
        # Консольный обработчик
        console_handler = logging.StreamHandler()
        console_handler.setLevel(logging.INFO)
        console_handler.setFormatter(formatter)
        root_logger.addHandler(console_handler)
    
    def get_logger(self, name: str) -> logging.Logger:
        """
        Получить логгер
        
        Args:
            name: Имя логгера
            
        Returns:
            logging.Logger: Логгер
        """
        if name not in self.loggers:
            self.loggers[name] = logging.getLogger(name)
        
        return self.loggers[name]
    
    def get_log_file_path(self) -> str:
        """Получить путь к файлу лога"""
        return os.path.join(self.log_dir, 'daur_ai.log')
    
    def get_recent_logs(self, limit: int = 100) -> List[str]:
        """
        Получить последние логи
        
        Args:
            limit: Максимальное количество строк
            
        Returns:
            List[str]: Последние логи
        """
        log_file = self.get_log_file_path()
        
        if not os.path.exists(log_file):
            return []
        
        try:
            with open(log_file, 'r', encoding='utf-8') as f:
                lines = f.readlines()
            
            return lines[-limit:]
        
        except Exception as e:
            return [f"Ошибка чтения логов: {e}"]
    
    def export_logs(self, output_file: str):
        """
        Экспортировать логи в файл
        
        Args:
            output_file: Путь к файлу экспорта
        """
        log_file = self.get_log_file_path()
        
        if os.path.exists(log_file):
            import shutil
            shutil.copy(log_file, output_file)


class ErrorTracker:
    """Отслеживание ошибок и исключений"""
    
    def __init__(self, max_errors: int = 1000):
        """
        Args:
            max_errors: Максимальное количество отслеживаемых ошибок
        """
        self.max_errors = max_errors
        self.errors = deque(maxlen=max_errors)
        self.error_counts = defaultdict(int)
        self.lock = threading.RLock()
        self.logger = logging.getLogger('daur_ai.error_tracker')
    
    def record_error(self, error_type: str, message: str, traceback: str = None):
        """
        Записать ошибку
        
        Args:
            error_type: Тип ошибки
            message: Сообщение об ошибке
            traceback: Трассировка стека
        """
        with self.lock:
            error_record = {
                'type': error_type,
                'message': message,
                'traceback': traceback,
                'timestamp': datetime.now().isoformat(),
                'count': self.error_counts[error_type] + 1
            }
            
            self.errors.append(error_record)
            self.error_counts[error_type] += 1
            
            self.logger.error(f"{error_type}: {message}")
    
    def get_recent_errors(self, limit: int = 10) -> List[Dict[str, Any]]:
        """
        Получить последние ошибки
        
        Args:
            limit: Максимальное количество ошибок
            
        Returns:
            List[Dict]: Последние ошибки
        """
        with self.lock:
            return list(self.errors)[-limit:]
    
    def get_error_summary(self) -> Dict[str, int]:
        """
        Получить сводку ошибок
        
        Returns:
            Dict: Количество ошибок по типам
        """
        with self.lock:
            return dict(self.error_counts)
    
    def get_top_errors(self, limit: int = 10) -> List[Tuple[str, int]]:
        """
        Получить топ ошибок
        
        Args:
            limit: Максимальное количество ошибок
            
        Returns:
            List[Tuple]: Топ ошибок с количеством
        """
        with self.lock:
            sorted_errors = sorted(
                self.error_counts.items(),
                key=lambda x: x[1],
                reverse=True
            )
            return sorted_errors[:limit]


class PerformanceProfiler:
    """Профилировщик производительности"""
    
    def __init__(self):
        """Инициализация профилировщика"""
        self.measurements = defaultdict(list)
        self.lock = threading.RLock()
        self.logger = logging.getLogger('daur_ai.profiler')
    
    def measure(self, operation_name: str, duration: float):
        """
        Записать измерение производительности
        
        Args:
            operation_name: Имя операции
            duration: Длительность в секундах
        """
        with self.lock:
            self.measurements[operation_name].append({
                'duration': duration,
                'timestamp': time.time()
            })
    
    def get_performance_stats(self, operation_name: str) -> Dict[str, Any]:
        """
        Получить статистику производительности операции
        
        Args:
            operation_name: Имя операции
            
        Returns:
            Dict: Статистика производительности
        """
        with self.lock:
            if operation_name not in self.measurements or len(self.measurements[operation_name]) == 0:
                return {
                    'count': 0,
                    'min': None,
                    'max': None,
                    'avg': None
                }
            
            durations = [m['duration'] for m in self.measurements[operation_name]]
            
            return {
                'count': len(durations),
                'min': round(min(durations), 4),
                'max': round(max(durations), 4),
                'avg': round(sum(durations) / len(durations), 4),
                'total': round(sum(durations), 4)
            }
    
    def get_all_performance_stats(self) -> Dict[str, Dict[str, Any]]:
        """Получить статистику всех операций"""
        result = {}
        for operation_name in self.measurements.keys():
            result[operation_name] = self.get_performance_stats(operation_name)
        return result
    
    def clear(self):
        """Очистить все измерения"""
        with self.lock:
            self.measurements.clear()


class MonitoringDashboard:
    """Панель мониторинга"""
    
    def __init__(self):
        """Инициализация панели"""
        self.system_monitor = SystemMonitor()
        self.logger = AdvancedLogger()
        self.error_tracker = ErrorTracker()
        self.profiler = PerformanceProfiler()
        self.logger_instance = self.logger.get_logger('daur_ai.dashboard')
    
    def start(self):
        """Запустить мониторинг"""
        self.system_monitor.start()
        self.logger_instance.info("Панель мониторинга запущена")
    
    def stop(self):
        """Остановить мониторинг"""
        self.system_monitor.stop()
        self.logger_instance.info("Панель мониторинга остановлена")
    
    def get_full_status(self) -> Dict[str, Any]:
        """
        Получить полный статус системы
        
        Returns:
            Dict: Полный статус
        """
        return {
            'system': self.system_monitor.get_current_status(),
            'metrics': self.system_monitor.get_metrics_stats(),
            'errors': {
                'recent': self.error_tracker.get_recent_errors(limit=10),
                'summary': self.error_tracker.get_error_summary(),
                'top': self.error_tracker.get_top_errors(limit=5)
            },
            'performance': self.profiler.get_all_performance_stats(),
            'timestamp': datetime.now().isoformat()
        }
    
    def export_report(self, output_file: str):
        """
        Экспортировать отчет мониторинга
        
        Args:
            output_file: Путь к файлу отчета
        """
        report = {
            'generated_at': datetime.now().isoformat(),
            'status': self.get_full_status(),
            'logs': self.logger.get_recent_logs(limit=50)
        }
        
        with open(output_file, 'w', encoding='utf-8') as f:
            json.dump(report, f, indent=2, ensure_ascii=False)
        
        self.logger_instance.info(f"Отчет экспортирован в {output_file}")


# Глобальная панель мониторинга
_monitoring_dashboard = None


def get_monitoring_dashboard() -> MonitoringDashboard:
    """Получить глобальную панель мониторинга"""
    global _monitoring_dashboard
    
    if _monitoring_dashboard is None:
        _monitoring_dashboard = MonitoringDashboard()
    
    return _monitoring_dashboard

