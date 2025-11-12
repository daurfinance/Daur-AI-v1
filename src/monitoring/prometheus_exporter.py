"""
Prometheus Metrics Exporter for Daur-AI v2.0
Экспорт метрик в формате Prometheus

Поддерживает:
- Экспорт метрик CPU, памяти, диска
- Экспорт метрик API
- Экспорт метрик базы данных
- Интеграция с Prometheus
- Grafana-совместимые метрики
"""

import logging
import time
from typing import Dict, List
from datetime import datetime
from src.hardware.real_hardware_monitor import RealHardwareMonitor

# Настройка логирования
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class PrometheusMetrics:
    """Генератор Prometheus метрик"""
    
    def __init__(self):
        """Инициализация"""
        self.monitor = RealHardwareMonitor()
        self.api_requests_total = 0
        self.api_request_duration_sum = 0.0
        self.api_request_count = 0
        self.start_time = time.time()
        
        logger.info("Prometheus Metrics initialized")
    
    def record_api_request(self, duration: float):
        """Записать API запрос"""
        self.api_requests_total += 1
        self.api_request_duration_sum += duration
        self.api_request_count += 1
    
    def _format_metric(self, name: str, value: float, labels: Dict = None, 
                      help_text: str = None, metric_type: str = "gauge") -> str:
        """Форматировать метрику в Prometheus формат"""
        lines = []
        
        if help_text:
            lines.append(f"# HELP {name} {help_text}")
        
        lines.append(f"# TYPE {name} {metric_type}")
        
        if labels:
            label_str = ",".join([f'{k}="{v}"' for k, v in labels.items()])
            lines.append(f"{name}{{{label_str}}} {value}")
        else:
            lines.append(f"{name} {value}")
        
        return "\n".join(lines)
    
    def get_cpu_metrics(self) -> str:
        """Получить CPU метрики"""
        cpu = self.monitor.get_cpu_metrics()
        
        lines = []
        lines.append(self._format_metric(
            "daur_cpu_usage_percent",
            cpu.percent,
            help_text="CPU usage percentage",
            metric_type="gauge"
        ))
        
        lines.append(self._format_metric(
            "daur_cpu_cores_logical",
            cpu.count_logical,
            help_text="Number of logical CPU cores",
            metric_type="gauge"
        ))
        
        lines.append(self._format_metric(
            "daur_cpu_cores_physical",
            cpu.count_physical,
            help_text="Number of physical CPU cores",
            metric_type="gauge"
        ))
        
        lines.append(self._format_metric(
            "daur_cpu_frequency_mhz",
            cpu.freq_current,
            help_text="Current CPU frequency in MHz",
            metric_type="gauge"
        ))
        
        # Per-core metrics
        for i, percent in enumerate(cpu.percent_per_core):
            lines.append(self._format_metric(
                "daur_cpu_core_usage_percent",
                percent,
                labels={"core": str(i)},
                help_text="CPU usage percentage per core",
                metric_type="gauge"
            ))
        
        return "\n".join(lines)
    
    def get_memory_metrics(self) -> str:
        """Получить метрики памяти"""
        memory = self.monitor.get_memory_metrics()
        
        lines = []
        lines.append(self._format_metric(
            "daur_memory_usage_percent",
            memory.percent,
            help_text="Memory usage percentage",
            metric_type="gauge"
        ))
        
        lines.append(self._format_metric(
            "daur_memory_used_bytes",
            memory.used,
            help_text="Memory used in bytes",
            metric_type="gauge"
        ))
        
        lines.append(self._format_metric(
            "daur_memory_available_bytes",
            memory.available,
            help_text="Memory available in bytes",
            metric_type="gauge"
        ))
        
        lines.append(self._format_metric(
            "daur_memory_total_bytes",
            memory.total,
            help_text="Total memory in bytes",
            metric_type="gauge"
        ))
        
        return "\n".join(lines)
    
    def get_disk_metrics(self) -> str:
        """Получить метрики диска"""
        disk_list = self.monitor.get_disk_metrics()
        
        lines = []
        for disk in disk_list:
            labels = {"device": disk.device, "mount_point": disk.mount_point}
            
            lines.append(self._format_metric(
                "daur_disk_usage_percent",
                disk.percent,
                labels=labels,
                help_text="Disk usage percentage",
                metric_type="gauge"
            ))
            
            lines.append(self._format_metric(
                "daur_disk_used_bytes",
                disk.used,
                labels=labels,
                help_text="Disk used in bytes",
                metric_type="gauge"
            ))
            
            lines.append(self._format_metric(
                "daur_disk_total_bytes",
                disk.total,
                labels=labels,
                help_text="Total disk space in bytes",
                metric_type="gauge"
            ))
        
        return "\n".join(lines)
    
    def get_api_metrics(self) -> str:
        """Получить метрики API"""
        lines = []
        
        lines.append(self._format_metric(
            "daur_api_requests_total",
            self.api_requests_total,
            help_text="Total API requests",
            metric_type="counter"
        ))
        
        if self.api_request_count > 0:
            avg_duration = self.api_request_duration_sum / self.api_request_count
            lines.append(self._format_metric(
                "daur_api_request_duration_seconds",
                avg_duration,
                help_text="Average API request duration in seconds",
                metric_type="gauge"
            ))
        
        uptime = time.time() - self.start_time
        lines.append(self._format_metric(
            "daur_uptime_seconds",
            uptime,
            help_text="System uptime in seconds",
            metric_type="counter"
        ))
        
        return "\n".join(lines)
    
    def get_all_metrics(self) -> str:
        """Получить все метрики"""
        sections = [
            "# DAUR-AI PROMETHEUS METRICS",
            f"# Generated: {datetime.now().isoformat()}",
            "",
            "# CPU Metrics",
            self.get_cpu_metrics(),
            "",
            "# Memory Metrics",
            self.get_memory_metrics(),
            "",
            "# Disk Metrics",
            self.get_disk_metrics(),
            "",
            "# API Metrics",
            self.get_api_metrics(),
        ]
        
        return "\n".join(sections)


class PrometheusExporter:
    """Экспортер метрик для Prometheus"""
    
    def __init__(self, app=None):
        """
        Инициализация экспортера
        
        Args:
            app: Flask приложение (опционально)
        """
        self.metrics = PrometheusMetrics()
        self.app = app
        
        if app:
            self._register_routes(app)
        
        logger.info("Prometheus Exporter initialized")
    
    def _register_routes(self, app):
        """Зарегистрировать маршруты в Flask"""
        @app.route('/metrics', methods=['GET'])
        def metrics():
            """Endpoint для Prometheus"""
            return self.metrics.get_all_metrics(), 200, {
                'Content-Type': 'text/plain; charset=utf-8'
            }
        
        logger.info("Prometheus metrics endpoint registered at /metrics")
    
    def export_to_file(self, filename: str) -> bool:
        """Экспортировать метрики в файл"""
        try:
            with open(filename, 'w') as f:
                f.write(self.metrics.get_all_metrics())
            logger.info(f"Metrics exported to {filename}")
            return True
        except Exception as e:
            logger.error(f"Error exporting metrics: {e}")
            return False
    
    def get_metrics_text(self) -> str:
        """Получить метрики в текстовом формате"""
        return self.metrics.get_all_metrics()


def create_prometheus_exporter(app=None):
    """Создать и вернуть экспортер"""
    return PrometheusExporter(app)
