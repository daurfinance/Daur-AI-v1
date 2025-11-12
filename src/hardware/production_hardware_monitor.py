"""
Production-Grade Hardware Monitor for Daur-AI v2.0
Полнофункциональный монитор оборудования с реальным мониторингом
"""

import psutil
import platform
import subprocess
import json
import logging
from datetime import datetime
from typing import Dict, List, Optional, Tuple
from dataclasses import dataclass, asdict, field
import threading
import time
from collections import deque

# Настройка логирования
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


@dataclass
class CPUInfo:
    """Информация о CPU"""
    percent: float
    count_physical: int
    count_logical: int
    freq_current: float
    freq_max: float
    temp: Optional[float] = None
    
    def to_dict(self):
        return asdict(self)


@dataclass
class MemoryInfo:
    """Информация о памяти"""
    total: int
    available: int
    percent: float
    used: int
    free: int
    
    def to_dict(self):
        return asdict(self)


@dataclass
class DiskInfo:
    """Информация о диске"""
    device: str
    mountpoint: str
    fstype: str
    total: int
    used: int
    free: int
    percent: float
    
    def to_dict(self):
        return asdict(self)


@dataclass
class GPUInfo:
    """Информация о GPU"""
    name: str
    memory_total: int
    memory_used: int
    memory_free: int
    memory_percent: float
    temperature: Optional[float] = None
    power_draw: Optional[float] = None
    
    def to_dict(self):
        return asdict(self)


@dataclass
class BatteryInfo:
    """Информация о батарее"""
    percent: float
    is_charging: bool
    power_plugged: bool
    time_left: Optional[int] = None
    status: str = "unknown"
    
    def to_dict(self):
        return asdict(self)


@dataclass
class NetworkInfo:
    """Информация о сети"""
    interface: str
    is_up: bool
    speed: int
    mtu: int
    bytes_sent: int
    bytes_recv: int
    packets_sent: int
    packets_recv: int
    errin: int
    errout: int
    dropin: int
    dropout: int
    
    def to_dict(self):
        return asdict(self)


@dataclass
class ProcessInfo:
    """Информация о процессе"""
    pid: int
    name: str
    status: str
    cpu_percent: float
    memory_percent: float
    memory_rss: int
    create_time: float
    
    def to_dict(self):
        return asdict(self)


