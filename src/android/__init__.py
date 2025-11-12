#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
Daur-AI: Модуль Android эмулятора BlueStacks
"""

from .bluestacks_manager import (
    BlueStacksVersion,
    AppType,
    AndroidApp,
    AndroidDevice,
    BlueStacksManager,
    get_bluestacks_manager
)

__all__ = [
    'BlueStacksVersion',
    'AppType',
    'AndroidApp',
    'AndroidDevice',
    'BlueStacksManager',
    'get_bluestacks_manager'
]

