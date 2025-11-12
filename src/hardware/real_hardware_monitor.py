"""
Real Hardware Monitor for Daur-AI v2.0
Полнофункциональный модуль мониторинга оборудования

Поддерживает:
- Мониторинг CPU (процент, частота, температура, ядра)
- Мониторинг памяти (RAM, использование, доступно)
- Мониторинг дисков (все разделы, использование, скорость)
- Мониторинг GPU NVIDIA (память, температура, мощность)
- Мониторинг батареи (процент, статус, время)
- Мониторинг сети (интерфейсы, трафик, ошибки)
- Топ процессов по CPU и памяти
- Непрерывный мониторинг в отдельном потоке
- История метрик
- Экспорт в JSON
"""

import psutil
import json
import logging
import threading
import time
from datetime import datetime
from typing import Dict, List, Optional, Tuple
from dataclasses import dataclass, asdict, field
from enum import Enum
from collections import deque
import subprocess
import os
import platform

# Настройка логирования
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class CPUFreqMode(Enum):
    """Режимы частоты CPU"""
    CURRENT = "current"
    MIN = "min"
    MAX = "max"


@dataclass
class CPUMetrics:
    """Метрики CPU"""
    timestamp: str
    percent: float  # Процент использования (0-100)
    percent_per_core: List[float]  # Процент на каждое ядро
    count_logical: int  # Количество логических ядер
    count_physical: int  # Количество физических ядер
    freq_current: float  # Текущая частота в МГц
    freq_min: float  # Минимальная частота в МГц
    freq_max: float  # Максимальная частота в МГц
    temperature: Optional[float] = None  # Температура в градусах Цельсия
    
    def to_dict(self):
        return asdict(self)
    
    def __getitem__(self, key):
        """Allow dict-like access"""
        return getattr(self, key)


@dataclass
class MemoryMetrics:
    """Метрики памяти"""
    timestamp: str
    total: int  # Всего памяти в байтах
    available: int  # Доступно в байтах
    used: int  # Использовано в байтах
    free: int  # Свободно в байтах
    percent: float  # Процент использования (0-100)
    
    def to_dict(self):
        return asdict(self)
    
    def __getitem__(self, key):
        """Allow dict-like access"""
        return getattr(self, key)


@dataclass
class DiskMetrics:
    """Метрики диска"""
    timestamp: str
    device: str  # Устройство (например, /dev/sda1)
    mount_point: str  # Точка монтирования
    total: int  # Всего в байтах
    used: int  # Использовано в байтах
    free: int  # Свободно в байтах
    percent: float  # Процент использования (0-100)
    read_speed: float = 0  # Скорость чтения в байт/сек
    write_speed: float = 0  # Скорость записи в байт/сек
    
    def to_dict(self):
        return asdict(self)
    
    def __getitem__(self, key):
        """Allow dict-like access"""
        return getattr(self, key)


@dataclass
class GPUMetrics:
    """Метрики GPU"""
    timestamp: str
    index: int  # Индекс GPU
    name: str  # Название GPU
    memory_total: int  # Всего памяти в МБ
    memory_used: int  # Использовано в МБ
    memory_free: int  # Свободно в МБ
    temperature: float  # Температура в градусах Цельсия
    power_draw: float  # Потребление мощности в Вт
    power_limit: float  # Лимит мощности в Вт
    utilization: float  # Процент использования (0-100)
    
    def to_dict(self):
        return asdict(self)
    
    def __getitem__(self, key):
        """Allow dict-like access"""
        return getattr(self, key)


@dataclass
class BatteryMetrics:
    """Метрики батареи"""
    timestamp: str
    percent: float  # Процент заряда (0-100)
    is_plugged: bool  # Подключена ли к сети
    status: str  # Статус (charging, discharging, full, unknown)
    time_left: Optional[int] = None  # Примерное время до разрядки в секундах
    
    def to_dict(self):
        return asdict(self)
    
    def __getitem__(self, key):
        """Allow dict-like access"""
        return getattr(self, key)


