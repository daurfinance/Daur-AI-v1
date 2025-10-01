# Daur-AI Docker Container
FROM python:3.11-slim

# Метаданные
LABEL maintainer="Daur-AI Team"
LABEL version="1.1"
LABEL description="Daur-AI - Автономный ИИ-агент с веб-панелью управления"

# Установка системных зависимостей
RUN apt-get update && apt-get install -y \
    build-essential \
    curl \
    git \
    wget \
    nodejs \
    npm \
    nginx \
    supervisor \
    && rm -rf /var/lib/apt/lists/*

# Создание пользователя
RUN useradd -m -s /bin/bash daur && \
    mkdir -p /app /var/log/daur-ai && \
    chown -R daur:daur /app /var/log/daur-ai

WORKDIR /app

# Копирование и установка Python зависимостей
COPY requirements.txt ./
RUN pip install --no-cache-dir -r requirements.txt
RUN pip install --no-cache-dir flask flask-cors psutil gunicorn

# Копирование исходного кода
COPY src/ ./src/
COPY config/ ./config/
COPY *.py ./
COPY *.md ./

# Сборка фронтенда
COPY daur-ai-web-panel/ ./frontend/
RUN cd frontend && npm install && npm run build

# Nginx конфигурация
RUN echo 'server { \
    listen 80; \
    location / { \
        root /app/frontend/dist; \
        try_files $uri /index.html; \
    } \
    location /api/ { \
        proxy_pass http://127.0.0.1:8000; \
        proxy_set_header Host $host; \
    } \
}' > /etc/nginx/sites-available/default

# Supervisor конфигурация
RUN echo '[supervisord] \
nodaemon=true \n\
[program:api] \
command=gunicorn --bind 127.0.0.1:8000 src.web.api_server:app \
directory=/app \
user=daur \n\
[program:nginx] \
command=nginx -g "daemon off;" \
' > /etc/supervisor/conf.d/daur-ai.conf

# Установка прав
RUN chown -R daur:daur /app

EXPOSE 80 8000

CMD ["/usr/bin/supervisord", "-c", "/etc/supervisor/conf.d/daur-ai.conf"]
