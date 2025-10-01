# 🐳 Daur-AI Docker Deployment

Полное руководство по развертыванию Daur-AI в Docker контейнерах.

## 🚀 Быстрый старт

### Автоматическая установка
```bash
# Клонирование репозитория
git clone https://github.com/daurfinance/Daur-AI-v1.git
cd Daur-AI-v1

# Запуск интерактивного скрипта
./docker-build.sh

# Или одной командой
./docker-build.sh run
```

### Ручная установка
```bash
# Сборка образа
docker build -t daur-ai:latest .

# Запуск контейнера
docker run -d \
  --name daur-ai-agent \
  -p 3000:80 \
  -p 8000:8000 \
  -v daur_data:/app/data \
  daur-ai:latest
```

## 📋 Требования

- **Docker**: версия 20.10+
- **Docker Compose**: версия 2.0+ (опционально)
- **RAM**: минимум 2GB, рекомендуется 4GB+
- **Диск**: минимум 5GB свободного места
- **CPU**: 2+ ядра для оптимальной производительности

## 🏗️ Архитектура контейнера

```
┌─────────────────────────────────────┐
│           Daur-AI Container         │
├─────────────────────────────────────┤
│  ┌─────────────┐  ┌─────────────┐   │
│  │    Nginx    │  │   Gunicorn  │   │
│  │   (Port 80) │  │  (Port 8000)│   │
│  │             │  │             │   │
│  │ Web Panel   │  │ Flask API   │   │
│  └─────────────┘  └─────────────┘   │
│         │                 │         │
│  ┌─────────────────────────────┐    │
│  │      Daur-AI Agent          │    │
│  │   (Python Application)      │    │
│  └─────────────────────────────┘    │
└─────────────────────────────────────┘
```

## 🔧 Конфигурация

### Переменные окружения

| Переменная | Описание | По умолчанию |
|------------|----------|--------------|
| `DAUR_API_HOST` | Хост для API сервера | `0.0.0.0` |
| `DAUR_API_PORT` | Порт для API сервера | `8000` |
| `DAUR_AI_SANDBOX` | Режим песочницы | `true` |
| `PYTHONUNBUFFERED` | Отключение буферизации Python | `1` |

### Порты

| Порт | Сервис | Описание |
|------|--------|----------|
| `80` | Nginx | Веб-панель управления |
| `8000` | Gunicorn | REST API |

### Volumes

| Volume | Путь в контейнере | Описание |
|--------|-------------------|----------|
| `daur_data` | `/app/data` | Пользовательские данные |
| `daur_logs` | `/var/log/daur-ai` | Логи системы |

## 🐙 Docker Compose

### Базовая конфигурация
```bash
# Запуск основного сервиса
docker-compose up -d
```

### С дополнительными сервисами
```bash
# Запуск с Ollama для локальных LLM
docker-compose --profile ollama up -d

# Запуск с кэшированием Redis
docker-compose --profile cache up -d

# Запуск с базой данных PostgreSQL
docker-compose --profile database up -d

# Запуск всех сервисов
docker-compose --profile ollama --profile cache --profile database up -d
```

## 🔍 Мониторинг и отладка

### Проверка статуса
```bash
# Статус контейнеров
docker ps

# Логи основного сервиса
docker logs daur-ai-agent

# Логи в реальном времени
docker logs -f daur-ai-agent

# Проверка здоровья
curl http://localhost:8000/health
```

### Вход в контейнер
```bash
# Интерактивная оболочка
docker exec -it daur-ai-agent /bin/bash

# Выполнение команды
docker exec daur-ai-agent ps aux
```

### Мониторинг ресурсов
```bash
# Использование ресурсов
docker stats daur-ai-agent

# Информация о контейнере
docker inspect daur-ai-agent
```

## 🌐 Доступ к сервисам

После успешного запуска доступны следующие URL:

- **🎛️ Веб-панель**: http://localhost:3000
- **🔌 REST API**: http://localhost:8000
- **🏥 Health Check**: http://localhost:8000/health
- **📊 API Docs**: http://localhost:8000/docs (если включено)

