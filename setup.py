#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
Daur-AI: Установочный скрипт
Скрипт для установки и сборки пакета Daur-AI

Версия: 1.0
Дата: 01.10.2025
"""

from setuptools import setup, find_packages
import os
import sys

# Чтение версии из файла
def get_version():
    """Получение версии из файла VERSION или config"""
    try:
        with open('VERSION', 'r') as f:
            return f.read().strip()
    except FileNotFoundError:
        return '1.0.0'

# Чтение описания из README
def get_long_description():
    """Получение длинного описания из README.md"""
    try:
        with open('README.md', 'r', encoding='utf-8') as f:
            return f.read()
    except FileNotFoundError:
        return "Универсальный автономный ИИ-агент для локального компьютера"

# Чтение зависимостей из requirements.txt
def get_requirements():
    """Получение списка зависимостей"""
    requirements = []
    try:
        with open('requirements.txt', 'r') as f:
            for line in f:
                line = line.strip()
                if line and not line.startswith('#'):
                    # Обработка условных зависимостей
                    if ';' in line:
                        package, condition = line.split(';', 1)
                        # Упрощенная обработка условий
                        if 'platform_system' in condition:
                            if ('Windows' in condition and sys.platform == 'win32') or \
                               ('Darwin' in condition and sys.platform == 'darwin') or \
                               ('Linux' in condition and sys.platform.startswith('linux')):
                                requirements.append(package.strip())
                        else:
                            requirements.append(package.strip())
                    else:
                        requirements.append(line)
    except FileNotFoundError:
        # Минимальные зависимости если файл не найден
        requirements = [
            'psutil>=5.8.0',
            'pillow>=8.0.0',
        ]
    
    return requirements

# Дополнительные зависимости для разработки
dev_requirements = [
    'pytest>=6.2.5',
    'black>=21.5b2',
    'flake8>=3.9.2',
    'mypy>=0.812',
]

# Дополнительные зависимости для AI
ai_requirements = [
    'torch>=1.10.0',
    'transformers>=4.18.0',
    'llama-cpp-python>=0.1.0',
]

# Дополнительные зависимости для GUI
gui_requirements = [
    'pyautogui>=0.9.53',
    'pynput>=1.7.0',
]

setup(
    name='daur-ai',
    version=get_version(),
    description='Универсальный автономный ИИ-агент для локального компьютера',
    long_description=get_long_description(),
    long_description_content_type='text/markdown',
    author='Daur Finance Team',
    author_email='info@daurfinance.com',
    url='https://github.com/daurfinance/Daur-AI-v1',
    
    packages=find_packages(),
    include_package_data=True,
    
    # Классификаторы
    classifiers=[
        'Development Status :: 4 - Beta',
        'Intended Audience :: Developers',
        'Intended Audience :: End Users/Desktop',
        'License :: Other/Proprietary License',
        'Operating System :: OS Independent',
        'Programming Language :: Python :: 3',
        'Programming Language :: Python :: 3.8',
        'Programming Language :: Python :: 3.9',
        'Programming Language :: Python :: 3.10',
        'Programming Language :: Python :: 3.11',
        'Topic :: Software Development :: Libraries :: Python Modules',
        'Topic :: System :: Systems Administration',
        'Topic :: Office/Business :: Office Suites',
    ],
    
    # Требования к Python
    python_requires='>=3.8',
    
    # Зависимости
    install_requires=get_requirements(),
    
    # Дополнительные зависимости
    extras_require={
        'dev': dev_requirements,
        'ai': ai_requirements,
        'gui': gui_requirements,
        'full': dev_requirements + ai_requirements + gui_requirements,
    },
    
    # Точки входа
    entry_points={
        'console_scripts': [
            'daur-ai=src.main:main',
            'daur-ai-console=src.main:main',
        ],
    },
    
    # Данные пакета
    package_data={
        'src': [
            'config/*.json',
            'docs/*.md',
            'install/*.sh',
        ],
    },
    
    # Дополнительные файлы
    data_files=[
        ('share/daur-ai/config', ['config/default_config.json']),
        ('share/daur-ai/docs', ['README.md', 'CHANGELOG.md']),
    ],
    
    # Ключевые слова
    keywords='ai agent automation desktop assistant',
    
    # Проект URLs
    project_urls={
        'Bug Reports': 'https://github.com/daurfinance/Daur-AI-v1/issues',
        'Source': 'https://github.com/daurfinance/Daur-AI-v1',
        'Documentation': 'https://github.com/daurfinance/Daur-AI-v1/docs',
    },
)
