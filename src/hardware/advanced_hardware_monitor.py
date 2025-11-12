"""
Advanced Hardware Monitoring for Daur-AI v2.0
Продвинутый мониторинг оборудования с предсказаниями и алертами

Поддерживает:
- Предсказание проблем (диск заполнится, память переполнится)
- Установка алертов с порогами
- История метрик
- Анализ трендов
- Автоматические уведомления
"""

import logging
import threading
import time
from typing import Dict, List, Optional, Callable
from dataclasses import dataclass
from datetime import datetime, timedelta
from collections import deque
from enum import Enum
from src.hardware.real_hardware_monitor import RealHardwareMonitor

# Настройка логирования
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class AlertSeverity(Enum):
    """Уровни серьезности алерта"""
    INFO = "info"
    WARNING = "warning"
    CRITICAL = "critical"


@dataclass
class Alert:
    """Алерт"""
    name: str
    message: str
    severity: AlertSeverity
    timestamp: datetime
    value: float
    threshold: float
    metric_type: str


@dataclass
class MetricHistory:
    """История метрики"""
    metric_name: str
    values: deque  # (timestamp, value)
    threshold: Optional[float] = None
    enabled: bool = True


class AlertRule:
    """Правило алерта"""
    
    def __init__(self, metric_type: str, threshold: float, 
                 severity: AlertSeverity = AlertSeverity.WARNING,
                 comparison: str = "greater"):
        """
        Args:
            metric_type: Тип метрики (cpu, memory, disk)
            threshold: Пороговое значение
            severity: Уровень серьезности
            comparison: Тип сравнения (greater, less, equal)
        """
        self.metric_type = metric_type
        self.threshold = threshold
        self.severity = severity
        self.comparison = comparison
        self.triggered = False
        self.last_trigger_time = None
    
    def check(self, value: float) -> bool:
        """Проверить правило"""
        if self.comparison == "greater":
            return value > self.threshold
        elif self.comparison == "less":
            return value < self.threshold
        elif self.comparison == "equal":
            return value == self.threshold
        return False


class HardwarePredictor:
    """Предсказание проблем с оборудованием"""
    
    def __init__(self, history_size: int = 100):
        """Инициализация предсказателя"""
        self.monitor = RealHardwareMonitor()
        self.history_size = history_size
        self.disk_history: deque = deque(maxlen=history_size)
        self.memory_history: deque = deque(maxlen=history_size)
        self.cpu_history: deque = deque(maxlen=history_size)
        
        logger.info("Hardware Predictor initialized")
    
    def _calculate_trend(self, values: List[float]) -> float:
        """Рассчитать тренд (наклон линии)"""
        if len(values) < 2:
            return 0.0
        
        n = len(values)
        x_sum = sum(range(n))
        y_sum = sum(values)
        xy_sum = sum(i * v for i, v in enumerate(values))
        x2_sum = sum(i * i for i in range(n))
        
        numerator = n * xy_sum - x_sum * y_sum
        denominator = n * x2_sum - x_sum * x_sum
        
        if denominator == 0:
            return 0.0
        
        return numerator / denominator
    
    def predict_disk_full(self, days: int = 7) -> Optional[str]:
        """Предсказать, когда диск заполнится"""
        disk_metrics = self.monitor.get_disk_metrics()
        
        if not disk_metrics:
            return None
        
        # Берём первый диск (обычно root)
        disk = disk_metrics[0]
        
        # Собираем историю
        self.disk_history.append((time.time(), disk.percent))
        
        if len(self.disk_history) < 10:
            return None
        
        # Рассчитываем тренд
        values = [v for _, v in self.disk_history]
        trend = self._calculate_trend(values)
        
        if trend <= 0:
            return "Disk usage is stable or decreasing"
        
        # Предсказываем время заполнения
        current_percent = disk.percent
        percent_per_second = trend / len(self.disk_history)
        
        if percent_per_second <= 0:
            return "Disk will not fill at current rate"
        
        seconds_to_full = (100 - current_percent) / percent_per_second
        hours_to_full = seconds_to_full / 3600
        days_to_full = hours_to_full / 24
        
        if days_to_full < 0:
            return None
        
        if days_to_full < 1:
            return f"⚠️ CRITICAL: Disk will be full in {hours_to_full:.1f} hours!"
        elif days_to_full < days:
            return f"⚠️ WARNING: Disk will be full in {days_to_full:.1f} days"
        else:
            return f"Disk usage is normal (will fill in {days_to_full:.1f} days)"
    
    def predict_memory_pressure(self) -> Optional[str]:
        """Предсказать нехватку памяти"""
        memory = self.monitor.get_memory_metrics()
        
        self.memory_history.append((time.time(), memory.percent))
        
        if len(self.memory_history) < 10:
            return None
        
        values = [v for _, v in self.memory_history]
        trend = self._calculate_trend(values)
        
        if memory.percent > 90:
            return f"🔴 CRITICAL: Memory usage is {memory.percent:.1f}%"
        elif memory.percent > 80:
            return f"🟠 WARNING: Memory usage is {memory.percent:.1f}%"
        elif trend > 0:
            return f"Memory usage is increasing ({trend:.2f}%/sample)"
        else:
            return f"Memory usage is stable at {memory.percent:.1f}%"
    
    def predict_cpu_load(self) -> Optional[str]:
        """Предсказать нагрузку на CPU"""
        cpu = self.monitor.get_cpu_metrics()
        
        self.cpu_history.append((time.time(), cpu.percent))
        
        if len(self.cpu_history) < 10:
            return None
        
        values = [v for _, v in self.cpu_history]
        trend = self._calculate_trend(values)
        avg_cpu = sum(values) / len(values)
        
        if cpu.percent > 90:
            return f"🔴 CRITICAL: CPU usage is {cpu.percent:.1f}%"
        elif cpu.percent > 80:
            return f"🟠 WARNING: CPU usage is {cpu.percent:.1f}%"
        elif trend > 0.5:
            return f"CPU load is increasing rapidly ({trend:.2f}%/sample)"
        elif avg_cpu > 70:
            return f"CPU is under sustained load (avg: {avg_cpu:.1f}%)"
        else:
            return f"CPU usage is normal ({cpu.percent:.1f}%)"
    
    def get_predictions(self) -> Dict[str, str]:
        """Получить все предсказания"""
        return {
            'disk': self.predict_disk_full() or "No disk prediction",
            'memory': self.predict_memory_pressure() or "Memory is normal",
            'cpu': self.predict_cpu_load() or "CPU is normal"
        }


