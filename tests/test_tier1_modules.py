"""
Test Suite for TIER 1 Modules
Comprehensive testing for Input Recorder, Messaging, Prometheus, Rate Limiter
"""

import sys
import os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import unittest
import json
import tempfile
from pathlib import Path

# Import modules
from src.input.input_recorder import InputRecorder, InputPlayer, MacroManager, ActionType, InputAction
from src.integrations.messaging_notifier import (
    SlackNotifier, DiscordNotifier, TelegramNotifier, MultiNotifier, Message, MessageType
)
from src.monitoring.prometheus_exporter import PrometheusMetrics, PrometheusExporter
from src.security.advanced_rate_limiter import AdvancedRateLimiter, DDoSDetector, SecurityMonitor


class TestInputRecorder(unittest.TestCase):
    """Тесты для Input Recorder"""
    
    def setUp(self):
        self.recorder = InputRecorder()
    
    def test_initialization(self):
        """Тест инициализации"""
        self.assertIsNotNone(self.recorder)
        self.assertFalse(self.recorder.is_recording)
        self.assertEqual(len(self.recorder.actions), 0)
    
    def test_add_pause(self):
        """Тест добавления паузы"""
        self.recorder.add_pause(2.0)
        self.assertEqual(len(self.recorder.actions), 1)
        self.assertEqual(self.recorder.actions[0].action_type, ActionType.PAUSE)
        self.assertEqual(self.recorder.actions[0].duration, 2.0)
    
    def test_get_statistics(self):
        """Тест получения статистики"""
        self.recorder.add_pause(1.0)
        self.recorder.add_pause(2.0)
        
        stats = self.recorder.get_statistics()
        self.assertEqual(stats['total_actions'], 2)
        self.assertIn('pause', stats['action_breakdown'])
    
    def test_save_and_load_recording(self):
        """Тест сохранения и загрузки записи"""
        self.recorder.add_pause(1.0)
        self.recorder.add_pause(2.0)
        
        with tempfile.NamedTemporaryFile(mode='w', suffix='.json', delete=False) as f:
            filename = f.name
        
        try:
            # Сохраняем
            self.assertTrue(self.recorder.save_recording(filename))
            
            # Загружаем в новый рекордер
            new_recorder = InputRecorder()
            self.assertTrue(new_recorder.load_recording(filename))
            
            # Проверяем
            self.assertEqual(len(new_recorder.actions), 2)
            self.assertEqual(new_recorder.actions[0].duration, 1.0)
            self.assertEqual(new_recorder.actions[1].duration, 2.0)
        
        finally:
            if os.path.exists(filename):
                os.unlink(filename)
    
    def test_clear_recording(self):
        """Тест очистки записи"""
        self.recorder.add_pause(1.0)
        self.assertEqual(len(self.recorder.actions), 1)
        
        self.recorder.clear_recording()
        self.assertEqual(len(self.recorder.actions), 0)


class TestInputPlayer(unittest.TestCase):
    """Тесты для Input Player"""
    
    def setUp(self):
        self.player = InputPlayer()
    
    def test_initialization(self):
        """Тест инициализации"""
        self.assertIsNotNone(self.player)
        self.assertFalse(self.player.is_playing)
    
    def test_play_empty_actions(self):
        """Тест воспроизведения пустого списка"""
        result = self.player.play([])
        self.assertFalse(result)
    
    def test_play_with_callback(self):
        """Тест воспроизведения с callback"""
        actions = [
            InputAction(ActionType.PAUSE, 0.0, duration=0.1),
            InputAction(ActionType.PAUSE, 0.1, duration=0.1)
        ]
        
        callback_count = [0]
        def callback(action, index, total):
            callback_count[0] += 1
        
        result = self.player.play(actions, on_action=callback)
        self.assertTrue(result)
        self.assertEqual(callback_count[0], 2)