## 🔧 Управление

### Основные команды
```bash
# Остановка
docker stop daur-ai-agent

# Перезапуск
docker restart daur-ai-agent

# Удаление
docker rm daur-ai-agent

# Обновление образа
docker pull daur-ai:latest
docker stop daur-ai-agent
docker rm daur-ai-agent
./docker-build.sh run
```

### Backup и восстановление
```bash
# Создание backup данных
docker run --rm -v daur_data:/data -v $(pwd):/backup alpine tar czf /backup/daur-backup.tar.gz /data

# Восстановление данных
docker run --rm -v daur_data:/data -v $(pwd):/backup alpine tar xzf /backup/daur-backup.tar.gz -C /
```

## 🚨 Troubleshooting

### Частые проблемы

#### Порт уже занят
```bash
# Проверка занятых портов
netstat -tuln | grep -E ':(80|8000)'

# Остановка конфликтующих сервисов
sudo systemctl stop nginx  # если установлен системный nginx
```

#### Недостаточно памяти
```bash
# Проверка использования памяти
docker stats

# Увеличение лимитов
docker run --memory=4g --name daur-ai-agent daur-ai:latest
```

#### Проблемы с правами доступа
```bash
# Проверка владельца volumes
docker exec daur-ai-agent ls -la /app/data

# Исправление прав
docker exec daur-ai-agent chown -R daur:daur /app/data
```

### Логи и диагностика

#### Системные логи
```bash
# Логи supervisor
docker exec daur-ai-agent cat /var/log/daur-ai/supervisord.log

# Логи API
docker exec daur-ai-agent cat /var/log/daur-ai/api.log

# Логи Nginx
docker exec daur-ai-agent cat /var/log/daur-ai/nginx.log
```

#### Проверка сервисов
```bash
# Статус процессов в контейнере
docker exec daur-ai-agent supervisorctl status

# Перезапуск сервиса
docker exec daur-ai-agent supervisorctl restart api
```

## 🔒 Безопасность

### Рекомендации по безопасности

1. **Не используйте root пользователя**
   ```bash
   # Контейнер запускается от пользователя daur
   docker exec daur-ai-agent whoami  # должно вернуть 'daur'
   ```

2. **Ограничьте сетевой доступ**
   ```bash
   # Привязка только к localhost
   docker run -p 127.0.0.1:3000:80 daur-ai:latest
   ```

3. **Используйте secrets для API ключей**
   ```bash
   # Через переменные окружения
   docker run -e OPENAI_API_KEY_FILE=/run/secrets/openai_key daur-ai:latest
   ```

4. **Регулярно обновляйте образы**
   ```bash
   # Проверка обновлений
   docker pull daur-ai:latest
   ```

## 📈 Масштабирование

### Горизонтальное масштабирование
```yaml
# docker-compose.scale.yml
version: '3.8'
services:
  daur-ai:
    # ... базовая конфигурация
    deploy:
      replicas: 3
  
  nginx-lb:
    image: nginx:alpine
    ports:
      - "80:80"
    # Конфигурация load balancer
```

### Вертикальное масштабирование
```bash
# Увеличение ресурсов
docker run \
  --memory=8g \
  --cpus=4 \
  --name daur-ai-agent \
  daur-ai:latest
```

## 🔄 CI/CD Integration

### GitHub Actions пример
```yaml
name: Deploy Daur-AI
on:
  push:
    branches: [main]

jobs:
  deploy:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v3
      - name: Build and Deploy
        run: |
          ./docker-build.sh build
          docker tag daur-ai:latest registry.example.com/daur-ai:latest
          docker push registry.example.com/daur-ai:latest
```

## 📞 Поддержка

- **📧 Email**: support@daur-ai.com
- **🐛 Issues**: https://github.com/daurfinance/Daur-AI-v1/issues
- **📖 Документация**: https://docs.daur-ai.com
- **💬 Discord**: https://discord.gg/daur-ai

## 📄 Лицензия

Этот проект распространяется под лицензией MIT. См. файл [LICENSE](LICENSE) для подробностей.
