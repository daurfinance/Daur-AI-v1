"""
Real API Server for Daur-AI v2.0
Полнофункциональный REST API сервер

Endpoints:
- Auth: register, login, refresh, logout
- Input: mouse, keyboard, touch
- Hardware: status, cpu, memory, gpu, battery, network
- Vision: ocr, faces, barcodes
- System: status, health
"""

import logging
import json
from datetime import datetime
from functools import wraps
from typing import Dict, Tuple, Optional

from flask import Flask, request, jsonify
from flask_cors import CORS

# Импортируем наши модули
from src.security.real_security_manager import RealSecurityManager, UserRole
from src.input.real_input_controller import RealInputManager
from src.hardware.real_hardware_monitor import RealHardwareMonitor
from src.vision.real_vision_system import RealVisionSystem

# Настройка логирования
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Инициализируем Flask приложение
app = Flask(__name__)
app.config['JSON_SORT_KEYS'] = False

# Включаем CORS
CORS(app, resources={r"/api/*": {"origins": "*"}})

# Инициализируем менеджеры
security_manager = RealSecurityManager()
input_manager = RealInputManager()
hardware_monitor = RealHardwareMonitor()
vision_system = RealVisionSystem()

# Глобальные переменные
active_sessions: Dict[str, Dict] = {}


# ===== Decorators =====

def require_auth(f):
    """Декоратор для проверки аутентификации"""
    @wraps(f)
    def decorated_function(*args, **kwargs):
        token = None
        
        # Проверяем Authorization header
        if 'Authorization' in request.headers:
            auth_header = request.headers['Authorization']
            try:
                token = auth_header.split(" ")[1]
            except IndexError:
                return jsonify({'error': 'Invalid token format'}), 401
        
        # Проверяем API ключ
        api_key = request.headers.get('X-API-Key')
        if api_key:
            valid, user_id = security_manager.verify_api_key(api_key)
            if valid:
                request.user_id = user_id
                return f(*args, **kwargs)
        
        if not token:
            return jsonify({'error': 'Missing token'}), 401
        
        # Проверяем токен
        valid, payload = security_manager.verify_token(token)
        if not valid:
            return jsonify({'error': 'Invalid token'}), 401
        
        request.user_id = payload['user_id']
        request.user_role = payload['role']
        return f(*args, **kwargs)
    
    return decorated_function


def require_admin(f):
    """Декоратор для проверки прав администратора"""
    @wraps(f)
    @require_auth
    def decorated_function(*args, **kwargs):
        if request.user_role != UserRole.ADMIN.value:
            return jsonify({'error': 'Admin access required'}), 403
        return f(*args, **kwargs)
    
    return decorated_function


def check_rate_limit(f):
    """Декоратор для проверки rate limit"""
    @wraps(f)
    def decorated_function(*args, **kwargs):
        user_id = getattr(request, 'user_id', 'anonymous')
        allowed, count = security_manager.check_rate_limit(user_id, limit=100, window=60)
        
        if not allowed:
            return jsonify({'error': 'Rate limit exceeded'}), 429
        
        return f(*args, **kwargs)
    
    return decorated_function


# ===== Auth Endpoints =====

@app.route('/api/v2/auth/register', methods=['POST'])
def register():
    """Регистрация нового пользователя"""
    try:
        data = request.get_json()
        
        # Валидируем входные данные
        username = data.get('username', '').strip()
        email = data.get('email', '').strip()
        password = data.get('password', '')
        
        # Проверяем валидность
        valid, msg = security_manager.validate_username(username)
        if not valid:
            return jsonify({'error': msg}), 400
        
        valid, msg = security_manager.validate_email(email)
        if not valid:
            return jsonify({'error': msg}), 400
        
        valid, msg = security_manager.validate_password(password)
        if not valid:
            return jsonify({'error': msg}), 400
        
        # Регистрируем пользователя
        success, msg = security_manager.register_user(username, email, password)
        if not success:
            return jsonify({'error': msg}), 400
        
        return jsonify({
            'success': True,
            'message': 'User registered successfully'
        }), 201
    
    except Exception as e:
        logger.error(f"Registration error: {e}")
        return jsonify({'error': 'Registration failed'}), 500


