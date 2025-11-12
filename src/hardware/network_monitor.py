#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
Daur-AI: Монитор сетевых интерфейсов
Мониторинг сетевых подключений, интерфейсов и устройств

Версия: 2.0
Дата: 25.10.2025
Автор: Manus AI
"""

import logging
import subprocess
from typing import Dict, List, Any, Optional
from dataclasses import dataclass, field
from datetime import datetime
from enum import Enum

try:
    import psutil
except ImportError:
    psutil = None


class ConnectionType(Enum):
    """Типы подключений"""
    ETHERNET = "ethernet"
    WIFI = "wifi"
    CELLULAR = "cellular"
    BLUETOOTH = "bluetooth"
    VPN = "vpn"
    UNKNOWN = "unknown"


@dataclass
class NetworkInterface:
    """Информация о сетевом интерфейсе"""
    name: str
    connection_type: ConnectionType
    is_up: bool
    mtu: int
    mac_address: str = ""
    ipv4_address: str = ""
    ipv6_address: str = ""
    broadcast: str = ""
    netmask: str = ""
    timestamp: datetime = field(default_factory=datetime.now)


@dataclass
class NetworkStats:
    """Статистика сетевого интерфейса"""
    interface: str
    bytes_sent: int
    bytes_recv: int
    packets_sent: int
    packets_recv: int
    errors_in: int
    errors_out: int
    dropped_in: int
    dropped_out: int
    timestamp: datetime = field(default_factory=datetime.now)


@dataclass
class ConnectedDevice:
    """Информация о подключенном устройстве"""
    name: str
    mac_address: str
    ip_address: str
    device_type: str  # phone, laptop, tablet, etc.
    signal_strength: int = 0  # 0-100
    connected_time: int = 0  # seconds
    timestamp: datetime = field(default_factory=datetime.now)


class NetworkMonitor:
    """Монитор сетевых интерфейсов"""
    
    def __init__(self):
        """Инициализация"""
        self.logger = logging.getLogger('daur_ai.network_monitor')
        self.interface_history: List[NetworkInterface] = []
        self.stats_history: List[NetworkStats] = []
        self.device_history: List[ConnectedDevice] = []
        self.logger.info("Network Monitor инициализирован")
    
    # ==================== СЕТЕВЫЕ ИНТЕРФЕЙСЫ ====================
    
    def get_network_interfaces(self) -> List[NetworkInterface]:
        """
        Получить информацию о сетевых интерфейсах
        
        Returns:
            List[NetworkInterface]: Список интерфейсов
        """
        if not psutil:
            self.logger.warning("psutil не установлен")
            return []
        
        try:
            interfaces = []
            
            # Получить информацию об интерфейсах
            if_addrs = psutil.net_if_addrs()
            if_stats = psutil.net_if_stats()
            
            for interface_name, addrs in if_addrs.items():
                stats = if_stats.get(interface_name)
                
                if not stats:
                    continue
                
                # Определить тип подключения
                conn_type = self._determine_connection_type(interface_name)
                
                # Получить адреса
                ipv4_addr = ""
                ipv6_addr = ""
                mac_addr = ""
                
                for addr in addrs:
                    if addr.family.name == 'AF_INET':
                        ipv4_addr = addr.address
                    elif addr.family.name == 'AF_INET6':
                        ipv6_addr = addr.address
                    elif addr.family.name == 'AF_LINK':
                        mac_addr = addr.address
                
                interface = NetworkInterface(
                    name=interface_name,
                    connection_type=conn_type,
                    is_up=stats.isup,
                    mtu=stats.mtu,
                    mac_address=mac_addr,
                    ipv4_address=ipv4_addr,
                    ipv6_address=ipv6_addr
                )
                
                interfaces.append(interface)
            
            self.interface_history.extend(interfaces)
            
            self.logger.info(f"Получена информация о {len(interfaces)} сетевых интерфейсах")
            return interfaces
        
        except Exception as e:
            self.logger.error(f"Ошибка получения информации об интерфейсах: {e}")
            return []
    
    def _determine_connection_type(self, interface_name: str) -> ConnectionType:
        """Определить тип подключения по имени интерфейса"""
        name_lower = interface_name.lower()
        
        if 'eth' in name_lower or 'en' in name_lower:
            return ConnectionType.ETHERNET
        elif 'wlan' in name_lower or 'wifi' in name_lower or 'wl' in name_lower:
            return ConnectionType.WIFI
        elif 'ppp' in name_lower or 'tun' in name_lower:
            return ConnectionType.VPN
        elif 'bt' in name_lower or 'bluetooth' in name_lower:
            return ConnectionType.BLUETOOTH
        
        return ConnectionType.UNKNOWN
    
    # ==================== СТАТИСТИКА СЕТИ ====================
    
    def get_network_stats(self) -> List[NetworkStats]:
        """
        Получить статистику сетевых интерфейсов
        
        Returns:
            List[NetworkStats]: Список статистики
        """
        if not psutil:
            self.logger.warning("psutil не установлен")
            return []
        
        try:
            stats_list = []
            
            net_io = psutil.net_io_counters(pernic=True)
            
            for interface_name, io_counters in net_io.items():
                stats = NetworkStats(
                    interface=interface_name,
                    bytes_sent=io_counters.bytes_sent,
                    bytes_recv=io_counters.bytes_recv,
                    packets_sent=io_counters.packets_sent,
                    packets_recv=io_counters.packets_recv,
                    errors_in=io_counters.errin,
                    errors_out=io_counters.errout,
                    dropped_in=io_counters.dropin,
                    dropped_out=io_counters.dropout
                )
                
                stats_list.append(stats)
            
            self.stats_history.extend(stats_list)
            
            self.logger.info(f"Получена статистика {len(stats_list)} интерфейсов")
            return stats_list
        
        except Exception as e:
            self.logger.error(f"Ошибка получения статистики сети: {e}")
            return []
    
    def get_bandwidth_usage(self) -> Dict[str, Dict[str, float]]:
        """
        Получить использование полосы пропускания
        
        Returns:
            Dict: Использование полосы пропускания по интерфейсам
        """
        if not psutil:
            return {}
        
        try:
            bandwidth = {}
            
            net_io = psutil.net_io_counters(pernic=True)
            
            for interface_name, io_counters in net_io.items():
                bandwidth[interface_name] = {
                    'bytes_sent': io_counters.bytes_sent,
                    'bytes_recv': io_counters.bytes_recv,
                    'packets_sent': io_counters.packets_sent,
                    'packets_recv': io_counters.packets_recv,
                    'total_bytes': io_counters.bytes_sent + io_counters.bytes_recv,
                    'total_packets': io_counters.packets_sent + io_counters.packets_recv
                }
            
            return bandwidth
        
        except Exception as e:
            self.logger.error(f"Ошибка получения использования полосы: {e}")
            return {}
    
    # ==================== ПОДКЛЮЧЕННЫЕ УСТРОЙСТВА ====================
    
    def get_connected_devices(self) -> List[ConnectedDevice]:
        """
        Получить список подключенных устройств
        
        Returns:
            List[ConnectedDevice]: Список подключенных устройств
        """
        try:
            devices = []
            
            # Использовать arp для получения подключенных устройств
            result = subprocess.run(
                ['arp', '-a'],
                capture_output=True,
                text=True,
                timeout=5
            )
            
            for line in result.stdout.split('\n'):
                if not line.strip():
                    continue
                
                # Парсинг строки ARP
                parts = line.split()
                if len(parts) >= 3:
                    try:
                        ip_addr = parts[0].strip('()')
                        mac_addr = parts[1]
                        
                        device = ConnectedDevice(
                            name=f"Device_{ip_addr}",
                            mac_address=mac_addr,
                            ip_address=ip_addr,
                            device_type="unknown"
                        )
                        
                        devices.append(device)
                    except (ValueError, IndexError):
                        continue
            
            self.device_history.extend(devices)
            
            self.logger.info(f"Найдено {len(devices)} подключенных устройств")
            return devices
        
        except Exception as e:
            self.logger.warning(f"Ошибка получения подключенных устройств: {e}")
            return []
    
    def get_wifi_networks(self) -> List[Dict[str, Any]]:
        """
        Получить список доступных WiFi сетей
        
        Returns:
            List: Список WiFi сетей
        """
        try:
            networks = []
            
            # Для Linux
            result = subprocess.run(
                ['nmcli', 'device', 'wifi', 'list'],
                capture_output=True,
                text=True,
                timeout=5
            )
            
            lines = result.stdout.split('\n')[1:]  # Пропустить заголовок
            
            for line in lines:
                if not line.strip():
                    continue
                
                parts = line.split()
                if len(parts) >= 5:
                    try:
                        network = {
                            'ssid': parts[1],
                            'signal': int(parts[2]),
                            'frequency': parts[3],
                            'security': ' '.join(parts[4:])
                        }
                        networks.append(network)
                    except (ValueError, IndexError):
                        continue
            
            self.logger.info(f"Найдено {len(networks)} WiFi сетей")
            return networks
        
        except Exception as e:
            self.logger.warning(f"Ошибка получения WiFi сетей: {e}")
            return []
    
    # ==================== ОБЩАЯ ИНФОРМАЦИЯ ====================
    
    def get_full_network_status(self) -> Dict[str, Any]:
        """
        Получить полный статус сети
        
        Returns:
            Dict: Полный статус сети
        """
        status = {
            'timestamp': datetime.now().isoformat(),
            'interfaces': [],
            'stats': [],
            'bandwidth': {},
            'devices': [],
            'wifi_networks': []
        }
        
        # Интерфейсы
        interfaces = self.get_network_interfaces()
        status['interfaces'] = [
            {
                'name': i.name,
                'type': i.connection_type.value,
                'is_up': i.is_up,
                'mtu': i.mtu,
                'mac_address': i.mac_address,
                'ipv4_address': i.ipv4_address,
                'ipv6_address': i.ipv6_address
            }
            for i in interfaces
        ]
        
        # Статистика
        stats = self.get_network_stats()
        status['stats'] = [
            {
                'interface': s.interface,
                'bytes_sent': s.bytes_sent,
                'bytes_recv': s.bytes_recv,
                'packets_sent': s.packets_sent,
                'packets_recv': s.packets_recv,
                'errors_in': s.errors_in,
                'errors_out': s.errors_out
            }
            for s in stats
        ]
        
        # Полоса пропускания
        status['bandwidth'] = self.get_bandwidth_usage()
        
        # Подключенные устройства
        devices = self.get_connected_devices()
        status['devices'] = [
            {
                'name': d.name,
                'mac_address': d.mac_address,
                'ip_address': d.ip_address,
                'device_type': d.device_type
            }
            for d in devices
        ]
        
        # WiFi сети
        status['wifi_networks'] = self.get_wifi_networks()
        
        return status
    
    # ==================== ИСТОРИЯ ====================
    
    def get_interface_history(self, limit: int = 100) -> List[Dict[str, Any]]:
        """Получить историю интерфейсов"""
        return [
            {
                'name': i.name,
                'type': i.connection_type.value,
                'is_up': i.is_up,
                'ipv4_address': i.ipv4_address,
                'timestamp': i.timestamp.isoformat()
            }
            for i in self.interface_history[-limit:]
        ]
    
    def get_stats_history(self, limit: int = 100) -> List[Dict[str, Any]]:
        """Получить историю статистики"""
        return [
            {
                'interface': s.interface,
                'bytes_sent': s.bytes_sent,
                'bytes_recv': s.bytes_recv,
                'timestamp': s.timestamp.isoformat()
            }
            for s in self.stats_history[-limit:]
        ]
    
    def clear_history(self):
        """Очистить историю"""
        self.interface_history.clear()
        self.stats_history.clear()
        self.device_history.clear()
        self.logger.info("История сети очищена")


# Глобальный экземпляр
_network_monitor = None


def get_network_monitor() -> NetworkMonitor:
    """Получить монитор сети"""
    global _network_monitor
    if _network_monitor is None:
        _network_monitor = NetworkMonitor()
    return _network_monitor

