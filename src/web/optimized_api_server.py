#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
Daur-AI: Оптимизированный Flask API сервер
Включает асинхронную обработку, кэширование, rate limiting, и улучшенную обработку ошибок

Версия: 2.0
Дата: 25.10.2025
Автор: Manus AI
"""

import logging
import json
import time
import threading
import queue
from typing import Dict, List, Any, Optional, Tuple
from datetime import datetime, timedelta
from functools import wraps
import hashlib

from flask import Flask, request, jsonify
from flask_cors import CORS
import psutil
import os
import sys

# Добавляем путь к модулям
project_root = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
sys.path.insert(0, project_root)

try:
    from src.config.settings import load_config
    from src.parser.optimized_command_parser import create_optimized_parser
    from src.executor.command_executor import CommandExecutor
    from src.ai.optimized_model_manager import create_optimized_manager
    from src.input.simple_controller import SimpleInputController
    from src.apps.manager import AppManager
    from src.files.manager import FileManager
except ImportError as e:
    print(f"Ошибка импорта: {e}")
    # Fallback импорты
    try:
        from src.config.settings import load_config
        from src.parser.command_parser import CommandParser
        from src.ai.simple_model import MockModelManager
        from src.input.simple_controller import SimpleInputController
        from src.apps.manager import AppManager
        from src.files.manager import FileManager
        CommandExecutor = None
    except ImportError as e2:
        print(f"Критическая ошибка импорта: {e2}")
        sys.exit(1)


class RateLimiter:
    """Ограничитель частоты запросов"""
    
    def __init__(self, max_requests: int = 100, window_seconds: int = 60):
        """
        Args:
            max_requests: Максимальное количество запросов
            window_seconds: Окно времени в секундах
        """
        self.max_requests = max_requests
        self.window_seconds = window_seconds
        self.requests = {}
        self.lock = threading.RLock()
    
    def is_allowed(self, client_id: str) -> bool:
        """
        Проверить, разрешен ли запрос для клиента
        
        Args:
            client_id: Идентификатор клиента (IP адрес)
            
        Returns:
            bool: True если запрос разрешен
        """
        with self.lock:
            now = time.time()
            
            # Очищаем старые записи
            if client_id in self.requests:
                self.requests[client_id] = [
                    req_time for req_time in self.requests[client_id]
                    if now - req_time < self.window_seconds
                ]
            else:
                self.requests[client_id] = []
            
            # Проверяем лимит
            if len(self.requests[client_id]) >= self.max_requests:
                return False
            
            # Добавляем новый запрос
            self.requests[client_id].append(now)
            return True


class RequestCache:
    """Кэш для результатов запросов"""
    
    def __init__(self, ttl: int = 300):
        """
        Args:
            ttl: Время жизни кэша в секундах
        """
        self.cache = {}
        self.ttl = ttl
        self.lock = threading.RLock()
    
    def get_key(self, method: str, path: str, params: Dict) -> str:
        """Генерация ключа кэша"""
        key_str = f"{method}:{path}:{json.dumps(params, sort_keys=True)}"
        return hashlib.md5(key_str.encode()).hexdigest()
    
    def get(self, key: str) -> Optional[Any]:
        """Получить значение из кэша"""
        with self.lock:
            if key in self.cache:
                value, timestamp = self.cache[key]
                if time.time() - timestamp < self.ttl:
                    return value
                else:
                    del self.cache[key]
        return None
    
    def set(self, key: str, value: Any):
        """Сохранить значение в кэш"""
        with self.lock:
            self.cache[key] = (value, time.time())
    
    def clear(self):
        """Очистить кэш"""
        with self.lock:
            self.cache.clear()


class OptimizedDaurWebAPI:
    """
    Оптимизированный веб API для управления Daur-AI агентом
    """
    
    def __init__(self, config: Dict[str, Any]):
        """
        Инициализация веб API
        
        Args:
            config (Dict): Конфигурация системы
        """
        self.logger = logging.getLogger('daur_ai.optimized_web_api')
        self.config = config
        
        # Flask приложение
        self.app = Flask(__name__)
        CORS(self.app)
        
        # Rate limiting
        self.rate_limiter = RateLimiter(max_requests=100, window_seconds=60)
        
        # Кэширование запросов
        self.request_cache = RequestCache(ttl=300)
        
        # Инициализация компонентов
        self._init_components()
        
        # Состояние агента
        self.agent_status = {
            'running': False,
            'last_command': None,
            'last_result': None,
            'start_time': None,
            'commands_executed': 0,
            'uptime_seconds': 0
        }
        
        # История команд
        self.command_history = []
        self.max_history = 100
        self.history_lock = threading.RLock()
        
        # Очередь команд для асинхронного выполнения
        self.command_queue = queue.Queue()
        self.command_worker_thread = None
        
        # Статистика API
        self.api_stats = {
            'total_requests': 0,
            'successful_requests': 0,
            'failed_requests': 0,
            'total_response_time': 0,
            'cache_hits': 0
        }
        self.stats_lock = threading.RLock()
        
        # Регистрация маршрутов
        self._register_routes()
        
        # Middleware для логирования и обработки ошибок
        self._setup_middleware()
        
        self.logger.info("Оптимизированный веб API инициализирован")
    
    def _init_components(self):
        """Инициализация компонентов системы"""
        
        try:
            # AI менеджер (оптимизированный)
            self.ai_manager = create_optimized_manager(self.config)
            
            # Системные компоненты
            import platform
            os_platform = platform.system()
            self.input_controller = SimpleInputController(os_platform)
            self.app_manager = AppManager(os_platform, self.input_controller)
            self.file_manager = FileManager()
            
            # Парсер команд (оптимизированный)
            self.command_parser = create_optimized_parser(self.ai_manager)
            
            # Исполнитель команд
            if CommandExecutor:
                self.command_executor = CommandExecutor(
                    input_controller=self.input_controller,
                    app_manager=self.app_manager,
                    file_manager=self.file_manager,
                    sandbox=True
                )
            else:
                self.command_executor = None
            
            self.logger.info("Компоненты системы инициализированы")
            
        except Exception as e:
            self.logger.error(f"Ошибка инициализации компонентов: {e}")
            raise
    
    def _setup_middleware(self):
        """Настройка middleware для обработки запросов"""
        
        @self.app.before_request
        def before_request():
            """Обработка перед запросом"""
            request.start_time = time.time()
            request.client_id = request.remote_addr
        
        @self.app.after_request
        def after_request(response):
            """Обработка после запроса"""
            if hasattr(request, 'start_time'):
                response_time = time.time() - request.start_time
                
                with self.stats_lock:
                    self.api_stats['total_requests'] += 1
                    self.api_stats['total_response_time'] += response_time
                    
                    if response.status_code < 400:
                        self.api_stats['successful_requests'] += 1
                    else:
                        self.api_stats['failed_requests'] += 1
                
                # Добавляем заголовки
                response.headers['X-Response-Time'] = str(round(response_time, 3))
                response.headers['X-API-Version'] = '2.0'
            
            return response
        
        @self.app.errorhandler(404)
        def not_found(error):
            """Обработка 404 ошибок"""
            return jsonify({
                'error': 'Endpoint не найден',
                'status': 404,
                'timestamp': datetime.now().isoformat()
            }), 404
        
        @self.app.errorhandler(500)
        def internal_error(error):
            """Обработка 500 ошибок"""
            self.logger.error(f"Внутренняя ошибка сервера: {error}")
            return jsonify({
                'error': 'Внутренняя ошибка сервера',
                'status': 500,
                'timestamp': datetime.now().isoformat()
            }), 500
    
    def _rate_limit_check(self, f):
        """Декоратор для проверки rate limiting"""
        @wraps(f)
        def decorated_function(*args, **kwargs):
            client_id = request.remote_addr
            
            if not self.rate_limiter.is_allowed(client_id):
                return jsonify({
                    'error': 'Превышен лимит запросов',
                    'status': 429,
                    'timestamp': datetime.now().isoformat()
                }), 429
            
            return f(*args, **kwargs)
        
        return decorated_function
    
    def _cache_response(self, cache_key: str = None):
        """Декоратор для кэширования ответов"""
        def decorator(f):
            @wraps(f)
            def decorated_function(*args, **kwargs):
                # Генерируем ключ кэша
                key = cache_key or self.request_cache.get_key(
                    request.method,
                    request.path,
                    request.args.to_dict()
                )
                
                # Проверяем кэш
                cached_response = self.request_cache.get(key)
                if cached_response is not None:
                    with self.stats_lock:
                        self.api_stats['cache_hits'] += 1
                    return cached_response
                
                # Выполняем функцию
                response = f(*args, **kwargs)
                
                # Кэшируем успешные ответы
                if isinstance(response, tuple) and len(response) > 1:
                    if response[1] < 400:
                        self.request_cache.set(key, response)
                else:
                    self.request_cache.set(key, response)
                
                return response
            
            return decorated_function
        return decorator
    
    def _register_routes(self):
        """Регистрация API маршрутов"""
        
        # Системная информация
        self.app.route('/health', methods=['GET'])(self._rate_limit_check(self.health_check))
        self.app.route('/system/status', methods=['GET'])(self._rate_limit_check(self._cache_response()(self.get_system_status)))
        self.app.route('/system/info', methods=['GET'])(self._rate_limit_check(self._cache_response()(self.get_system_info)))
        
        # Управление агентом
        self.app.route('/agent/status', methods=['GET'])(self._rate_limit_check(self.get_agent_status))
        self.app.route('/agent/start', methods=['POST'])(self._rate_limit_check(self.start_agent))
        self.app.route('/agent/stop', methods=['POST'])(self._rate_limit_check(self.stop_agent))
        self.app.route('/agent/stats', methods=['GET'])(self._rate_limit_check(self.get_agent_stats))
        
        # Выполнение команд
        self.app.route('/commands/execute', methods=['POST'])(self._rate_limit_check(self.execute_command))
        self.app.route('/commands/parse', methods=['POST'])(self._rate_limit_check(self.parse_command))
        self.app.route('/commands/history', methods=['GET'])(self._rate_limit_check(self.get_command_history))
        self.app.route('/commands/clear-history', methods=['POST'])(self._rate_limit_check(self.clear_command_history))
        
        # AI модели
        self.app.route('/ai/models', methods=['GET'])(self._rate_limit_check(self._cache_response()(self.get_ai_models)))
        self.app.route('/ai/status', methods=['GET'])(self._rate_limit_check(self.get_ai_status))
        self.app.route('/ai/test', methods=['POST'])(self._rate_limit_check(self.test_ai_model))
        self.app.route('/ai/stats', methods=['GET'])(self._rate_limit_check(self.get_ai_stats))
        
        # Файловые операции
        self.app.route('/files/list', methods=['GET'])(self._rate_limit_check(self.list_files))
        self.app.route('/files/create', methods=['POST'])(self._rate_limit_check(self.create_file))
        self.app.route('/files/read', methods=['GET'])(self._rate_limit_check(self.read_file))
        self.app.route('/files/delete', methods=['DELETE'])(self._rate_limit_check(self.delete_file))
        
        # Процессы и приложения
        self.app.route('/processes/list', methods=['GET'])(self._rate_limit_check(self._cache_response()(self.list_processes)))
        self.app.route('/apps/launch', methods=['POST'])(self._rate_limit_check(self.launch_app))
        
        # API статистика
        self.app.route('/api/stats', methods=['GET'])(self._rate_limit_check(self.get_api_stats))
        self.app.route('/api/health', methods=['GET'])(self._rate_limit_check(self.get_api_health))
        
        self.logger.info("API маршруты зарегистрированы")
    
    def health_check(self):
        """Проверка здоровья API"""
        return jsonify({
            'status': 'healthy',
            'timestamp': datetime.now().isoformat(),
            'version': '2.0',
            'components': {
                'ai_manager': self.ai_manager is not None,
                'command_parser': self.command_parser is not None,
                'command_executor': self.command_executor is not None,
                'input_controller': self.input_controller is not None
            }
        })
    
    def get_system_status(self):
        """Получение статуса системы"""
        try:
            cpu_percent = psutil.cpu_percent(interval=0.5)
            cpu_count = psutil.cpu_count()
            memory = psutil.virtual_memory()
            disk = psutil.disk_usage('/')
            process_count = len(psutil.pids())
            
            return jsonify({
                'cpu': {
                    'percent': round(cpu_percent, 1),
                    'count': cpu_count
                },
                'memory': {
                    'total': memory.total,
                    'available': memory.available,
                    'percent': round(memory.percent, 1),
                    'used': memory.used
                },
                'disk': {
                    'total': disk.total,
                    'free': disk.free,
                    'used': disk.used,
                    'percent': round((disk.used / disk.total) * 100, 1)
                },
                'processes': {
                    'count': process_count
                },
                'timestamp': datetime.now().isoformat()
            })
            
        except Exception as e:
            self.logger.error(f"Ошибка получения статуса системы: {e}")
            return jsonify({'error': str(e)}), 500
    
    def get_system_info(self):
        """Получение информации о системе"""
        try:
            import platform
            
            return jsonify({
                'platform': {
                    'system': platform.system(),
                    'release': platform.release(),
                    'version': platform.version(),
                    'machine': platform.machine(),
                    'processor': platform.processor()
                },
                'python': {
                    'version': platform.python_version(),
                    'implementation': platform.python_implementation()
                },
                'daur_ai': {
                    'version': '2.0',
                    'components': {
                        'ai_manager': type(self.ai_manager).__name__,
                        'command_parser': type(self.command_parser).__name__,
                        'command_executor': type(self.command_executor).__name__ if self.command_executor else None
                    }
                }
            })
            
        except Exception as e:
            self.logger.error(f"Ошибка получения информации о системе: {e}")
            return jsonify({'error': str(e)}), 500
    
    def get_agent_status(self):
        """Получение статуса агента"""
        if self.agent_status['running'] and self.agent_status['start_time']:
            uptime = time.time() - datetime.fromisoformat(self.agent_status['start_time']).timestamp()
            self.agent_status['uptime_seconds'] = int(uptime)
        
        return jsonify(self.agent_status)
    
    def start_agent(self):
        """Запуск агента"""
        try:
            if self.agent_status['running']:
                return jsonify({'error': 'Агент уже запущен'}), 400
            
            self.agent_status.update({
                'running': True,
                'start_time': datetime.now().isoformat(),
                'commands_executed': 0
            })
            
            self.logger.info("Агент запущен")
            return jsonify({'status': 'Агент запущен', 'timestamp': datetime.now().isoformat()})
            
        except Exception as e:
            self.logger.error(f"Ошибка запуска агента: {e}")
            return jsonify({'error': str(e)}), 500
    
    def stop_agent(self):
        """Остановка агента"""
        try:
            self.agent_status['running'] = False
            self.logger.info("Агент остановлен")
            return jsonify({'status': 'Агент остановлен', 'timestamp': datetime.now().isoformat()})
            
        except Exception as e:
            self.logger.error(f"Ошибка остановки агента: {e}")
            return jsonify({'error': str(e)}), 500
    
    def get_agent_stats(self):
        """Получение статистики агента"""
        return jsonify({
            'agent_status': self.agent_status,
            'parser_stats': self.command_parser.get_parse_stats(),
            'ai_stats': self.ai_manager.get_model_stats(),
            'timestamp': datetime.now().isoformat()
        })
    
    def execute_command(self):
        """Выполнение команды"""
        try:
            data = request.get_json()
            command_text = data.get('command', '')
            
            if not command_text:
                return jsonify({'error': 'Команда не указана'}), 400
            
            # Парсим команду
            parsed_command = self.command_parser.parse(command_text)
            
            # Выполняем команду
            if self.command_executor:
                result = self.command_executor.execute(parsed_command.to_dict())
            else:
                result = {
                    'success': False,
                    'message': 'Исполнитель команд недоступен',
                    'execution_time': 0
                }
            
            # Сохраняем в историю
            with self.history_lock:
                self.command_history.append({
                    'command': command_text,
                    'parsed': parsed_command.to_dict(),
                    'result': result,
                    'timestamp': datetime.now().isoformat()
                })
                
                if len(self.command_history) > self.max_history:
                    self.command_history.pop(0)
            
            # Обновляем статус агента
            if self.agent_status['running']:
                self.agent_status['commands_executed'] += 1
                self.agent_status['last_command'] = command_text
                self.agent_status['last_result'] = result
            
            return jsonify({
                'success': result.get('success', False),
                'command': command_text,
                'parsed': parsed_command.to_dict(),
                'result': result,
                'timestamp': datetime.now().isoformat()
            })
            
        except Exception as e:
            self.logger.error(f"Ошибка выполнения команды: {e}")
            return jsonify({'error': str(e)}), 500
    
    def parse_command(self):
        """Парсинг команды без выполнения"""
        try:
            data = request.get_json()
            command_text = data.get('command', '')
            
            if not command_text:
                return jsonify({'error': 'Команда не указана'}), 400
            
            parsed_command = self.command_parser.parse(command_text)
            
            return jsonify({
                'command': command_text,
                'parsed': parsed_command.to_dict(),
                'timestamp': datetime.now().isoformat()
            })
            
        except Exception as e:
            self.logger.error(f"Ошибка парсинга команды: {e}")
            return jsonify({'error': str(e)}), 500
    
    def get_command_history(self):
        """Получение истории команд"""
        limit = request.args.get('limit', 10, type=int)
        
        with self.history_lock:
            history = self.command_history[-limit:]
        
        return jsonify({
            'history': history,
            'total': len(self.command_history),
            'timestamp': datetime.now().isoformat()
        })
    
    def clear_command_history(self):
        """Очистка истории команд"""
        with self.history_lock:
            self.command_history.clear()
        
        return jsonify({'status': 'История очищена', 'timestamp': datetime.now().isoformat()})
    
    def get_ai_models(self):
        """Получение списка доступных моделей"""
        models = []
        for model_type, model in self.ai_manager.models.items():
            models.append({
                'type': model_type.value,
                'name': type(model).__name__,
                'active': model_type == self.ai_manager.active_model_type
            })
        
        return jsonify({
            'models': models,
            'active_model': self.ai_manager.active_model_type.value if self.ai_manager.active_model_type else None,
            'timestamp': datetime.now().isoformat()
        })
    
    def get_ai_status(self):
        """Получение статуса AI"""
        return jsonify({
            'active_model': self.ai_manager.active_model_type.value if self.ai_manager.active_model_type else None,
            'available_models': [m.value for m in self.ai_manager.models.keys()],
            'cache_stats': self.ai_manager.get_cache_stats(),
            'model_stats': self.ai_manager.get_model_stats(),
            'timestamp': datetime.now().isoformat()
        })
    
    def test_ai_model(self):
        """Тестирование AI модели"""
        try:
            data = request.get_json()
            prompt = data.get('prompt', 'Привет, как дела?')
            
            result = self.ai_manager.generate_response(prompt)
            
            return jsonify({
                'prompt': prompt,
                'response': result.get('response'),
                'model': result.get('model'),
                'from_cache': result.get('from_cache'),
                'processing_time': result.get('processing_time'),
                'timestamp': datetime.now().isoformat()
            })
            
        except Exception as e:
            self.logger.error(f"Ошибка тестирования AI модели: {e}")
            return jsonify({'error': str(e)}), 500
    
    def get_ai_stats(self):
        """Получение статистики AI"""
        return jsonify(self.ai_manager.get_full_stats())
    
    def list_files(self):
        """Получение списка файлов"""
        try:
            path = request.args.get('path', os.path.expanduser('~'))
            
            if not os.path.exists(path):
                return jsonify({'error': 'Путь не найден'}), 404
            
            files = []
            for item in os.listdir(path):
                item_path = os.path.join(path, item)
                files.append({
                    'name': item,
                    'path': item_path,
                    'is_dir': os.path.isdir(item_path),
                    'size': os.path.getsize(item_path) if os.path.isfile(item_path) else None
                })
            
            return jsonify({
                'path': path,
                'files': files,
                'timestamp': datetime.now().isoformat()
            })
            
        except Exception as e:
            self.logger.error(f"Ошибка получения списка файлов: {e}")
            return jsonify({'error': str(e)}), 500
    
    def create_file(self):
        """Создание файла"""
        try:
            data = request.get_json()
            path = data.get('path')
            content = data.get('content', '')
            
            if not path:
                return jsonify({'error': 'Путь не указан'}), 400
            
            os.makedirs(os.path.dirname(path), exist_ok=True)
            
            with open(path, 'w', encoding='utf-8') as f:
                f.write(content)
            
            return jsonify({
                'status': 'Файл создан',
                'path': path,
                'timestamp': datetime.now().isoformat()
            })
            
        except Exception as e:
            self.logger.error(f"Ошибка создания файла: {e}")
            return jsonify({'error': str(e)}), 500
    
    def read_file(self):
        """Чтение файла"""
        try:
            path = request.args.get('path')
            
            if not path or not os.path.exists(path):
                return jsonify({'error': 'Файл не найден'}), 404
            
            with open(path, 'r', encoding='utf-8') as f:
                content = f.read()
            
            return jsonify({
                'path': path,
                'content': content,
                'timestamp': datetime.now().isoformat()
            })
            
        except Exception as e:
            self.logger.error(f"Ошибка чтения файла: {e}")
            return jsonify({'error': str(e)}), 500
    
    def delete_file(self):
        """Удаление файла"""
        try:
            path = request.args.get('path')
            
            if not path or not os.path.exists(path):
                return jsonify({'error': 'Файл не найден'}), 404
            
            if os.path.isdir(path):
                import shutil
                shutil.rmtree(path)
            else:
                os.remove(path)
            
            return jsonify({
                'status': 'Файл удален',
                'path': path,
                'timestamp': datetime.now().isoformat()
            })
            
        except Exception as e:
            self.logger.error(f"Ошибка удаления файла: {e}")
            return jsonify({'error': str(e)}), 500
    
    def list_processes(self):
        """Получение списка процессов"""
        try:
            processes = []
            for proc in psutil.process_iter(['pid', 'name', 'status']):
                try:
                    processes.append({
                        'pid': proc.info['pid'],
                        'name': proc.info['name'],
                        'status': proc.info['status']
                    })
                except (psutil.NoSuchProcess, psutil.AccessDenied):
                    pass
            
            return jsonify({
                'processes': processes,
                'count': len(processes),
                'timestamp': datetime.now().isoformat()
            })
            
        except Exception as e:
            self.logger.error(f"Ошибка получения списка процессов: {e}")
            return jsonify({'error': str(e)}), 500
    
    def launch_app(self):
        """Запуск приложения"""
        try:
            data = request.get_json()
            app_name = data.get('app_name')
            
            if not app_name:
                return jsonify({'error': 'Имя приложения не указано'}), 400
            
            # Используем app_manager для запуска
            if self.app_manager:
                result = self.app_manager.launch(app_name)
            else:
                result = {'success': False, 'message': 'App manager недоступен'}
            
            return jsonify({
                'app_name': app_name,
                'result': result,
                'timestamp': datetime.now().isoformat()
            })
            
        except Exception as e:
            self.logger.error(f"Ошибка запуска приложения: {e}")
            return jsonify({'error': str(e)}), 500
    
    def get_api_stats(self):
        """Получение статистики API"""
        avg_response_time = 0
        if self.api_stats['total_requests'] > 0:
            avg_response_time = self.api_stats['total_response_time'] / self.api_stats['total_requests']
        
        return jsonify({
            'total_requests': self.api_stats['total_requests'],
            'successful_requests': self.api_stats['successful_requests'],
            'failed_requests': self.api_stats['failed_requests'],
            'cache_hits': self.api_stats['cache_hits'],
            'average_response_time': round(avg_response_time, 4),
            'timestamp': datetime.now().isoformat()
        })
    
    def get_api_health(self):
        """Получение полного здоровья API"""
        return jsonify({
            'api_stats': {
                'total_requests': self.api_stats['total_requests'],
                'successful_requests': self.api_stats['successful_requests'],
                'failed_requests': self.api_stats['failed_requests'],
                'cache_hits': self.api_stats['cache_hits']
            },
            'parser_stats': self.command_parser.get_parse_stats(),
            'ai_stats': self.ai_manager.get_model_stats(),
            'agent_status': self.agent_status,
            'timestamp': datetime.now().isoformat()
        })
    
    def run(self, host: str = '0.0.0.0', port: int = 8000, debug: bool = False):
        """
        Запуск API сервера
        
        Args:
            host: Хост для прослушивания
            port: Порт для прослушивания
            debug: Режим отладки
        """
        self.logger.info(f"Запуск API сервера на {host}:{port}")
        self.app.run(host=host, port=port, debug=debug, threaded=True)
    
    def shutdown(self):
        """Корректное завершение работы"""
        self.ai_manager.shutdown()
        self.logger.info("Оптимизированный API сервер завершил работу")


def create_optimized_api(config: Dict[str, Any]) -> OptimizedDaurWebAPI:
    """
    Фабрика для создания оптимизированного API
    
    Args:
        config: Конфигурация
        
    Returns:
        OptimizedDaurWebAPI: Инициализированный API
    """
    return OptimizedDaurWebAPI(config)


if __name__ == '__main__':
    # Загружаем конфигурацию
    config = load_config()
    
    # Создаем и запускаем API
    api = create_optimized_api(config)
    api.run(host='0.0.0.0', port=8000, debug=False)

