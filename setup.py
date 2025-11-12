#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
Daur-AI v2.0 Setup Script
Install and configure Daur-AI package
"""

from setuptools import setup, find_packages
import os
import sys

def get_version():
    try:
        with open('VERSION', 'r') as f:
            return f.read().strip()
    except FileNotFoundError:
        return '2.0.0'

def get_long_description():
    try:
        with open('README.md', 'r', encoding='utf-8') as f:
            return f.read()
    except FileNotFoundError:
        return "Daur-AI: Revolutionary Autonomous AI Agent"

def get_requirements():
    requirements = []
    with open('requirements.txt', 'r') as f:
        for line in f:
            line = line.strip()
            if line and not line.startswith('#'):
                requirements.append(line)
    return requirements

setup(
    name='daur-ai',
    version=get_version(),
    description='Revolutionary Autonomous AI Agent with Computer Vision and System Control',
    long_description=get_long_description(),
    long_description_content_type='text/markdown',
    author='Daur Finance',
    author_email='info@daurfinance.com',
    url='https://github.com/daurfinance/Daur-AI-v1',
    license='MIT',
    
    packages=find_packages(include=['src', 'src.*']),
    
    python_requires='>=3.8',
    install_requires=get_requirements(),
    
    extras_require={
        'dev': [
            'pytest>=6.2.5',
            'pytest-asyncio>=0.21.0',
            'pytest-cov>=4.0.0',
            'black>=21.5b2',
            'flake8>=3.9.2',
            'mypy>=0.812',
        ],
        'test': [
            'pytest>=6.2.5',
            'pytest-asyncio>=0.21.0',
            'pytest-cov>=4.0.0',
        ],
    },
    
    entry_points={
        'console_scripts': [
            'daur-ai=src.main:main',
            'daur-demo=run_demo:main',
        ],
    },
    
    classifiers=[
        'Development Status :: 4 - Beta',
        'Intended Audience :: Developers',
        'License :: OSI Approved :: MIT License',
        'Natural Language :: English',
        'Natural Language :: Russian',
        'Programming Language :: Python :: 3',
        'Programming Language :: Python :: 3.8',
        'Programming Language :: Python :: 3.9',
        'Programming Language :: Python :: 3.10',
        'Programming Language :: Python :: 3.11',
        'Programming Language :: Python :: 3.12',
        'Operating System :: OS Independent',
        'Topic :: Software Development :: Libraries :: Python Modules',
        'Topic :: Scientific/Engineering :: Artificial Intelligence',
    ],
    
    keywords=[
        'ai',
        'agent',
        'automation',
        'computer-vision',
        'mouse-control',
        'keyboard-control',
        'system-automation',
        'rpa',
        'robotic-process-automation',
    ],
)
