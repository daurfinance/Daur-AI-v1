from typing import Dict, Any, Optional, List
import time
import logging
import json
from pathlib import Path
import psutil
import threading
from dataclasses import dataclass, asdict
from datetime import datetime

@dataclass
class SystemMetrics:
    """Метрики состояния системы."""
    cpu_percent: float
    memory_percent: float
    disk_usage_percent: float
    network_io_counters: Dict[str, int]
    timestamp: float

@dataclass
class ApplicationMetrics:
    """Метрики приложения."""
    active_tasks: int
    ai_requests_per_minute: float
    average_response_time: float
    error_rate: float
    timestamp: float

class MetricsCollector:
    """Сборщик метрик системы и приложения."""
    
    def __init__(self, metrics_dir: Path):
        self.metrics_dir = metrics_dir
        self.metrics_dir.mkdir(parents=True, exist_ok=True)
        
        self.system_metrics_file = self.metrics_dir / "system_metrics.json"
        self.app_metrics_file = self.metrics_dir / "app_metrics.json"
        
        self._stop_collection = threading.Event()
        self._collection_thread: Optional[threading.Thread] = None
        
        self.logger = logging.getLogger(__name__)
        
        # Метрики приложения
        self._ai_requests_count = 0
        self._response_times: List[float] = []
        self._error_count = 0
        self._active_tasks = 0
        self._last_minute = time.time()
    
    def start_collection(self, interval: float = 60.0) -> None:
        """Запускает сбор метрик в отдельном потоке.
        
        Args:
            interval: Интервал сбора метрик в секундах
        """
        if self._collection_thread is not None:
            return
            
        self._stop_collection.clear()
        self._collection_thread = threading.Thread(
            target=self._collect_metrics_loop,
            args=(interval,)
        )
        self._collection_thread.daemon = True
        self._collection_thread.start()
        
    def stop_collection(self) -> None:
        """Останавливает сбор метрик."""
        if self._collection_thread is None:
            return
            
        self._stop_collection.set()
        self._collection_thread.join()
        self._collection_thread = None
    
    def collect_system_metrics(self) -> SystemMetrics:
        """Собирает текущие метрики системы."""
        return SystemMetrics(
            cpu_percent=psutil.cpu_percent(),
            memory_percent=psutil.virtual_memory().percent,
            disk_usage_percent=psutil.disk_usage('/').percent,
            network_io_counters=dict(psutil.net_io_counters()._asdict()),
            timestamp=time.time()
        )
    
    def collect_app_metrics(self) -> ApplicationMetrics:
        """Собирает текущие метрики приложения."""
        current_time = time.time()
        time_diff = current_time - self._last_minute
        
        if time_diff >= 60:
            requests_per_minute = self._ai_requests_count / (time_diff / 60)
            self._ai_requests_count = 0
            self._last_minute = current_time
        else:
            requests_per_minute = self._ai_requests_count
        
        avg_response_time = (
            sum(self._response_times) / len(self._response_times)
            if self._response_times else 0
        )
        
        return ApplicationMetrics(
            active_tasks=self._active_tasks,
            ai_requests_per_minute=requests_per_minute,
            average_response_time=avg_response_time,
            error_rate=self._error_count / max(1, self._ai_requests_count),
            timestamp=current_time
        )
    
    def _collect_metrics_loop(self, interval: float) -> None:
        """Основной цикл сбора метрик."""
        while not self._stop_collection.is_set():
            try:
                system_metrics = self.collect_system_metrics()
                app_metrics = self.collect_app_metrics()
                
                self._save_metrics(system_metrics, app_metrics)
                self._check_thresholds(system_metrics, app_metrics)
                
            except Exception as e:
                self.logger.error(f"Error collecting metrics: {e}")
                
            self._stop_collection.wait(interval)
    
    def _save_metrics(self, 
                     system_metrics: SystemMetrics,
                     app_metrics: ApplicationMetrics) -> None:
        """Сохраняет метрики в файлы."""
        # Сохранение системных метрик
        self._save_json(self.system_metrics_file, asdict(system_metrics))
        
        # Сохранение метрик приложения
        self._save_json(self.app_metrics_file, asdict(app_metrics))
    
    def _save_json(self, file_path: Path, data: Dict[str, Any]) -> None:
        """Сохраняет данные в JSON файл."""
        try:
            with open(file_path, 'w') as f:
                json.dump(data, f, indent=2)
        except Exception as e:
            self.logger.error(f"Error saving metrics to {file_path}: {e}")
    
    def _check_thresholds(self,
                         system_metrics: SystemMetrics,
                         app_metrics: ApplicationMetrics) -> None:
        """Проверяет метрики на превышение пороговых значений."""
        # Проверка CPU
        if system_metrics.cpu_percent > 80:
            self.logger.warning("High CPU usage detected!")
            
        # Проверка памяти
        if system_metrics.memory_percent > 90:
            self.logger.warning("High memory usage detected!")
            
        # Проверка диска
        if system_metrics.disk_usage_percent > 90:
            self.logger.warning("High disk usage detected!")
            
        # Проверка ошибок приложения
        if app_metrics.error_rate > 0.1:  # Более 10% ошибок
            self.logger.warning("High error rate detected!")
            
        # Проверка времени отклика
        if app_metrics.average_response_time > 5.0:  # Более 5 секунд
            self.logger.warning("High response time detected!")
    
    # Методы для обновления метрик приложения
    def record_ai_request(self) -> None:
        """Регистрирует новый AI запрос."""
        self._ai_requests_count += 1
    
    def record_response_time(self, time_seconds: float) -> None:
        """Регистрирует время ответа."""
        self._response_times.append(time_seconds)
        if len(self._response_times) > 1000:
            self._response_times = self._response_times[-1000:]
    
    def record_error(self) -> None:
        """Регистрирует ошибку."""
        self._error_count += 1
    
    def update_active_tasks(self, count: int) -> None:
        """Обновляет количество активных задач."""
        self._active_tasks = count