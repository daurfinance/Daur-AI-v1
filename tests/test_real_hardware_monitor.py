"""
Unit тесты для RealHardwareMonitor
"""

import unittest
import json
import os
import time
from src.hardware.real_hardware_monitor import (
    RealHardwareMonitor,
    CPUMetrics,
    MemoryMetrics,
    DiskMetrics,
    GPUMetrics,
    BatteryMetrics,
    NetworkMetrics,
    ProcessMetrics
)


class TestRealHardwareMonitor(unittest.TestCase):
    """Тесты для RealHardwareMonitor"""
    
    def setUp(self):
        """Подготовка к тестам"""
        self.monitor = RealHardwareMonitor(history_size=100)
    
    def tearDown(self):
        """Очистка после тестов"""
        self.monitor.cleanup()
    
    # ===== CPU Tests =====
    
    def test_get_cpu_metrics(self):
        """Тест получения метрик CPU"""
        metrics = self.monitor.get_cpu_metrics()
        
        self.assertIsNotNone(metrics)
        self.assertIsInstance(metrics, CPUMetrics)
        self.assertGreaterEqual(metrics.percent, 0)
        self.assertLessEqual(metrics.percent, 100)
        self.assertGreater(metrics.count_logical, 0)
        self.assertGreater(metrics.count_physical, 0)
        self.assertEqual(len(metrics.percent_per_core), metrics.count_logical)
    
    def test_cpu_metrics_to_dict(self):
        """Тест конвертации CPU метрик в dict"""
        metrics = self.monitor.get_cpu_metrics()
        data = metrics.to_dict()
        
        self.assertIsInstance(data, dict)
        self.assertIn('timestamp', data)
        self.assertIn('percent', data)
        self.assertIn('count_logical', data)
    
    def test_cpu_frequency(self):
        """Тест получения частоты CPU"""
        metrics = self.monitor.get_cpu_metrics()
        
        self.assertGreater(metrics.freq_current, 0)
        self.assertGreater(metrics.freq_max, 0)
        self.assertGreaterEqual(metrics.freq_min, 0)
        self.assertLessEqual(metrics.freq_current, metrics.freq_max)
    
    def test_cpu_temperature(self):
        """Тест получения температуры CPU"""
        metrics = self.monitor.get_cpu_metrics()
        
        # Температура может быть None если не поддерживается
        if metrics.temperature is not None:
            self.assertGreater(metrics.temperature, 0)
            self.assertLess(metrics.temperature, 150)  # Разумный диапазон
    
    # ===== Memory Tests =====
    
    def test_get_memory_metrics(self):
        """Тест получения метрик памяти"""
        metrics = self.monitor.get_memory_metrics()
        
        self.assertIsNotNone(metrics)
        self.assertIsInstance(metrics, MemoryMetrics)
        self.assertGreater(metrics.total, 0)
        self.assertGreaterEqual(metrics.used, 0)
        self.assertGreaterEqual(metrics.free, 0)
        self.assertGreaterEqual(metrics.percent, 0)
        self.assertLessEqual(metrics.percent, 100)
    
    def test_memory_metrics_consistency(self):
        """Тест консистентности метрик памяти"""
        metrics = self.monitor.get_memory_metrics()
        
        # used + free должно быть примерно равно total
        self.assertAlmostEqual(
            metrics.used + metrics.free,
            metrics.total,
            delta=metrics.total * 0.1  # 10% допуска
        )
    
    def test_memory_metrics_to_dict(self):
        """Тест конвертации памяти в dict"""
        metrics = self.monitor.get_memory_metrics()
        data = metrics.to_dict()
        
        self.assertIsInstance(data, dict)
        self.assertIn('timestamp', data)
        self.assertIn('percent', data)
        self.assertIn('total', data)
    
    # ===== Disk Tests =====
    
    def test_get_disk_metrics(self):
        """Тест получения метрик дисков"""
        metrics_list = self.monitor.get_disk_metrics()
        
        self.assertIsInstance(metrics_list, list)
        self.assertGreater(len(metrics_list), 0)
        
        for metrics in metrics_list:
            self.assertIsInstance(metrics, DiskMetrics)
            self.assertGreater(metrics.total, 0)
            self.assertGreaterEqual(metrics.used, 0)
            self.assertGreaterEqual(metrics.free, 0)
            self.assertGreaterEqual(metrics.percent, 0)
            self.assertLessEqual(metrics.percent, 100)
    
    def test_disk_metrics_consistency(self):
        """Тест консистентности метрик дисков"""
        metrics_list = self.monitor.get_disk_metrics()
        
        for metrics in metrics_list:
            # used + free должно быть примерно равно total
            self.assertAlmostEqual(
                metrics.used + metrics.free,
                metrics.total,
                delta=metrics.total * 0.1  # 10% допуска
            )
    
    # ===== Battery Tests =====
    
    def test_get_battery_metrics(self):
        """Тест получения метрик батареи"""
        metrics = self.monitor.get_battery_metrics()
        
        # Батарея может быть None если не поддерживается
        if metrics is not None:
            self.assertIsInstance(metrics, BatteryMetrics)
            self.assertGreaterEqual(metrics.percent, 0)
            self.assertLessEqual(metrics.percent, 100)
            self.assertIn(metrics.status, ['charging', 'discharging', 'full', 'unknown'])
    
    # ===== Network Tests =====
    
    def test_get_network_metrics(self):
        """Тест получения метрик сети"""
        metrics_list = self.monitor.get_network_metrics()
        
        self.assertIsInstance(metrics_list, list)
        self.assertGreater(len(metrics_list), 0)
        
        for metrics in metrics_list:
            self.assertIsInstance(metrics, NetworkMetrics)
            self.assertGreaterEqual(metrics.bytes_sent, 0)
            self.assertGreaterEqual(metrics.bytes_recv, 0)
            self.assertGreaterEqual(metrics.packets_sent, 0)
            self.assertGreaterEqual(metrics.packets_recv, 0)
    
    # ===== Process Tests =====
    
    def test_get_top_processes(self):
        """Тест получения топ процессов"""
        metrics_list = self.monitor.get_top_processes(limit=5)
        
        self.assertIsInstance(metrics_list, list)
        self.assertLessEqual(len(metrics_list), 5)
        
        for metrics in metrics_list:
            self.assertIsInstance(metrics, ProcessMetrics)
            self.assertGreater(metrics.pid, 0)
            self.assertGreaterEqual(metrics.cpu_percent, 0)
            self.assertGreaterEqual(metrics.memory_percent, 0)
    
    def test_top_processes_by_memory(self):
        """Тест получения топ процессов по памяти"""
        metrics_list = self.monitor.get_top_processes(limit=5, sort_by="memory")
        
        self.assertIsInstance(metrics_list, list)
        self.assertLessEqual(len(metrics_list), 5)
        
        # Проверяем что отсортировано по памяти
        for i in range(len(metrics_list) - 1):
            self.assertGreaterEqual(
                metrics_list[i].memory_percent,
                metrics_list[i + 1].memory_percent
            )
    
    # ===== Full Status Tests =====
    
    def test_get_full_status(self):
        """Тест получения полного статуса"""
        status = self.monitor.get_full_status()
        
        self.assertIsInstance(status, dict)
        self.assertIn('timestamp', status)
        self.assertIn('cpu', status)
        self.assertIn('memory', status)
        self.assertIn('disks', status)
        self.assertIn('network', status)
        self.assertIn('top_processes_cpu', status)
        self.assertIn('top_processes_memory', status)
    
    # ===== History Tests =====
    
    def test_cpu_history(self):
        """Тест истории CPU"""
        # Собираем несколько метрик
        for _ in range(5):
            self.monitor.get_cpu_metrics()
        
        history = self.monitor.get_history("cpu", limit=10)
        self.assertGreater(len(history), 0)
        self.assertLessEqual(len(history), 10)
    
    def test_memory_history(self):
        """Тест истории памяти"""
        # Собираем несколько метрик
        for _ in range(5):
            self.monitor.get_memory_metrics()
        
        history = self.monitor.get_history("memory", limit=10)
        self.assertGreater(len(history), 0)
        self.assertLessEqual(len(history), 10)
    
    def test_history_limit(self):
        """Тест ограничения размера истории"""
        # Собираем много метрик
        for _ in range(150):
            self.monitor.get_cpu_metrics()
        
        # История должна быть ограничена размером 100
        self.assertEqual(len(self.monitor.cpu_history), 100)
    
    # ===== Monitoring Tests =====
    
    def test_start_stop_monitoring(self):
        """Тест запуска и остановки мониторинга"""
        self.monitor.start_monitoring(interval=1)
        self.assertTrue(self.monitor.monitoring)
        
        time.sleep(2)
        
        # Проверяем что метрики собираются
        self.assertGreater(len(self.monitor.cpu_history), 0)
        
        self.monitor.stop_monitoring()
        self.assertFalse(self.monitor.monitoring)
    
    def test_monitoring_interval(self):
        """Тест интервала мониторинга"""
        self.monitor.start_monitoring(interval=1)
        
        initial_count = len(self.monitor.cpu_history)
        time.sleep(3)
        final_count = len(self.monitor.cpu_history)
        
        # Должно быть примерно 3 новых метрики (с допуском)
        self.assertGreater(final_count - initial_count, 1)
        self.assertLess(final_count - initial_count, 6)
        
        self.monitor.stop_monitoring()
    
    # ===== Save/Load Tests =====
    
    def test_save_metrics(self):
        """Тест сохранения метрик"""
        # Собираем метрики
        self.monitor.get_cpu_metrics()
        self.monitor.get_memory_metrics()
        self.monitor.get_disk_metrics()
        
        # Сохраняем
        filepath = "/tmp/test_metrics.json"
        result = self.monitor.save_metrics(filepath)
        
        self.assertTrue(result)
        self.assertTrue(os.path.exists(filepath))
        
        # Проверяем содержимое
        with open(filepath, 'r') as f:
            data = json.load(f)
        
        self.assertIn('timestamp', data)
        self.assertIn('cpu', data)
        self.assertIn('memory', data)
        
        # Очистка
        os.remove(filepath)
    
    # ===== Error Handling Tests =====
    
    def test_invalid_history_type(self):
        """Тест получения истории с неверным типом"""
        history = self.monitor.get_history("invalid_type", limit=10)
        self.assertEqual(history, [])
    
    def test_multiple_monitors(self):
        """Тест нескольких мониторов"""
        monitor1 = RealHardwareMonitor()
        monitor2 = RealHardwareMonitor()
        
        metrics1 = monitor1.get_cpu_metrics()
        metrics2 = monitor2.get_cpu_metrics()
        
        self.assertIsNotNone(metrics1)
        self.assertIsNotNone(metrics2)
        
        monitor1.cleanup()
        monitor2.cleanup()


if __name__ == '__main__':
    unittest.main()

