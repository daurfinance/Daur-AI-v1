# Dockerfile для Daur-AI
# Версия: 1.0
# Дата: 09.05.2025

# Используем Python 3.10 в качестве базового образа
FROM python:3.10-slim

# Метаданные о контейнере
LABEL maintainer="Daur-AI Team <support@daur-ai.com>"
LABEL version="1.0"
LABEL description="Универсальный автономный ИИ-агент"

# Установка переменных окружения
ENV PYTHONFAULTHANDLER=1 \
    PYTHONUNBUFFERED=1 \
    PYTHONHASHSEED=random \
    PIP_NO_CACHE_DIR=1 \
    PIP_DISABLE_PIP_VERSION_CHECK=1 \
    DEBIAN_FRONTEND=noninteractive

# Установка системных зависимостей
RUN apt-get update && apt-get install -y --no-install-recommends \
    build-essential \
    curl \
    git \
    libx11-dev \
    libxtst-dev \
    libpng-dev \
    libjpeg-dev \
    libxcb1-dev \
    && apt-get clean \
    && rm -rf /var/lib/apt/lists/*

# Создание пользователя без привилегий root
RUN groupadd -g 1000 daurai && \
    useradd -u 1000 -g daurai -ms /bin/bash daurai

# Создание директорий приложения
RUN mkdir -p /app/models /app/logs /app/config
WORKDIR /app

# Копирование requirements.txt и установка зависимостей
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Копирование файлов проекта
COPY --chown=daurai:daurai src/ /app/src/
COPY --chown=daurai:daurai config/ /app/config/
COPY --chown=daurai:daurai LICENSE README.md ./

# Создание директорий для пользовательских данных
RUN mkdir -p /data/logs /data/models /data/config && \
    chown -R daurai:daurai /data

# Настройка переменных окружения для работы в контейнере
ENV DAUR_AI_CONFIG_PATH=/data/config/config.json \
    DAUR_AI_LOG_PATH=/data/logs/ \
    DAUR_AI_MODEL_PATH=/data/models/ \
    DAUR_AI_SANDBOX=true

# Настройка объема для персистентности данных
VOLUME ["/data"]

# Переключение на пользователя без привилегий
USER daurai

# Запуск приложения в консольном режиме
CMD ["python", "src/main.py", "--ui", "console"]

# Информация о порте
EXPOSE 8080

# Документация
# Использование:
#   docker build -t daur-ai:latest .
#   docker run -it --name daur-ai-agent \
#     -v /path/to/local/data:/data \
#     --network host \
#     daur-ai:latest

# Запуск с графическим интерфейсом (требуется настройка X11):
#   docker run -it --name daur-ai-gui \
#     -e DISPLAY=$DISPLAY \
#     -v /tmp/.X11-unix:/tmp/.X11-unix \
#     -v /path/to/local/data:/data \
#     daur-ai:latest python src/main.py --ui gui
