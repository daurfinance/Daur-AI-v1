#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
Скрипт для запуска веб-интерфейса
Daur-AI v2.0
"""

import os
import sys
import argparse
from flask import Flask, render_template, request, jsonify

# Добавление корневой директории проекта в путь для импорта
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

app = Flask(__name__, 
            template_folder=os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), 'src/web/templates'),
            static_folder=os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), 'src/web/static'))

@app.route('/')
def index():
    """Главная страница"""
    return render_template('index.html', title="Daur-AI v2.0")

@app.route('/api/status')
def status():
    """API для получения статуса системы"""
    return jsonify({
        'status': 'online',
        'version': '2.0.0',
        'components': {
            'ai_core': 'active',
            'language_model': 'ready',
            'vision': 'ready',
            'telegram': 'inactive'
        }
    })

@app.route('/api/query', methods=['POST'])
def query():
    """API для обработки запросов"""
    data = request.json
    if not data or 'query' not in data:
        return jsonify({'error': 'No query provided'}), 400
    
    # Здесь будет обработка запроса через AI
    query_text = data['query']
    
    # Демонстрационный ответ
    response = {
        'query': query_text,
        'response': f"Это демонстрационный ответ на запрос: {query_text}",
        'timestamp': __import__('datetime').datetime.now().isoformat()
    }
    
    return jsonify(response)

def create_demo_templates():
    """Создает демонстрационные шаблоны, если они не существуют"""
    templates_dir = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), 'src/web/templates')
    static_dir = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), 'src/web/static')
    
    os.makedirs(templates_dir, exist_ok=True)
    os.makedirs(static_dir, exist_ok=True)
    os.makedirs(os.path.join(static_dir, 'css'), exist_ok=True)
    os.makedirs(os.path.join(static_dir, 'js'), exist_ok=True)
    
    # Создание index.html
    index_html = """<!DOCTYPE html>
<html lang="ru">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>{{ title }}</title>
    <link rel="stylesheet" href="{{ url_for('static', filename='css/style.css') }}">
</head>
<body>
    <div class="container">
        <header>
            <h1>Daur-AI v2.0</h1>
            <p>Веб-интерфейс для тестирования на MacBook</p>
        </header>
        
        <main>
            <section class="status-panel">
                <h2>Статус системы</h2>
                <div id="status-display">Загрузка...</div>
            </section>
            
            <section class="query-panel">
                <h2>Отправить запрос</h2>
                <div class="query-form">
                    <textarea id="query-input" placeholder="Введите ваш запрос здесь..."></textarea>
                    <button id="send-query">Отправить</button>
                </div>
            </section>
            
            <section class="response-panel">
                <h2>Ответ системы</h2>
                <div id="response-display">Здесь будет отображаться ответ системы</div>
            </section>
        </main>
        
        <footer>
            <p>&copy; 2025 Daur Finance. Все права защищены.</p>
            <p>Контакты: daur@daur-ai.tech | Telegram: @daur_abd</p>
        </footer>
    </div>
    
    <script src="{{ url_for('static', filename='js/main.js') }}"></script>
</body>
</html>
"""
    
    # Создание style.css
    style_css = """/* Основные стили */
:root {
    --primary-color: #00ffff;
    --secondary-color: #ff00ff;
    --bg-color: #1e1e2e;
    --panel-bg: #2d2d3d;
    --text-color: #ffffff;
}

body {
    font-family: 'Arial', sans-serif;
    background-color: var(--bg-color);
    color: var(--text-color);
    margin: 0;
    padding: 0;
    line-height: 1.6;
}

.container {
    max-width: 1200px;
    margin: 0 auto;
    padding: 20px;
}

/* Заголовок */
header {
    text-align: center;
    margin-bottom: 30px;
    border-bottom: 1px solid var(--primary-color);
    padding-bottom: 20px;
}

header h1 {
    color: var(--primary-color);
    font-size: 2.5rem;
    margin-bottom: 10px;
}

/* Основные секции */
section {
    background-color: var(--panel-bg);
    border-radius: 8px;
    padding: 20px;
    margin-bottom: 20px;
    box-shadow: 0 4px 6px rgba(0, 0, 0, 0.1);
}

section h2 {
    color: var(--primary-color);
    border-bottom: 1px solid var(--secondary-color);
    padding-bottom: 10px;
    margin-top: 0;
}

/* Форма запроса */
.query-form {
    display: flex;
    flex-direction: column;
}

#query-input {
    background-color: rgba(0, 0, 0, 0.2);
    border: 1px solid var(--primary-color);
    border-radius: 4px;
    padding: 10px;
    color: var(--text-color);
    font-size: 1rem;
    min-height: 100px;
    margin-bottom: 10px;
    resize: vertical;
}

#send-query {
    background-color: var(--primary-color);
    color: var(--bg-color);
    border: none;
    border-radius: 4px;
    padding: 10px 20px;
    font-size: 1rem;
    cursor: pointer;
    align-self: flex-end;
    transition: background-color 0.3s;
}

