#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
Daur-AI: Тесты для валидации улучшений backend
Версия: 2.0
Дата: 25.10.2025
Автор: Manus AI
"""

import unittest
import sys
import os
import time
import tempfile
from pathlib import Path

# Добавляем src в путь
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'src'))

from monitoring.advanced_monitoring import (
    MetricsCollector, SystemMonitor, AdvancedLogger, ErrorTracker, PerformanceProfiler
)
from reliability.error_handling import (
    RetryConfig, RetryStrategy, CircuitBreaker, ResilientExecutor, FallbackHandler, HealthChecker
)
from performance.optimization import (
    ThreadPool, MemoryOptimizer, SmartCache, LoadBalancer, BatchProcessor, PerformanceMonitor
)
from security.security_manager import (
    PasswordValidator, TokenManager, InputValidator, SecurityPolicy, AuditLogger
)
from features.advanced_features import (
    ResultCache, TaskScheduler, NotificationManager, AnalyticsCollector
)


class TestMonitoring(unittest.TestCase):
    """Тесты для модуля мониторинга"""
    
    def setUp(self):
        """Подготовка к тестам"""
        self.metrics = MetricsCollector(max_samples=100)
    
    def test_metrics_collection(self):
        """Тест сбора метрик"""
        self.metrics.record('test_metric', 10.5)
        self.metrics.record('test_metric', 20.3)
        self.metrics.record('test_metric', 15.7)
        
        stats = self.metrics.get_stats('test_metric')
        
        self.assertEqual(stats['count'], 3)
        self.assertEqual(stats['min'], 10.5)
        self.assertEqual(stats['max'], 20.3)
        self.assertAlmostEqual(stats['avg'], 15.5, places=1)
    
    def test_error_tracker(self):
        """Тест отслеживания ошибок"""
        tracker = ErrorTracker(max_errors=10)
        
        tracker.record_error('ValueError', 'Invalid value')
        tracker.record_error('ValueError', 'Invalid value')
        tracker.record_error('TypeError', 'Type error')
        
        summary = tracker.get_error_summary()
        
        self.assertEqual(summary['ValueError'], 2)
        self.assertEqual(summary['TypeError'], 1)
    
    def test_performance_profiler(self):
        """Тест профилировщика производительности"""
        profiler = PerformanceProfiler()
        
        profiler.measure('operation_1', 0.5)
        profiler.measure('operation_1', 0.3)
        profiler.measure('operation_1', 0.7)
        
        stats = profiler.get_performance_stats('operation_1')
        
        self.assertEqual(stats['count'], 3)
        self.assertEqual(stats['min'], 0.3)
        self.assertEqual(stats['max'], 0.7)


class TestReliability(unittest.TestCase):
    """Тесты для модуля надежности"""
    
    def test_retry_config_linear(self):
        """Тест линейной стратегии повторов"""
        config = RetryConfig(
            max_attempts=3,
            initial_delay=1.0,
            strategy=RetryStrategy.LINEAR
        )
        
        self.assertEqual(config.get_delay(0), 1.0)
        self.assertEqual(config.get_delay(1), 2.0)
        self.assertEqual(config.get_delay(2), 3.0)
    
    def test_retry_config_exponential(self):
        """Тест экспоненциальной стратегии повторов"""
        config = RetryConfig(
            max_attempts=3,
            initial_delay=1.0,
            strategy=RetryStrategy.EXPONENTIAL
        )
        
        self.assertEqual(config.get_delay(0), 1.0)
        self.assertEqual(config.get_delay(1), 2.0)
        self.assertEqual(config.get_delay(2), 4.0)
    
    def test_circuit_breaker(self):
        """Тест circuit breaker"""
        breaker = CircuitBreaker(failure_threshold=2, recovery_timeout=1)
        
        def failing_func():
            raise Exception("Test error")
        
        # Первые две попытки должны вызвать исключение
        for _ in range(2):
            with self.assertRaises(Exception):
                breaker.call(failing_func)
        
        # Третья попытка должна быть заблокирована
        with self.assertRaises(Exception) as context:
            breaker.call(failing_func)
        
        self.assertIn("Circuit breaker открыт", str(context.exception))
    
    def test_fallback_handler(self):
        """Тест обработчика fallback"""
        handler = FallbackHandler()
        
        def main_func(x):
            if x < 0:
                raise ValueError("Negative value")
            return x * 2
        
        def fallback_func(x):
            return 0
        
        handler.register_fallback('main_func', fallback_func)
        
        # Успешный вызов
        result = handler.execute_with_fallback(main_func, 'main_func', 5)
        self.assertEqual(result, 10)
        
        # Вызов с fallback
        result = handler.execute_with_fallback(main_func, 'main_func', -5)
        self.assertEqual(result, 0)
    
    def test_health_checker(self):
        """Тест проверки здоровья"""
        checker = HealthChecker()
        
        def check_service_1():
            return True
        
        def check_service_2():
            return False
        
        checker.register_check('service_1', check_service_1)
        checker.register_check('service_2', check_service_2)
        
        results = checker.run_checks()
        
        self.assertTrue(results['service_1']['healthy'])
        self.assertFalse(results['service_2']['healthy'])
        self.assertFalse(checker.is_healthy())


class TestPerformance(unittest.TestCase):
    """Тесты для модуля производительности"""
    
    def test_smart_cache(self):
        """Тест интеллектуального кэша"""
        cache = SmartCache(max_size=3, ttl=10)
        
        cache.set('key1', 'value1')
        cache.set('key2', 'value2')
        cache.set('key3', 'value3')
        
        self.assertEqual(cache.get('key1'), 'value1')
        self.assertEqual(cache.get('key2'), 'value2')
        
        # Добавляем четвертый элемент (должен вытеснить самый старый)
        cache.set('key4', 'value4')
        
        # Проверяем, что кэш работает
        self.assertEqual(cache.get('key2'), 'value2')
        self.assertEqual(cache.get('key4'), 'value4')
        
        # Проверяем статистику
        stats = cache.get_stats()
        self.assertEqual(stats['max_size'], 3)
    
    def test_load_balancer(self):
        """Тест балансировщика нагрузки"""
        balancer = LoadBalancer(num_workers=3)
        
        # Отправляем задачи
        for i in range(5):
            balancer.submit_task(f"task_{i}")
        
        loads = balancer.get_loads()
        
        # Проверяем, что нагрузка распределена
        self.assertEqual(sum(loads), 5)
        self.assertTrue(max(loads) - min(loads) <= 1)
    
    def test_batch_processor(self):
        """Тест обработчика пакетов"""
        processor = BatchProcessor(batch_size=3, timeout=5.0)
        
        # Добавляем элементы
        batch1 = processor.add_item('item1')
        self.assertIsNone(batch1)
        
        batch2 = processor.add_item('item2')
        self.assertIsNone(batch2)
        
        batch3 = processor.add_item('item3')
        self.assertIsNotNone(batch3)
        self.assertEqual(len(batch3), 3)


class TestSecurity(unittest.TestCase):
    """Тесты для модуля безопасности"""
    
    def setUp(self):
        """Подготовка к тестам"""
        self.policy = SecurityPolicy()
        self.validator = PasswordValidator(self.policy)
    
    def test_password_validation(self):
        """Тест валидации пароля"""
        # Слабый пароль
        is_valid, error = self.validator.validate('weak')
        self.assertFalse(is_valid)
        
        # Сильный пароль
        is_valid, error = self.validator.validate('StrongPass123!')
        self.assertTrue(is_valid)
    
    def test_password_hashing(self):
        """Тест хэширования пароля"""
        password = 'TestPassword123!'
        hashed, salt = self.validator.hash_password(password)
        
        # Проверяем пароль
        is_correct = self.validator.verify_password(password, hashed, salt)
        self.assertTrue(is_correct)
        
        # Проверяем неправильный пароль
        is_correct = self.validator.verify_password('WrongPassword', hashed, salt)
        self.assertFalse(is_correct)
    
    def test_token_manager(self):
        """Тест менеджера токенов"""
        manager = TokenManager('secret_key_123', token_lifetime=10)
        
        token = manager.generate_token('user_1', ['read', 'write'])
        
        is_valid, token_data = manager.verify_token(token)
        
        self.assertTrue(is_valid)
        self.assertEqual(token_data['user_id'], 'user_1')
        self.assertIn('read', token_data['permissions'])
    
    def test_input_validator(self):
        """Тест валидатора входных данных"""
        validator = InputValidator(self.policy)
        
        # Проверяем запрещенные команды
        is_valid, error = validator.validate_command('rm -rf /')
        self.assertFalse(is_valid)
        
        # Проверяем SQL injection
        is_valid, error = validator.validate_command("'; DROP TABLE users; --")
        self.assertFalse(is_valid)
        
        # Проверяем валидную команду
        is_valid, error = validator.validate_command('ls -la')
        self.assertTrue(is_valid)


class TestFeatures(unittest.TestCase):
    """Тесты для модуля расширенных функций"""
    
    def test_task_scheduler(self):
        """Тест планировщика задач"""
        scheduler = TaskScheduler()
        scheduler.start()
        
        executed = []
        
        def test_task():
            executed.append(True)
        
        # Планируем задачу с задержкой 0.5 сек
        task_id = scheduler.schedule_task(test_task, delay=0.5)
        
        # Ждем выполнения
        time.sleep(1)
        
        self.assertTrue(len(executed) > 0)
        
        scheduler.stop()
    
    def test_notification_manager(self):
        """Тест менеджера уведомлений"""
        manager = NotificationManager()
        
        received = []
        
        def on_event(notification):
            received.append(notification)
        
        manager.subscribe('test_event', on_event)
        manager.notify('test_event', {'data': 'test'})
        
        self.assertEqual(len(received), 1)
        self.assertEqual(received[0]['type'], 'test_event')
    
    def test_analytics_collector(self):
        """Тест сборщика аналитики"""
        collector = AnalyticsCollector()
        
        collector.track_event('user_login', {'user_id': '123'})
        collector.track_event('user_login', {'user_id': '456'})
        collector.track_event('user_logout', {'user_id': '123'})
        
        login_count = collector.get_event_count('user_login')
        self.assertEqual(login_count, 2)
        
        collector.track_metric('response_time', 0.5)
        collector.track_metric('response_time', 0.3)
        
        stats = collector.get_metric_stats('response_time')
        self.assertEqual(stats['count'], 2)


class TestIntegration(unittest.TestCase):
    """Интеграционные тесты"""
    
    def test_resilient_executor(self):
        """Тест устойчивого исполнителя"""
        executor = ResilientExecutor()
        
        attempt_count = 0
        
        def flaky_function():
            nonlocal attempt_count
            attempt_count += 1
            if attempt_count < 3:
                raise Exception("Temporary error")
            return "Success"
        
        result = executor.execute(flaky_function)
        
        self.assertTrue(result['success'])
        self.assertEqual(result['result'], "Success")
        self.assertEqual(result['attempts'], 3)
    
    def test_monitoring_dashboard(self):
        """Тест панели мониторинга"""
        from monitoring.advanced_monitoring import MonitoringDashboard
        
        dashboard = MonitoringDashboard()
        dashboard.start()
        
        time.sleep(1)
        
        status = dashboard.get_full_status()
        
        self.assertIn('system', status)
        self.assertIn('metrics', status)
        self.assertIn('errors', status)
        
        dashboard.stop()


def run_tests():
    """Запустить все тесты"""
    loader = unittest.TestLoader()
    suite = unittest.TestSuite()
    
    # Добавляем все тесты
    suite.addTests(loader.loadTestsFromTestCase(TestMonitoring))
    suite.addTests(loader.loadTestsFromTestCase(TestReliability))
    suite.addTests(loader.loadTestsFromTestCase(TestPerformance))
    suite.addTests(loader.loadTestsFromTestCase(TestSecurity))
    suite.addTests(loader.loadTestsFromTestCase(TestFeatures))
    suite.addTests(loader.loadTestsFromTestCase(TestIntegration))
    
    runner = unittest.TextTestRunner(verbosity=2)
    result = runner.run(suite)
    
    return result.wasSuccessful()


if __name__ == '__main__':
    success = run_tests()
    sys.exit(0 if success else 1)

