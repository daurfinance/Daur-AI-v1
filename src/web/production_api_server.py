"""
Production-Grade REST API Server for Daur-AI v2.0
"""

from flask import Flask, request, jsonify
from flask_cors import CORS
from flask_limiter import Limiter
from flask_limiter.util import get_remote_address
import logging
from datetime import datetime
from functools import wraps
import json

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

app = Flask(__name__)
CORS(app)
limiter = Limiter(app=app, key_func=get_remote_address, default_limits=["200 per day", "50 per hour"])

# Импорт модулей
from src.input.production_input_controller import ProductionInputManager
from src.hardware.production_hardware_monitor import ProductionHardwareMonitor
from src.vision.production_vision_system import ProductionVisionSystem
from src.security.production_security import ProductionSecurityManager

# Инициализация
input_manager = ProductionInputManager()
hardware_monitor = ProductionHardwareMonitor()
vision_system = ProductionVisionSystem()
security_manager = ProductionSecurityManager()

# Глобальные переменные
api_version = "2.0"
start_time = datetime.now()


def require_token(f):
    """Декоратор для требования токена"""
    @wraps(f)
    def decorated_function(*args, **kwargs):
        token = request.headers.get('Authorization', '').replace('Bearer ', '')
        if not token or not security_manager.verify_token(token):
            return jsonify({'error': 'Unauthorized'}), 401
        return f(*args, **kwargs)
    return decorated_function


# ============= AUTH ENDPOINTS =============

@app.route('/api/v2/auth/register', methods=['POST'])
@limiter.limit("5 per hour")
def register():
    """Регистрация пользователя"""
    try:
        data = request.get_json()
        
        # Валидация
        schema = {
            'username': {'type': str, 'required': True, 'min_length': 3, 'max_length': 50},
            'password': {'type': str, 'required': True, 'min_length': 8},
            'email': {'type': str, 'required': True}
        }
        
        valid, error = security_manager.validate_input(data, schema)
        if not valid:
            return jsonify({'error': error}), 400
        
        success = security_manager.create_user(
            data['username'],
            data['password'],
            data['email']
        )
        
        if success:
            return jsonify({'message': 'User registered successfully'}), 201
        else:
            return jsonify({'error': 'User already exists'}), 409
    
    except Exception as e:
        logger.error(f"Error in register: {e}")
        return jsonify({'error': str(e)}), 500


@app.route('/api/v2/auth/login', methods=['POST'])
@limiter.limit("10 per hour")
def login():
    """Вход пользователя"""
    try:
        data = request.get_json()
        
        token = security_manager.authenticate(
            data.get('username'),
            data.get('password')
        )
        
        if token:
            return jsonify({'token': token, 'expires_in': 86400}), 200
        else:
            return jsonify({'error': 'Invalid credentials'}), 401
    
    except Exception as e:
        logger.error(f"Error in login: {e}")
        return jsonify({'error': str(e)}), 500


# ============= INPUT ENDPOINTS =============

@app.route('/api/v2/input/mouse/move', methods=['POST'])
@require_token
def mouse_move():
    """Переместить мышь"""
    try:
        data = request.get_json()
        success = input_manager.mouse.move_to(
            data['x'],
            data['y'],
            data.get('duration', 0.5)
        )
        return jsonify({'success': success}), 200 if success else 400
    except Exception as e:
        return jsonify({'error': str(e)}), 500


@app.route('/api/v2/input/mouse/click', methods=['POST'])
@require_token
def mouse_click():
    """Нажать кнопку мыши"""
    try:
        data = request.get_json()
        success = input_manager.mouse.click(
            data.get('x'),
            data.get('y'),
            data.get('button', 'left')
        )
        return jsonify({'success': success}), 200 if success else 400
    except Exception as e:
        return jsonify({'error': str(e)}), 500


@app.route('/api/v2/input/keyboard/type', methods=['POST'])
@require_token
def keyboard_type():
    """Напечатать текст"""
    try:
        data = request.get_json()
        success = input_manager.keyboard.type_text(
            data['text'],
            data.get('interval', 0.05)
        )
        return jsonify({'success': success}), 200 if success else 400
    except Exception as e:
        return jsonify({'error': str(e)}), 500


@app.route('/api/v2/input/keyboard/hotkey', methods=['POST'])
@require_token
def keyboard_hotkey():
    """Нажать комбинацию клавиш"""
    try:
        data = request.get_json()
        success = input_manager.keyboard.hotkey(*data['keys'])
        return jsonify({'success': success}), 200 if success else 400
    except Exception as e:
        return jsonify({'error': str(e)}), 500


