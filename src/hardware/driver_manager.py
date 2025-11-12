#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
Daur-AI: Модуль управления драйверами и оборудованием
Управление устройствами, драйверами и аппаратными ресурсами

Версия: 2.0
Дата: 25.10.2025
Автор: Manus AI
"""

import logging
import subprocess
import json
from typing import Dict, List, Any, Optional, Tuple
from enum import Enum
from dataclasses import dataclass, field
from datetime import datetime
import platform
import psutil


class DeviceType(Enum):
    """Типы устройств"""
    CPU = "cpu"
    GPU = "gpu"
    RAM = "ram"
    DISK = "disk"
    NETWORK = "network"
    AUDIO = "audio"
    CAMERA = "camera"
    USB = "usb"
    PRINTER = "printer"
    MONITOR = "monitor"


class DriverStatus(Enum):
    """Статусы драйверов"""
    INSTALLED = "installed"
    OUTDATED = "outdated"
    MISSING = "missing"
    ERROR = "error"
    DISABLED = "disabled"


@dataclass
class Device:
    """Устройство"""
    device_id: str
    name: str
    device_type: DeviceType
    manufacturer: str = ""
    model: str = ""
    driver_version: str = ""
    status: str = "active"
    created_at: datetime = field(default_factory=datetime.now)


@dataclass
class Driver:
    """Драйвер"""
    driver_id: str
    name: str
    version: str
    device_type: DeviceType
    status: DriverStatus = DriverStatus.INSTALLED
    last_updated: datetime = field(default_factory=datetime.now)
    path: str = ""


@dataclass
class HardwareInfo:
    """Информация об оборудовании"""
    cpu_count: int = 0
    cpu_percent: float = 0.0
    ram_total: int = 0
    ram_used: int = 0
    ram_percent: float = 0.0
    disk_total: int = 0
    disk_used: int = 0
    disk_percent: float = 0.0
    timestamp: datetime = field(default_factory=datetime.now)


class HardwareMonitor:
    """Монитор оборудования"""
    
    def __init__(self):
        """Инициализация"""
        self.logger = logging.getLogger('daur_ai.hardware_monitor')
    
    def get_cpu_info(self) -> Dict[str, Any]:
        """
        Получить информацию о CPU
        
        Returns:
            Dict: Информация о CPU
        """
        try:
            return {
                'count': psutil.cpu_count(),
                'percent': psutil.cpu_percent(interval=1),
                'freq': psutil.cpu_freq().current if psutil.cpu_freq() else 0,
                'load_average': psutil.getloadavg() if hasattr(psutil, 'getloadavg') else (0, 0, 0)
            }
        except Exception as e:
            self.logger.error(f"Ошибка получения информации CPU: {e}")
            return {}
    
    def get_memory_info(self) -> Dict[str, Any]:
        """
        Получить информацию о памяти
        
        Returns:
            Dict: Информация о памяти
        """
        try:
            mem = psutil.virtual_memory()
            return {
                'total': mem.total,
                'used': mem.used,
                'available': mem.available,
                'percent': mem.percent,
                'free': mem.free
            }
        except Exception as e:
            self.logger.error(f"Ошибка получения информации о памяти: {e}")
            return {}
    
    def get_disk_info(self, path: str = '/') -> Dict[str, Any]:
        """
        Получить информацию о диске
        
        Args:
            path: Путь для проверки
            
        Returns:
            Dict: Информация о диске
        """
        try:
            disk = psutil.disk_usage(path)
            return {
                'total': disk.total,
                'used': disk.used,
                'free': disk.free,
                'percent': disk.percent
            }
        except Exception as e:
            self.logger.error(f"Ошибка получения информации о диске: {e}")
            return {}
    
    def get_network_info(self) -> Dict[str, Any]:
        """
        Получить информацию о сети
        
        Returns:
            Dict: Информация о сети
        """
        try:
            net = psutil.net_if_stats()
            return {
                'interfaces': list(net.keys()),
                'stats': {name: {
                    'isup': stats.isup,
                    'speed': stats.speed,
                    'mtu': stats.mtu
                } for name, stats in net.items()}
            }
        except Exception as e:
            self.logger.error(f"Ошибка получения информации о сети: {e}")
            return {}
    
    def get_process_info(self, pid: Optional[int] = None) -> List[Dict[str, Any]]:
        """
        Получить информацию о процессах
        
        Args:
            pid: ID процесса (если None, все процессы)
            
        Returns:
            List: Информация о процессах
        """
        try:
            processes = []
            
            if pid:
                try:
                    p = psutil.Process(pid)
                    processes.append({
                        'pid': p.pid,
                        'name': p.name(),
                        'status': p.status(),
                        'cpu_percent': p.cpu_percent(),
                        'memory_percent': p.memory_percent()
                    })
                except psutil.NoSuchProcess:
                    pass
            else:
                for p in psutil.process_iter(['pid', 'name', 'status']):
                    try:
                        processes.append({
                            'pid': p.info['pid'],
                            'name': p.info['name'],
                            'status': p.info['status'],
                            'cpu_percent': p.cpu_percent(),
                            'memory_percent': p.memory_percent()
                        })
                    except (psutil.NoSuchProcess, psutil.AccessDenied):
                        pass
            
            return processes
        
        except Exception as e:
            self.logger.error(f"Ошибка получения информации о процессах: {e}")
            return []
    
    def get_hardware_info(self) -> HardwareInfo:
        """
        Получить полную информацию об оборудовании
        
        Returns:
            HardwareInfo: Информация об оборудовании
        """
        cpu_info = self.get_cpu_info()
        mem_info = self.get_memory_info()
        disk_info = self.get_disk_info()
        
        return HardwareInfo(
            cpu_count=cpu_info.get('count', 0),
            cpu_percent=cpu_info.get('percent', 0.0),
            ram_total=mem_info.get('total', 0),
            ram_used=mem_info.get('used', 0),
            ram_percent=mem_info.get('percent', 0.0),
            disk_total=disk_info.get('total', 0),
            disk_used=disk_info.get('used', 0),
            disk_percent=disk_info.get('percent', 0.0)
        )


class DriverManager:
    """Менеджер драйверов"""
    
    def __init__(self):
        """Инициализация"""
        self.logger = logging.getLogger('daur_ai.driver_manager')
        self.devices: Dict[str, Device] = {}
        self.drivers: Dict[str, Driver] = {}
        self.hardware_monitor = HardwareMonitor()
    
    def detect_devices(self) -> List[Device]:
        """
        Обнаружить устройства в системе
        
        Returns:
            List[Device]: Список обнаруженных устройств
        """
        devices = []
        
        try:
            # Обнаружение CPU
            cpu_device = Device(
                "cpu_0",
                "Processor",
                DeviceType.CPU,
                manufacturer=platform.processor(),
                model=platform.machine()
            )
            devices.append(cpu_device)
            self.devices["cpu_0"] = cpu_device
            
            # Обнаружение RAM
            mem_info = self.hardware_monitor.get_memory_info()
            ram_device = Device(
                "ram_0",
                "System Memory",
                DeviceType.RAM,
                model=f"{mem_info.get('total', 0) // (1024**3)}GB"
            )
            devices.append(ram_device)
            self.devices["ram_0"] = ram_device
            
            # Обнаружение дисков
            disk_info = self.hardware_monitor.get_disk_info()
            disk_device = Device(
                "disk_0",
                "System Disk",
                DeviceType.DISK,
                model=f"{disk_info.get('total', 0) // (1024**3)}GB"
            )
            devices.append(disk_device)
            self.devices["disk_0"] = disk_device
            
            # Обнаружение сетевых интерфейсов
            net_info = self.hardware_monitor.get_network_info()
            for i, interface in enumerate(net_info.get('interfaces', [])):
                net_device = Device(
                    f"net_{i}",
                    f"Network Interface {interface}",
                    DeviceType.NETWORK,
                    model=interface
                )
                devices.append(net_device)
                self.devices[f"net_{i}"] = net_device
            
            self.logger.info(f"Обнаружено устройств: {len(devices)}")
            return devices
        
        except Exception as e:
            self.logger.error(f"Ошибка обнаружения устройств: {e}")
            return devices
    
    def get_device_info(self, device_id: str) -> Optional[Dict[str, Any]]:
        """
        Получить информацию об устройстве
        
        Args:
            device_id: ID устройства
            
        Returns:
            Optional[Dict]: Информация об устройстве
        """
        if device_id not in self.devices:
            return None
        
        device = self.devices[device_id]
        
        return {
            'device_id': device.device_id,
            'name': device.name,
            'type': device.device_type.value,
            'manufacturer': device.manufacturer,
            'model': device.model,
            'driver_version': device.driver_version,
            'status': device.status
        }
    
    def install_driver(self, driver_id: str, name: str, device_type: DeviceType,
                      version: str = "1.0.0") -> bool:
        """
        Установить драйвер
        
        Args:
            driver_id: ID драйвера
            name: Имя драйвера
            device_type: Тип устройства
            version: Версия драйвера
            
        Returns:
            bool: Успешность операции
        """
        try:
            driver = Driver(driver_id, name, version, device_type)
            self.drivers[driver_id] = driver
            self.logger.info(f"Драйвер установлен: {driver_id} ({name} v{version})")
            return True
        
        except Exception as e:
            self.logger.error(f"Ошибка установки драйвера: {e}")
            return False
    
    def update_driver(self, driver_id: str, new_version: str) -> bool:
        """
        Обновить драйвер
        
        Args:
            driver_id: ID драйвера
            new_version: Новая версия
            
        Returns:
            bool: Успешность операции
        """
        if driver_id not in self.drivers:
            self.logger.error(f"Драйвер не найден: {driver_id}")
            return False
        
        try:
            self.drivers[driver_id].version = new_version
            self.drivers[driver_id].last_updated = datetime.now()
            self.logger.info(f"Драйвер обновлен: {driver_id} -> v{new_version}")
            return True
        
        except Exception as e:
            self.logger.error(f"Ошибка обновления драйвера: {e}")
            return False
    
    def uninstall_driver(self, driver_id: str) -> bool:
        """
        Удалить драйвер
        
        Args:
            driver_id: ID драйвера
            
        Returns:
            bool: Успешность операции
        """
        if driver_id in self.drivers:
            del self.drivers[driver_id]
            self.logger.info(f"Драйвер удален: {driver_id}")
            return True
        
        return False
    
    def get_driver_status(self, driver_id: str) -> Optional[DriverStatus]:
        """
        Получить статус драйвера
        
        Args:
            driver_id: ID драйвера
            
        Returns:
            Optional[DriverStatus]: Статус драйвера
        """
        if driver_id not in self.drivers:
            return None
        
        return self.drivers[driver_id].status
    
    def check_device_health(self) -> Dict[str, Any]:
        """
        Проверить здоровье устройств
        
        Returns:
            Dict: Результаты проверки
        """
        health_status = {
            'timestamp': datetime.now().isoformat(),
            'devices': {},
            'overall_status': 'healthy'
        }
        
        try:
            hardware_info = self.hardware_monitor.get_hardware_info()
            
            # Проверка CPU
            if hardware_info.cpu_percent > 90:
                health_status['overall_status'] = 'warning'
            
            health_status['devices']['cpu'] = {
                'status': 'warning' if hardware_info.cpu_percent > 90 else 'healthy',
                'usage': hardware_info.cpu_percent
            }
            
            # Проверка памяти
            if hardware_info.ram_percent > 90:
                health_status['overall_status'] = 'warning'
            
            health_status['devices']['memory'] = {
                'status': 'warning' if hardware_info.ram_percent > 90 else 'healthy',
                'usage': hardware_info.ram_percent
            }
            
            # Проверка диска
            if hardware_info.disk_percent > 90:
                health_status['overall_status'] = 'critical'
            
            health_status['devices']['disk'] = {
                'status': 'critical' if hardware_info.disk_percent > 90 else 'warning' if hardware_info.disk_percent > 75 else 'healthy',
                'usage': hardware_info.disk_percent
            }
            
            self.logger.info(f"Проверка здоровья завершена: {health_status['overall_status']}")
            return health_status
        
        except Exception as e:
            self.logger.error(f"Ошибка проверки здоровья: {e}")
            return health_status
    
    def get_status(self) -> Dict[str, Any]:
        """Получить статус менеджера"""
        return {
            'devices': len(self.devices),
            'drivers': len(self.drivers),
            'hardware_info': self.hardware_monitor.get_hardware_info().__dict__
        }


# Глобальные экземпляры
_hardware_monitor = None
_driver_manager = None


def get_hardware_monitor() -> HardwareMonitor:
    """Получить монитор оборудования"""
    global _hardware_monitor
    if _hardware_monitor is None:
        _hardware_monitor = HardwareMonitor()
    return _hardware_monitor


def get_driver_manager() -> DriverManager:
    """Получить менеджер драйверов"""
    global _driver_manager
    if _driver_manager is None:
        _driver_manager = DriverManager()
    return _driver_manager

