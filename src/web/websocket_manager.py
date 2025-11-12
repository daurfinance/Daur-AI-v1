#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
Daur-AI: WebSocket менеджер для real-time управления
Real-time управление устройствами через WebSocket

Версия: 2.0
Дата: 25.10.2025
Автор: Manus AI
"""

import logging
import json
from typing import Dict, Any, Callable, List
from datetime import datetime
from enum import Enum

try:
    from flask_socketio import SocketIO, emit, join_room, leave_room, rooms
except ImportError:
    SocketIO = None
    emit = None


class EventType(Enum):
    """Типы WebSocket событий"""
    CONNECT = "connect"
    DISCONNECT = "disconnect"
    MOUSE_MOVE = "mouse_move"
    MOUSE_CLICK = "mouse_click"
    KEYBOARD_TYPE = "keyboard_type"
    KEYBOARD_HOTKEY = "keyboard_hotkey"
    TOUCH_TAP = "touch_tap"
    TOUCH_SWIPE = "touch_swipe"
    HARDWARE_STATUS = "hardware_status"
    NETWORK_STATUS = "network_status"
    FACE_DETECT = "face_detect"
    BARCODE_DETECT = "barcode_detect"
    SCREEN_CAPTURE = "screen_capture"
    COMMAND = "command"
    ERROR = "error"
    STATUS = "status"


class WebSocketManager:
    """Менеджер WebSocket соединений"""
    
    def __init__(self, app=None):
        """
        Инициализация
        
        Args:
            app: Flask приложение
        """
        self.logger = logging.getLogger('daur_ai.websocket_manager')
        self.socketio = None
        self.connected_clients: Dict[str, Dict[str, Any]] = {}
        self.event_handlers: Dict[str, List[Callable]] = {}
        
        if app:
            self.init_app(app)
        
        self.logger.info("WebSocket Manager инициализирован")
    
    def init_app(self, app):
        """Инициализировать с Flask приложением"""
        try:
            self.socketio = SocketIO(app, cors_allowed_origins="*")
            self._register_handlers()
            self.logger.info("WebSocket инициализирован с Flask приложением")
        except Exception as e:
            self.logger.error(f"Ошибка инициализации WebSocket: {e}")
    
    def _register_handlers(self):
        """Зарегистрировать обработчики событий"""
        if not self.socketio:
            return
        
        @self.socketio.on('connect')
        def handle_connect():
            """Обработка подключения"""
            client_id = request.sid
            self.connected_clients[client_id] = {
                'connected_at': datetime.now().isoformat(),
                'last_activity': datetime.now().isoformat(),
                'events_count': 0
            }
            
            self.logger.info(f"Клиент подключен: {client_id}")
            
            emit('status', {
                'status': 'connected',
                'client_id': client_id,
                'timestamp': datetime.now().isoformat()
            })
            
            self._emit_event(EventType.CONNECT, {'client_id': client_id})
        
        @self.socketio.on('disconnect')
        def handle_disconnect():
            """Обработка отключения"""
            client_id = request.sid
            
            if client_id in self.connected_clients:
                del self.connected_clients[client_id]
            
            self.logger.info(f"Клиент отключен: {client_id}")
            self._emit_event(EventType.DISCONNECT, {'client_id': client_id})
        
        @self.socketio.on('mouse_move')
        def handle_mouse_move(data):
            """Обработка движения мыши"""
            try:
                x = data.get('x')
                y = data.get('y')
                duration = data.get('duration', 0.5)
                
                import pyautogui
                pyautogui.moveTo(x, y, duration=duration)
                
                self._update_client_activity(request.sid)
                
                emit('response', {
                    'status': 'success',
                    'message': f'Mouse moved to ({x}, {y})',
                    'timestamp': datetime.now().isoformat()
                })
                
                self._emit_event(EventType.MOUSE_MOVE, {'x': x, 'y': y})
            
            except Exception as e:
                self.logger.error(f"Ошибка движения мыши: {e}")
                emit('response', {'status': 'error', 'error': str(e)})
        
        @self.socketio.on('mouse_click')
        def handle_mouse_click(data):
            """Обработка клика мыши"""
            try:
                x = data.get('x')
                y = data.get('y')
                button = data.get('button', 'left')
                clicks = data.get('clicks', 1)
                
                import pyautogui
                pyautogui.moveTo(x, y, duration=0.2)
                pyautogui.click(x, y, clicks=clicks, button=button)
                
                self._update_client_activity(request.sid)
                
                emit('response', {
                    'status': 'success',
                    'message': f'{button} click at ({x}, {y})',
                    'timestamp': datetime.now().isoformat()
                })
                
                self._emit_event(EventType.MOUSE_CLICK, {'x': x, 'y': y, 'button': button})
            
            except Exception as e:
                self.logger.error(f"Ошибка клика мыши: {e}")
                emit('response', {'status': 'error', 'error': str(e)})
        
        @self.socketio.on('keyboard_type')
        def handle_keyboard_type(data):
            """Обработка печати текста"""
            try:
                text = data.get('text')
                interval = data.get('interval', 0.05)
                
                import pyautogui
                pyautogui.typewrite(text, interval=interval)
                
                self._update_client_activity(request.sid)
                
                emit('response', {
                    'status': 'success',
                    'message': f'Typed: {text[:50]}...',
                    'timestamp': datetime.now().isoformat()
                })
                
                self._emit_event(EventType.KEYBOARD_TYPE, {'text': text[:20]})
            
            except Exception as e:
                self.logger.error(f"Ошибка печати: {e}")
                emit('response', {'status': 'error', 'error': str(e)})
        
        @self.socketio.on('keyboard_hotkey')
        def handle_keyboard_hotkey(data):
            """Обработка комбинации клавиш"""
            try:
                keys = data.get('keys', [])
                
                import pyautogui
                pyautogui.hotkey(*keys)
                
                self._update_client_activity(request.sid)
                
                emit('response', {
                    'status': 'success',
                    'message': f'Hotkey executed: {"+".join(keys)}',
                    'timestamp': datetime.now().isoformat()
                })
                
                self._emit_event(EventType.KEYBOARD_HOTKEY, {'keys': keys})
            
            except Exception as e:
                self.logger.error(f"Ошибка комбинации клавиш: {e}")
                emit('response', {'status': 'error', 'error': str(e)})
        
        @self.socketio.on('touch_tap')
        def handle_touch_tap(data):
            """Обработка tap жеста"""
            try:
                x = data.get('x')
                y = data.get('y')
                duration = data.get('duration', 0.1)
                
                try:
                    from ..input.touch_controller import get_touch_controller
                    touch = get_touch_controller()
                    success = touch.tap(x, y, duration)
                except ImportError:
                    success = False
                
                self._update_client_activity(request.sid)
                
                emit('response', {
                    'status': 'success' if success else 'failed',
                    'message': 'Tap executed' if success else 'Failed to execute tap',
                    'timestamp': datetime.now().isoformat()
                })
                
                self._emit_event(EventType.TOUCH_TAP, {'x': x, 'y': y})
            
            except Exception as e:
                self.logger.error(f"Ошибка tap жеста: {e}")
                emit('response', {'status': 'error', 'error': str(e)})
        
        @self.socketio.on('hardware_status')
        def handle_hardware_status():
            """Получить статус оборудования"""
            try:
                try:
                    from ..hardware.advanced_hardware_monitor import get_advanced_hardware_monitor
                    monitor = get_advanced_hardware_monitor()
                    status = monitor.get_full_hardware_status()
                except ImportError:
                    status = {}
                
                self._update_client_activity(request.sid)
                
                emit('response', {
                    'status': 'success',
                    'data': status,
                    'timestamp': datetime.now().isoformat()
                })
                
                self._emit_event(EventType.HARDWARE_STATUS, {})
            
            except Exception as e:
                self.logger.error(f"Ошибка получения статуса оборудования: {e}")
                emit('response', {'status': 'error', 'error': str(e)})
        
        @self.socketio.on('command')
        def handle_command(data):
            """Обработка команды"""
            try:
                command = data.get('command')
                args = data.get('args', {})
                
                self.logger.info(f"Команда получена: {command} с аргументами: {args}")
                
                self._update_client_activity(request.sid)
                
                emit('response', {
                    'status': 'success',
                    'command': command,
                    'timestamp': datetime.now().isoformat()
                })
                
                self._emit_event(EventType.COMMAND, {'command': command})
            
            except Exception as e:
                self.logger.error(f"Ошибка команды: {e}")
                emit('response', {'status': 'error', 'error': str(e)})
    
    def register_event_handler(self, event_type: EventType, handler: Callable):
        """
        Зарегистрировать обработчик события
        
        Args:
            event_type: Тип события
            handler: Функция-обработчик
        """
        if event_type not in self.event_handlers:
            self.event_handlers[event_type] = []
        
        self.event_handlers[event_type].append(handler)
        self.logger.info(f"Обработчик зарегистрирован для события: {event_type.value}")
    
    def _emit_event(self, event_type: EventType, data: Dict[str, Any]):
        """Отправить событие всем обработчикам"""
        if event_type in self.event_handlers:
            for handler in self.event_handlers[event_type]:
                try:
                    handler(data)
                except Exception as e:
                    self.logger.error(f"Ошибка обработчика события {event_type.value}: {e}")
    
    def _update_client_activity(self, client_id: str):
        """Обновить время последней активности клиента"""
        if client_id in self.connected_clients:
            self.connected_clients[client_id]['last_activity'] = datetime.now().isoformat()
            self.connected_clients[client_id]['events_count'] += 1
    
    def broadcast_status(self, status: Dict[str, Any]):
        """Отправить статус всем клиентам"""
        if self.socketio:
            self.socketio.emit('status', {
                'data': status,
                'timestamp': datetime.now().isoformat()
            }, broadcast=True)
    
    def get_connected_clients_count(self) -> int:
        """Получить количество подключенных клиентов"""
        return len(self.connected_clients)
    
    def get_connected_clients(self) -> Dict[str, Dict[str, Any]]:
        """Получить информацию о подключенных клиентах"""
        return self.connected_clients.copy()
    
    def disconnect_client(self, client_id: str):
        """Отключить клиента"""
        if self.socketio and client_id in self.connected_clients:
            self.socketio.disconnect(client_id)
            del self.connected_clients[client_id]
            self.logger.info(f"Клиент отключен: {client_id}")


# Глобальный экземпляр
_websocket_manager = None


def get_websocket_manager() -> WebSocketManager:
    """Получить менеджер WebSocket"""
    global _websocket_manager
    if _websocket_manager is None:
        _websocket_manager = WebSocketManager()
    return _websocket_manager


def init_websocket(app):
    """Инициализировать WebSocket с приложением"""
    manager = get_websocket_manager()
    manager.init_app(app)
    return manager