#send-query:hover {
    background-color: var(--secondary-color);
}

/* Панели отображения */
#status-display, #response-display {
    background-color: rgba(0, 0, 0, 0.2);
    border: 1px solid var(--secondary-color);
    border-radius: 4px;
    padding: 15px;
    min-height: 50px;
}

#response-display {
    min-height: 200px;
    white-space: pre-wrap;
}

/* Футер */
footer {
    text-align: center;
    margin-top: 30px;
    padding-top: 20px;
    border-top: 1px solid var(--primary-color);
    font-size: 0.9rem;
    color: rgba(255, 255, 255, 0.7);
}

/* Адаптивность */
@media (max-width: 768px) {
    .container {
        padding: 10px;
    }
    
    header h1 {
        font-size: 2rem;
    }
    
    #send-query {
        width: 100%;
    }
}
"""
    
    # Создание main.js
    main_js = """// Функция для получения статуса системы
function fetchStatus() {
    fetch('/api/status')
        .then(response => response.json())
        .then(data => {
            const statusDisplay = document.getElementById('status-display');
            let statusHtml = `<p><strong>Статус:</strong> ${data.status === 'online' ? 'Онлайн' : 'Офлайн'}</p>`;
            statusHtml += `<p><strong>Версия:</strong> ${data.version}</p>`;
            statusHtml += '<p><strong>Компоненты:</strong></p><ul>';
            
            for (const [component, status] of Object.entries(data.components)) {
                const statusText = status === 'active' ? 'Активен' : 
                                  status === 'ready' ? 'Готов' : 'Неактивен';
                const statusColor = status === 'active' ? '#00ff00' : 
                                   status === 'ready' ? '#00aaff' : '#ff0000';
                
                statusHtml += `<li>${formatComponentName(component)}: <span style="color: ${statusColor}">${statusText}</span></li>`;
            }
            
            statusHtml += '</ul>';
            statusDisplay.innerHTML = statusHtml;
        })
        .catch(error => {
            console.error('Ошибка при получении статуса:', error);
            document.getElementById('status-display').innerHTML = 
                '<p style="color: #ff0000">Ошибка при получении статуса системы</p>';
        });
}

// Форматирование названий компонентов
function formatComponentName(name) {
    const names = {
        'ai_core': 'Ядро ИИ',
        'language_model': 'Языковая модель',
        'vision': 'Компьютерное зрение',
        'telegram': 'Telegram-бот'
    };
    
    return names[name] || name;
}

// Обработка отправки запроса
document.getElementById('send-query').addEventListener('click', function() {
    const queryInput = document.getElementById('query-input');
    const query = queryInput.value.trim();
    
    if (!query) {
        alert('Пожалуйста, введите запрос');
        return;
    }
    
    const responseDisplay = document.getElementById('response-display');
    responseDisplay.innerHTML = 'Обработка запроса...';
    
    fetch('/api/query', {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json'
        },
        body: JSON.stringify({ query: query })
    })
    .then(response => response.json())
    .then(data => {
        responseDisplay.innerHTML = `<p><strong>Запрос:</strong> ${data.query}</p>
                                    <p><strong>Ответ:</strong> ${data.response}</p>
                                    <p><strong>Время:</strong> ${new Date(data.timestamp).toLocaleString()}</p>`;
    })
    .catch(error => {
        console.error('Ошибка при отправке запроса:', error);
        responseDisplay.innerHTML = '<p style="color: #ff0000">Ошибка при обработке запроса</p>';
    });
});

// Загрузка статуса при загрузке страницы
document.addEventListener('DOMContentLoaded', fetchStatus);

// Обновление статуса каждые 30 секунд
setInterval(fetchStatus, 30000);
"""
    
    # Запись файлов
    with open(os.path.join(templates_dir, 'index.html'), 'w') as f:
        f.write(index_html)
    
    with open(os.path.join(static_dir, 'css', 'style.css'), 'w') as f:
        f.write(style_css)
    
    with open(os.path.join(static_dir, 'js', 'main.js'), 'w') as f:
        f.write(main_js)

def main():
    """Основная функция скрипта"""
    parser = argparse.ArgumentParser(description="Запуск веб-интерфейса Daur-AI v2.0")
    parser.add_argument("--host", default="127.0.0.1", help="Хост для запуска сервера (по умолчанию: 127.0.0.1)")
    parser.add_argument("--port", type=int, default=8000, help="Порт для запуска сервера (по умолчанию: 8000)")
    parser.add_argument("--debug", action="store_true", help="Запуск в режиме отладки")
    args = parser.parse_args()
    
    print("🌐 Запуск веб-интерфейса Daur-AI v2.0")
    print(f"🔗 Адрес: http://{args.host}:{args.port}")
    
    # Создание демонстрационных шаблонов
    create_demo_templates()
    
    # Запуск сервера
    app.run(host=args.host, port=args.port, debug=args.debug)

if __name__ == "__main__":
    main()