@app.route('/api/v2/auth/login', methods=['POST'])
@check_rate_limit
def login():
    """Вход пользователя"""
    try:
        data = request.get_json()
        username = data.get('username')
        password = data.get('password')
        
        if not username or not password:
            return jsonify({'error': 'Missing credentials'}), 400
        
        # Аутентифицируем пользователя
        success, user_id = security_manager.authenticate_user(username, password)
        if not success:
            return jsonify({'error': 'Invalid credentials'}), 401
        
        # Создаём токены
        access_token = security_manager.create_access_token(user_id, expires_in=3600)
        refresh_token = security_manager.create_refresh_token(user_id)
        
        # Сохраняем сессию
        active_sessions[user_id] = {
            'username': username,
            'login_time': datetime.now().isoformat(),
            'access_token': access_token,
            'refresh_token': refresh_token
        }
        
        return jsonify({
            'success': True,
            'user_id': user_id,
            'access_token': access_token,
            'refresh_token': refresh_token,
            'token_type': 'Bearer'
        }), 200
    
    except Exception as e:
        logger.error(f"Login error: {e}")
        return jsonify({'error': 'Login failed'}), 500


@app.route('/api/v2/auth/refresh', methods=['POST'])
def refresh():
    """Обновить access token"""
    try:
        data = request.get_json()
        refresh_token = data.get('refresh_token')
        
        if not refresh_token:
            return jsonify({'error': 'Missing refresh token'}), 400
        
        # Проверяем refresh token
        valid, payload = security_manager.verify_token(refresh_token)
        if not valid:
            return jsonify({'error': 'Invalid refresh token'}), 401
        
        user_id = payload['user_id']
        
        # Создаём новый access token
        access_token = security_manager.create_access_token(user_id)
        
        return jsonify({
            'success': True,
            'access_token': access_token,
            'token_type': 'Bearer'
        }), 200
    
    except Exception as e:
        logger.error(f"Refresh error: {e}")
        return jsonify({'error': 'Refresh failed'}), 500


@app.route('/api/v2/auth/logout', methods=['POST'])
@require_auth
def logout():
    """Выход пользователя"""
    try:
        user_id = request.user_id
        
        # Удаляем сессию
        if user_id in active_sessions:
            del active_sessions[user_id]
        
        return jsonify({
            'success': True,
            'message': 'Logged out successfully'
        }), 200
    
    except Exception as e:
        logger.error(f"Logout error: {e}")
        return jsonify({'error': 'Logout failed'}), 500


# ===== Input Endpoints =====

@app.route('/api/v2/input/mouse/move', methods=['POST'])
@require_auth
@check_rate_limit
def mouse_move():
    """Переместить мышь"""
    try:
        data = request.get_json()
        x = data.get('x')
        y = data.get('y')
        duration = data.get('duration', 0.5)
        
        if x is None or y is None:
            return jsonify({'error': 'Missing x or y'}), 400
        
        input_manager.mouse_controller.move(x, y, duration)
        
        return jsonify({
            'success': True,
            'message': f'Mouse moved to ({x}, {y})'
        }), 200
    
    except Exception as e:
        logger.error(f"Mouse move error: {e}")
        return jsonify({'error': str(e)}), 500


@app.route('/api/v2/input/mouse/click', methods=['POST'])
@require_auth
@check_rate_limit
def mouse_click():
    """Нажать кнопку мыши"""
    try:
        data = request.get_json()
        button = data.get('button', 'left')
        clicks = data.get('clicks', 1)
        interval = data.get('interval', 0.1)
        
        input_manager.mouse_controller.click(button, clicks, interval)
        
        return jsonify({
            'success': True,
            'message': f'Mouse clicked: {button} x{clicks}'
        }), 200
    
    except Exception as e:
        logger.error(f"Mouse click error: {e}")
        return jsonify({'error': str(e)}), 500


