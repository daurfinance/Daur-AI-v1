#!/bin/bash
# Daur-AI Docker Build Script
# Автоматическая сборка и запуск контейнера

set -e

# Цвета для вывода
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Функции для вывода
info() {
    echo -e "${BLUE}ℹ️  $1${NC}"
}

success() {
    echo -e "${GREEN}✅ $1${NC}"
}

warning() {
    echo -e "${YELLOW}⚠️  $1${NC}"
}

error() {
    echo -e "${RED}❌ $1${NC}"
}

# Проверка зависимостей
check_dependencies() {
    info "Проверка зависимостей..."
    
    if ! command -v docker &> /dev/null; then
        error "Docker не установлен. Установите Docker и повторите попытку."
        exit 1
    fi
    
    if ! command -v docker-compose &> /dev/null; then
        warning "docker-compose не найден. Будет использоваться docker compose."
        COMPOSE_CMD="docker compose"
    else
        COMPOSE_CMD="docker-compose"
    fi
    
    success "Зависимости проверены"
}

# Сборка образа
build_image() {
    info "Сборка Docker образа Daur-AI..."
    
    # Проверяем наличие фронтенда
    if [ ! -d "daur-ai-web-panel/dist" ]; then
        info "Сборка фронтенда..."
        cd daur-ai-web-panel
        if [ ! -d "node_modules" ]; then
            npm install
        fi
        npm run build
        cd ..
        success "Фронтенд собран"
    fi
    
    # Сборка Docker образа
    docker build -t daur-ai:latest . || {
        error "Ошибка сборки Docker образа"
        exit 1
    }
    
    success "Docker образ собран успешно"
}

# Запуск контейнера
run_container() {
    info "Запуск Daur-AI контейнера..."
    
    # Остановка существующих контейнеров
    docker stop daur-ai-agent 2>/dev/null || true
    docker rm daur-ai-agent 2>/dev/null || true
    
    # Запуск нового контейнера
    docker run -d \
        --name daur-ai-agent \
        --restart unless-stopped \
        -p 3000:80 \
        -p 8000:8000 \
        -v daur_data:/app/data \
        -v daur_logs:/var/log/daur-ai \
        -e DAUR_AI_SANDBOX=true \
        -e PYTHONUNBUFFERED=1 \
        daur-ai:latest || {
        error "Ошибка запуска контейнера"
        exit 1
    }
    
    success "Контейнер запущен"
}

# Запуск через docker-compose
run_compose() {
    info "Запуск через docker-compose..."
    
    $COMPOSE_CMD down 2>/dev/null || true
    $COMPOSE_CMD up -d || {
        error "Ошибка запуска через docker-compose"
        exit 1
    }
    
    success "Сервисы запущены через docker-compose"
}

# Проверка здоровья
health_check() {
    info "Проверка здоровья сервисов..."
    
    # Ждем запуска
    sleep 10
    
    # Проверка веб-панели
    if curl -f http://localhost:3000 >/dev/null 2>&1; then
        success "Веб-панель доступна: http://localhost:3000"
    else
        warning "Веб-панель недоступна"
    fi
    
    # Проверка API
    if curl -f http://localhost:8000/health >/dev/null 2>&1; then
        success "API доступно: http://localhost:8000"
    else
        warning "API недоступно"
    fi
}

# Показ логов
show_logs() {
    info "Показ логов контейнера..."
    docker logs -f daur-ai-agent
}

# Остановка контейнера
stop_container() {
    info "Остановка Daur-AI контейнера..."
    docker stop daur-ai-agent 2>/dev/null || true
    docker rm daur-ai-agent 2>/dev/null || true
    success "Контейнер остановлен"
}

# Очистка
cleanup() {
    info "Очистка Docker ресурсов..."
    docker system prune -f
    success "Очистка завершена"
}

# Показ статуса
show_status() {
    info "Статус Daur-AI сервисов:"
    echo
    
    # Статус контейнера
    if docker ps | grep -q daur-ai-agent; then
        success "Контейнер daur-ai-agent: ЗАПУЩЕН"
    else
        warning "Контейнер daur-ai-agent: ОСТАНОВЛЕН"
    fi
    
    # Проверка портов
    if netstat -tuln 2>/dev/null | grep -q :3000; then
        success "Порт 3000: ЗАНЯТ (веб-панель)"
    else
        warning "Порт 3000: СВОБОДЕН"
    fi
    
    if netstat -tuln 2>/dev/null | grep -q :8000; then
        success "Порт 8000: ЗАНЯТ (API)"
    else
        warning "Порт 8000: СВОБОДЕН"
    fi
    
    echo
    info "Доступные URL:"
    echo "  🌐 Веб-панель: http://localhost:3000"
    echo "  🔌 API: http://localhost:8000"
    echo "  🏥 Health: http://localhost:8000/health"
}

# Главное меню
show_menu() {
    echo
    echo "🤖 Daur-AI Docker Management"
    echo "=============================="
    echo "1) Сборка образа"
    echo "2) Запуск контейнера"
    echo "3) Запуск через docker-compose"
    echo "4) Остановка"
    echo "5) Показать логи"
    echo "6) Статус"
    echo "7) Проверка здоровья"
    echo "8) Очистка"
    echo "9) Выход"
    echo
}

# Основная логика
main() {
    echo "🚀 Daur-AI Docker Build & Run Script"
    echo "====================================="
    
    check_dependencies
    
    if [ $# -eq 0 ]; then
        # Интерактивный режим
        while true; do
            show_menu
            read -p "Выберите действие (1-9): " choice
            
            case $choice in
                1) build_image ;;
                2) build_image && run_container && health_check ;;
                3) build_image && run_compose && health_check ;;
                4) stop_container ;;
                5) show_logs ;;
                6) show_status ;;
                7) health_check ;;
                8) cleanup ;;
                9) exit 0 ;;
                *) warning "Неверный выбор. Попробуйте снова." ;;
            esac
            
            echo
            read -p "Нажмите Enter для продолжения..."
        done
    else
        # Режим командной строки
        case $1 in
            build) build_image ;;
            run) build_image && run_container && health_check ;;
            compose) build_image && run_compose && health_check ;;
            stop) stop_container ;;
            logs) show_logs ;;
            status) show_status ;;
            health) health_check ;;
            clean) cleanup ;;
            *)
                echo "Использование: $0 [build|run|compose|stop|logs|status|health|clean]"
                echo "Или запустите без параметров для интерактивного режима"
                exit 1
                ;;
        esac
    fi
}

# Обработка сигналов
trap 'echo; warning "Прервано пользователем"; exit 1' INT TERM

# Запуск
main "$@"