# ============= HARDWARE ENDPOINTS =============

@app.route('/api/v2/hardware/status', methods=['GET'])
@require_token
def hardware_status():
    """Получить статус оборудования"""
    try:
        status = hardware_monitor.get_full_status()
        return jsonify(status), 200
    except Exception as e:
        return jsonify({'error': str(e)}), 500


@app.route('/api/v2/hardware/cpu', methods=['GET'])
@require_token
def hardware_cpu():
    """Получить информацию о CPU"""
    try:
        cpu_info = hardware_monitor.get_cpu_info()
        return jsonify(cpu_info.to_dict() if cpu_info else {}), 200
    except Exception as e:
        return jsonify({'error': str(e)}), 500


@app.route('/api/v2/hardware/memory', methods=['GET'])
@require_token
def hardware_memory():
    """Получить информацию о памяти"""
    try:
        mem_info = hardware_monitor.get_memory_info()
        return jsonify(mem_info.to_dict() if mem_info else {}), 200
    except Exception as e:
        return jsonify({'error': str(e)}), 500


@app.route('/api/v2/hardware/gpu', methods=['GET'])
@require_token
def hardware_gpu():
    """Получить информацию о GPU"""
    try:
        gpu_info = hardware_monitor.get_gpu_info()
        return jsonify([g.to_dict() for g in (gpu_info or [])]), 200
    except Exception as e:
        return jsonify({'error': str(e)}), 500


@app.route('/api/v2/hardware/battery', methods=['GET'])
@require_token
def hardware_battery():
    """Получить информацию о батарее"""
    try:
        battery_info = hardware_monitor.get_battery_info()
        return jsonify(battery_info.to_dict() if battery_info else {}), 200
    except Exception as e:
        return jsonify({'error': str(e)}), 500


# ============= VISION ENDPOINTS =============

@app.route('/api/v2/vision/ocr', methods=['POST'])
@require_token
def vision_ocr():
    """Извлечь текст из изображения"""
    try:
        data = request.get_json()
        result = vision_system.ocr_engine.extract_text_from_image(data['image_path'])
        return jsonify(result.to_dict() if result else {}), 200
    except Exception as e:
        return jsonify({'error': str(e)}), 500


@app.route('/api/v2/vision/faces', methods=['POST'])
@require_token
def vision_faces():
    """Детектировать лица"""
    try:
        data = request.get_json()
        faces = vision_system.face_recognition.detect_faces(data['image_path'])
        return jsonify([f.to_dict() for f in faces]), 200
    except Exception as e:
        return jsonify({'error': str(e)}), 500


@app.route('/api/v2/vision/barcodes', methods=['POST'])
@require_token
def vision_barcodes():
    """Детектировать штрих-коды"""
    try:
        data = request.get_json()
        barcodes = vision_system.barcode_recognition.detect_barcodes(data['image_path'])
        return jsonify([b.to_dict() for b in barcodes]), 200
    except Exception as e:
        return jsonify({'error': str(e)}), 500


# ============= SYSTEM ENDPOINTS =============

@app.route('/api/v2/status', methods=['GET'])
def api_status():
    """Статус API"""
    return jsonify({
        'status': 'running',
        'version': api_version,
        'uptime': str(datetime.now() - start_time),
        'timestamp': datetime.now().isoformat()
    }), 200


@app.route('/api/v2/health', methods=['GET'])
def api_health():
    """Проверка здоровья"""
    try:
        cpu = hardware_monitor.get_cpu_info()
        mem = hardware_monitor.get_memory_info()
        
        health = {
            'status': 'healthy',
            'cpu_percent': cpu.percent if cpu else 0,
            'memory_percent': mem.percent if mem else 0,
            'timestamp': datetime.now().isoformat()
        }
        
        return jsonify(health), 200
    except Exception as e:
        return jsonify({'status': 'unhealthy', 'error': str(e)}), 500


@app.errorhandler(404)
def not_found(error):
    """Обработчик 404"""
    return jsonify({'error': 'Not found'}), 404


@app.errorhandler(500)
def internal_error(error):
    """Обработчик 500"""
    logger.error(f"Internal error: {error}")
    return jsonify({'error': 'Internal server error'}), 500


if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=False, ssl_context='adhoc')

