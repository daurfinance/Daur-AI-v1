# Daur-AI v2.0: Быстрый старт

**Версия:** 2.0  
**Дата:** 25 октября 2025

---

## ⚡ За 5 минут

### 1. Установка зависимостей

```bash
cd /home/ubuntu/Daur-AI-v1

# Установить основные зависимости
pip3 install -r requirements.txt

# Установить дополнительные зависимости
pip3 install pyautogui opencv-python face-recognition pyzbar psutil netifaces openai flask-socketio
```

### 2. Запуск API сервера

```bash
# Запустить Flask API
python3 -m src.web.enhanced_api_server

# Сервер будет доступен на http://localhost:5000
```

### 3. Первые команды

#### Получить статус оборудования:
```bash
curl http://localhost:5000/api/v2/hardware/status
```

#### Переместить мышь:
```bash
curl -X POST http://localhost:5000/api/v2/mouse/move \
  -H "Content-Type: application/json" \
  -d '{"x": 400, "y": 300, "duration": 0.5}'
```

#### Напечатать текст:
```bash
curl -X POST http://localhost:5000/api/v2/keyboard/type \
  -H "Content-Type: application/json" \
  -d '{"text": "Hello, World!", "interval": 0.05}'
```

---

## 🎯 Основные сценарии

### Сценарий 1: Мониторинг оборудования

```python
from src.hardware.advanced_hardware_monitor import get_advanced_hardware_monitor

monitor = get_advanced_hardware_monitor()

# Получить статус
status = monitor.get_full_hardware_status()
print(f"CPU: {status['cpu_percent']}%")
print(f"Memory: {status['memory_percent']}%")

# Получить информацию о GPU
gpus = monitor.get_all_gpu_info()
for gpu in gpus:
    print(f"GPU {gpu.index}: {gpu.temperature}°C")

# Получить батарею
battery = monitor.get_battery_info()
if battery:
    print(f"Battery: {battery.percent}%")
```

### Сценарий 2: Управление мышью и клавиатурой

```python
from src.input.advanced_mouse_controller import get_advanced_mouse_controller
from src.input.keyboard_controller import get_keyboard_controller

mouse = get_advanced_mouse_controller()
keyboard = get_keyboard_controller()

# Переместить мышь
mouse.move_to(400, 300, duration=0.5)

# Кликнуть
mouse.click(button='left')

# Напечатать текст
keyboard.type_text("Hello, World!", interval=0.05)

# Горячие клавиши
keyboard.press_hotkey(['ctrl', 'a'])
keyboard.press_hotkey(['ctrl', 'c'])
```

### Сценарий 3: Анализ изображений

```python
from src.ai.openai_vision_analyzer import get_openai_vision_analyzer

analyzer = get_openai_vision_analyzer()

# Анализировать изображение
analysis = analyzer.analyze_image('photo.jpg', detailed=True)
print(f"Description: {analysis.description}")
print(f"Objects: {analysis.objects}")

# Извлечь текст
text = analyzer.extract_text_from_image('document.png')
print(f"Text: {text}")
```

### Сценарий 4: Распознавание лиц

```python
from src.vision.face_recognition_module import get_face_recognition_module

face_module = get_face_recognition_module()

# Добавить известное лицо
face_module.add_known_face('john.jpg', 'John Doe')

# Распознать лица
recognized = face_module.recognize_faces('photo.jpg')
for face in recognized:
    print(f"{face.name}: {face.confidence:.2f}")
```

### Сценарий 5: Работа с QR кодами

```python
from src.vision.barcode_recognition_module import get_barcode_recognition_module

barcode_module = get_barcode_recognition_module()

# Детектировать штрих-коды
barcodes = barcode_module.detect_barcodes_in_image('qr_code.png')
for barcode in barcodes:
    print(f"Type: {barcode.barcode_type.value}")
    print(f"Data: {barcode.data}")

# Валидировать QR код
validation = barcode_module.validate_qr_code('https://example.com')
print(f"Valid: {validation['is_valid']}")
```

---

## 🔌 REST API Примеры

### Mouse API

```bash
# Переместить мышь
curl -X POST http://localhost:5000/api/v2/mouse/move \
  -H "Content-Type: application/json" \
  -d '{"x": 400, "y": 300, "duration": 0.5}'

# Нажать кнопку мыши
curl -X POST http://localhost:5000/api/v2/mouse/click \
  -H "Content-Type: application/json" \
  -d '{"button": "left", "clicks": 1}'

# Нарисовать круг
curl -X POST http://localhost:5000/api/v2/mouse/pattern/circle \
  -H "Content-Type: application/json" \
  -d '{"center_x": 500, "center_y": 500, "radius": 100, "duration": 2.0}'

# Найти изображение
curl -X POST http://localhost:5000/api/v2/mouse/find-image \
  -H "Content-Type: application/json" \
  -d '{"image_path": "button.png", "confidence": 0.8}'
```

### Keyboard API

```bash
# Напечатать текст
curl -X POST http://localhost:5000/api/v2/keyboard/type \
  -H "Content-Type: application/json" \
  -d '{"text": "Hello, World!", "interval": 0.05}'

# Горячие клавиши
curl -X POST http://localhost:5000/api/v2/keyboard/hotkey \
  -H "Content-Type: application/json" \
  -d '{"keys": ["ctrl", "c"]}'
```

### Hardware API

```bash
# Получить статус оборудования
curl http://localhost:5000/api/v2/hardware/status

# Получить информацию о GPU
curl http://localhost:5000/api/v2/hardware/gpu

# Получить информацию о батарее
curl http://localhost:5000/api/v2/hardware/battery

# Получить температуру
curl http://localhost:5000/api/v2/hardware/temperature
```

### Network API

```bash
# Получить статус сети
curl http://localhost:5000/api/v2/network/status

# Получить сетевые интерфейсы
curl http://localhost:5000/api/v2/network/interfaces
```

### Vision API

```bash
# Детектировать лица
curl -X POST http://localhost:5000/api/v2/vision/faces/detect \
  -H "Content-Type: application/json" \
  -d '{"image_path": "photo.jpg"}'

# Детектировать штрих-коды
curl -X POST http://localhost:5000/api/v2/vision/barcodes/detect \
  -H "Content-Type: application/json" \
  -d '{"image_path": "qr_code.png"}'
```

---

## 🧪 Тестирование

```bash
# Запустить все тесты
python3 tests/test_new_modules.py

# Запустить примеры
python3 examples/automation_examples.py
```

---

## 📚 Документация

- **Полное руководство:** `COMPLETE_IMPLEMENTATION_GUIDE.md`
- **Расширения:** `EXPANSION_GUIDE.md`
- **Управление устройствами:** `DEVICE_MANAGEMENT.md`
- **Backend улучшения:** `BACKEND_IMPROVEMENTS.md`

---

## 🚀 Следующие шаги

1. **Интеграция в ваше приложение** - Используйте REST API или импортируйте модули напрямую
2. **Настройка конфигурации** - Создайте файл `.env` с необходимыми переменными
3. **Добавление аутентификации** - Защитите API ключами
4. **Развертывание** - Используйте Docker или облачные сервисы

---

## 💡 Советы

- 🔑 Используйте OpenAI API для интеллектуального анализа изображений
- 📊 Мониторьте оборудование для оптимизации производительности
- 🔄 Используйте WebSocket для real-time управления
- 🧪 Тестируйте перед развертыванием в production

---

## 📞 Помощь

**Telegram:** @daur.abd  
**GitHub Issues:** https://github.com/daurfinance/Daur-AI-v1/issues

---

**Готово к использованию!** 🎉

