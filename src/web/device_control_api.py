#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
Daur-AI: REST API для управления устройствами
Endpoints для управления мышкой, клавиатурой, оборудованием и зрением

Версия: 2.0
Дата: 25.10.2025
Автор: Manus AI
"""

import logging
from flask import Blueprint, request, jsonify
from typing import Dict, Any, List
from datetime import datetime

# Импортировать контроллеры
try:
    from ..input.advanced_mouse_controller import get_advanced_mouse_controller
except ImportError:
    get_advanced_mouse_controller = None

try:
    from ..input.touch_controller import get_touch_controller
except ImportError:
    get_touch_controller = None

try:
    from ..input.keyboard_controller import get_keyboard_controller
except ImportError:
    get_keyboard_controller = None

try:
    from ..hardware.advanced_hardware_monitor import get_advanced_hardware_monitor
except ImportError:
    get_advanced_hardware_monitor = None

try:
    from ..hardware.network_monitor import get_network_monitor
except ImportError:
    get_network_monitor = None

try:
    from ..vision.face_recognition_module import get_face_recognition_module
except ImportError:
    get_face_recognition_module = None

try:
    from ..vision.barcode_recognition_module import get_barcode_recognition_module
except ImportError:
    get_barcode_recognition_module = None

try:
    from ..vision.screen_recognition import get_screen_analyzer
except ImportError:
    get_screen_analyzer = None


# Создать Blueprint
device_control_api = Blueprint('device_control_api', __name__, url_prefix='/api/v2')

logger = logging.getLogger('daur_ai.device_control_api')


# ==================== MOUSE ENDPOINTS ====================

@device_control_api.route('/mouse/move', methods=['POST'])
def mouse_move():
    """Переместить мышь"""
    try:
        data = request.get_json()
        x = data.get('x')
        y = data.get('y')
        duration = data.get('duration', 0.5)
        
        if x is None or y is None:
            return jsonify({'error': 'x and y coordinates required'}), 400
        
        mouse = get_advanced_mouse_controller()
        if not mouse:
            return jsonify({'error': 'Mouse controller not available'}), 503
        
        import pyautogui
        pyautogui.moveTo(x, y, duration=duration)
        
        return jsonify({
            'status': 'success',
            'message': f'Mouse moved to ({x}, {y})',
            'timestamp': datetime.now().isoformat()
        })
    
    except Exception as e:
        logger.error(f"Error moving mouse: {e}")
        return jsonify({'error': str(e)}), 500


@device_control_api.route('/mouse/click', methods=['POST'])
def mouse_click():
    """Нажать кнопку мыши"""
    try:
        data = request.get_json()
        x = data.get('x')
        y = data.get('y')
        button = data.get('button', 'left')
        clicks = data.get('clicks', 1)
        
        if x is None or y is None:
            return jsonify({'error': 'x and y coordinates required'}), 400
        
        import pyautogui
        pyautogui.moveTo(x, y, duration=0.2)
        pyautogui.click(x, y, clicks=clicks, button=button)
        
        return jsonify({
            'status': 'success',
            'message': f'{button} click at ({x}, {y})',
            'timestamp': datetime.now().isoformat()
        })
    
    except Exception as e:
        logger.error(f"Error clicking mouse: {e}")
        return jsonify({'error': str(e)}), 500


@device_control_api.route('/mouse/pattern/circle', methods=['POST'])
def mouse_draw_circle():
    """Нарисовать круг мышкой"""
    try:
        data = request.get_json()
        center_x = data.get('center_x')
        center_y = data.get('center_y')
        radius = data.get('radius', 100)
        duration = data.get('duration', 1.0)
        
        if center_x is None or center_y is None:
            return jsonify({'error': 'center_x and center_y required'}), 400
        
        mouse = get_advanced_mouse_controller()
        if not mouse:
            return jsonify({'error': 'Mouse controller not available'}), 503
        
        success = mouse.draw_circle(center_x, center_y, radius, duration)
        
        return jsonify({
            'status': 'success' if success else 'failed',
            'message': 'Circle drawn' if success else 'Failed to draw circle',
            'timestamp': datetime.now().isoformat()
        })
    
    except Exception as e:
        logger.error(f"Error drawing circle: {e}")
        return jsonify({'error': str(e)}), 500


@device_control_api.route('/mouse/find-image', methods=['POST'])
def mouse_find_image():
    """Найти изображение на экране"""
    try:
        data = request.get_json()
        image_path = data.get('image_path')
        confidence = data.get('confidence', 0.8)
        
        if not image_path:
            return jsonify({'error': 'image_path required'}), 400
        
        mouse = get_advanced_mouse_controller()
        if not mouse:
            return jsonify({'error': 'Mouse controller not available'}), 503
        
        location = mouse.find_image_on_screen(image_path, confidence)
        
        if location:
            return jsonify({
                'status': 'success',
                'location': {'x': location[0], 'y': location[1]},
                'timestamp': datetime.now().isoformat()
            })
        else:
            return jsonify({
                'status': 'not_found',
                'message': 'Image not found on screen',
                'timestamp': datetime.now().isoformat()
            })
    
    except Exception as e:
        logger.error(f"Error finding image: {e}")
        return jsonify({'error': str(e)}), 500


# ==================== KEYBOARD ENDPOINTS ====================

@device_control_api.route('/keyboard/type', methods=['POST'])
def keyboard_type():
    """Напечатать текст"""
    try:
        data = request.get_json()
        text = data.get('text')
        interval = data.get('interval', 0.05)
        
        if not text:
            return jsonify({'error': 'text required'}), 400
        
        keyboard = get_keyboard_controller()
        if not keyboard:
            return jsonify({'error': 'Keyboard controller not available'}), 503
        
        keyboard.type_text(text, interval=interval)
        
        return jsonify({
            'status': 'success',
            'message': f'Typed: {text[:50]}...',
            'timestamp': datetime.now().isoformat()
        })
    
    except Exception as e:
        logger.error(f"Error typing: {e}")
        return jsonify({'error': str(e)}), 500


@device_control_api.route('/keyboard/hotkey', methods=['POST'])
def keyboard_hotkey():
    """Выполнить комбинацию клавиш"""
    try:
        data = request.get_json()
        keys = data.get('keys', [])
        
        if not keys:
            return jsonify({'error': 'keys required'}), 400
        
        keyboard = get_keyboard_controller()
        if not keyboard:
            return jsonify({'error': 'Keyboard controller not available'}), 503
        
        import pyautogui
        pyautogui.hotkey(*keys)
        
        return jsonify({
            'status': 'success',
            'message': f'Hotkey executed: {"+".join(keys)}',
            'timestamp': datetime.now().isoformat()
        })
    
    except Exception as e:
        logger.error(f"Error executing hotkey: {e}")
        return jsonify({'error': str(e)}), 500


# ==================== TOUCH ENDPOINTS ====================

@device_control_api.route('/touch/tap', methods=['POST'])
def touch_tap():
    """Tap (одиночное касание)"""
    try:
        data = request.get_json()
        x = data.get('x')
        y = data.get('y')
        duration = data.get('duration', 0.1)
        
        if x is None or y is None:
            return jsonify({'error': 'x and y coordinates required'}), 400
        
        touch = get_touch_controller()
        if not touch:
            return jsonify({'error': 'Touch controller not available'}), 503
        
        success = touch.tap(x, y, duration)
        
        return jsonify({
            'status': 'success' if success else 'failed',
            'message': 'Tap executed' if success else 'Failed to execute tap',
            'timestamp': datetime.now().isoformat()
        })
    
    except Exception as e:
        logger.error(f"Error executing tap: {e}")
        return jsonify({'error': str(e)}), 500


@device_control_api.route('/touch/swipe', methods=['POST'])
def touch_swipe():
    """Swipe (свайп)"""
    try:
        data = request.get_json()
        start_x = data.get('start_x')
        start_y = data.get('start_y')
        end_x = data.get('end_x')
        end_y = data.get('end_y')
        duration = data.get('duration', 0.5)
        
        if None in [start_x, start_y, end_x, end_y]:
            return jsonify({'error': 'start_x, start_y, end_x, end_y required'}), 400
        
        touch = get_touch_controller()
        if not touch:
            return jsonify({'error': 'Touch controller not available'}), 503
        
        success = touch.swipe(start_x, start_y, end_x, end_y, duration)
        
        return jsonify({
            'status': 'success' if success else 'failed',
            'message': 'Swipe executed' if success else 'Failed to execute swipe',
            'timestamp': datetime.now().isoformat()
        })
    
    except Exception as e:
        logger.error(f"Error executing swipe: {e}")
        return jsonify({'error': str(e)}), 500


# ==================== HARDWARE ENDPOINTS ====================

@device_control_api.route('/hardware/status', methods=['GET'])
def hardware_status():
    """Получить статус оборудования"""
    try:
        monitor = get_advanced_hardware_monitor()
        if not monitor:
            return jsonify({'error': 'Hardware monitor not available'}), 503
        
        status = monitor.get_full_hardware_status()
        
        return jsonify({
            'status': 'success',
            'data': status,
            'timestamp': datetime.now().isoformat()
        })
    
    except Exception as e:
        logger.error(f"Error getting hardware status: {e}")
        return jsonify({'error': str(e)}), 500


@device_control_api.route('/hardware/gpu', methods=['GET'])
def hardware_gpu():
    """Получить информацию о GPU"""
    try:
        monitor = get_advanced_hardware_monitor()
        if not monitor:
            return jsonify({'error': 'Hardware monitor not available'}), 503
        
        gpus = monitor.get_all_gpu_info()
        
        return jsonify({
            'status': 'success',
            'gpus': [
                {
                    'index': g.index,
                    'name': g.name,
                    'type': g.gpu_type.value,
                    'total_memory': g.total_memory,
                    'used_memory': g.used_memory,
                    'temperature': g.temperature,
                    'power_usage': g.power_usage
                }
                for g in gpus
            ],
            'timestamp': datetime.now().isoformat()
        })
    
    except Exception as e:
        logger.error(f"Error getting GPU info: {e}")
        return jsonify({'error': str(e)}), 500


@device_control_api.route('/hardware/battery', methods=['GET'])
def hardware_battery():
    """Получить информацию о батарее"""
    try:
        monitor = get_advanced_hardware_monitor()
        if not monitor:
            return jsonify({'error': 'Hardware monitor not available'}), 503
        
        battery = monitor.get_battery_info()
        
        if battery:
            return jsonify({
                'status': 'success',
                'battery': {
                    'percent': battery.percent,
                    'seconds_left': battery.seconds_left,
                    'power_plugged': battery.power_plugged,
                    'health': battery.health
                },
                'timestamp': datetime.now().isoformat()
            })
        else:
            return jsonify({
                'status': 'not_found',
                'message': 'Battery not found',
                'timestamp': datetime.now().isoformat()
            })
    
    except Exception as e:
        logger.error(f"Error getting battery info: {e}")
        return jsonify({'error': str(e)}), 500


@device_control_api.route('/hardware/temperature', methods=['GET'])
def hardware_temperature():
    """Получить информацию о температуре"""
    try:
        monitor = get_advanced_hardware_monitor()
        if not monitor:
            return jsonify({'error': 'Hardware monitor not available'}), 503
        
        temps = monitor.get_all_temperatures()
        health = monitor.check_temperature_health()
        
        return jsonify({
            'status': 'success',
            'temperatures': [
                {
                    'component': t.component,
                    'label': t.label,
                    'current': t.current,
                    'high': t.high,
                    'critical': t.critical
                }
                for t in temps
            ],
            'health': health,
            'timestamp': datetime.now().isoformat()
        })
    
    except Exception as e:
        logger.error(f"Error getting temperature: {e}")
        return jsonify({'error': str(e)}), 500


# ==================== NETWORK ENDPOINTS ====================

@device_control_api.route('/network/status', methods=['GET'])
def network_status():
    """Получить статус сети"""
    try:
        monitor = get_network_monitor()
        if not monitor:
            return jsonify({'error': 'Network monitor not available'}), 503
        
        status = monitor.get_full_network_status()
        
        return jsonify({
            'status': 'success',
            'data': status,
            'timestamp': datetime.now().isoformat()
        })
    
    except Exception as e:
        logger.error(f"Error getting network status: {e}")
        return jsonify({'error': str(e)}), 500


@device_control_api.route('/network/interfaces', methods=['GET'])
def network_interfaces():
    """Получить информацию о сетевых интерфейсах"""
    try:
        monitor = get_network_monitor()
        if not monitor:
            return jsonify({'error': 'Network monitor not available'}), 503
        
        interfaces = monitor.get_network_interfaces()
        
        return jsonify({
            'status': 'success',
            'interfaces': [
                {
                    'name': i.name,
                    'type': i.connection_type.value,
                    'is_up': i.is_up,
                    'ipv4_address': i.ipv4_address,
                    'ipv6_address': i.ipv6_address,
                    'mac_address': i.mac_address
                }
                for i in interfaces
            ],
            'timestamp': datetime.now().isoformat()
        })
    
    except Exception as e:
        logger.error(f"Error getting network interfaces: {e}")
        return jsonify({'error': str(e)}), 500


# ==================== VISION ENDPOINTS ====================

@device_control_api.route('/vision/faces/detect', methods=['POST'])
def vision_detect_faces():
    """Детектировать лица на изображении"""
    try:
        data = request.get_json()
        image_path = data.get('image_path')
        
        if not image_path:
            return jsonify({'error': 'image_path required'}), 400
        
        face_module = get_face_recognition_module()
        if not face_module:
            return jsonify({'error': 'Face recognition module not available'}), 503
        
        faces = face_module.detect_faces_in_image(image_path)
        
        return jsonify({
            'status': 'success',
            'faces_count': len(faces),
            'faces': [
                {
                    'location': {
                        'top': f.location.top,
                        'right': f.location.right,
                        'bottom': f.location.bottom,
                        'left': f.location.left
                    },
                    'confidence': f.confidence
                }
                for f in faces
            ],
            'timestamp': datetime.now().isoformat()
        })
    
    except Exception as e:
        logger.error(f"Error detecting faces: {e}")
        return jsonify({'error': str(e)}), 500


@device_control_api.route('/vision/barcodes/detect', methods=['POST'])
def vision_detect_barcodes():
    """Детектировать штрих-коды на изображении"""
    try:
        data = request.get_json()
        image_path = data.get('image_path')
        
        if not image_path:
            return jsonify({'error': 'image_path required'}), 400
        
        barcode_module = get_barcode_recognition_module()
        if not barcode_module:
            return jsonify({'error': 'Barcode recognition module not available'}), 503
        
        barcodes = barcode_module.detect_barcodes_in_image(image_path)
        
        return jsonify({
            'status': 'success',
            'barcodes_count': len(barcodes),
            'barcodes': [
                {
                    'type': b.barcode_type.value,
                    'data': b.data,
                    'confidence': b.confidence
                }
                for b in barcodes
            ],
            'timestamp': datetime.now().isoformat()
        })
    
    except Exception as e:
        logger.error(f"Error detecting barcodes: {e}")
        return jsonify({'error': str(e)}), 500


# ==================== STATUS ENDPOINTS ====================

@device_control_api.route('/status', methods=['GET'])
def api_status():
    """Получить статус API"""
    return jsonify({
        'status': 'online',
        'version': '2.0',
        'modules': {
            'mouse': get_advanced_mouse_controller() is not None,
            'touch': get_touch_controller() is not None,
            'keyboard': get_keyboard_controller() is not None,
            'hardware': get_advanced_hardware_monitor() is not None,
            'network': get_network_monitor() is not None,
            'face_recognition': get_face_recognition_module() is not None,
            'barcode_recognition': get_barcode_recognition_module() is not None,
            'screen_analyzer': get_screen_analyzer() is not None
        },
        'timestamp': datetime.now().isoformat()
    })


@device_control_api.route('/health', methods=['GET'])
def api_health():
    """Проверка здоровья API"""
    try:
        monitor = get_advanced_hardware_monitor()
        
        if not monitor:
            return jsonify({'status': 'degraded', 'message': 'Hardware monitor not available'}), 503
        
        health = monitor.check_temperature_health()
        
        return jsonify({
            'status': health['status'],
            'temperature_health': health,
            'timestamp': datetime.now().isoformat()
        })
    
    except Exception as e:
        logger.error(f"Error checking health: {e}")
        return jsonify({'status': 'error', 'error': str(e)}), 500


def register_device_control_api(app):
    """Зарегистрировать API в Flask приложении"""
    app.register_blueprint(device_control_api)
    logger.info("Device Control API registered")