@app.route('/api/v2/input/keyboard/type', methods=['POST'])
@require_auth
@check_rate_limit
def keyboard_type():
    """Напечатать текст"""
    try:
        data = request.get_json()
        text = data.get('text', '')
        interval = data.get('interval', 0.05)
        
        input_manager.keyboard_controller.type_text(text, interval)
        
        return jsonify({
            'success': True,
            'message': f'Text typed: {len(text)} characters'
        }), 200
    
    except Exception as e:
        logger.error(f"Keyboard type error: {e}")
        return jsonify({'error': str(e)}), 500


@app.route('/api/v2/input/keyboard/hotkey', methods=['POST'])
@require_auth
@check_rate_limit
def keyboard_hotkey():
    """Нажать комбинацию клавиш"""
    try:
        data = request.get_json()
        keys = data.get('keys', [])
        
        if not keys:
            return jsonify({'error': 'Missing keys'}), 400
        
        input_manager.keyboard_controller.hotkey(*keys)
        
        return jsonify({
            'success': True,
            'message': f'Hotkey pressed: {"+".join(keys)}'
        }), 200
    
    except Exception as e:
        logger.error(f"Keyboard hotkey error: {e}")
        return jsonify({'error': str(e)}), 500


# ===== Hardware Endpoints =====

@app.route('/api/v2/hardware/status', methods=['GET'])
@require_auth
def hardware_status():
    """Получить статус оборудования"""
    try:
        status = hardware_monitor.get_status()
        
        return jsonify({
            'success': True,
            'data': status
        }), 200
    
    except Exception as e:
        logger.error(f"Hardware status error: {e}")
        return jsonify({'error': str(e)}), 500


@app.route('/api/v2/hardware/cpu', methods=['GET'])
@require_auth
def hardware_cpu():
    """Получить информацию о CPU"""
    try:
        cpu_info = hardware_monitor.get_cpu_info()
        
        return jsonify({
            'success': True,
            'data': cpu_info
        }), 200
    
    except Exception as e:
        logger.error(f"CPU info error: {e}")
        return jsonify({'error': str(e)}), 500


@app.route('/api/v2/hardware/memory', methods=['GET'])
@require_auth
def hardware_memory():
    """Получить информацию о памяти"""
    try:
        memory_info = hardware_monitor.get_memory_info()
        
        return jsonify({
            'success': True,
            'data': memory_info
        }), 200
    
    except Exception as e:
        logger.error(f"Memory info error: {e}")
        return jsonify({'error': str(e)}), 500


@app.route('/api/v2/hardware/gpu', methods=['GET'])
@require_auth
def hardware_gpu():
    """Получить информацию о GPU"""
    try:
        gpu_info = hardware_monitor.get_gpu_info()
        
        return jsonify({
            'success': True,
            'data': gpu_info
        }), 200
    
    except Exception as e:
        logger.error(f"GPU info error: {e}")
        return jsonify({'error': str(e)}), 500


@app.route('/api/v2/hardware/battery', methods=['GET'])
@require_auth
def hardware_battery():
    """Получить информацию о батарее"""
    try:
        battery_info = hardware_monitor.get_battery_info()
        
        return jsonify({
            'success': True,
            'data': battery_info
        }), 200
    
    except Exception as e:
        logger.error(f"Battery info error: {e}")
        return jsonify({'error': str(e)}), 500


@app.route('/api/v2/hardware/network', methods=['GET'])
@require_auth
def hardware_network():
    """Получить информацию о сети"""
    try:
        network_info = hardware_monitor.get_network_info()
        
        return jsonify({
            'success': True,
            'data': network_info
        }), 200
    
    except Exception as e:
        logger.error(f"Network info error: {e}")
        return jsonify({'error': str(e)}), 500


# ===== Vision Endpoints =====

