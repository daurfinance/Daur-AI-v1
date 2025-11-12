# Daur-AI v2.0 на MacBook - Быстрая Справка

## ⚡ 5-Минутный Старт

### Вариант 1: Самый Простой (Docker)

```bash
# 1. Откройте Terminal (Cmd + Space, введите "Terminal")

# 2. Установите Homebrew (если не установлен)
/bin/bash -c "$(curl -fsSL https://raw.githubusercontent.com/Homebrew/install/HEAD/install.sh)"

# 3. Установите Docker
brew install --cask docker

# 4. Откройте Docker из Applications

# 5. Клонируйте проект
cd ~/Documents
git clone https://github.com/daurfinance/Daur-AI-v1.git
cd Daur-AI-v1

# 6. Запустите
docker run -p 5000:5000 daur-ai:latest

# 7. Откройте браузер
# http://localhost:5000/api/v2/health
```

---

### Вариант 2: С Python (Для Разработчиков)

```bash
# 1. Откройте Terminal

# 2. Установите Homebrew
/bin/bash -c "$(curl -fsSL https://raw.githubusercontent.com/Homebrew/install/HEAD/install.sh)"

# 3. Установите Python
brew install python@3.11

# 4. Клонируйте проект
cd ~/Documents
git clone https://github.com/daurfinance/Daur-AI-v1.git
cd Daur-AI-v1

# 5. Создайте виртуальное окружение
python3.11 -m venv venv
source venv/bin/activate

# 6. Установите зависимости
pip install -r requirements.txt

# 7. Запустите
python3 src/web/real_api_server.py

# 8. Откройте браузер
# http://localhost:5000/api/v2/health
```

---

### Вариант 3: Полный Стек (Production)

```bash
# 1. Установите Docker (см. выше)

# 2. Клонируйте проект
cd ~/Documents
git clone https://github.com/daurfinance/Daur-AI-v1.git
cd Daur-AI-v1

# 3. Запустите полный стек
docker-compose up -d

# 4. Проверьте статус
docker-compose ps

# 5. Доступ к сервисам:
# API: http://localhost:5000
# Grafana: http://localhost:3000 (admin/admin)
# Prometheus: http://localhost:9090
```

---

## 🔍 Проверка Работы

```bash
# Проверить здоровье API
curl http://localhost:5000/api/v2/health

# Получить статус системы
curl http://localhost:5000/api/v2/status

# Получить информацию о CPU
curl http://localhost:5000/api/v2/hardware/cpu
```

---

## 🛑 Остановка

```bash
# Если запущен API напрямую
Ctrl + C

# Если Docker контейнер
docker stop daur-ai

# Если docker-compose
docker-compose down
```

---

## 📋 Чек-Лист Установки

- [ ] Homebrew установлен: `brew --version`
- [ ] Python 3.11 установлен: `python3.11 --version`
- [ ] Git установлен: `git --version`
- [ ] Docker установлен: `docker --version`
- [ ] Проект клонирован: `ls ~/Documents/Daur-AI-v1`
- [ ] Зависимости установлены: `pip list | grep flask`
- [ ] API запущен: `curl http://localhost:5000/api/v2/health`

---

## 🆘 Частые Ошибки

| Ошибка | Решение |
|--------|---------|
| "Command not found: brew" | Переустановите Homebrew |
| "Port 5000 already in use" | `lsof -i :5000` и `kill -9 <PID>` |
| "ModuleNotFoundError" | `source venv/bin/activate` |
| "Docker command not found" | Закройте Terminal и откройте заново |
| "Permission denied" | Используйте `sudo` |

---

## 📞 Поддержка

1. Прочитайте `MACOS_INSTALLATION_GUIDE.md` (полное руководство)
2. Проверьте логи: `docker logs -f daur-ai`
3. Проверьте здоровье: `curl http://localhost:5000/api/v2/health`

---

## 📚 Полезные Ссылки

- **Полное руководство:** `MACOS_INSTALLATION_GUIDE.md`
- **Docker руководство:** `DOCKER_QUICK_START.md`
- **API документация:** `DAUR_AI_V2_PRODUCTION_GUIDE.md`

---

*Daur-AI v2.0 - Production Ready*

