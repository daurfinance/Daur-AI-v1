#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
Daur-AI: Улучшенный Flask API сервер
Полная интеграция с агентом, исполнителем команд и AI моделями

Версия: 1.2
Дата: 01.10.2025
"""

import logging
import json
import time
import threading
import queue
from typing import Dict, List, Any, Optional
from datetime import datetime
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
    from src.parser.enhanced_command_parser import create_enhanced_parser
    from src.executor.command_executor import CommandExecutor
    from src.ai.enhanced_model_manager import EnhancedModelManager
    from src.input.simple_controller import SimpleInputController
    from src.apps.manager import AppManager
    from src.files.manager import FileManager
except ImportError as e:
    print(f"Ошибка импорта: {e}")
    # Fallback импорты
    try:
        from src.config.settings import load_config
        from src.parser.command_parser import CommandParser
        from src.ai.simple_model import MockModelManager as EnhancedModelManager
        from src.input.simple_controller import SimpleInputController
        from src.apps.manager import AppManager
        from src.files.manager import FileManager
        CommandExecutor = None
    except ImportError as e2:
        print(f"Критическая ошибка импорта: {e2}")
        sys.exit(1)


class EnhancedDaurWebAPI:
    """
    Улучшенный веб API для управления Daur-AI агентом
    """
    
    def __init__(self, config: Dict[str, Any]):
        """
        Инициализация веб API
        
        Args:
            config (Dict): Конфигурация системы
        """
        self.logger = logging.getLogger('daur_ai.enhanced_web_api')
        self.config = config
        
        # Flask приложение
        self.app = Flask(__name__)
        CORS(self.app)  # Разрешаем CORS для веб-панели
        
        # Инициализация компонентов
        self._init_components()
        
        # Состояние агента
        self.agent_status = {
            'running': False,
            'last_command': None,
            'last_result': None,
            'start_time': None,
            'commands_executed': 0
        }
        
        # История команд
        self.command_history = []
        self.max_history = 100
        
        # Очередь команд для асинхронного выполнения
        self.command_queue = queue.Queue()
        self.command_worker_thread = None
        
        # Регистрация маршрутов
        self._register_routes()
        
        self.logger.info("Улучшенный веб API инициализирован")
    
    def _init_components(self):
        """Инициализация компонентов системы"""
        
        try:
            # AI менеджер
            self.ai_manager = EnhancedModelManager(self.config)
            
            # Системные компоненты
            import platform
            os_platform = platform.system()
            self.input_controller = SimpleInputController(os_platform)
            self.app_manager = AppManager(os_platform, self.input_controller)
            self.file_manager = FileManager()
            
            # Парсер команд
            if callable(create_enhanced_parser):
                self.command_parser = create_enhanced_parser(self.ai_manager)
            else:
                from src.parser.command_parser import CommandParser
                self.command_parser = CommandParser(self.ai_manager)
            
            # Исполнитель команд
            if CommandExecutor:
                self.command_executor = CommandExecutor(
                    input_controller=self.input_controller,
                    app_manager=self.app_manager,
                    file_manager=self.file_manager,
                    sandbox=True  # API всегда в безопасном режиме
                )
            else:
                self.command_executor = None
            
            self.logger.info("Компоненты системы инициализированы")
            
        except Exception as e:
            self.logger.error(f"Ошибка инициализации компонентов: {e}")
            raise
    
    def _register_routes(self):
        """Регистрация API маршрутов"""
        
        # Системная информация
        self.app.route('/health', methods=['GET'])(self.health_check)
        self.app.route('/system/status', methods=['GET'])(self.get_system_status)
        self.app.route('/system/info', methods=['GET'])(self.get_system_info)
        
        # Управление агентом
        self.app.route('/agent/status', methods=['GET'])(self.get_agent_status)
        self.app.route('/agent/start', methods=['POST'])(self.start_agent)
        self.app.route('/agent/stop', methods=['POST'])(self.stop_agent)
        self.app.route('/agent/stats', methods=['GET'])(self.get_agent_stats)
        
        # Выполнение команд
        self.app.route('/commands/execute', methods=['POST'])(self.execute_command)
        self.app.route('/commands/history', methods=['GET'])(self.get_command_history)
        self.app.route('/commands/clear-history', methods=['POST'])(self.clear_command_history)
        
        # AI модели
        self.app.route('/ai/models', methods=['GET'])(self.get_ai_models)
        self.app.route('/ai/status', methods=['GET'])(self.get_ai_status)
        self.app.route('/ai/test', methods=['POST'])(self.test_ai_model)
        
        # Файловые операции
        self.app.route('/files/list', methods=['GET'])(self.list_files)
        self.app.route('/files/create', methods=['POST'])(self.create_file)
        self.app.route('/files/read', methods=['GET'])(self.read_file)
        self.app.route('/files/delete', methods=['DELETE'])(self.delete_file)
        
        # Процессы и приложения
        self.app.route('/processes/list', methods=['GET'])(self.list_processes)
        self.app.route('/apps/launch', methods=['POST'])(self.launch_app)
        
        # Логи
        self.app.route('/logs/recent', methods=['GET'])(self.get_recent_logs)
        
        self.logger.info("API маршруты зарегистрированы")
    
    def health_check(self):
        """Проверка здоровья API"""
        return jsonify({
            'status': 'healthy',
            'timestamp': datetime.now().isoformat(),
            'version': '1.2',
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
            # CPU информация
            cpu_percent = psutil.cpu_percent(interval=1)
            cpu_count = psutil.cpu_count()
            
            # Память
            memory = psutil.virtual_memory()
            
            # Диск
            disk = psutil.disk_usage('/')
            
            # Процессы
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
                    'version': '1.2',
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
        return jsonify(self.agent_status)
    
    def start_agent(self):
        """Запуск агента"""
        try:
            if self.agent_status['running']:
                return jsonify({'error': 'Агент уже запущен'}), 400
            
            # Запускаем worker поток для команд
            if not self.command_worker_thread or not self.command_worker_thread.is_alive():
                self.command_worker_thread = threading.Thread(target=self._command_worker, daemon=True)
                self.command_worker_thread.start()
            
            self.agent_status.update({
                'running': True,
                'start_time': datetime.now().isoformat(),
                'commands_executed': 0
            })
            
            self.logger.info("Агент запущен через API")
            return jsonify({'message': 'Агент запущен', 'status': self.agent_status})
            
        except Exception as e:
            self.logger.error(f"Ошибка запуска агента: {e}")
            return jsonify({'error': str(e)}), 500
    
    def stop_agent(self):
        """Остановка агента"""
        try:
            self.agent_status['running'] = False
            
            self.logger.info("Агент остановлен через API")
            return jsonify({'message': 'Агент остановлен', 'status': self.agent_status})
            
        except Exception as e:
            self.logger.error(f"Ошибка остановки агента: {e}")
            return jsonify({'error': str(e)}), 500
    
    def get_agent_stats(self):
        """Получение статистики агента"""
        try:
            stats = {
                'agent_status': self.agent_status,
                'command_history_count': len(self.command_history),
                'queue_size': self.command_queue.qsize() if hasattr(self.command_queue, 'qsize') else 0
            }
            
            # Добавляем статистику исполнителя если доступен
            if self.command_executor:
                stats['executor_stats'] = self.command_executor.get_stats()
            
            return jsonify(stats)
            
        except Exception as e:
            self.logger.error(f"Ошибка получения статистики агента: {e}")
            return jsonify({'error': str(e)}), 500
    
    def execute_command(self):
        """Выполнение команды"""
        try:
            data = request.get_json()
            if not data or 'command' not in data:
                return jsonify({'error': 'Команда не указана'}), 400
            
            command_text = data['command'].strip()
            if not command_text:
                return jsonify({'error': 'Пустая команда'}), 400
            
            # Добавляем команду в очередь для асинхронного выполнения
            command_id = f"cmd_{int(time.time() * 1000)}"
            
            command_entry = {
                'id': command_id,
                'command': command_text,
                'timestamp': datetime.now().isoformat(),
                'status': 'queued'
            }
            
            # Синхронное выполнение для API
            try:
                # Парсинг команды
                parsed_command = self.command_parser.parse(command_text)
                
                if not parsed_command or parsed_command.get('command_type') == 'unknown':
                    error_msg = parsed_command.get('parameters', {}).get('error', 'Не удалось распознать команду')
                    command_entry.update({
                        'status': 'failed',
                        'error': error_msg,
                        'result': None
                    })
                else:
                    # Выполнение команды
                    if self.command_executor:
                        execution_result = self.command_executor.execute(parsed_command)
                        
                        command_entry.update({
                            'status': 'completed' if execution_result.get('success') else 'failed',
                            'result': execution_result,
                            'parsed_command': parsed_command
                        })
                        
                        # Обновляем статистику агента
                        self.agent_status['commands_executed'] += 1
                        self.agent_status['last_command'] = command_text
                        self.agent_status['last_result'] = execution_result
                    else:
                        command_entry.update({
                            'status': 'failed',
                            'error': 'Исполнитель команд недоступен',
                            'result': None
                        })
                
                # Добавляем в историю
                self.command_history.append(command_entry)
                if len(self.command_history) > self.max_history:
                    self.command_history.pop(0)
                
                return jsonify({
                    'command_id': command_id,
                    'status': command_entry['status'],
                    'result': command_entry.get('result'),
                    'message': 'Команда выполнена' if command_entry['status'] == 'completed' else command_entry.get('error', 'Ошибка выполнения')
                })
                
            except Exception as e:
                self.logger.error(f"Ошибка выполнения команды: {e}")
                command_entry.update({
                    'status': 'failed',
                    'error': str(e),
                    'result': None
                })
                
                self.command_history.append(command_entry)
                return jsonify({'error': str(e)}), 500
            
        except Exception as e:
            self.logger.error(f"Ошибка API выполнения команды: {e}")
            return jsonify({'error': str(e)}), 500
    
    def get_command_history(self):
        """Получение истории команд"""
        try:
            limit = request.args.get('limit', 50, type=int)
            offset = request.args.get('offset', 0, type=int)
            
            # Ограничиваем лимит
            limit = min(limit, 100)
            
            # Получаем срез истории
            history_slice = self.command_history[offset:offset + limit]
            
            return jsonify({
                'commands': history_slice,
                'total': len(self.command_history),
                'limit': limit,
                'offset': offset
            })
            
        except Exception as e:
            self.logger.error(f"Ошибка получения истории команд: {e}")
            return jsonify({'error': str(e)}), 500
    
    def clear_command_history(self):
        """Очистка истории команд"""
        try:
            self.command_history.clear()
            return jsonify({'message': 'История команд очищена'})
            
        except Exception as e:
            self.logger.error(f"Ошибка очистки истории команд: {e}")
            return jsonify({'error': str(e)}), 500
    
    def get_ai_models(self):
        """Получение списка AI моделей"""
        try:
            models_info = {
                'available_models': [],
                'active_model': None,
                'model_status': {}
            }
            
            if hasattr(self.ai_manager, 'get_available_models'):
                models_info['available_models'] = self.ai_manager.get_available_models()
            
            if hasattr(self.ai_manager, 'get_active_model'):
                models_info['active_model'] = self.ai_manager.get_active_model()
            
            if hasattr(self.ai_manager, 'get_model_status'):
                models_info['model_status'] = self.ai_manager.get_model_status()
            
            return jsonify(models_info)
            
        except Exception as e:
            self.logger.error(f"Ошибка получения списка AI моделей: {e}")
            return jsonify({'error': str(e)}), 500
    
    def get_ai_status(self):
        """Получение статуса AI"""
        try:
            ai_status = {
                'manager_type': type(self.ai_manager).__name__,
                'available': self.ai_manager is not None,
                'models': {}
            }
            
            # Проверяем доступность различных типов моделей
            if hasattr(self.ai_manager, 'ollama_manager'):
                ai_status['models']['ollama'] = {
                    'available': hasattr(self.ai_manager.ollama_manager, 'is_available') and self.ai_manager.ollama_manager.is_available(),
                    'models': getattr(self.ai_manager.ollama_manager, 'available_models', [])
                }
            
            if hasattr(self.ai_manager, 'openai_manager'):
                ai_status['models']['openai'] = {
                    'available': hasattr(self.ai_manager.openai_manager, 'is_available') and self.ai_manager.openai_manager.is_available()
                }
            
            return jsonify(ai_status)
            
        except Exception as e:
            self.logger.error(f"Ошибка получения статуса AI: {e}")
            return jsonify({'error': str(e)}), 500
    
    def test_ai_model(self):
        """Тестирование AI модели"""
        try:
            data = request.get_json()
            test_prompt = data.get('prompt', 'Привет! Как дела?')
            
            if hasattr(self.ai_manager, 'generate_response'):
                start_time = time.time()
                response = self.ai_manager.generate_response(test_prompt)
                end_time = time.time()
                
                return jsonify({
                    'success': True,
                    'prompt': test_prompt,
                    'response': response,
                    'response_time': round(end_time - start_time, 2),
                    'model': getattr(self.ai_manager, 'active_model_type', 'unknown')
                })
            else:
                return jsonify({
                    'success': False,
                    'error': 'AI менеджер не поддерживает генерацию ответов'
                })
                
        except Exception as e:
            self.logger.error(f"Ошибка тестирования AI модели: {e}")
            return jsonify({'error': str(e)}), 500
    
    def list_files(self):
        """Список файлов"""
        try:
            directory = request.args.get('directory', os.path.expanduser('~/daur_ai_files'))
            
            if not os.path.exists(directory):
                os.makedirs(directory, exist_ok=True)
            
            files = []
            for item in os.listdir(directory):
                item_path = os.path.join(directory, item)
                files.append({
                    'name': item,
                    'type': 'directory' if os.path.isdir(item_path) else 'file',
                    'size': os.path.getsize(item_path) if os.path.isfile(item_path) else 0,
                    'modified': datetime.fromtimestamp(os.path.getmtime(item_path)).isoformat()
                })
            
            return jsonify({
                'files': files,
                'directory': directory,
                'count': len(files)
            })
            
        except Exception as e:
            self.logger.error(f"Ошибка получения списка файлов: {e}")
            return jsonify({'error': str(e)}), 500
    
    def create_file(self):
        """Создание файла"""
        try:
            data = request.get_json()
            filename = data.get('filename')
            content = data.get('content', '')
            
            if not filename:
                return jsonify({'error': 'Имя файла не указано'}), 400
            
            # Безопасный путь
            safe_dir = os.path.expanduser('~/daur_ai_files')
            os.makedirs(safe_dir, exist_ok=True)
            
            safe_filename = "".join(c for c in filename if c.isalnum() or c in "._-")
            file_path = os.path.join(safe_dir, safe_filename)
            
            with open(file_path, 'w', encoding='utf-8') as f:
                f.write(content)
            
            return jsonify({
                'message': f'Файл создан: {safe_filename}',
                'file_path': file_path,
                'size': len(content)
            })
            
        except Exception as e:
            self.logger.error(f"Ошибка создания файла: {e}")
            return jsonify({'error': str(e)}), 500
    
    def read_file(self):
        """Чтение файла"""
        try:
            filename = request.args.get('filename')
            if not filename:
                return jsonify({'error': 'Имя файла не указано'}), 400
            
            safe_dir = os.path.expanduser('~/daur_ai_files')
            file_path = os.path.join(safe_dir, filename)
            
            if not os.path.exists(file_path):
                return jsonify({'error': 'Файл не найден'}), 404
            
            with open(file_path, 'r', encoding='utf-8') as f:
                content = f.read()
            
            return jsonify({
                'filename': filename,
                'content': content,
                'size': len(content),
                'modified': datetime.fromtimestamp(os.path.getmtime(file_path)).isoformat()
            })
            
        except Exception as e:
            self.logger.error(f"Ошибка чтения файла: {e}")
            return jsonify({'error': str(e)}), 500
    
    def delete_file(self):
        """Удаление файла"""
        try:
            filename = request.args.get('filename')
            if not filename:
                return jsonify({'error': 'Имя файла не указано'}), 400
            
            safe_dir = os.path.expanduser('~/daur_ai_files')
            file_path = os.path.join(safe_dir, filename)
            
            if not os.path.exists(file_path):
                return jsonify({'error': 'Файл не найден'}), 404
            
            os.remove(file_path)
            
            return jsonify({'message': f'Файл удален: {filename}'})
            
        except Exception as e:
            self.logger.error(f"Ошибка удаления файла: {e}")
            return jsonify({'error': str(e)}), 500
    
    def list_processes(self):
        """Список процессов"""
        try:
            limit = request.args.get('limit', 20, type=int)
            limit = min(limit, 100)  # Ограничиваем максимум
            
            processes = []
            for proc in psutil.process_iter(['pid', 'name', 'cpu_percent', 'memory_percent']):
                try:
                    processes.append({
                        'pid': proc.info['pid'],
                        'name': proc.info['name'],
                        'cpu_percent': round(proc.info['cpu_percent'] or 0, 1),
                        'memory_percent': round(proc.info['memory_percent'] or 0, 1)
                    })
                except (psutil.NoSuchProcess, psutil.AccessDenied):
                    pass
            
            # Сортируем по использованию CPU
            processes.sort(key=lambda x: x['cpu_percent'], reverse=True)
            
            return jsonify({
                'processes': processes[:limit],
                'total_count': len(processes),
                'limit': limit
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
            
            # В API режиме не запускаем реальные приложения
            return jsonify({
                'message': f'[API MODE] Запуск приложения заблокирован: {app_name}',
                'app_name': app_name,
                'blocked': True
            })
            
        except Exception as e:
            self.logger.error(f"Ошибка запуска приложения: {e}")
            return jsonify({'error': str(e)}), 500
    
    def get_recent_logs(self):
        """Получение последних логов"""
        try:
            limit = request.args.get('limit', 100, type=int)
            limit = min(limit, 1000)  # Ограничиваем максимум
            
            # Заглушка для логов (в реальной системе читали бы из файла логов)
            logs = [
                {
                    'timestamp': datetime.now().isoformat(),
                    'level': 'INFO',
                    'message': 'API сервер работает',
                    'component': 'enhanced_api_server'
                }
            ]
            
            return jsonify({
                'logs': logs,
                'count': len(logs),
                'limit': limit
            })
            
        except Exception as e:
            self.logger.error(f"Ошибка получения логов: {e}")
            return jsonify({'error': str(e)}), 500
    
    def _command_worker(self):
        """Worker поток для обработки команд"""
        self.logger.info("Запущен worker поток для команд")
        
        while True:
            try:
                if not self.agent_status['running']:
                    time.sleep(1)
                    continue
                
                # Здесь можно добавить обработку команд из очереди
                # Пока просто ждем
                time.sleep(0.1)
                
            except Exception as e:
                self.logger.error(f"Ошибка в worker потоке: {e}")
                time.sleep(1)
    
    def run(self, host='0.0.0.0', port=8000, debug=False):
        """Запуск веб сервера"""
        self.logger.info(f"Запуск улучшенного API сервера на {host}:{port}")
        self.app.run(host=host, port=port, debug=debug, threaded=True)


def main():
    """Главная функция запуска API сервера"""
    
    # Настройка логирования
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s [%(levelname)s] %(name)s: %(message)s'
    )
    
    try:
        # Загрузка конфигурации
        config = load_config()
        
        # Создание и запуск API
        api = EnhancedDaurWebAPI(config)
        
        # Запуск сервера
        port = int(os.environ.get('PORT', 8000))
        api.run(host='0.0.0.0', port=port, debug=False)
        
    except KeyboardInterrupt:
        print("\nОстановка сервера...")
    except Exception as e:
        print(f"Ошибка запуска сервера: {e}")
        sys.exit(1)


if __name__ == '__main__':
    main()