class ProductionHardwareMonitor:
    """Полнофункциональный монитор оборудования"""
    
    def __init__(self, history_size: int = 100):
        self.history_size = history_size
        self.cpu_history: deque = deque(maxlen=history_size)
        self.memory_history: deque = deque(maxlen=history_size)
        self.disk_history: deque = deque(maxlen=history_size)
        self.gpu_history: deque = deque(maxlen=history_size)
        self.battery_history: deque = deque(maxlen=history_size)
        self.network_history: deque = deque(maxlen=history_size)
        
        self.is_monitoring = False
        self.monitor_thread = None
        self.monitor_interval = 1.0  # Секунды
    
    def get_cpu_info(self) -> CPUInfo:
        """Получить информацию о CPU"""
        try:
            cpu_percent = psutil.cpu_percent(interval=0.1)
            cpu_count_physical = psutil.cpu_count(logical=False) or 1
            cpu_count_logical = psutil.cpu_count(logical=True) or 1
            cpu_freq = psutil.cpu_freq()
            
            cpu_temp = None
            try:
                temps = psutil.sensors_temperatures()
                if 'coretemp' in temps:
                    cpu_temp = temps['coretemp'][0].current
                elif 'acpitz' in temps:
                    cpu_temp = temps['acpitz'][0].current
            except Exception as e:
                pass
            
            info = CPUInfo(
                percent=cpu_percent,
                count_physical=cpu_count_physical,
                count_logical=cpu_count_logical,
                freq_current=cpu_freq.current if cpu_freq else 0,
                freq_max=cpu_freq.max if cpu_freq else 0,
                temp=cpu_temp
            )
            
            self.cpu_history.append({
                'timestamp': datetime.now().isoformat(),
                'data': info.to_dict()
            })
            
            logger.info(f"CPU: {cpu_percent}%, Temp: {cpu_temp}°C")
            return info
        except Exception as e:
            logger.error(f"Error getting CPU info: {e}")
            return None
    
    def get_memory_info(self) -> MemoryInfo:
        """Получить информацию о памяти"""
        try:
            mem = psutil.virtual_memory()
            
            info = MemoryInfo(
                total=mem.total,
                available=mem.available,
                percent=mem.percent,
                used=mem.used,
                free=mem.free
            )
            
            self.memory_history.append({
                'timestamp': datetime.now().isoformat(),
                'data': info.to_dict()
            })
            
            logger.info(f"Memory: {mem.percent}% ({mem.used / (1024**3):.2f} GB / {mem.total / (1024**3):.2f} GB)")
            return info
        except Exception as e:
            logger.error(f"Error getting memory info: {e}")
            return None
    
    def get_disk_info(self) -> List[DiskInfo]:
        """Получить информацию о дисках"""
        try:
            disks_info = []
            partitions = psutil.disk_partitions()
            
            for partition in partitions:
                try:
                    usage = psutil.disk_usage(partition.mountpoint)
                    
                    info = DiskInfo(
                        device=partition.device,
                        mountpoint=partition.mountpoint,
                        fstype=partition.fstype,
                        total=usage.total,
                        used=usage.used,
                        free=usage.free,
                        percent=usage.percent
                    )
                    disks_info.append(info)
                    logger.info(f"Disk {partition.device}: {usage.percent}% ({usage.used / (1024**3):.2f} GB / {usage.total / (1024**3):.2f} GB)")
                except PermissionError:
                    continue
            
            self.disk_history.append({
                'timestamp': datetime.now().isoformat(),
                'data': [d.to_dict() for d in disks_info]
            })
            
            return disks_info
        except Exception as e:
            logger.error(f"Error getting disk info: {e}")
            return []
    
    def get_gpu_info(self) -> Optional[List[GPUInfo]]:
        """Получить информацию о GPU (NVIDIA)"""
        try:
            gpus_info = []
            
            # Проверяем NVIDIA GPU
            try:
                result = subprocess.run(
                    ['nvidia-smi', '--query-gpu=index,name,memory.total,memory.used,memory.free,temperature.gpu,power.draw',
                     '--format=csv,noheader,nounits'],
                    capture_output=True,
                    text=True,
                    timeout=5
                )
                
                if result.returncode == 0:
                    for line in result.stdout.strip().split('\n'):
                        if line:
                            parts = [p.strip() for p in line.split(',')]
                            if len(parts) >= 7:
                                try:
                                    info = GPUInfo(
                                        name=parts[1],
                                        memory_total=int(float(parts[2])) * 1024 * 1024,  # MB to bytes
                                        memory_used=int(float(parts[3])) * 1024 * 1024,
                                        memory_free=int(float(parts[4])) * 1024 * 1024,
                                        memory_percent=(int(float(parts[3])) / int(float(parts[2])) * 100) if int(float(parts[2])) > 0 else 0,
                                        temperature=float(parts[5]) if parts[5] != 'N/A' else None,
                                        power_draw=float(parts[6]) if parts[6] != 'N/A' else None
                                    )
                                    gpus_info.append(info)
                                    logger.info(f"GPU {parts[1]}: {info.memory_percent:.1f}% Memory, Temp: {info.temperature}°C")
                                except (ValueError, IndexError):
                                    continue
            except (FileNotFoundError, subprocess.TimeoutExpired):
                logger.warning("NVIDIA GPU not found or nvidia-smi not available")
            
            if gpus_info:
                self.gpu_history.append({
                    'timestamp': datetime.now().isoformat(),
                    'data': [g.to_dict() for g in gpus_info]
                })
                return gpus_info
            
            return None
        except Exception as e:
            logger.error(f"Error getting GPU info: {e}")
            return None
    
    def get_battery_info(self) -> Optional[BatteryInfo]:
        """Получить информацию о батарее"""
        try:
            battery = psutil.sensors_battery()
            
            if battery is None:
                logger.warning("No battery found (desktop system)")
                return None
            
            # Определяем статус батареи
            if battery.power_plugged:
                status = "charging" if battery.percent < 100 else "charged"
            else:
                status = "discharging"
            
            info = BatteryInfo(
                percent=battery.percent,
                is_charging=not battery.power_plugged,
                power_plugged=battery.power_plugged,
                time_left=battery.secsleft if battery.secsleft != psutil.POWER_TIME_UNLIMITED else None,
                status=status
            )
            
            self.battery_history.append({
                'timestamp': datetime.now().isoformat(),
                'data': info.to_dict()
            })
            
            logger.info(f"Battery: {battery.percent}%, Status: {status}, Time left: {battery.secsleft}s")
            return info
        except Exception as e:
            logger.error(f"Error getting battery info: {e}")
            return None
    
    def get_network_info(self) -> List[NetworkInfo]:
        """Получить информацию о сети"""
        try:
            networks_info = []
            stats = psutil.net_if_stats()
            io_counters = psutil.net_io_counters(pernic=True)
            
            for interface, stat in stats.items():
                try:
                    io = io_counters.get(interface)
                    
                    info = NetworkInfo(
                        interface=interface,
                        is_up=stat.isup,
                        speed=stat.speed,
                        mtu=stat.mtu,
                        bytes_sent=io.bytes_sent if io else 0,
                        bytes_recv=io.bytes_recv if io else 0,
                        packets_sent=io.packets_sent if io else 0,
                        packets_recv=io.packets_recv if io else 0,
                        errin=io.errin if io else 0,
                        errout=io.errout if io else 0,
                        dropin=io.dropin if io else 0,
                        dropout=io.dropout if io else 0
                    )
                    networks_info.append(info)
                    logger.info(f"Network {interface}: Up={stat.isup}, Speed={stat.speed} Mbps")
                except Exception as e:
                    logger.warning(f"Error getting info for interface {interface}: {e}")
            
            self.network_history.append({
                'timestamp': datetime.now().isoformat(),
                'data': [n.to_dict() for n in networks_info]
            })
            
            return networks_info
        except Exception as e:
            logger.error(f"Error getting network info: {e}")
            return []
    
    def get_top_processes(self, n: int = 10) -> List[ProcessInfo]:
        """Получить топ процессов по использованию CPU"""
        try:
            processes_info = []
            
            for proc in psutil.process_iter(['pid', 'name', 'status', 'cpu_percent', 'memory_percent', 'memory_rss', 'create_time']):
                try:
                    info = ProcessInfo(
                        pid=proc.info['pid'],
                        name=proc.info['name'],
                        status=proc.info['status'],
                        cpu_percent=proc.info['cpu_percent'] or 0,
                        memory_percent=proc.info['memory_percent'] or 0,
                        memory_rss=proc.info['memory_rss'] or 0,
                        create_time=proc.info['create_time']
                    )
                    processes_info.append(info)
                except (psutil.NoSuchProcess, psutil.AccessDenied, psutil.ZombieProcess):
                    continue
            
            # Сортируем по CPU usage
            processes_info.sort(key=lambda x: x.cpu_percent, reverse=True)
            
            logger.info(f"Top {n} processes by CPU usage")
            return processes_info[:n]
        except Exception as e:
            logger.error(f"Error getting top processes: {e}")
            return []
    
    def get_full_status(self) -> Dict:
        """Получить полный статус системы"""
        try:
            status = {
                'timestamp': datetime.now().isoformat(),
                'platform': {
                    'system': platform.system(),
                    'release': platform.release(),
                    'version': platform.version(),
                    'machine': platform.machine(),
                    'processor': platform.processor()
                },
                'cpu': self.get_cpu_info().to_dict() if self.get_cpu_info() else None,
                'memory': self.get_memory_info().to_dict() if self.get_memory_info() else None,
                'disks': [d.to_dict() for d in self.get_disk_info()],
                'gpu': [g.to_dict() for g in (self.get_gpu_info() or [])],
                'battery': self.get_battery_info().to_dict() if self.get_battery_info() else None,
                'network': [n.to_dict() for n in self.get_network_info()],
                'top_processes': [p.to_dict() for p in self.get_top_processes(5)]
            }
            
            logger.info("Full system status retrieved")
            return status
        except Exception as e:
            logger.error(f"Error getting full status: {e}")
            return {}
    
    def start_continuous_monitoring(self, interval: float = 1.0):
        """Начать непрерывный мониторинг"""
        if self.is_monitoring:
            return
        
        self.is_monitoring = True
        self.monitor_interval = interval
        
        def monitor_loop():
            while self.is_monitoring:
                try:
                    self.get_cpu_info()
                    self.get_memory_info()
                    self.get_disk_info()
                    self.get_gpu_info()
                    self.get_battery_info()
                    self.get_network_info()
                    time.sleep(self.monitor_interval)
                except Exception as e:
                    logger.error(f"Error in monitoring loop: {e}")
        
        self.monitor_thread = threading.Thread(target=monitor_loop, daemon=True)
        self.monitor_thread.start()
        logger.info(f"Continuous monitoring started (interval: {interval}s)")
    
    def stop_continuous_monitoring(self):
        """Остановить непрерывный мониторинг"""
        self.is_monitoring = False
        if self.monitor_thread:
            self.monitor_thread.join(timeout=5)
        logger.info("Continuous monitoring stopped")
    
    def get_history(self, metric: str) -> List[Dict]:
        """Получить историю метрики"""
        history_map = {
            'cpu': self.cpu_history,
            'memory': self.memory_history,
            'disk': self.disk_history,
            'gpu': self.gpu_history,
            'battery': self.battery_history,
            'network': self.network_history
        }
        
        return list(history_map.get(metric, []))
    
    def export_to_json(self, filepath: str) -> bool:
        """Экспортировать историю в JSON"""
        try:
            data = {
                'timestamp': datetime.now().isoformat(),
                'cpu_history': list(self.cpu_history),
                'memory_history': list(self.memory_history),
                'disk_history': list(self.disk_history),
                'gpu_history': list(self.gpu_history),
                'battery_history': list(self.battery_history),
                'network_history': list(self.network_history)
            }
            
            with open(filepath, 'w') as f:
                json.dump(data, f, indent=2)
            
            logger.info(f"History exported to {filepath}")
            return True
        except Exception as e:
            logger.error(f"Error exporting history: {e}")
            return False


# Экспорт основных классов
__all__ = [
    'ProductionHardwareMonitor',
    'CPUInfo',
    'MemoryInfo',
    'DiskInfo',
    'GPUInfo',
    'BatteryInfo',
    'NetworkInfo',
    'ProcessInfo'
]

