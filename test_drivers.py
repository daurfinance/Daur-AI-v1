#!/usr/bin/env python3
"""
Тестирование низкоуровневых драйверов Daur-AI
Демонстрация возможностей прямого доступа к оборудованию
"""

import sys
import os
import time
import logging
import numpy as np

# Добавляем путь к модулям
sys.path.insert(0, '/home/ubuntu/Daur-AI-v1/src')

from drivers.screen_driver import ScreenDriver
from drivers.input_driver import InputDriver
from drivers.camera_driver import CameraDriver

# Настройка логирования
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)

def test_screen_driver():
    """Тестирует драйвер экрана"""
    print("\n" + "="*50)
    print("ТЕСТИРОВАНИЕ ДРАЙВЕРА ЭКРАНА")
    print("="*50)
    
    try:
        # Инициализация драйвера
        screen_driver = ScreenDriver()
        
        print(f"Драйвер инициализирован: {screen_driver.is_initialized}")
        print(f"Информация о экране: {screen_driver.get_screen_info()}")
        
        if screen_driver.is_initialized:
            # Захват кадра
            print("\nЗахватываем кадр...")
            frame = screen_driver.capture_frame()
            
            if frame is not None and frame.size > 0:
                print(f"Кадр захвачен: {frame.shape}")
                
                # Запуск непрерывного захвата
                print("\nЗапускаем непрерывный захват (5 секунд)...")
                screen_driver.start_continuous_capture(fps=10)
                
                time.sleep(5)
                
                # Получаем последний кадр
                latest_frame = screen_driver.get_latest_frame()
                if latest_frame is not None:
                    print(f"Последний кадр: {latest_frame.shape}")
                
                screen_driver.stop_continuous_capture()
                print("Непрерывный захват остановлен")
            else:
                print("Не удалось захватить кадр")
        
        # Очистка
        screen_driver.cleanup()
        print("✅ Тест драйвера экрана завершен")
        
    except Exception as e:
        print(f"❌ Ошибка тестирования драйвера экрана: {e}")

def test_input_driver():
    """Тестирует драйвер ввода"""
    print("\n" + "="*50)
    print("ТЕСТИРОВАНИЕ ДРАЙВЕРА ВВОДА")
    print("="*50)
    
    try:
        # Инициализация драйвера
        input_driver = InputDriver()
        
        device_list = input_driver.get_device_list()
        print(f"Найдено клавиатур: {len(device_list['keyboards'])}")
        print(f"Найдено мышей: {len(device_list['mice'])}")
        
        # Показываем информацию об устройствах
        for device_path, device_info in device_list['all_devices'].items():
            print(f"  {device_path}: {device_info['name']} ({device_info['type']})")
        
        # Тестируем виртуальные устройства
        if input_driver.virtual_keyboard_fd:
            print("\n✅ Виртуальная клавиатура создана")
            
            # Отправляем тестовое нажатие (пробел)
            print("Отправляем нажатие пробела...")
            input_driver.send_key_event(57, True)  # KEY_SPACE press
            time.sleep(0.1)
            input_driver.send_key_event(57, False)  # KEY_SPACE release
            
        if input_driver.virtual_mouse_fd:
            print("✅ Виртуальная мышь создана")
            
            # Отправляем движение мыши
            print("Отправляем движение мыши...")
            input_driver.send_mouse_event(x=10, y=10)
        
        # Запускаем мониторинг событий на короткое время
        print("\nЗапускаем мониторинг событий (3 секунды)...")
        input_driver.start_event_monitoring()
        
        time.sleep(3)
        
        # Получаем события
        events = input_driver.get_events()
        print(f"Получено событий: {len(events)}")
        
        for event in events[:5]:  # Показываем первые 5 событий
            print(f"  {event['device_type']}: type={event['type']}, code={event['code']}, value={event['value']}")
        
        input_driver.stop_event_monitoring()
        
        # Очистка
        input_driver.cleanup()
        print("✅ Тест драйвера ввода завершен")
        
    except Exception as e:
        print(f"❌ Ошибка тестирования драйвера ввода: {e}")