@dataclass
class NetworkMetrics:
    """Метрики сети"""
    timestamp: str
    interface: str  # Название интерфейса
    bytes_sent: int  # Отправлено байт
    bytes_recv: int  # Получено байт
    packets_sent: int  # Отправлено пакетов
    packets_recv: int  # Получено пакетов
    errin: int  # Ошибки входящих
    errout: int  # Ошибки исходящих
    dropin: int  # Потеряно входящих пакетов
    dropout: int  # Потеряно исходящих пакетов
    
    def to_dict(self):
        return asdict(self)
    
    def __getitem__(self, key):
        """Allow dict-like access"""
        return getattr(self, key)


@dataclass
class ProcessMetrics:
    """Метрики процесса"""
    timestamp: str
    pid: int  # ID процесса
    name: str  # Имя процесса
    cpu_percent: float  # Процент CPU
    memory_percent: float  # Процент памяти
    memory_mb: float  # Использовано памяти в МБ
    
    def to_dict(self):
        return asdict(self)


class RealHardwareMonitor:
    """Полнофункциональный монитор оборудования"""
    
    def __init__(self, history_size: int = 1000):
        """
        Инициализация монитора
        
        Args:
            history_size: Размер истории для каждого типа метрик
        """
        self.history_size = history_size
        self.cpu_history: deque = deque(maxlen=history_size)
        self.memory_history: deque = deque(maxlen=history_size)
        self.disk_history: deque = deque(maxlen=history_size)
        self.gpu_history: deque = deque(maxlen=history_size)
        self.battery_history: deque = deque(maxlen=history_size)
        self.network_history: deque = deque(maxlen=history_size)
        self.process_history: deque = deque(maxlen=history_size)
        
        self.monitoring = False
        self.monitor_thread = None
        self.lock = threading.Lock()
        
        # Для расчёта скорости диска
        self.last_disk_io = {}
        self.last_disk_io_time = time.time()
        
        # Для расчёта скорости сети
        self.last_net_io = {}
        self.last_net_io_time = time.time()
        
        logger.info("Real Hardware Monitor initialized")
    
    def get_cpu_metrics(self) -> CPUMetrics:
        """Получить метрики CPU"""
        try:
            percent = psutil.cpu_percent(interval=0.1)
            percent_per_core = psutil.cpu_percent(interval=0.1, percpu=True)
            count_logical = psutil.cpu_count(logical=True)
            count_physical = psutil.cpu_count(logical=False)
            
            freq = psutil.cpu_freq()
            freq_current = freq.current if freq else 0
            freq_min = freq.min if freq else 0
            freq_max = freq.max if freq else 0
            
            # Попытка получить температуру
            temperature = None
            try:
                temps = psutil.sensors_temperatures()
                if temps:
                    # Берём среднюю температуру
                    all_temps = []
                    for name, entries in temps.items():
                        for entry in entries:
                            all_temps.append(entry.current)
                    if all_temps:
                        temperature = sum(all_temps) / len(all_temps)
            except Exception as e:
                logger.debug(f"Could not get CPU temperature: {e}")
            
            metrics = CPUMetrics(
                timestamp=datetime.now().isoformat(),
                percent=percent,
                percent_per_core=percent_per_core,
                count_logical=count_logical,
                count_physical=count_physical,
                freq_current=freq_current,
                freq_min=freq_min,
                freq_max=freq_max,
                temperature=temperature
            )
            
            with self.lock:
                self.cpu_history.append(metrics)
            
            logger.debug(f"CPU: {percent}% @ {freq_current:.0f}MHz")
            return metrics
        except Exception as e:
            logger.error(f"Error getting CPU metrics: {e}")
            return None
    
    def get_memory_metrics(self) -> MemoryMetrics:
        """Получить метрики памяти"""
        try:
            mem = psutil.virtual_memory()
            
            metrics = MemoryMetrics(
                timestamp=datetime.now().isoformat(),
                total=mem.total,
                available=mem.available,
                used=mem.used,
                free=mem.free,
                percent=mem.percent
            )
            
            with self.lock:
                self.memory_history.append(metrics)
            
            logger.debug(f"Memory: {mem.percent}% ({mem.used / (1024**3):.1f}GB / {mem.total / (1024**3):.1f}GB)")
            return metrics
        except Exception as e:
            logger.error(f"Error getting memory metrics: {e}")
            return None
    
    def get_disk_metrics(self) -> List[DiskMetrics]:
        """Получить метрики дисков"""
        try:
            metrics_list = []
            current_time = time.time()
            
            for partition in psutil.disk_partitions():
                try:
                    usage = psutil.disk_usage(partition.mountpoint)
                    
                    # Расчёт скорости
                    read_speed = 0
                    write_speed = 0
                    
                    try:
                        io_counters = psutil.disk_io_counters(perdisk=True)
                        if partition.device in io_counters:
                            current_io = io_counters[partition.device]
                            if partition.device in self.last_disk_io:
                                time_delta = current_time - self.last_disk_io_time
                                if time_delta > 0:
                                    read_speed = (current_io.read_bytes - self.last_disk_io[partition.device].read_bytes) / time_delta
                                    write_speed = (current_io.write_bytes - self.last_disk_io[partition.device].write_bytes) / time_delta
                            self.last_disk_io[partition.device] = current_io
                    except Exception as e:
                        logger.debug(f"Could not get disk IO speed: {e}")
                    
                    metrics = DiskMetrics(
                        timestamp=datetime.now().isoformat(),
                        device=partition.device,
                        mount_point=partition.mountpoint,
                        total=usage.total,
                        used=usage.used,
                        free=usage.free,
                        percent=usage.percent,
                        read_speed=read_speed,
                        write_speed=write_speed
                    )
                    
                    metrics_list.append(metrics)
                except Exception as e:
                    logger.debug(f"Error getting metrics for {partition.device}: {e}")
            
            self.last_disk_io_time = current_time
            
            with self.lock:
                for metrics in metrics_list:
                    self.disk_history.append(metrics)
            
            logger.debug(f"Disk: {len(metrics_list)} partitions")
            return metrics_list
        except Exception as e:
            logger.error(f"Error getting disk metrics: {e}")
            return []
    
    def get_gpu_metrics(self) -> List[GPUMetrics]:
        """Получить метрики GPU NVIDIA"""
        try:
            metrics_list = []
            
            # Используем nvidia-smi для получения информации о GPU
            try:
                result = subprocess.run(
                    ['nvidia-smi', '--query-gpu=index,name,memory.total,memory.used,memory.free,temperature.gpu,power.draw,power.limit,utilization.gpu',
                     '--format=csv,noheader,nounits'],
                    capture_output=True,
                    text=True,
                    timeout=5
                )
                
                if result.returncode == 0:
                    for line in result.stdout.strip().split('\n'):
                        if line:
                            parts = [p.strip() for p in line.split(',')]
                            if len(parts) >= 9:
                                metrics = GPUMetrics(
                                    timestamp=datetime.now().isoformat(),
                                    index=int(parts[0]),
                                    name=parts[1],
                                    memory_total=int(float(parts[2])),
                                    memory_used=int(float(parts[3])),
                                    memory_free=int(float(parts[4])),
                                    temperature=float(parts[5]),
                                    power_draw=float(parts[6]),
                                    power_limit=float(parts[7]),
                                    utilization=float(parts[8])
                                )
                                metrics_list.append(metrics)
            except (FileNotFoundError, subprocess.TimeoutExpired):
                logger.debug("nvidia-smi not found or timed out")
            
            with self.lock:
                for metrics in metrics_list:
                    self.gpu_history.append(metrics)
            
            if metrics_list:
                logger.debug(f"GPU: {len(metrics_list)} GPUs found")
            
            return metrics_list
        except Exception as e:
            logger.error(f"Error getting GPU metrics: {e}")
            return []
    
    def get_battery_metrics(self) -> Optional[BatteryMetrics]:
        """Получить метрики батареи"""
        try:
            battery = psutil.sensors_battery()
            if battery is None:
                return None
            
            status_map = {
                0: "charging",
                1: "discharging",
                2: "full",
                3: "unknown"
            }
            
            metrics = BatteryMetrics(
                timestamp=datetime.now().isoformat(),
                percent=battery.percent,
                status=status_map.get(battery.power_plugged, "unknown"),
                time_remaining=battery.secsleft if battery.secsleft != psutil.POWER_TIME_UNLIMITED else None,
                power_plugged=battery.power_plugged
            )
            
            with self.lock:
                self.battery_history.append(metrics)
            
            logger.debug(f"Battery: {battery.percent}% ({metrics.status})")
            return metrics
        except Exception as e:
            logger.debug(f"Error getting battery metrics: {e}")
            return None
    
    def get_network_metrics(self) -> List[NetworkMetrics]:
        """Получить метрики сети"""
        try:
            metrics_list = []
            current_time = time.time()
            
            net_io = psutil.net_io_counters(pernic=True)
            
            for interface, stats in net_io.items():
                metrics = NetworkMetrics(
                    timestamp=datetime.now().isoformat(),
                    interface=interface,
                    bytes_sent=stats.bytes_sent,
                    bytes_recv=stats.bytes_recv,
                    packets_sent=stats.packets_sent,
                    packets_recv=stats.packets_recv,
                    errin=stats.errin,
                    errout=stats.errout,
                    dropin=stats.dropin,
                    dropout=stats.dropout
                )
                metrics_list.append(metrics)
            
            self.last_net_io_time = current_time
            
            with self.lock:
                for metrics in metrics_list:
                    self.network_history.append(metrics)
            
            logger.debug(f"Network: {len(metrics_list)} interfaces")
            return metrics_list
        except Exception as e:
            logger.error(f"Error getting network metrics: {e}")
            return []
    
    def get_top_processes(self, limit: int = 10, sort_by: str = "cpu") -> List[ProcessMetrics]:
        """Получить топ процессов"""
        try:
            processes = []
            
            for proc in psutil.process_iter(['pid', 'name', 'cpu_percent', 'memory_percent']):
                try:
                    pinfo = proc.as_dict(attrs=['pid', 'name', 'cpu_percent', 'memory_percent'])
                    if pinfo['cpu_percent'] is not None and pinfo['memory_percent'] is not None:
                        processes.append(pinfo)
                except (psutil.NoSuchProcess, psutil.AccessDenied):
                    pass
            
            # Сортируем по CPU или памяти
            if sort_by == "memory":
                processes.sort(key=lambda x: x['memory_percent'], reverse=True)
            else:
                processes.sort(key=lambda x: x['cpu_percent'], reverse=True)
            
            metrics_list = []
            for proc in processes[:limit]:
                try:
                    p = psutil.Process(proc['pid'])
                    memory_mb = p.memory_info().rss / (1024 * 1024)
                    
                    metrics = ProcessMetrics(
                        timestamp=datetime.now().isoformat(),
                        pid=proc['pid'],
                        name=proc['name'],
                        cpu_percent=proc['cpu_percent'],
                        memory_percent=proc['memory_percent'],
                        memory_mb=memory_mb
                    )
                    metrics_list.append(metrics)
                except (psutil.NoSuchProcess, psutil.AccessDenied):
                    pass
            
            with self.lock:
                for metrics in metrics_list:
                    self.process_history.append(metrics)
            
            logger.debug(f"Top {limit} processes by {sort_by}")
            return metrics_list
        except Exception as e:
            logger.error(f"Error getting process metrics: {e}")
            return []
    
    def get_full_status(self) -> Dict:
        """Получить полный статус системы"""
        return {
            "timestamp": datetime.now().isoformat(),
            "cpu": self.get_cpu_metrics().to_dict() if self.get_cpu_metrics() else None,
            "memory": self.get_memory_metrics().to_dict() if self.get_memory_metrics() else None,
            "disks": [m.to_dict() for m in self.get_disk_metrics()],
            "gpus": [m.to_dict() for m in self.get_gpu_metrics()],
            "battery": self.get_battery_metrics().to_dict() if self.get_battery_metrics() else None,
            "network": [m.to_dict() for m in self.get_network_metrics()],
            "top_processes_cpu": [m.to_dict() for m in self.get_top_processes(limit=5, sort_by="cpu")],
            "top_processes_memory": [m.to_dict() for m in self.get_top_processes(limit=5, sort_by="memory")]
        }
    
    def start_monitoring(self, interval: int = 5):
        """Начать непрерывный мониторинг"""
        if self.monitoring:
            logger.warning("Monitoring already started")
            return
        
        self.monitoring = True
        self.monitor_thread = threading.Thread(target=self._monitor_loop, args=(interval,), daemon=True)
        self.monitor_thread.start()
        logger.info(f"Monitoring started with interval {interval}s")
    
    def stop_monitoring(self):
        """Остановить мониторинг"""
        self.monitoring = False
        if self.monitor_thread:
            self.monitor_thread.join(timeout=5)
        logger.info("Monitoring stopped")
    
    def _monitor_loop(self, interval: int):
        """Цикл мониторинга"""
        while self.monitoring:
            try:
                self.get_cpu_metrics()
                self.get_memory_metrics()
                self.get_disk_metrics()
                self.get_gpu_metrics()
                self.get_battery_metrics()
                self.get_network_metrics()
                self.get_top_processes(limit=5)
                
                time.sleep(interval)
            except Exception as e:
                logger.error(f"Error in monitoring loop: {e}")
                time.sleep(interval)
    
    def save_metrics(self, filepath: str):
        """Сохранить метрики в JSON"""
        try:
            data = {
                "timestamp": datetime.now().isoformat(),
                "cpu": [m.to_dict() for m in self.cpu_history],
                "memory": [m.to_dict() for m in self.memory_history],
                "disk": [m.to_dict() for m in self.disk_history],
                "gpu": [m.to_dict() for m in self.gpu_history],
                "battery": [m.to_dict() for m in self.battery_history],
                "network": [m.to_dict() for m in self.network_history],
                "process": [m.to_dict() for m in self.process_history]
            }
            
            with open(filepath, 'w') as f:
                json.dump(data, f, indent=2)
            
            logger.info(f"Metrics saved to {filepath}")
            return True
        except Exception as e:
            logger.error(f"Error saving metrics: {e}")
            return False
    
    def get_history(self, metric_type: str, limit: int = 100) -> List:
        """Получить историю метрик"""
        history_map = {
            "cpu": self.cpu_history,
            "memory": self.memory_history,
            "disk": self.disk_history,
            "gpu": self.gpu_history,
            "battery": self.battery_history,
            "network": self.network_history,
            "process": self.process_history
        }
        
        history = history_map.get(metric_type, [])
        return list(history)[-limit:] if history else []
    
    def cleanup(self):
        """Очистить ресурсы"""
        self.stop_monitoring()
        logger.info("Hardware Monitor cleaned up")


# Экспорт основных классов
__all__ = [
    'RealHardwareMonitor',
    'CPUMetrics',
    'MemoryMetrics',
    'DiskMetrics',
    'GPUMetrics',
    'BatteryMetrics',
    'NetworkMetrics',
    'ProcessMetrics'
]