class AdvancedHardwareMonitor:
    """Продвинутый мониторинг оборудования"""
    
    def __init__(self):
        """Инициализация"""
        self.monitor = RealHardwareMonitor()
        self.predictor = HardwarePredictor()
        self.alerts: List[Alert] = []
        self.alert_rules: Dict[str, AlertRule] = {}
        self.metric_history: Dict[str, MetricHistory] = {}
        self.alert_callbacks: List[Callable] = []
        self.lock = threading.Lock()
        self.monitoring = False
        self.monitor_thread = None
        
        logger.info("Advanced Hardware Monitor initialized")
    
    def add_alert_rule(self, metric_type: str, threshold: float,
                      severity: AlertSeverity = AlertSeverity.WARNING) -> bool:
        """Добавить правило алерта"""
        rule = AlertRule(metric_type, threshold, severity)
        with self.lock:
            self.alert_rules[f"{metric_type}_{threshold}"] = rule
        logger.info(f"Alert rule added: {metric_type} > {threshold}")
        return True
    
    def remove_alert_rule(self, metric_type: str, threshold: float) -> bool:
        """Удалить правило алерта"""
        key = f"{metric_type}_{threshold}"
        with self.lock:
            if key in self.alert_rules:
                del self.alert_rules[key]
                logger.info(f"Alert rule removed: {key}")
                return True
        return False
    
    def register_alert_callback(self, callback: Callable) -> bool:
        """Зарегистрировать callback для алертов"""
        with self.lock:
            self.alert_callbacks.append(callback)
        logger.info("Alert callback registered")
        return True
    
    def _check_alerts(self):
        """Проверить все правила алертов"""
        cpu = self.monitor.get_cpu_metrics()
        memory = self.monitor.get_memory_metrics()
        disk_list = self.monitor.get_disk_metrics()
        
        with self.lock:
            # Проверяем CPU
            for rule_key, rule in self.alert_rules.items():
                if rule.metric_type == "cpu" and rule.check(cpu.percent):
                    if not rule.triggered:
                        self._trigger_alert(
                            "CPU Alert",
                            f"CPU usage is {cpu.percent:.1f}%",
                            rule.severity,
                            cpu.percent,
                            rule.threshold,
                            "cpu"
                        )
                        rule.triggered = True
                        rule.last_trigger_time = datetime.now()
                elif rule.metric_type == "cpu" and not rule.check(cpu.percent):
                    rule.triggered = False
            
            # Проверяем Memory
            for rule_key, rule in self.alert_rules.items():
                if rule.metric_type == "memory" and rule.check(memory.percent):
                    if not rule.triggered:
                        self._trigger_alert(
                            "Memory Alert",
                            f"Memory usage is {memory.percent:.1f}%",
                            rule.severity,
                            memory.percent,
                            rule.threshold,
                            "memory"
                        )
                        rule.triggered = True
                        rule.last_trigger_time = datetime.now()
                elif rule.metric_type == "memory" and not rule.check(memory.percent):
                    rule.triggered = False
            
            # Проверяем Disk
            for disk in disk_list:
                for rule_key, rule in self.alert_rules.items():
                    if rule.metric_type == "disk" and rule.check(disk.percent):
                        if not rule.triggered:
                            self._trigger_alert(
                                "Disk Alert",
                                f"Disk usage is {disk.percent:.1f}% on {disk.mount_point}",
                                rule.severity,
                                disk.percent,
                                rule.threshold,
                                "disk"
                            )
                            rule.triggered = True
                            rule.last_trigger_time = datetime.now()
                    elif rule.metric_type == "disk" and not rule.check(disk.percent):
                        rule.triggered = False
    
    def _trigger_alert(self, name: str, message: str, severity: AlertSeverity,
                      value: float, threshold: float, metric_type: str):
        """Триггер алерта"""
        alert = Alert(
            name=name,
            message=message,
            severity=severity,
            timestamp=datetime.now(),
            value=value,
            threshold=threshold,
            metric_type=metric_type
        )
        
        self.alerts.append(alert)
        logger.warning(f"ALERT: {name} - {message}")
        
        # Вызываем callbacks
        for callback in self.alert_callbacks:
            try:
                callback(alert)
            except Exception as e:
                logger.error(f"Error in alert callback: {e}")
    
    def start_monitoring(self, interval: int = 5):
        """Начать мониторинг"""
        if self.monitoring:
            logger.warning("Monitoring already running")
            return False
        
        self.monitoring = True
        self.monitor_thread = threading.Thread(
            target=self._monitoring_loop,
            args=(interval,),
            daemon=True
        )
        self.monitor_thread.start()
        logger.info(f"Monitoring started (interval: {interval}s)")
        return True
    
    def _monitoring_loop(self, interval: int):
        """Цикл мониторинга"""
        while self.monitoring:
            try:
                self._check_alerts()
                time.sleep(interval)
            except Exception as e:
                logger.error(f"Error in monitoring loop: {e}")
    
    def stop_monitoring(self):
        """Остановить мониторинг"""
        self.monitoring = False
        if self.monitor_thread:
            self.monitor_thread.join(timeout=5)
        logger.info("Monitoring stopped")
    
    def get_alerts(self, limit: int = 100) -> List[Alert]:
        """Получить последние алерты"""
        with self.lock:
            return self.alerts[-limit:] if self.alerts else []
    
    def get_active_alerts(self) -> List[Alert]:
        """Получить активные алерты"""
        with self.lock:
            now = datetime.now()
            # Алерты активны если они были в последние 5 минут
            return [a for a in self.alerts if (now - a.timestamp).seconds < 300]
    
    def clear_alerts(self):
        """Очистить историю алертов"""
        with self.lock:
            self.alerts.clear()
        logger.info("Alerts cleared")
    
    def get_health_status(self) -> Dict:
        """Получить статус здоровья системы"""
        cpu = self.monitor.get_cpu_metrics()
        memory = self.monitor.get_memory_metrics()
        disk_list = self.monitor.get_disk_metrics()
        
        predictions = self.predictor.get_predictions()
        active_alerts = self.get_active_alerts()
        
        return {
            'timestamp': datetime.now().isoformat(),
            'cpu': {
                'usage': cpu.percent,
                'status': 'critical' if cpu.percent > 90 else 'warning' if cpu.percent > 80 else 'ok'
            },
            'memory': {
                'usage': memory.percent,
                'status': 'critical' if memory.percent > 90 else 'warning' if memory.percent > 80 else 'ok'
            },
            'disk': {
                'usage': disk_list[0].percent if disk_list else 0,
                'status': 'critical' if disk_list and disk_list[0].percent > 90 else 'warning' if disk_list and disk_list[0].percent > 80 else 'ok'
            },
            'predictions': predictions,
            'active_alerts': len(active_alerts),
            'total_alerts': len(self.alerts)
        }