def test_camera_driver():
    """Тестирует драйвер камеры"""
    print("\n" + "="*50)
    print("ТЕСТИРОВАНИЕ ДРАЙВЕРА КАМЕРЫ")
    print("="*50)
    
    try:
        # Инициализация драйвера
        camera_driver = CameraDriver()
        
        camera_list = camera_driver.get_camera_list()
        print(f"Найдено камер: {len(camera_list)}")
        
        # Показываем информацию о камерах
        for device_path, camera_info in camera_list.items():
            print(f"  {device_path}: {camera_info['name']}")
            print(f"    Драйвер: {camera_info['driver']}")
            print(f"    Форматы: {len(camera_info['formats'])}")
        
        # Тестируем первую доступную камеру
        if camera_list:
            first_camera = list(camera_list.keys())[0]
            print(f"\nТестируем камеру: {first_camera}")
            
            # Открываем камеру
            if camera_driver.open_camera(first_camera, width=320, height=240):
                print("✅ Камера открыта")
                
                # Захватываем несколько кадров
                print("Захватываем кадры (5 секунд)...")
                
                for i in range(10):
                    frame = camera_driver.capture_frame(first_camera)
                    if frame is not None:
                        print(f"  Кадр {i+1}: {frame.shape}")
                    time.sleep(0.5)
                
                # Закрываем камеру
                camera_driver.close_camera(first_camera)
                print("Камера закрыта")
            else:
                print("❌ Не удалось открыть камеру")
        else:
            print("⚠️  Камеры не найдены")
        
        # Очистка
        camera_driver.cleanup()
        print("✅ Тест драйвера камеры завершен")
        
    except Exception as e:
        print(f"❌ Ошибка тестирования драйвера камеры: {e}")

def test_system_access():
    """Тестирует системный доступ"""
    print("\n" + "="*50)
    print("ТЕСТИРОВАНИЕ СИСТЕМНОГО ДОСТУПА")
    print("="*50)
    
    try:
        # Проверяем доступ к устройствам
        devices_to_check = [
            '/dev/fb0',      # Framebuffer
            '/dev/input',    # Input devices
            '/dev/video0',   # Camera
            '/dev/uinput',   # Virtual input
            '/dev/mem',      # Memory access
        ]
        
        for device in devices_to_check:
            if os.path.exists(device):
                try:
                    # Проверяем права доступа
                    stat_info = os.stat(device)
                    readable = os.access(device, os.R_OK)
                    writable = os.access(device, os.W_OK)
                    
                    print(f"✅ {device}: R={readable}, W={writable}")
                except Exception as e:
                    print(f"⚠️  {device}: {e}")
            else:
                print(f"❌ {device}: не существует")
        
        # Проверяем права пользователя
        print(f"\nПользователь: {os.getenv('USER', 'unknown')}")
        print(f"UID: {os.getuid()}")
        print(f"GID: {os.getgid()}")
        
        # Проверяем группы
        try:
            import grp
            groups = [grp.getgrgid(gid).gr_name for gid in os.getgroups()]
            print(f"Группы: {', '.join(groups)}")
        except:
            print("Не удалось получить информацию о группах")
        
        print("✅ Тест системного доступа завершен")
        
    except Exception as e:
        print(f"❌ Ошибка тестирования системного доступа: {e}")

def main():
    """Главная функция тестирования"""
    print("🚀 ТЕСТИРОВАНИЕ НИЗКОУРОВНЕВЫХ ДРАЙВЕРОВ DAUR-AI")
    print("Версия: 1.0")
    print("Дата:", time.strftime("%Y-%m-%d %H:%M:%S"))
    
    # Проверяем права доступа
    if os.getuid() != 0:
        print("\n⚠️  ВНИМАНИЕ: Запуск не от root. Некоторые функции могут быть недоступны.")
        print("Для полного тестирования запустите: sudo python3 test_drivers.py")
    
    # Запускаем тесты
    test_system_access()
    test_screen_driver()
    test_input_driver()
    test_camera_driver()
    
    print("\n" + "="*50)
    print("🎉 ВСЕ ТЕСТЫ ЗАВЕРШЕНЫ")
    print("="*50)
    
    print("\n📋 РЕЗЮМЕ:")
    print("- Драйверы реализуют прямой доступ к оборудованию")
    print("- Обход системных защит через низкоуровневые API")
    print("- Поддержка framebuffer, input events, V4L2")
    print("- Готовность к интеграции с AI компонентами")

if __name__ == "__main__":
    main()
