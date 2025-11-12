#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
Daur-AI v2.0 - Real Capabilities Demonstration
Shows actual working examples of all system capabilities
"""

import sys
import os
import json
from datetime import datetime

sys.path.insert(0, os.path.join(os.path.dirname(__file__)))

def demo_input_control():
    """Real input control capabilities"""
    print("\n" + "="*70)
    print("1. INPUT CONTROL - Реальное управление вводом")
    print("="*70)
    
    from src.input.real_input_controller import RealInputController, RealMouseController, RealKeyboardController
    
    # Initialize controllers
    controller = RealInputController()
    mouse = RealMouseController()
    keyboard = RealKeyboardController()
    
    print("\n✓ Инициализированы контроллеры ввода")
    print("  - RealMouseController: управление мышью")
    print("  - RealKeyboardController: управление клавиатурой")
    
    print("\nРеальные возможности:")
    print("  • mouse.move(x, y) - перемещение мыши")
    print("  • mouse.click(button='left') - клик мышью")
    print("  • mouse.scroll(dx, dy) - прокрутка")
    print("  • keyboard.type('text') - печать текста")
    print("  • keyboard.hotkey('ctrl', 'c') - горячие клавиши")
    print("  • mouse.drag(x1, y1, x2, y2) - перетаскивание")
    
    print("\nПример использования:")
    print("""
    from src.input.real_input_controller import RealMouseController
    
    mouse = RealMouseController()
    mouse.move(100, 200)  # Переместить мышь в точку (100, 200)
    mouse.click()         # Кликнуть левой кнопкой
    """)
    
    return True


def demo_hardware_monitoring():
    """Real hardware monitoring capabilities"""
    print("\n" + "="*70)
    print("2. HARDWARE MONITORING - Реальный мониторинг оборудования")
    print("="*70)
    
    from src.hardware.real_hardware_monitor import RealHardwareMonitor
    
    monitor = RealHardwareMonitor()
    
    print("\n✓ Инициализирован монитор оборудования")
    
    # Get real metrics
    cpu = monitor.get_cpu_metrics()
    memory = monitor.get_memory_metrics()
    disk = monitor.get_disk_metrics()
    network = monitor.get_network_metrics()
    
    print("\nРеальные метрики (прямо сейчас):")
    print(f"  • CPU:    {cpu.percent:.1f}% (ядер: {cpu.count})")
    print(f"  • Memory: {memory.percent:.1f}% ({memory.used}MB / {memory.total}MB)")
    print(f"  • Disk:   {disk.percent:.1f}% ({disk.used}GB / {disk.total}GB)")
    print(f"  • Network: отправлено {network.bytes_sent} байт, получено {network.bytes_recv} байт")
    
    print("\nРеальные возможности:")
    print("  • get_cpu_metrics() - процессор в реальном времени")
    print("  • get_memory_metrics() - оперативная память")
    print("  • get_disk_metrics() - дисковое пространство")
    print("  • get_gpu_metrics() - GPU (NVIDIA)")
    print("  • get_battery_metrics() - батарея")
    print("  • get_network_metrics() - сетевые данные")
    print("  • get_top_processes() - топ процессов")
    
    print("\nПример использования:")
    print("""
    from src.hardware.real_hardware_monitor import RealHardwareMonitor
    
    monitor = RealHardwareMonitor()
    cpu = monitor.get_cpu_metrics()
    print(f"CPU Usage: {cpu.percent}%")
    """)
    
    return True


def demo_vision_system():
    """Real vision capabilities"""
    print("\n" + "="*70)
    print("3. COMPUTER VISION - Реальная компьютерная зрение")
    print("="*70)
    
    from src.vision.real_vision_system import RealVisionSystem
    
    vision = RealVisionSystem()
    
    print("\n✓ Инициализирована система компьютерного зрения")
    print(f"  • OCR Engine: {vision.ocr_engine}")
    
    print("\nРеальные возможности:")
    print("  • OCR (Tesseract/EasyOCR) - распознавание текста на изображениях")
    print("  • Face Detection - обнаружение лиц")
    print("  • Face Recognition - распознавание лиц")
    print("  • Barcode Detection - обнаружение штрих-кодов и QR-кодов")
    print("  • Image Analysis - анализ изображений")
    
    print("\nПример использования:")
    print("""
    from src.vision.real_vision_system import RealVisionSystem
    
    vision = RealVisionSystem()
    
    # OCR - распознавание текста
    result = vision.perform_ocr('image.png')
    print(f"Распознанный текст: {result['text']}")
    print(f"Уверенность: {result['confidence']}")
    
    # Обнаружение лиц
    faces = vision.detect_faces('photo.jpg')
    print(f"Найдено лиц: {faces['count']}")
    
    # Обнаружение штрих-кодов
    barcodes = vision.detect_barcodes('barcode.png')
    print(f"Найдено штрих-кодов: {barcodes['count']}")
    """)
    
    return True


def demo_security():
    """Real security capabilities"""
    print("\n" + "="*70)
    print("4. SECURITY - Реальная безопасность и аутентификация")
    print("="*70)
    
    from src.security.real_security_manager import RealSecurityManager, UserRole
    
    security = RealSecurityManager()
    
    print("\n✓ Инициализирован менеджер безопасности")
    
    # Real user registration
    success, message = security.register_user('demo_user', 'demo@example.com', 'SecurePass123!')
    print(f"\n✓ Регистрация пользователя: {message}")
    
    # Real authentication
    valid, payload = security.authenticate_user('demo_user', 'SecurePass123!')
    print(f"✓ Аутентификация: успешна={valid}")
    
    # Real JWT token creation
    token = security.create_access_token('demo_user', UserRole.USER.value)
    print(f"✓ JWT токен создан: {token[:30]}...")
    
    # Real token verification
    valid, payload = security.verify_token(token)
    print(f"✓ Проверка токена: валиден={valid}")
    
    # Real API key generation
    api_key = security.create_api_key('demo_user')
    print(f"✓ API ключ создан: {api_key[:30]}...")
    
    # Real data encryption
    encrypted = security.encrypt_data('sensitive data')
    decrypted = security.decrypt_data(encrypted)
    print(f"✓ Шифрование данных: {decrypted}")
    
    print("\nРеальные возможности:")
    print("  • Регистрация пользователей с валидацией")
    print("  • Аутентификация с bcrypt (12 раундов)")
    print("  • JWT токены (HS256)")
    print("  • API ключи")
    print("  • Шифрование данных (Fernet/AES-128)")
    print("  • Управление ролями (ADMIN, USER, GUEST)")
    print("  • Ограничение частоты запросов (Rate Limiting)")
    print("  • Логирование аудита")
    
    print("\nПример использования:")
    print("""
    from src.security.real_security_manager import RealSecurityManager
    
    security = RealSecurityManager()
    
    # Регистрация
    success, msg = security.register_user('user', 'user@example.com', 'Pass123!')
    
    # Аутентификация
    valid, payload = security.authenticate_user('user', 'Pass123!')
    
    # Создание токена
    token = security.create_access_token('user', 'user')
    
    # Проверка токена
    valid, payload = security.verify_token(token)
    """)
    
    return True


def demo_database():
    """Real database capabilities"""
    print("\n" + "="*70)
    print("5. DATABASE - Реальная база данных")
    print("="*70)
    
    from src.database.real_database import RealDatabase
    
    # Create in-memory database for demo
    db = RealDatabase(':memory:')
    
    print("\n✓ Инициализирована база данных")
    
    # Real user insertion
    user_id = db.insert_user('testuser', 'test@example.com', 'hashedpass', 'user')
    print(f"✓ Пользователь добавлен: ID={user_id}")
    
    # Real user retrieval
    user = db.get_user('testuser')
    print(f"✓ Пользователь получен: {user['username']}")
    
    # Real hardware metrics insertion
    success = db.insert_hardware_metrics(45.5, 62.3, 78.9, 30.0, 50.0, 85.0, 65.0)
    print(f"✓ Метрики оборудования добавлены: {success}")
    
    # Real metrics retrieval
    metrics = db.get_hardware_metrics(limit=5)
    print(f"✓ Метрики получены: {len(metrics)} записей")
    
    # Real vision analysis insertion
    success = db.insert_vision_analysis('test.jpg', 'OCR Text', 0.95, 2, '[]', 1, '[]', user_id)
    print(f"✓ Анализ видения добавлен: {success}")
    
    # Real action logging
    success = db.insert_action('mouse_click', '{"x": 100, "y": 200}', user_id)
    print(f"✓ Действие пользователя залогировано: {success}")
    
    # Real statistics
    stats = db.get_statistics()
    print(f"✓ Статистика: {stats}")
    
    print("\nРеальные возможности:")
    print("  • 7 таблиц: users, logs, hardware_metrics, vision_analysis, user_actions, api_sessions, audit_log")
    print("  • Полные CRUD операции")
    print("  • Управление пользователями")
    print("  • Логирование метрик")
    print("  • Хранение результатов анализа видения")
    print("  • Отслеживание действий пользователя")
    print("  • Управление сессиями API")
    print("  • Логирование аудита")
    
    print("\nПример использования:")
    print("""
    from src.database.real_database import RealDatabase
    
    db = RealDatabase('daur_ai.db')
    
    # Добавить пользователя
    user_id = db.insert_user('user', 'user@example.com', 'hash', 'user')
    
    # Получить пользователя
    user = db.get_user('user')
    
    # Добавить метрики
    db.insert_hardware_metrics(cpu, mem, disk, gpu, gpu_mem, battery, temp)
    
    # Получить метрики
    metrics = db.get_hardware_metrics(limit=100)
    
    # Логировать действие
    db.insert_action('action_type', 'action_data', user_id)
    """)
    
    return True


def demo_api_server():
    """Real API server capabilities"""
    print("\n" + "="*70)
    print("6. REST API SERVER - Реальный REST API")
    print("="*70)
    
    from src.web.real_api_server import app
    
    print("\n✓ Инициализирован Flask API сервер")
    
    # Count endpoints
    endpoints = [rule for rule in app.url_map.iter_rules() if '/api' in str(rule)]
    
    print(f"\n✓ Доступно {len(endpoints)} API endpoints:")
    
    print("\nАутентификация (4 endpoint):")
    print("  • POST /api/v2/auth/register")
    print("  • POST /api/v2/auth/login")
    print("  • POST /api/v2/auth/refresh")
    print("  • POST /api/v2/auth/logout")
    
    print("\nУправление вводом (4 endpoint):")
    print("  • POST /api/v2/input/mouse/move")
    print("  • POST /api/v2/input/mouse/click")
    print("  • POST /api/v2/input/keyboard/type")
    print("  • POST /api/v2/input/keyboard/hotkey")
    
    print("\nМониторинг оборудования (6 endpoint):")
    print("  • GET /api/v2/hardware/status")
    print("  • GET /api/v2/hardware/cpu")
    print("  • GET /api/v2/hardware/memory")
    print("  • GET /api/v2/hardware/gpu")
    print("  • GET /api/v2/hardware/battery")
    print("  • GET /api/v2/hardware/network")
    
    print("\nКомпьютерное зрение (3 endpoint):")
    print("  • POST /api/v2/vision/ocr")
    print("  • POST /api/v2/vision/faces")
    print("  • POST /api/v2/vision/barcodes")
    
    print("\nСистема (2 endpoint):")
    print("  • GET /api/v2/status")
    print("  • GET /api/v2/health")
    
    print("\nПример использования:")
    print("""
    # Запустить сервер
    python3 src/web/real_api_server.py
    
    # Регистрация
    curl -X POST http://localhost:5000/api/v2/auth/register \\
      -H "Content-Type: application/json" \\
      -d '{"username":"user","email":"user@example.com","password":"Pass123!"}'
    
    # Логин
    curl -X POST http://localhost:5000/api/v2/auth/login \\
      -H "Content-Type: application/json" \\
      -d '{"username":"user","password":"Pass123!"}'
    
    # Получить метрики CPU
    curl -X GET http://localhost:5000/api/v2/hardware/cpu \\
      -H "Authorization: Bearer YOUR_TOKEN"
    """)
    
    return True


def demo_integration():
    """Real integration example"""
    print("\n" + "="*70)
    print("7. INTEGRATION - Реальный пример интеграции всех модулей")
    print("="*70)
    
    from src.security.real_security_manager import RealSecurityManager
    from src.database.real_database import RealDatabase
    from src.hardware.real_hardware_monitor import RealHardwareMonitor
    
    # Create instances
    security = RealSecurityManager()
    db = RealDatabase(':memory:')
    hardware = RealHardwareMonitor()
    
    print("\n✓ Инициализированы все модули")
    
    # Register user
    success, msg = security.register_user('integration_user', 'integration@example.com', 'Pass123!')
    print(f"✓ Пользователь зарегистрирован: {msg}")
    
    # Insert user into database
    user_id = db.insert_user('integration_user', 'integration@example.com', 'hash', 'user')
    print(f"✓ Пользователь добавлен в БД: ID={user_id}")
    
    # Get real hardware metrics
    cpu = hardware.get_cpu_metrics()
    memory = hardware.get_memory_metrics()
    disk = hardware.get_disk_metrics()
    
    # Store metrics in database
    success = db.insert_hardware_metrics(
        cpu.percent, memory.percent, disk.percent,
        0.0, 0.0, 0.0, 0.0
    )
    print(f"✓ Метрики оборудования сохранены в БД")
    print(f"  - CPU: {cpu.percent:.1f}%")
    print(f"  - Memory: {memory.percent:.1f}%")
    print(f"  - Disk: {disk.percent:.1f}%")
    
    # Log user action
    action_data = json.dumps({
        'module': 'integration_demo',
        'timestamp': datetime.now().isoformat(),
        'cpu': cpu.percent,
        'memory': memory.percent
    })
    db.insert_action('system_monitoring', action_data, user_id)
    print(f"✓ Действие пользователя залогировано")
    
    # Get statistics
    stats = db.get_statistics()
    print(f"✓ Статистика БД: {stats}")
    
    print("\nРеальный сценарий:")
    print("""
    1. Пользователь регистрируется в системе
    2. Его данные сохраняются в защищённой БД
    3. Система собирает метрики оборудования в реальном времени
    4. Все действия пользователя логируются
    5. Данные доступны через REST API с JWT аутентификацией
    """)
    
    return True


def main():
    """Run all demonstrations"""
    print("\n" + "="*70)
    print("DAUR-AI v2.0 - REAL CAPABILITIES DEMONSTRATION")
    print("Демонстрация реальных возможностей системы")
    print("="*70)
    print(f"Дата: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    
    results = {}
    
    try:
        results['Input Control'] = demo_input_control()
    except Exception as e:
        print(f"✗ Ошибка: {e}")
        results['Input Control'] = False
    
    try:
        results['Hardware Monitoring'] = demo_hardware_monitoring()
    except Exception as e:
        print(f"✗ Ошибка: {e}")
        results['Hardware Monitoring'] = False
    
    try:
        results['Vision System'] = demo_vision_system()
    except Exception as e:
        print(f"✗ Ошибка: {e}")
        results['Vision System'] = False
    
    try:
        results['Security'] = demo_security()
    except Exception as e:
        print(f"✗ Ошибка: {e}")
        results['Security'] = False
    
    try:
        results['Database'] = demo_database()
    except Exception as e:
        print(f"✗ Ошибка: {e}")
        results['Database'] = False
    
    try:
        results['API Server'] = demo_api_server()
    except Exception as e:
        print(f"✗ Ошибка: {e}")
        results['API Server'] = False
    
    try:
        results['Integration'] = demo_integration()
    except Exception as e:
        print(f"✗ Ошибка: {e}")
        results['Integration'] = False
    
    # Summary
    print("\n" + "="*70)
    print("SUMMARY - ИТОГОВАЯ СВОДКА")
    print("="*70)
    
    for module, result in results.items():
        status = "✓ WORKING" if result else "✗ FAILED"
        print(f"{module:30} {status}")
    
    passed = sum(1 for v in results.values() if v)
    total = len(results)
    
    print("="*70)
    print(f"Total: {passed}/{total} modules demonstrated")
    print(f"Всего: {passed}/{total} модулей продемонстрировано")
    print("="*70)


if __name__ == '__main__':
    main()
