# Daur-AI v2.0 macOS - Полное руководство установки

## 📋 Содержание

1. [Требования](#требования)
2. [Быстрый старт](#быстрый-старт)
3. [Подробная установка](#подробная-установка)
4. [Запуск приложения](#запуск-приложения)
5. [Решение проблем](#решение-проблем)

---

## Требования

### Минимальные требования:
- **macOS**: 10.15 или выше
- **Xcode**: 15.0 или выше (скачайте из App Store)
- **Swift**: 5.0 или выше (входит в Xcode)
- **Docker**: для запуска API сервера (опционально)

### Проверка версий:

```bash
# Проверьте версию macOS
sw_vers

# Проверьте версию Xcode
xcode-select --version

# Проверьте версию Swift
swift --version
```

---

## Быстрый старт

### Шаг 1: Скачайте проект с GitHub

```bash
# Клонируйте репозиторий
git clone https://github.com/daurfinance/Daur-AI-v1.git
cd Daur-AI-v1/macos-app-xcode
```

### Шаг 2: Откройте проект в Xcode

```bash
# Откройте проект
open Daur-AI.xcodeproj
```

Или просто дважды нажмите на файл `Daur-AI.xcodeproj` в Finder.

### Шаг 3: Запустите Docker контейнер (если нужен API)

```bash
# Убедитесь, что Docker запущен
docker run -p 8000:8000 daur-ai-api:latest
```

### Шаг 4: Соберите и запустите приложение

В Xcode:
1. Нажмите **Product** → **Build** (Cmd+B)
2. Нажмите **Product** → **Run** (Cmd+R)

Или нажмите кнопку **Play** ▶️ в верхней части Xcode.

---

## Подробная установка

### 1. Установка Xcode (если не установлен)

```bash
# Скачайте Xcode из App Store или выполните:
xcode-select --install

# Установите дополнительные компоненты
sudo xcode-select --switch /Applications/Xcode.app/Contents/Developer
```

### 2. Клонирование репозитория

```bash
# Перейдите в папку, где хотите сохранить проект
cd ~/Documents

# Клонируйте репозиторий
git clone https://github.com/daurfinance/Daur-AI-v1.git

# Перейдите в папку проекта
cd Daur-AI-v1/macos-app-xcode
```

### 3. Структура проекта

```
Daur-AI.xcodeproj/
├── Daur-AI/
│   ├── AppDelegate.swift              # Главный делегат приложения
│   ├── MainViewController.swift        # Главный контроллер с вкладками
│   ├── Info.plist                     # Конфигурация приложения
│   ├── Services/
│   │   └── APIService.swift           # Сервис для работы с API
│   └── ViewControllers/
│       ├── DashboardViewController.swift    # Мониторинг системы
│       ├── HardwareViewController.swift     # Информация о железе
│       ├── VisionViewController.swift       # Компьютерное зрение
│       └── SettingsViewController.swift     # Настройки подключения
└── README.md                          # Документация
```

### 4. Подготовка Docker контейнера (опционально)

Если вы хотите использовать API сервер:

```bash
# Перейдите в корень репозитория
cd ~/Documents/Daur-AI-v1

# Соберите Docker образ
docker build -t daur-ai-api:latest .

# Запустите контейнер
docker run -p 8000:8000 daur-ai-api:latest
```

Или используйте готовый образ:

```bash
docker run -p 8000:8000 daurfinance/daur-ai-api:latest
```

---

## Запуск приложения

### Способ 1: Из Xcode (рекомендуется для разработки)

```bash
# Откройте проект
open Daur-AI.xcodeproj

# В Xcode:
# 1. Выберите target "Daur-AI"
# 2. Выберите "My Mac" в качестве destination
# 3. Нажмите Product → Run (Cmd+R)
```

### Способ 2: Из командной строки

```bash
# Соберите проект
xcodebuild -scheme Daur-AI -configuration Debug

# Запустите приложение
open ./build/Debug/Daur-AI.app
```

### Способ 3: Создание готового .app файла

```bash
# Соберите для Release
xcodebuild -scheme Daur-AI -configuration Release

# Найдите .app файл в:
# ~/Library/Developer/Xcode/DerivedData/Daur-AI-xxx/Build/Products/Release/
```

---

## Использование приложения

### Dashboard (Панель управления)
- **CPU Usage**: Процент использования процессора
- **Memory Usage**: Использование оперативной памяти
- **Disk Usage**: Использование дискового пространства
- Обновление каждые 2 секунды

### Hardware (Аппаратура)
- Информация о системе
- Характеристики оборудования
- Загружается при открытии вкладки

### Vision (Компьютерное зрение)
- Загрузка изображений
- OCR (распознавание текста)
- Face Detection (распознавание лиц)
- Barcode Recognition (распознавание штрих-кодов)

### Settings (Настройки)
- **API Host**: адрес сервера (по умолчанию: localhost)
- **API Port**: порт сервера (по умолчанию: 8000)
- **Username**: имя пользователя для входа
- **Password**: пароль для входа
- Кнопка **Connect**: подключение к API
- Кнопка **Login**: вход в систему

---

## Решение проблем

### Проблема: "Cannot find 'APIService' in scope"

**Решение:**
1. Убедитесь, что файл `APIService.swift` находится в папке `Services`
2. В Xcode: **Product** → **Clean Build Folder** (Cmd+Shift+K)
3. Пересоберите проект: **Product** → **Build** (Cmd+B)

### Проблема: "Failed to connect to API"

**Решение:**
1. Убедитесь, что Docker контейнер запущен:
   ```bash
   docker ps
   ```
2. Проверьте, что порт 8000 открыт:
   ```bash
   lsof -i :8000
   ```
3. Попробуйте подключиться вручную в вкладке Settings

### Проблема: "Xcode cannot find the project"

**Решение:**
1. Убедитесь, что вы находитесь в правильной папке:
   ```bash
   ls -la Daur-AI.xcodeproj
   ```
2. Попробуйте открыть проект заново:
   ```bash
   open Daur-AI.xcodeproj
   ```

### Проблема: "Build failed with Swift compilation error"

**Решение:**
1. Очистите build folder:
   ```bash
   rm -rf ~/Library/Developer/Xcode/DerivedData/
   ```
2. Пересоберите проект:
   ```bash
   xcodebuild clean build
   ```

### Проблема: "Permission denied" при запуске Docker

**Решение:**
```bash
# Добавьте себя в группу docker
sudo usermod -aG docker $USER

# Перезагрузитесь или выполните:
newgrp docker
```

---

## Дополнительная информация

### Системные требования для API

Если вы хотите запустить API сервер на своем MacBook:

```bash
# Требования:
# - Python 3.8+
# - Flask
# - psutil
# - PyJWT
# - bcrypt

# Установка зависимостей:
pip install -r requirements.txt

# Запуск API сервера:
python src/web/api_server.py
```

### Контакты и поддержка

- **GitHub**: https://github.com/daurfinance/Daur-AI-v1
- **Email**: support@daur.finance
- **Documentation**: https://daur.finance/docs

---

## Лицензия

Copyright © 2025 Daur Finance. All rights reserved.

---

**Версия**: 2.0
**Дата**: October 26, 2025
**Автор**: Daur Finance Team
