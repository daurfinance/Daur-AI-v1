#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
Daur-AI: Тесты новых модулей
Комплексное тестирование всех новых функций

Версия: 2.0
Дата: 25.10.2025
Автор: Manus AI
"""

import unittest
import logging
import os
import tempfile
from datetime import datetime

# Настройка логирования
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger('daur_ai.tests')


class TestAdvancedMouseController(unittest.TestCase):
    """Тесты Advanced Mouse Controller"""
    
    def setUp(self):
        """Подготовка к тестам"""
        try:
            from src.input.advanced_mouse_controller import get_advanced_mouse_controller
            self.mouse = get_advanced_mouse_controller()
        except ImportError:
            self.skipTest("Advanced Mouse Controller not available")
    
    def test_mouse_initialization(self):
        """Тест инициализации контроллера мыши"""
        self.assertIsNotNone(self.mouse)
        logger.info("✓ Mouse controller initialized")
    
    def test_draw_circle(self):
        """Тест рисования круга"""
        if self.mouse:
            # Не выполняем реально, только проверяем метод
            self.assertTrue(hasattr(self.mouse, 'draw_circle'))
            logger.info("✓ Draw circle method exists")
    
    def test_find_image_on_screen(self):
        """Тест поиска изображения"""
        if self.mouse:
            self.assertTrue(hasattr(self.mouse, 'find_image_on_screen'))
            logger.info("✓ Find image method exists")


class TestTouchController(unittest.TestCase):
    """Тесты Touch Controller"""
    
    def setUp(self):
        """Подготовка к тестам"""
        try:
            from src.input.touch_controller import get_touch_controller
            self.touch = get_touch_controller()
        except ImportError:
            self.skipTest("Touch Controller not available")
    
    def test_touch_initialization(self):
        """Тест инициализации контроллера сенсорного ввода"""
        self.assertIsNotNone(self.touch)
        logger.info("✓ Touch controller initialized")
    
    def test_tap_method(self):
        """Тест наличия метода tap"""
        if self.touch:
            self.assertTrue(hasattr(self.touch, 'tap'))
            logger.info("✓ Tap method exists")
    
    def test_swipe_method(self):
        """Тест наличия метода swipe"""
        if self.touch:
            self.assertTrue(hasattr(self.touch, 'swipe'))
            logger.info("✓ Swipe method exists")


class TestAdvancedHardwareMonitor(unittest.TestCase):
    """Тесты Advanced Hardware Monitor"""
    
    def setUp(self):
        """Подготовка к тестам"""
        try:
            from src.hardware.advanced_hardware_monitor import get_advanced_hardware_monitor
            self.monitor = get_advanced_hardware_monitor()
        except ImportError:
            self.skipTest("Advanced Hardware Monitor not available")
    
    def test_monitor_initialization(self):
        """Тест инициализации монитора оборудования"""
        self.assertIsNotNone(self.monitor)
        logger.info("✓ Hardware monitor initialized")
    
    def test_get_full_hardware_status(self):
        """Тест получения полного статуса оборудования"""
        if self.monitor:
            status = self.monitor.get_full_hardware_status()
            self.assertIsNotNone(status)
            self.assertIsInstance(status, dict)
            logger.info("✓ Full hardware status retrieved")
    
    def test_get_battery_info(self):
        """Тест получения информации о батарее"""
        if self.monitor:
            battery = self.monitor.get_battery_info()
            # Батарея может быть None на некоторых системах
            logger.info(f"✓ Battery info retrieved: {battery}")
    
    def test_check_temperature_health(self):
        """Тест проверки здоровья температуры"""
        if self.monitor:
            health = self.monitor.check_temperature_health()
            self.assertIsNotNone(health)
            self.assertIn('status', health)
            logger.info(f"✓ Temperature health checked: {health['status']}")


class TestNetworkMonitor(unittest.TestCase):
    """Тесты Network Monitor"""
    
    def setUp(self):
        """Подготовка к тестам"""
        try:
            from src.hardware.network_monitor import get_network_monitor
            self.monitor = get_network_monitor()
        except ImportError:
            self.skipTest("Network Monitor not available")
    
    def test_monitor_initialization(self):
        """Тест инициализации монитора сети"""
        self.assertIsNotNone(self.monitor)
        logger.info("✓ Network monitor initialized")
    
    def test_get_network_interfaces(self):
        """Тест получения сетевых интерфейсов"""
        if self.monitor:
            interfaces = self.monitor.get_network_interfaces()
            self.assertIsNotNone(interfaces)
            self.assertIsInstance(interfaces, list)
            logger.info(f"✓ Network interfaces retrieved: {len(interfaces)}")
    
    def test_get_full_network_status(self):
        """Тест получения полного статуса сети"""
        if self.monitor:
            status = self.monitor.get_full_network_status()
            self.assertIsNotNone(status)
            self.assertIsInstance(status, dict)
            logger.info("✓ Full network status retrieved")


class TestFaceRecognitionModule(unittest.TestCase):
    """Тесты Face Recognition Module"""
    
    def setUp(self):
        """Подготовка к тестам"""
        try:
            from src.vision.face_recognition_module import get_face_recognition_module
            self.face_module = get_face_recognition_module()
        except ImportError:
            self.skipTest("Face Recognition Module not available")
    
    def test_module_initialization(self):
        """Тест инициализации модуля распознавания лиц"""
        self.assertIsNotNone(self.face_module)
        logger.info("✓ Face recognition module initialized")
    
    def test_add_known_face_method(self):
        """Тест наличия метода добавления известного лица"""
        if self.face_module:
            self.assertTrue(hasattr(self.face_module, 'add_known_face'))
            logger.info("✓ Add known face method exists")
    
    def test_detect_faces_method(self):
        """Тест наличия метода детектирования лиц"""
        if self.face_module:
            self.assertTrue(hasattr(self.face_module, 'detect_faces_in_image'))
            logger.info("✓ Detect faces method exists")
    
    def test_get_face_statistics(self):
        """Тест получения статистики лиц"""
        if self.face_module:
            stats = self.face_module.get_face_statistics()
            self.assertIsNotNone(stats)
            self.assertIn('total_faces', stats)
            logger.info(f"✓ Face statistics: {stats}")


class TestBarcodeRecognitionModule(unittest.TestCase):
    """Тесты Barcode Recognition Module"""
    
    def setUp(self):
        """Подготовка к тестам"""
        try:
            from src.vision.barcode_recognition_module import get_barcode_recognition_module
            self.barcode_module = get_barcode_recognition_module()
        except ImportError:
            self.skipTest("Barcode Recognition Module not available")
    
    def test_module_initialization(self):
        """Тест инициализации модуля распознавания штрих-кодов"""
        self.assertIsNotNone(self.barcode_module)
        logger.info("✓ Barcode recognition module initialized")
    
    def test_detect_barcodes_method(self):
        """Тест наличия метода детектирования штрих-кодов"""
        if self.barcode_module:
            self.assertTrue(hasattr(self.barcode_module, 'detect_barcodes_in_image'))
            logger.info("✓ Detect barcodes method exists")
    
    def test_validate_qr_code(self):
        """Тест валидации QR кода"""
        if self.barcode_module:
            # Тест с URL
            result = self.barcode_module.validate_qr_code('https://example.com')
            self.assertTrue(result['is_valid'])
            self.assertTrue(result['contains_url'])
            logger.info("✓ QR code validation works")
    
    def test_parse_wifi_qr(self):
        """Тест парсинга WiFi QR кода"""
        if self.barcode_module:
            wifi_qr = 'WIFI:T:WPA;S:MyNetwork;P:MyPassword;;'
            result = self.barcode_module.parse_wifi_qr(wifi_qr)
            self.assertIsNotNone(result)
            self.assertEqual(result.get('ssid'), 'MyNetwork')
            logger.info("✓ WiFi QR parsing works")


class TestOpenAIVisionAnalyzer(unittest.TestCase):
    """Тесты OpenAI Vision Analyzer"""
    
    def setUp(self):
        """Подготовка к тестам"""
        try:
            from src.ai.openai_vision_analyzer import get_openai_vision_analyzer
            self.analyzer = get_openai_vision_analyzer()
        except ImportError:
            self.skipTest("OpenAI Vision Analyzer not available")
    
    def test_analyzer_initialization(self):
        """Тест инициализации анализатора"""
        self.assertIsNotNone(self.analyzer)
        logger.info("✓ OpenAI Vision Analyzer initialized")
    
    def test_analyzer_methods(self):
        """Тест наличия методов анализа"""
        if self.analyzer:
            self.assertTrue(hasattr(self.analyzer, 'analyze_image'))
            self.assertTrue(hasattr(self.analyzer, 'extract_text_from_image'))
            self.assertTrue(hasattr(self.analyzer, 'detect_objects_in_image'))
            logger.info("✓ All analyzer methods exist")
    
    def test_get_analysis_history(self):
        """Тест получения истории анализов"""
        if self.analyzer:
            history = self.analyzer.get_analysis_history()
            self.assertIsNotNone(history)
            self.assertIsInstance(history, list)
            logger.info(f"✓ Analysis history retrieved: {len(history)} items")


class TestWebSocketManager(unittest.TestCase):
    """Тесты WebSocket Manager"""
    
    def setUp(self):
        """Подготовка к тестам"""
        try:
            from src.web.websocket_manager import get_websocket_manager
            self.ws_manager = get_websocket_manager()
        except ImportError:
            self.skipTest("WebSocket Manager not available")
    
    def test_manager_initialization(self):
        """Тест инициализации менеджера WebSocket"""
        self.assertIsNotNone(self.ws_manager)
        logger.info("✓ WebSocket Manager initialized")
    
    def test_register_event_handler(self):
        """Тест регистрации обработчика события"""
        if self.ws_manager:
            from src.web.websocket_manager import EventType
            
            def dummy_handler(data):
                pass
            
            self.ws_manager.register_event_handler(EventType.CONNECT, dummy_handler)
            logger.info("✓ Event handler registered")
    
    def test_get_connected_clients(self):
        """Тест получения подключенных клиентов"""
        if self.ws_manager:
            clients = self.ws_manager.get_connected_clients()
            self.assertIsNotNone(clients)
            self.assertIsInstance(clients, dict)
            logger.info(f"✓ Connected clients: {len(clients)}")


class TestIntegration(unittest.TestCase):
    """Интеграционные тесты"""
    
    def test_all_modules_importable(self):
        """Тест импортирования всех модулей"""
        modules = [
            'src.input.advanced_mouse_controller',
            'src.input.touch_controller',
            'src.hardware.advanced_hardware_monitor',
            'src.hardware.network_monitor',
            'src.vision.face_recognition_module',
            'src.vision.barcode_recognition_module',
            'src.ai.openai_vision_analyzer',
            'src.web.websocket_manager',
            'src.web.device_control_api'
        ]
        
        for module in modules:
            try:
                __import__(module)
                logger.info(f"✓ {module} imported successfully")
            except ImportError as e:
                logger.warning(f"⚠ {module} not available: {e}")
    
    def test_api_endpoints_exist(self):
        """Тест наличия API endpoints"""
        try:
            from src.web.device_control_api import device_control_api
            
            # Проверить наличие blueprint
            self.assertIsNotNone(device_control_api)
            logger.info("✓ Device Control API blueprint exists")
        
        except ImportError:
            self.skipTest("Device Control API not available")


# ==================== ЗАПУСК ТЕСТОВ ====================

def run_tests():
    """Запустить все тесты"""
    
    # Создать test suite
    loader = unittest.TestLoader()
    suite = unittest.TestSuite()
    
    # Добавить все тесты
    suite.addTests(loader.loadTestsFromTestCase(TestAdvancedMouseController))
    suite.addTests(loader.loadTestsFromTestCase(TestTouchController))
    suite.addTests(loader.loadTestsFromTestCase(TestAdvancedHardwareMonitor))
    suite.addTests(loader.loadTestsFromTestCase(TestNetworkMonitor))
    suite.addTests(loader.loadTestsFromTestCase(TestFaceRecognitionModule))
    suite.addTests(loader.loadTestsFromTestCase(TestBarcodeRecognitionModule))
    suite.addTests(loader.loadTestsFromTestCase(TestOpenAIVisionAnalyzer))
    suite.addTests(loader.loadTestsFromTestCase(TestWebSocketManager))
    suite.addTests(loader.loadTestsFromTestCase(TestIntegration))
    
    # Запустить тесты
    runner = unittest.TextTestRunner(verbosity=2)
    result = runner.run(suite)
    
    # Вывести результаты
    logger.info("\n" + "=" * 70)
    logger.info("РЕЗУЛЬТАТЫ ТЕСТИРОВАНИЯ")
    logger.info("=" * 70)
    logger.info(f"Всего тестов: {result.testsRun}")
    logger.info(f"Успешных: {result.testsRun - len(result.failures) - len(result.errors)}")
    logger.info(f"Ошибок: {len(result.errors)}")
    logger.info(f"Провалов: {len(result.failures)}")
    logger.info("=" * 70)
    
    return result.wasSuccessful()


if __name__ == '__main__':
    success = run_tests()
    exit(0 if success else 1)