class TestMacroManager(unittest.TestCase):
    """Тесты для Macro Manager"""
    
    def setUp(self):
        self.temp_dir = tempfile.mkdtemp()
        self.manager = MacroManager(self.temp_dir)
    
    def test_initialization(self):
        """Тест инициализации"""
        self.assertIsNotNone(self.manager)
        self.assertTrue(os.path.exists(self.temp_dir))
    
    def test_save_and_load_macro(self):
        """Тест сохранения и загрузки макроса"""
        # Создаем макрос вручную
        actions = [
            InputAction(ActionType.PAUSE, 0.0, duration=0.5),
            InputAction(ActionType.PAUSE, 0.5, duration=0.5)
        ]
        
        self.manager.macros['test_macro'] = actions
        self.assertTrue(self.manager.save_macro('test_macro'))
        
        # Загружаем
        self.manager.macros.clear()
        self.assertTrue(self.manager.load_macro('test_macro'))
        self.assertEqual(len(self.manager.macros['test_macro']), 2)
    
    def test_list_macros(self):
        """Тест списка макросов"""
        actions = [InputAction(ActionType.PAUSE, 0.0, duration=0.5)]
        
        self.manager.macros['macro1'] = actions
        self.manager.macros['macro2'] = actions
        
        self.manager.save_macro('macro1')
        self.manager.save_macro('macro2')
        
        macros = self.manager.list_macros()
        self.assertIn('macro1', macros)
        self.assertIn('macro2', macros)
    
    def test_delete_macro(self):
        """Тест удаления макроса"""
        actions = [InputAction(ActionType.PAUSE, 0.0, duration=0.5)]
        
        self.manager.macros['test'] = actions
        self.manager.save_macro('test')
        
        self.assertTrue(self.manager.delete_macro('test'))
        self.assertNotIn('test', self.manager.list_macros())


class TestMessaging(unittest.TestCase):
    """Тесты для Messaging Notifier"""
    
    def test_message_creation(self):
        """Тест создания сообщения"""
        msg = Message("Test", "Test message", MessageType.INFO)
        self.assertEqual(msg.title, "Test")
        self.assertEqual(msg.text, "Test message")
        self.assertEqual(msg.message_type, MessageType.INFO)
    
    def test_multi_notifier_initialization(self):
        """Тест инициализации MultiNotifier"""
        notifier = MultiNotifier()
        self.assertIsNotNone(notifier)
        self.assertEqual(len(notifier.notifiers), 0)


class TestPrometheusMetrics(unittest.TestCase):
    """Тесты для Prometheus Metrics"""
    
    def setUp(self):
        self.metrics = PrometheusMetrics()
    
    def test_initialization(self):
        """Тест инициализации"""
        self.assertIsNotNone(self.metrics)
        self.assertEqual(self.metrics.api_requests_total, 0)
    
    def test_record_api_request(self):
        """Тест записи API запроса"""
        self.metrics.record_api_request(0.5)
        self.assertEqual(self.metrics.api_requests_total, 1)
        self.assertEqual(self.metrics.api_request_duration_sum, 0.5)
    
    def test_format_metric(self):
        """Тест форматирования метрики"""
        metric = self.metrics._format_metric("test_metric", 42.0)
        self.assertIn("test_metric", metric)
        self.assertIn("42", metric)
    
    def test_get_all_metrics(self):
        """Тест получения всех метрик"""
        metrics_text = self.metrics.get_all_metrics()
        self.assertIn("DAUR-AI PROMETHEUS METRICS", metrics_text)
        self.assertIn("daur_cpu", metrics_text)
        self.assertIn("daur_memory", metrics_text)


class TestPrometheusExporter(unittest.TestCase):
    """Тесты для Prometheus Exporter"""
    
    def setUp(self):
        self.exporter = PrometheusExporter()
    
    def test_initialization(self):
        """Тест инициализации"""
        self.assertIsNotNone(self.exporter)
        self.assertIsNotNone(self.exporter.metrics)
    
    def test_export_to_file(self):
        """Тест экспорта в файл"""
        with tempfile.NamedTemporaryFile(mode='w', suffix='.txt', delete=False) as f:
            filename = f.name
        
        try:
            self.assertTrue(self.exporter.export_to_file(filename))
            self.assertTrue(os.path.exists(filename))
            
            with open(filename, 'r') as f:
                content = f.read()
                self.assertIn("DAUR-AI PROMETHEUS METRICS", content)
        
        finally:
            if os.path.exists(filename):
                os.unlink(filename)


