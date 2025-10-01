#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
Daur-AI: Flask API сервер для веб-панели
Предоставляет REST API для управления агентом через веб-интерфейс

Версия: 1.1
Дата: 01.10.2025
"""

import logging
import json
import time
import threading
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
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from src.agent.core import DaurAgent
from src.config.settings import load_config


class DaurWebAPI:
    """
    Веб API для управления Daur-AI агентом
    """
    
    def __init__(self, config: Dict[str, Any]):
        """
        Инициализация веб API
        
        Args:
            config (Dict): Конфигурация системы
        """
        self.logger = logging.getLogger('daur_ai.web_api')
        self.config = config
        
        # Flask приложение
        self.app = Flask(__name__)
        CORS(self.app)  # Разрешаем CORS для веб-панели
        
        # Состояние агента
        self.agent = None
        self.agent_status = 'stopped'  # stopped, starting, running, stopping, error
        self.agent_thread = None
        
        # История команд и логов
        self.command_history = []
        self.system_logs = []
        self.max_history = 100
        self.max_logs = 500
        
        # Статистика системы
        self.system_stats = {
            'cpu_percent': 0,
            'memory_percent': 0,
            'disk_percent': 0,
            'process_count': 0,
            'last_update': None
        }
        
        # Информация об ИИ моделях
        self.ai_info = {
            'active_model': 'simple',
            'available_models': ['simple'],
            'model_status': 'ready'
        }
        
        # Настройка маршрутов
        self._setup_routes()
        
        # Запуск фонового обновления статистики
        self._start_stats_updater()
        
        self.logger.info("Веб API инициализирован")
    
    def _setup_routes(self):
        """Настройка маршрутов Flask"""
        
        @self.app.route('/api/status', methods=['GET'])
        def get_status():
            """Получение общего статуса системы"""
            return jsonify({
                'agent_status': self.agent_status,
                'system_stats': self.system_stats,
                'ai_info': self.ai_info,
                'timestamp': datetime.now().isoformat()
            })
        
        @self.app.route('/api/agent/start', methods=['POST'])
        def start_agent():
            """Запуск агента"""
            try:
                if self.agent_status in ['running', 'starting']:
                    return jsonify({'error': 'Агент уже запущен или запускается'}), 400
                
                self.agent_status = 'starting'
                self._add_log('info', 'Запуск Daur-AI агента...')
                
                # Запускаем агента в отдельном потоке
                self.agent_thread = threading.Thread(target=self._start_agent_thread)
                self.agent_thread.daemon = True
                self.agent_thread.start()
                
                return jsonify({'message': 'Агент запускается', 'status': self.agent_status})
                
            except Exception as e:
                self.logger.error(f"Ошибка запуска агента: {e}")
                self.agent_status = 'error'
                self._add_log('error', f'Ошибка запуска агента: {str(e)}')
                return jsonify({'error': str(e)}), 500
        
        @self.app.route('/api/agent/stop', methods=['POST'])
        def stop_agent():
            """Остановка агента"""
            try:
                if self.agent_status in ['stopped', 'stopping']:
                    return jsonify({'error': 'Агент уже остановлен или останавливается'}), 400
                
                self.agent_status = 'stopping'
                self._add_log('info', 'Остановка Daur-AI агента...')
                
                if self.agent:
                    self.agent.cleanup()
                    self.agent = None
                
                self.agent_status = 'stopped'
                self._add_log('success', 'Daur-AI агент остановлен')
                
                return jsonify({'message': 'Агент остановлен', 'status': self.agent_status})
                
            except Exception as e:
                self.logger.error(f"Ошибка остановки агента: {e}")
                self.agent_status = 'error'
                self._add_log('error', f'Ошибка остановки агента: {str(e)}')
                return jsonify({'error': str(e)}), 500
        
        @self.app.route('/api/commands/execute', methods=['POST'])
        def execute_command():
            """Выполнение команды"""
            try:
                data = request.get_json()
                command_text = data.get('command', '').strip()
                
                if not command_text:
                    return jsonify({'error': 'Команда не может быть пустой'}), 400
                
                if self.agent_status != 'running':
                    return jsonify({'error': 'Агент не запущен'}), 400
                
                # Создаем запись команды
                command_record = {
                    'id': int(time.time() * 1000),
                    'text': command_text,
                    'timestamp': datetime.now().isoformat(),
                    'status': 'executing',
                    'result': None
                }
                
                self.command_history.insert(0, command_record)
                if len(self.command_history) > self.max_history:
                    self.command_history = self.command_history[:self.max_history]
                
                self._add_log('info', f'Выполнение команды: {command_text}')
                
                # Выполняем команду через агента
                try:
                    if self.agent:
                        result = self.agent.handle_command(command_text)
                        command_record['status'] = 'completed'
                        command_record['result'] = result
                        self._add_log('success', f'Команда выполнена: {command_text}')
                    else:
                        command_record['status'] = 'error'
                        command_record['result'] = 'Агент недоступен'
                        self._add_log('error', 'Попытка выполнения команды при недоступном агенте')
                        
                except Exception as e:
                    command_record['status'] = 'error'
                    command_record['result'] = str(e)
                    self._add_log('error', f'Ошибка выполнения команды: {str(e)}')
                
                return jsonify({
                    'message': 'Команда принята к выполнению',
                    'command_id': command_record['id'],
                    'status': command_record['status'],
                    'result': command_record['result']
                })
                
            except Exception as e:
                self.logger.error(f"Ошибка выполнения команды: {e}")
                self._add_log('error', f'Ошибка API выполнения команды: {str(e)}')
                return jsonify({'error': str(e)}), 500
        
        @self.app.route('/api/commands/history', methods=['GET'])
        def get_command_history():
            """Получение истории команд"""
            limit = request.args.get('limit', 50, type=int)
            return jsonify({
                'commands': self.command_history[:limit],
                'total': len(self.command_history)
            })
        
        @self.app.route('/api/commands/history', methods=['DELETE'])
        def clear_command_history():
            """Очистка истории команд"""
            self.command_history.clear()
            self._add_log('info', 'История команд очищена')
            return jsonify({'message': 'История команд очищена'})
        
        @self.app.route('/api/logs', methods=['GET'])
        def get_logs():
            """Получение системных логов"""
            limit = request.args.get('limit', 100, type=int)
            return jsonify({
                'logs': self.system_logs[:limit],
                'total': len(self.system_logs)
            })
        
        @self.app.route('/api/logs', methods=['DELETE'])
        def clear_logs():
            """Очистка логов"""
            self.system_logs.clear()
            self._add_log('info', 'Логи очищены')
            return jsonify({'message': 'Логи очищены'})
        
        @self.app.route('/api/ai/models', methods=['GET'])
        def get_ai_models():
            """Получение информации об ИИ моделях"""
            return jsonify(self.ai_info)
        
        @self.app.route('/api/ai/models/switch', methods=['POST'])
        def switch_ai_model():
            """Переключение ИИ модели"""
            try:
                data = request.get_json()
                model_name = data.get('model', '').strip()
                
                if not model_name:
                    return jsonify({'error': 'Имя модели не указано'}), 400
                
                if model_name not in self.ai_info['available_models']:
                    return jsonify({'error': 'Модель не найдена'}), 404
                
                # Здесь можно добавить логику переключения модели в агенте
                self.ai_info['active_model'] = model_name
                self._add_log('success', f'Переключение на модель: {model_name}')
                
                return jsonify({
                    'message': f'Переключено на модель {model_name}',
                    'active_model': model_name
                })
                
            except Exception as e:
                self.logger.error(f"Ошибка переключения модели: {e}")
                return jsonify({'error': str(e)}), 500
        
        @self.app.route('/api/system/stats', methods=['GET'])
        def get_system_stats():
            """Получение статистики системы"""
            self._update_system_stats()
            return jsonify(self.system_stats)
        
        @self.app.route('/health', methods=['GET'])
        def health_check():
            """Проверка здоровья API"""
            return jsonify({
                'status': 'healthy',
                'timestamp': datetime.now().isoformat(),
                'version': '1.1'
            })
    
    def _start_agent_thread(self):
        """Запуск агента в отдельном потоке"""
        try:
            self.agent = DaurAgent(self.config, ui_mode="api", sandbox=True)
            
            # Обновляем информацию об ИИ моделях
            if hasattr(self.agent, 'ai_manager'):
                self.ai_info['available_models'] = ['simple', 'ollama', 'openai']
                self.ai_info['active_model'] = 'enhanced'
            
            self.agent_status = 'running'
            self._add_log('success', 'Daur-AI агент успешно запущен')
            
        except Exception as e:
            self.logger.error(f"Ошибка в потоке агента: {e}")
            self.agent_status = 'error'
            self._add_log('error', f'Ошибка запуска агента: {str(e)}')
    
    def _add_log(self, log_type: str, message: str):
        """Добавление записи в лог"""
        log_entry = {
            'id': int(time.time() * 1000),
            'type': log_type,  # info, success, warning, error
            'message': message,
            'timestamp': datetime.now().isoformat()
        }
        
        self.system_logs.insert(0, log_entry)
        if len(self.system_logs) > self.max_logs:
            self.system_logs = self.system_logs[:self.max_logs]
        
        # Также логируем в стандартный логгер
        if log_type == 'error':
            self.logger.error(message)
        elif log_type == 'warning':
            self.logger.warning(message)
        else:
            self.logger.info(message)
    
    def _update_system_stats(self):
        """Обновление статистики системы"""
        try:
            # CPU
            cpu_percent = psutil.cpu_percent(interval=0.1)
            
            # Память
            memory = psutil.virtual_memory()
            memory_percent = memory.percent
            
            # Диск
            disk = psutil.disk_usage('/')
            disk_percent = (disk.used / disk.total) * 100
            
            # Процессы
            process_count = len(psutil.pids())
            
            self.system_stats = {
                'cpu_percent': round(cpu_percent, 1),
                'memory_percent': round(memory_percent, 1),
                'disk_percent': round(disk_percent, 1),
                'process_count': process_count,
                'last_update': datetime.now().isoformat()
            }
            
        except Exception as e:
            self.logger.error(f"Ошибка обновления статистики: {e}")
    
    def _start_stats_updater(self):
        """Запуск фонового обновления статистики"""
        def update_stats():
            while True:
                try:
                    self._update_system_stats()
                    time.sleep(5)  # Обновляем каждые 5 секунд
                except Exception as e:
                    self.logger.error(f"Ошибка в обновлении статистики: {e}")
                    time.sleep(10)
        
        stats_thread = threading.Thread(target=update_stats)
        stats_thread.daemon = True
        stats_thread.start()
    
    def run(self, host: str = '0.0.0.0', port: int = 8000, debug: bool = False):
        """
        Запуск веб сервера
        
        Args:
            host (str): Хост для привязки
            port (int): Порт для привязки
            debug (bool): Режим отладки
        """
        self.logger.info(f"Запуск веб API сервера на {host}:{port}")
        self._add_log('info', f'Веб API сервер запущен на {host}:{port}')
        
        try:
            self.app.run(host=host, port=port, debug=debug, threaded=True)
        except Exception as e:
            self.logger.error(f"Ошибка запуска веб сервера: {e}")
            self._add_log('error', f'Ошибка запуска веб сервера: {str(e)}')
    
    def cleanup(self):
        """Очистка ресурсов"""
        self.logger.info("Очистка веб API")
        if self.agent:
            self.agent.cleanup()


def main():
    """Основная функция для запуска веб API"""
    # Настройка логирования
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
    )
    
    try:
        # Загрузка конфигурации
        config = load_config()
        
        # Создание и запуск веб API
        web_api = DaurWebAPI(config)
        
        # Запуск сервера
        host = os.getenv('DAUR_API_HOST', '0.0.0.0')
        port = int(os.getenv('DAUR_API_PORT', '8000'))
        debug = os.getenv('DAUR_API_DEBUG', 'false').lower() == 'true'
        
        print(f"🚀 Запуск Daur-AI Web API")
        print(f"📡 Сервер: http://{host}:{port}")
        print(f"🔧 Отладка: {'включена' if debug else 'отключена'}")
        print(f"📊 Панель управления: http://localhost:3000 (после запуска React)")
        print(f"🏥 Проверка здоровья: http://{host}:{port}/health")
        print()
        
        web_api.run(host=host, port=port, debug=debug)
        
    except KeyboardInterrupt:
        print("\n🛑 Остановка сервера...")
    except Exception as e:
        print(f"❌ Критическая ошибка: {e}")
        import traceback
        traceback.print_exc()
    finally:
        if 'web_api' in locals():
            web_api.cleanup()


if __name__ == "__main__":
    main()
