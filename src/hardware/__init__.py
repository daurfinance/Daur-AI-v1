#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
Daur-AI: Модуль управления оборудованием
"""

from .driver_manager import (
    DeviceType,
    DriverStatus,
    Device,
    Driver,
    HardwareInfo,
    HardwareMonitor,
    DriverManager,
    get_hardware_monitor,
    get_driver_manager
)

try:
    from .advanced_hardware_monitor import (
        GPUType,
        GPUInfo,
        BatteryInfo,
        TemperatureInfo,
        AdvancedHardwareMonitor,
        get_advanced_hardware_monitor
    )
except ImportError:
    pass

try:
    from .network_monitor import (
        ConnectionType,
        NetworkInterface,
        NetworkStats,
        ConnectedDevice,
        NetworkMonitor,
        get_network_monitor
    )
except ImportError:
    pass

__all__ = [
    'DeviceType',
    'DriverStatus',
    'Device',
    'Driver',
    'HardwareInfo',
    'HardwareMonitor',
    'DriverManager',
    'get_hardware_monitor',
    'get_driver_manager',
    'GPUType',
    'GPUInfo',
    'BatteryInfo',
    'TemperatureInfo',
    'AdvancedHardwareMonitor',
    'get_advanced_hardware_monitor',
    'ConnectionType',
    'NetworkInterface',
    'NetworkStats',
    'ConnectedDevice',
    'NetworkMonitor',
    'get_network_monitor'
]