class TestAdvancedRateLimiter(unittest.TestCase):
    """Тесты для Advanced Rate Limiter"""
    
    def setUp(self):
        self.limiter = AdvancedRateLimiter()
    
    def test_initialization(self):
        """Тест инициализации"""
        self.assertIsNotNone(self.limiter)
        self.assertGreater(len(self.limiter.rules), 0)
    
    def test_add_rule(self):
        """Тест добавления правила"""
        from src.security.advanced_rate_limiter import RateLimitRule
        
        rule = RateLimitRule("test", 10, 60)
        self.assertTrue(self.limiter.add_rule(rule))
        self.assertIn("test", self.limiter.rules)
    
    def test_block_and_unblock_ip(self):
        """Тест блокировки и разблокировки IP"""
        ip = "192.168.1.1"
        
        self.assertTrue(self.limiter.block_ip(ip))
        self.assertTrue(self.limiter.is_ip_blocked(ip))
        
        self.assertTrue(self.limiter.unblock_ip(ip))
        self.assertFalse(self.limiter.is_ip_blocked(ip))
    
    def test_whitelist_ip(self):
        """Тест добавления IP в белый список"""
        ip = "192.168.1.1"
        
        self.assertTrue(self.limiter.whitelist_ip(ip))
        self.assertIn(ip, self.limiter.whitelist_ips)
    
    def test_get_statistics(self):
        """Тест получения статистики"""
        stats = self.limiter.get_statistics()
        self.assertIn('total_ips_tracked', stats)
        self.assertIn('blocked_ips', stats)


class TestDDoSDetector(unittest.TestCase):
    """Тесты для DDoS Detector"""
    
    def setUp(self):
        self.detector = DDoSDetector(window_size=60, threshold=100)
    
    def test_initialization(self):
        """Тест инициализации"""
        self.assertIsNotNone(self.detector)
        self.assertFalse(self.detector.under_attack)
    
    def test_record_request(self):
        """Тест записи запроса"""
        self.assertTrue(self.detector.record_request("192.168.1.1"))
        self.assertEqual(len(self.detector.request_history), 1)
    
    def test_get_suspicious_ips(self):
        """Тест получения подозрительных IP"""
        for i in range(10):
            self.detector.record_request("192.168.1.1")
        
        suspicious = self.detector.get_suspicious_ips(5)
        self.assertEqual(len(suspicious), 1)
        self.assertEqual(suspicious[0][0], "192.168.1.1")
        self.assertEqual(suspicious[0][1], 10)
    
    def test_get_statistics(self):
        """Тест получения статистики"""
        self.detector.record_request("192.168.1.1")
        
        stats = self.detector.get_statistics()
        self.assertIn('total_requests', stats)
        self.assertIn('unique_ips', stats)
        self.assertIn('under_attack', stats)


class TestSecurityMonitor(unittest.TestCase):
    """Тесты для Security Monitor"""
    
    def setUp(self):
        self.monitor = SecurityMonitor()
    
    def test_initialization(self):
        """Тест инициализации"""
        self.assertIsNotNone(self.monitor)
        self.assertIsNotNone(self.monitor.rate_limiter)
        self.assertIsNotNone(self.monitor.ddos_detector)
    
    def test_check_request(self):
        """Тест проверки запроса"""
        allowed, reason = self.monitor.check_request("192.168.1.1")
        self.assertTrue(allowed)
    
    def test_get_security_status(self):
        """Тест получения статуса безопасности"""
        status = self.monitor.get_security_status()
        self.assertIn('rate_limiter', status)
        self.assertIn('ddos_detector', status)
        self.assertIn('threat_level', status)


def run_tests():
    """Запустить все тесты"""
    loader = unittest.TestLoader()
    suite = unittest.TestSuite()
    
    # Добавляем тесты
    suite.addTests(loader.loadTestsFromTestCase(TestInputRecorder))
    suite.addTests(loader.loadTestsFromTestCase(TestInputPlayer))
    suite.addTests(loader.loadTestsFromTestCase(TestMacroManager))
    suite.addTests(loader.loadTestsFromTestCase(TestMessaging))
    suite.addTests(loader.loadTestsFromTestCase(TestPrometheusMetrics))
    suite.addTests(loader.loadTestsFromTestCase(TestPrometheusExporter))
    suite.addTests(loader.loadTestsFromTestCase(TestAdvancedRateLimiter))
    suite.addTests(loader.loadTestsFromTestCase(TestDDoSDetector))
    suite.addTests(loader.loadTestsFromTestCase(TestSecurityMonitor))
    
    runner = unittest.TextTestRunner(verbosity=2)
    result = runner.run(suite)
    
    return result.wasSuccessful()


if __name__ == '__main__':
    success = run_tests()
    sys.exit(0 if success else 1)