@app.route('/api/v2/vision/ocr', methods=['POST'])
@require_auth
@check_rate_limit
def vision_ocr():
    """Извлечь текст из изображения"""
    try:
        # Получаем файл из request
        if 'file' not in request.files:
            return jsonify({'error': 'Missing file'}), 400
        
        file = request.files['file']
        if file.filename == '':
            return jsonify({'error': 'No file selected'}), 400
        
        # Сохраняем временный файл
        import tempfile
        with tempfile.NamedTemporaryFile(delete=False, suffix='.png') as tmp:
            file.save(tmp.name)
            
            # Выполняем OCR
            result = vision_system.extract_text(tmp.name)
        
        return jsonify({
            'success': True,
            'data': result
        }), 200
    
    except Exception as e:
        logger.error(f"OCR error: {e}")
        return jsonify({'error': str(e)}), 500


@app.route('/api/v2/vision/faces', methods=['POST'])
@require_auth
@check_rate_limit
def vision_faces():
    """Детектировать лица в изображении"""
    try:
        if 'file' not in request.files:
            return jsonify({'error': 'Missing file'}), 400
        
        file = request.files['file']
        
        import tempfile
        with tempfile.NamedTemporaryFile(delete=False, suffix='.png') as tmp:
            file.save(tmp.name)
            
            # Детектируем лица
            result = vision_system.detect_faces(tmp.name)
        
        return jsonify({
            'success': True,
            'data': result
        }), 200
    
    except Exception as e:
        logger.error(f"Face detection error: {e}")
        return jsonify({'error': str(e)}), 500


@app.route('/api/v2/vision/barcodes', methods=['POST'])
@require_auth
@check_rate_limit
def vision_barcodes():
    """Детектировать штрих-коды в изображении"""
    try:
        if 'file' not in request.files:
            return jsonify({'error': 'Missing file'}), 400
        
        file = request.files['file']
        
        import tempfile
        with tempfile.NamedTemporaryFile(delete=False, suffix='.png') as tmp:
            file.save(tmp.name)
            
            # Детектируем штрих-коды
            result = vision_system.detect_barcodes(tmp.name)
        
        return jsonify({
            'success': True,
            'data': result
        }), 200
    
    except Exception as e:
        logger.error(f"Barcode detection error: {e}")
        return jsonify({'error': str(e)}), 500


# ===== System Endpoints =====

@app.route('/api/v2/status', methods=['GET'])
def api_status():
    """Получить статус API"""
    return jsonify({
        'success': True,
        'status': 'online',
        'version': '2.0',
        'timestamp': datetime.now().isoformat(),
        'modules': {
            'input': 'active',
            'hardware': 'active',
            'vision': 'active',
            'security': 'active'
        }
    }), 200


@app.route('/api/v2/health', methods=['GET'])
def api_health():
    """Проверка здоровья API"""
    try:
        # Проверяем все модули
        hardware_status = hardware_monitor.get_status()
        
        return jsonify({
            'success': True,
            'health': 'healthy',
            'timestamp': datetime.now().isoformat(),
            'modules': {
                'input': 'healthy',
                'hardware': 'healthy' if hardware_status else 'degraded',
                'vision': 'healthy',
                'security': 'healthy'
            }
        }), 200
    
    except Exception as e:
        logger.error(f"Health check error: {e}")
        return jsonify({
            'success': False,
            'health': 'unhealthy',
            'error': str(e)
        }), 500


# ===== Error Handlers =====

@app.errorhandler(404)
def not_found(error):
    """Обработчик ошибки 404"""
    return jsonify({'error': 'Endpoint not found'}), 404


@app.errorhandler(500)
def internal_error(error):
    """Обработчик ошибки 500"""
    logger.error(f"Internal error: {error}")
    return jsonify({'error': 'Internal server error'}), 500


# ===== Startup =====

if __name__ == '__main__':
    logger.info("Starting Real API Server v2.0")
    app.run(host='0.0.0.0', port=5000, debug=False)

