#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
Скрипт для загрузки встроенной языковой модели
Daur-AI v2.0
"""

import os
import sys
import argparse
import requests
from tqdm import tqdm
import hashlib

# Добавление корневой директории проекта в путь для импорта
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

# Конфигурация моделей
MODELS = {
    "small": {
        "name": "llama-2-7b-chat.Q4_K_M.gguf",
        "url": "https://huggingface.co/TheBloke/Llama-2-7B-Chat-GGUF/resolve/main/llama-2-7b-chat.Q4_K_M.gguf",
        "size": 4212859520,  # ~4.2GB
        "md5": "e0b99920df1b6b3fcc2bca4ed67f718b"
    },
    "medium": {
        "name": "llama-2-13b-chat.Q4_K_M.gguf",
        "url": "https://huggingface.co/TheBloke/Llama-2-13B-Chat-GGUF/resolve/main/llama-2-13b-chat.Q4_K_M.gguf",
        "size": 8136425344,  # ~8.1GB
        "md5": "3b8547c10b1ae0e35943e5e3b1d6c2c1"
    },
    "tiny": {
        "name": "tinyllama-1.1b-chat-v1.0.Q4_K_M.gguf",
        "url": "https://huggingface.co/TheBloke/TinyLlama-1.1B-Chat-v1.0-GGUF/resolve/main/tinyllama-1.1b-chat-v1.0.Q4_K_M.gguf",
        "size": 684358656,  # ~684MB
        "md5": "64d6d3e5e3f5b53016b4e9ece2d93268"
    }
}

def calculate_md5(file_path):
    """Вычисляет MD5-хеш файла"""
    hash_md5 = hashlib.md5()
    with open(file_path, "rb") as f:
        for chunk in iter(lambda: f.read(4096), b""):
            hash_md5.update(chunk)
    return hash_md5.hexdigest()

def download_file(url, destination, expected_size=None, expected_md5=None):
    """Загружает файл с отображением прогресса"""
    response = requests.get(url, stream=True)
    total_size = int(response.headers.get('content-length', 0))
    
    if expected_size and total_size != expected_size:
        print(f"⚠️ Предупреждение: Размер файла на сервере ({total_size} байт) отличается от ожидаемого ({expected_size} байт)")
    
    block_size = 1024  # 1 Кбайт
    progress_bar = tqdm(total=total_size, unit='iB', unit_scale=True, desc="Загрузка")
    
    with open(destination, 'wb') as file:
        for data in response.iter_content(block_size):
            progress_bar.update(len(data))
            file.write(data)
    
    progress_bar.close()
    
    if total_size != 0 and progress_bar.n != total_size:
        print("❌ Ошибка: Не удалось загрузить файл полностью")
        return False
    
    if expected_md5:
        print("🔍 Проверка целостности файла...")
        file_md5 = calculate_md5(destination)
        if file_md5 != expected_md5:
            print(f"❌ Ошибка: MD5-хеш файла не совпадает с ожидаемым")
            print(f"   Ожидаемый: {expected_md5}")
            print(f"   Полученный: {file_md5}")
            return False
        print("✅ MD5-хеш файла совпадает с ожидаемым")
    
    return True

def main():
    """Основная функция скрипта"""
    parser = argparse.ArgumentParser(description="Загрузчик встроенной языковой модели для Daur-AI v2.0")
    parser.add_argument("--model", choices=["tiny", "small", "medium"], default="tiny",
                        help="Размер модели для загрузки (по умолчанию: tiny)")
    parser.add_argument("--force", action="store_true", help="Принудительно загрузить модель, даже если она уже существует")
    parser.add_argument("--output-dir", default="models", help="Директория для сохранения модели (по умолчанию: models)")
    args = parser.parse_args()
    
    # Создание директории для моделей, если она не существует
    models_dir = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), args.output_dir)
    os.makedirs(models_dir, exist_ok=True)
    
    model_info = MODELS[args.model]
    model_path = os.path.join(models_dir, model_info["name"])
    
    print(f"🤖 Загрузка модели: {model_info['name']}")
    print(f"📂 Путь сохранения: {model_path}")
    print(f"📊 Размер модели: {model_info['size'] / (1024*1024*1024):.2f} ГБ")
    
    # Проверка, существует ли файл модели
    if os.path.exists(model_path) and not args.force:
        print(f"⚠️ Файл модели уже существует: {model_path}")
        
        # Проверка размера файла
        file_size = os.path.getsize(model_path)
        if file_size != model_info["size"]:
            print(f"⚠️ Размер существующего файла ({file_size} байт) отличается от ожидаемого ({model_info['size']} байт)")
            overwrite = input("Хотите загрузить модель заново? (y/n): ").lower() == 'y'
            if not overwrite:
                print("❌ Загрузка отменена")
                return
        else:
            print("✅ Размер файла соответствует ожидаемому")
            
            # Проверка MD5-хеша
            print("🔍 Проверка целостности файла...")
            file_md5 = calculate_md5(model_path)
            if file_md5 == model_info["md5"]:
                print("✅ MD5-хеш файла совпадает с ожидаемым")
                print("✅ Модель уже загружена и готова к использованию")
                return
            else:
                print(f"⚠️ MD5-хеш файла не совпадает с ожидаемым")
                print(f"   Ожидаемый: {model_info['md5']}")
                print(f"   Полученный: {file_md5}")
                overwrite = input("Хотите загрузить модель заново? (y/n): ").lower() == 'y'
                if not overwrite:
                    print("❌ Загрузка отменена")
                    return
    
    # Загрузка модели
    print(f"⏳ Начинаем загрузку модели с {model_info['url']}")
    success = download_file(
        model_info["url"], 
        model_path, 
        expected_size=model_info["size"], 
        expected_md5=model_info["md5"]
    )
    
    if success:
        print(f"✅ Модель успешно загружена и сохранена в {model_path}")
        print("✅ Модель готова к использованию")
        
        # Создание файла конфигурации
        config_path = os.path.join(models_dir, "config.txt")
        with open(config_path, "w") as f:
            f.write(f"model_path={model_path}\n")
            f.write(f"model_type={args.model}\n")
            f.write(f"download_date={__import__('datetime').datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n")
        
        print(f"✅ Файл конфигурации создан: {config_path}")
    else:
        print("❌ Не удалось загрузить модель")
        if os.path.exists(model_path):
            os.remove(model_path)
            print(f"🗑️ Удален неполный файл: {model_path}")

if __name__ == "__main__":
    main()
