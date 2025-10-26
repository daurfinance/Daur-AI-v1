# Daur-AI v2.0 - macOS Application

Готовый Xcode проект для macOS приложения Daur-AI.

## 📋 Структура проекта

```
Daur-AI.xcodeproj/
├── Daur-AI/
│   ├── AppDelegate.swift           # Главный делегат приложения
│   ├── MainViewController.swift     # Главный контроллер с 4 вкладками
│   ├── Info.plist                  # Конфигурация приложения
│   ├── Services/
│   │   └── APIService.swift        # Сервис для работы с API
│   └── ViewControllers/
│       ├── DashboardViewController.swift    # Мониторинг системы
│       ├── HardwareViewController.swift     # Информация о железе
│       ├── VisionViewController.swift       # Компьютерное зрение
│       └── SettingsViewController.swift     # Настройки подключения
```

## 🚀 Как использовать

### Шаг 1: Откройте проект в Xcode

```bash
# Откройте Finder и перейдите к файлу
open Daur-AI.xcodeproj
```

Или просто дважды нажмите на файл `Daur-AI.xcodeproj`

### Шаг 2: Убедитесь, что Docker контейнер запущен

На вашем MacBook должен быть запущен Docker контейнер с API сервером:

```bash
docker run -p 8000:8000 daur-ai-api:latest
```

### Шаг 3: Соберите и запустите приложение

В Xcode:
1. Нажмите **Product** → **Build** (Cmd+B)
2. Нажмите **Product** → **Run** (Cmd+R)

Или просто нажмите кнопку **Play** в верхней части Xcode.

## 📱 Функции приложения

### Dashboard (Панель управления)
- Мониторинг CPU в реальном времени
- Мониторинг памяти (RAM)
- Мониторинг диска (Storage)
- Обновление каждые 2 секунды

### Hardware (Аппаратура)
- Информация о системе
- Характеристики оборудования

### Vision (Компьютерное зрение)
- OCR (распознавание текста)
- Загрузка изображений для анализа

### Settings (Настройки)
- Подключение к API серверу
- Аутентификация (логин/пароль)
- Сохранение параметров подключения

## 🔌 Подключение к API

Приложение автоматически подключается к API серверу на:
- **Host**: localhost
- **Port**: 8000

Вы можете изменить эти параметры в вкладке Settings.

## 📝 Требования

- macOS 10.15 или выше
- Xcode 15.0 или выше
- Swift 5.0 или выше
- Docker с запущенным контейнером Daur-AI API

## 🛠️ Разработка

Все файлы написаны на Swift с использованием Cocoa фреймворка для macOS.

### Основные компоненты:

1. **AppDelegate** - управление жизненным циклом приложения
2. **MainViewController** - главный контроллер с табами
3. **APIService** - сервис для работы с REST API
4. **ViewControllers** - контроллеры для каждой вкладки

## 📦 Сборка для распространения

Для создания готового .app файла:

1. В Xcode выберите **Product** → **Archive**
2. Нажмите **Distribute App**
3. Выберите **Direct Distribution**
4. Сохраните .app файл

## 🐛 Решение проблем

### Приложение не подключается к API
- Убедитесь, что Docker контейнер запущен
- Проверьте, что порт 8000 открыт
- Проверьте настройки в вкладке Settings

### Ошибки при сборке
- Очистите build folder: **Product** → **Clean Build Folder** (Cmd+Shift+K)
- Пересоберите проект: **Product** → **Build** (Cmd+B)

## 📄 Лицензия

Copyright © 2025 Daur Finance. All rights reserved.
