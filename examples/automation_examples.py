#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
Daur-AI: Примеры использования модулей
Примеры автоматизации форм, мониторинга и сценариев

Версия: 2.0
Дата: 25.10.2025
Автор: Manus AI
"""

import logging
import time
from typing import Dict, Any, List

# Настройка логирования
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger('daur_ai.examples')


# ==================== ПРИМЕР 1: АВТОМАТИЗАЦИЯ ФОРМ ====================

class FormAutomationExample:
    """Пример автоматизации заполнения форм"""
    
    @staticmethod
    def fill_login_form(username: str, password: str):
        """
        Пример: Заполнить форму входа
        
        Args:
            username: Имя пользователя
            password: Пароль
        """
        try:
            import pyautogui
            
            logger.info("Начинаем заполнение формы входа...")
            
            # Найти поле username
            logger.info("Ищем поле username...")
            time.sleep(1)
            
            # Кликнуть на поле username
            pyautogui.click(400, 300)
            time.sleep(0.5)
            
            # Очистить поле
            pyautogui.hotkey('ctrl', 'a')
            time.sleep(0.2)
            
            # Ввести username
            pyautogui.typewrite(username, interval=0.05)
            time.sleep(0.5)
            
            # Перейти на поле пароля (Tab)
            pyautogui.press('tab')
            time.sleep(0.5)
            
            # Ввести пароль
            pyautogui.typewrite(password, interval=0.05)
            time.sleep(0.5)
            
            # Нажать Enter для отправки
            pyautogui.press('enter')
            
            logger.info("Форма заполнена и отправлена")
            return True
        
        except Exception as e:
            logger.error(f"Ошибка заполнения формы: {e}")
            return False
    
    @staticmethod
    def fill_registration_form(data: Dict[str, str]):
        """
        Пример: Заполнить форму регистрации
        
        Args:
            data: Словарь с данными (name, email, password, confirm_password)
        """
        try:
            import pyautogui
            
            logger.info("Начинаем заполнение формы регистрации...")
            
            fields = ['name', 'email', 'password', 'confirm_password']
            field_positions = {
                'name': (400, 250),
                'email': (400, 320),
                'password': (400, 390),
                'confirm_password': (400, 460)
            }
            
            for field in fields:
                if field in data:
                    # Кликнуть на поле
                    x, y = field_positions[field]
                    pyautogui.click(x, y)
                    time.sleep(0.3)
                    
                    # Очистить поле
                    pyautogui.hotkey('ctrl', 'a')
                    time.sleep(0.2)
                    
                    # Ввести данные
                    pyautogui.typewrite(data[field], interval=0.03)
                    time.sleep(0.3)
            
            # Найти и кликнуть кнопку регистрации
            logger.info("Отправляем форму...")
            pyautogui.click(400, 530)  # Кнопка "Register"
            
            logger.info("Форма регистрации заполнена и отправлена")
            return True
        
        except Exception as e:
            logger.error(f"Ошибка заполнения формы регистрации: {e}")
            return False


# ==================== ПРИМЕР 2: МОНИТОРИНГ СИСТЕМЫ ====================

class SystemMonitoringExample:
    """Пример мониторинга системы"""
    
    @staticmethod
    def monitor_hardware_health():
        """Пример: Мониторить здоровье оборудования"""
        try:
            from src.hardware.advanced_hardware_monitor import get_advanced_hardware_monitor
            
            logger.info("Начинаем мониторинг оборудования...")
            
            monitor = get_advanced_hardware_monitor()
            
            # Получить статус
            status = monitor.get_full_hardware_status()
            
            # Проверить температуру
            health = monitor.check_temperature_health()
            
            logger.info(f"Статус здоровья: {health['status']}")
            logger.info(f"Процессор: {health.get('cpu_status', 'unknown')}")
            logger.info(f"GPU: {health.get('gpu_status', 'unknown')}")
            
            # Получить батарею
            battery = monitor.get_battery_info()
            if battery:
                logger.info(f"Батарея: {battery.percent}%")
            
            return status
        
        except Exception as e:
            logger.error(f"Ошибка мониторинга: {e}")
            return None
    
    @staticmethod
    def monitor_network_status():
        """Пример: Мониторить статус сети"""
        try:
            from src.hardware.network_monitor import get_network_monitor
            
            logger.info("Начинаем мониторинг сети...")
            
            monitor = get_network_monitor()
            
            # Получить статус
            status = monitor.get_full_network_status()
            
            # Получить интерфейсы
            interfaces = monitor.get_network_interfaces()
            
            logger.info(f"Активных интерфейсов: {len([i for i in interfaces if i.is_up])}")
            
            for interface in interfaces:
                if interface.is_up:
                    logger.info(f"  {interface.name}: {interface.ipv4_address}")
            
            return status
        
        except Exception as e:
            logger.error(f"Ошибка мониторинга сети: {e}")
            return None
    
    @staticmethod
    def continuous_monitoring(interval: int = 5, duration: int = 60):
        """
        Пример: Непрерывный мониторинг
        
        Args:
            interval: Интервал проверки (секунды)
            duration: Длительность мониторинга (секунды)
        """
        try:
            from src.hardware.advanced_hardware_monitor import get_advanced_hardware_monitor
            
            logger.info(f"Начинаем непрерывный мониторинг на {duration} секунд...")
            
            monitor = get_advanced_hardware_monitor()
            start_time = time.time()
            
            while time.time() - start_time < duration:
                # Получить текущий статус
                status = monitor.get_full_hardware_status()
                
                # Получить температуры
                temps = monitor.get_all_temperatures()
                
                # Вывести информацию
                logger.info(f"Время: {datetime.now().strftime('%H:%M:%S')}")
                
                if temps:
                    for temp in temps[:3]:  # Первые 3 датчика
                        logger.info(f"  {temp.label}: {temp.current}°C")
                
                # Ждать перед следующей проверкой
                time.sleep(interval)
            
            logger.info("Мониторинг завершен")
            return True
        
        except Exception as e:
            logger.error(f"Ошибка непрерывного мониторинга: {e}")
            return False


# ==================== ПРИМЕР 3: СЦЕНАРИИ АВТОМАТИЗАЦИИ ====================

class AutomationScenarios:
    """Примеры сценариев автоматизации"""
    
    @staticmethod
    def screenshot_and_analyze():
        """Пример: Снять скриншот и проанализировать его"""
        try:
            import pyautogui
            from src.vision.screen_recognition import get_screen_analyzer
            from src.ai.openai_vision_analyzer import get_openai_vision_analyzer
            
            logger.info("Снимаем скриншот...")
            
            # Снять скриншот
            screenshot = pyautogui.screenshot()
            screenshot_path = '/tmp/screenshot.png'
            screenshot.save(screenshot_path)
            
            logger.info(f"Скриншот сохранен: {screenshot_path}")
            
            # Анализировать с OpenAI
            analyzer = get_openai_vision_analyzer()
            analysis = analyzer.analyze_image(screenshot_path, detailed=True)
            
            if analysis:
                logger.info(f"Описание: {analysis.description}")
                logger.info(f"Объекты: {', '.join(analysis.objects)}")
                logger.info(f"Тип сцены: {analysis.scene_type}")
            
            return analysis
        
        except Exception as e:
            logger.error(f"Ошибка анализа скриншота: {e}")
            return None
    
    @staticmethod
    def detect_and_click_button(button_image_path: str):
        """
        Пример: Найти кнопку на экране и кликнуть на нее
        
        Args:
            button_image_path: Путь к изображению кнопки
        """
        try:
            import pyautogui
            from src.input.advanced_mouse_controller import get_advanced_mouse_controller
            
            logger.info(f"Ищем кнопку: {button_image_path}")
            
            mouse = get_advanced_mouse_controller()
            
            # Найти кнопку
            location = mouse.find_image_on_screen(button_image_path, confidence=0.8)
            
            if location:
                logger.info(f"Кнопка найдена в: {location}")
                
                # Кликнуть на кнопку
                pyautogui.click(location[0], location[1])
                
                logger.info("Кнопка нажата")
                return True
            else:
                logger.warning("Кнопка не найдена")
                return False
        
        except Exception as e:
            logger.error(f"Ошибка поиска и клика: {e}")
            return False
    
    @staticmethod
    def web_automation_scenario():
        """Пример: Сценарий автоматизации веб-сайта"""
        try:
            import pyautogui
            
            logger.info("Начинаем сценарий автоматизации веб-сайта...")
            
            # 1. Открыть браузер (Alt+Tab или другой способ)
            logger.info("1. Открываем браузер...")
            time.sleep(2)
            
            # 2. Перейти на сайт (Ctrl+L для адресной строки)
            logger.info("2. Переходим на сайт...")
            pyautogui.hotkey('ctrl', 'l')
            time.sleep(0.5)
            pyautogui.typewrite('example.com', interval=0.05)
            pyautogui.press('enter')
            time.sleep(3)
            
            # 3. Найти и заполнить форму
            logger.info("3. Заполняем форму...")
            pyautogui.click(400, 300)
            time.sleep(0.3)
            pyautogui.typewrite('test@example.com', interval=0.03)
            time.sleep(0.5)
            
            # 4. Отправить форму
            logger.info("4. Отправляем форму...")
            pyautogui.press('tab')
            time.sleep(0.3)
            pyautogui.press('enter')
            
            logger.info("Сценарий завершен")
            return True
        
        except Exception as e:
            logger.error(f"Ошибка сценария: {e}")
            return False
    
    @staticmethod
    def data_extraction_scenario():
        """Пример: Сценарий извлечения данных"""
        try:
            import pyautogui
            from src.vision.screen_recognition import get_screen_analyzer
            from src.ai.openai_vision_analyzer import get_openai_vision_analyzer
            
            logger.info("Начинаем сценарий извлечения данных...")
            
            # 1. Снять скриншот
            logger.info("1. Снимаем скриншот...")
            screenshot = pyautogui.screenshot()
            screenshot_path = '/tmp/data_screenshot.png'
            screenshot.save(screenshot_path)
            
            # 2. Извлечь текст
            logger.info("2. Извлекаем текст...")
            analyzer = get_openai_vision_analyzer()
            text = analyzer.extract_text_from_image(screenshot_path)
            
            if text:
                logger.info(f"Извлеченный текст:\n{text}")
            
            # 3. Детектировать объекты
            logger.info("3. Детектируем объекты...")
            objects = analyzer.detect_objects_in_image(screenshot_path)
            
            if objects:
                logger.info(f"Найдено объектов: {len(objects)}")
                for obj in objects[:3]:
                    logger.info(f"  - {obj.get('name', 'unknown')}")
            
            logger.info("Сценарий завершен")
            return True
        
        except Exception as e:
            logger.error(f"Ошибка сценария извлечения: {e}")
            return False


# ==================== ЗАПУСК ПРИМЕРОВ ====================

def run_examples():
    """Запустить все примеры"""
    
    logger.info("=" * 50)
    logger.info("ПРИМЕРЫ ИСПОЛЬЗОВАНИЯ DAUR-AI")
    logger.info("=" * 50)
    
    # Пример 1: Мониторинг
    logger.info("\n[ПРИМЕР 1] Мониторинг оборудования")
    logger.info("-" * 50)
    SystemMonitoringExample.monitor_hardware_health()
    
    # Пример 2: Мониторинг сети
    logger.info("\n[ПРИМЕР 2] Мониторинг сети")
    logger.info("-" * 50)
    SystemMonitoringExample.monitor_network_status()
    
    # Пример 3: Анализ скриншота
    logger.info("\n[ПРИМЕР 3] Анализ скриншота")
    logger.info("-" * 50)
    # AutomationScenarios.screenshot_and_analyze()
    
    logger.info("\n" + "=" * 50)
    logger.info("ВСЕ ПРИМЕРЫ ЗАВЕРШЕНЫ")
    logger.info("=" * 50)


if __name__ == '__main__':
    from datetime import datetime
    run_examples()

