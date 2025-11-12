#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
Daur-AI: Модуль обучения AI-моделей
Реализует функциональность для дообучения моделей ИИ на основе
логов действий пользователя

Версия: 1.0
Дата: 09.05.2025
"""

import os
import json
import time
import logging
import tempfile
import datetime
from typing import Dict, List, Any, Optional, Union, Tuple
from pathlib import Path

# Попытка импорта библиотек для обучения моделей
try:
    import torch
    from torch.utils.data import Dataset, DataLoader
    HAS_TORCH = True
except ImportError:
    HAS_TORCH = False
    
try:
    from transformers import (
        AutoTokenizer, 
        AutoModelForCausalLM, 
        Trainer, 
        TrainingArguments,
        DataCollatorForLanguageModeling
    )
    HAS_TRANSFORMERS = True
except ImportError:
    HAS_TRANSFORMERS = False


class LogDataset(Dataset):
    """
    Датасет для обучения моделей ИИ на логах действий пользователя
    """
    
    def __init__(self, tokenizer, log_entries, max_length=512):
        """
        Инициализация датасета
        
        Args:
            tokenizer: Токенизатор для модели
            log_entries (List[Dict]): Список записей логов действий
            max_length (int): Максимальная длина последовательности
        """
        self.tokenizer = tokenizer
        self.log_entries = log_entries
        self.max_length = max_length
        self.examples = self._prepare_examples()
    
    def _prepare_examples(self):
        """
        Подготовка примеров для обучения из логов действий
        
        Returns:
            List[Dict]: Список примеров для обучения
        """
        examples = []
        
        for entry in self.log_entries:
            # Получение команды и соответствующих действий
            if 'command' in entry and 'action' in entry:
                command = entry['command']
                action = entry.get('action', {})
                result = entry.get('result', 'unknown')
                
                # Формирование текста для обучения
                if result == 'success':
                    text = f"Command: {command}\nAction: {json.dumps(action, ensure_ascii=False)}\n"
                    
                    # Токенизация текста
                    encodings = self.tokenizer(
                        text,
                        max_length=self.max_length,
                        padding="max_length",
                        truncation=True,
                        return_tensors="pt"
                    )
                    
                    examples.append({
                        "input_ids": encodings.input_ids[0],
                        "attention_mask": encodings.attention_mask[0]
                    })
        
        return examples
    
    def __len__(self):
        return len(self.examples)
    
    def __getitem__(self, idx):
        return self.examples[idx]


class AITrainer:
    """
    Модуль для обучения AI-моделей на основе логов действий пользователя
    """
    
    def __init__(self, model_path, output_dir=None):
        """
        Инициализация тренера моделей
        
        Args:
            model_path (str): Путь к исходной модели для дообучения
            output_dir (str, optional): Директория для сохранения обученной модели
        """
        self.logger = logging.getLogger('daur_ai.trainer')
        self.model_path = model_path
        
        if output_dir is None:
            timestamp = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
            self.output_dir = os.path.join(
                os.path.dirname(model_path), 
                f"finetuned_{timestamp}"
            )
        else:
            self.output_dir = output_dir
        
        # Проверка наличия необходимых библиотек
        if not (HAS_TORCH and HAS_TRANSFORMERS):
            self.logger.error(
                "Для обучения моделей требуются библиотеки PyTorch и Transformers"
            )
            self.available = False
        else:
            self.available = True
            self.logger.info("Модуль обучения AI инициализирован")
    
    def process_logs(self, log_path):
        """
        Обработка файлов логов для создания обучающего датасета
        
        Args:
            log_path (str): Путь к директории с логами или к конкретному файлу
            
        Returns:
            List[Dict]: Список записей логов
        """
        log_entries = []
        
        try:
            log_path_obj = Path(log_path)
            
            if log_path_obj.is_file():
                # Один файл с логами
                log_files = [log_path_obj]
            elif log_path_obj.is_dir():
                # Директория с логами
                log_files = list(log_path_obj.glob("*.log"))
                log_files.extend(log_path_obj.glob("*.json"))
            else:
                self.logger.error(f"Указанный путь не существует: {log_path}")
                return []
            
            for log_file in log_files:
                try:
                    self.logger.info(f"Обработка файла логов: {log_file}")
                    
                    with open(log_file, 'r', encoding='utf-8') as f:
                        if log_file.suffix.lower() == '.json':
                            # Формат JSON
                            data = json.load(f)
                            if isinstance(data, list):
                                log_entries.extend(data)
                            elif isinstance(data, dict):
                                log_entries.append(data)
                        else:
                            # Формат текстового лога
                            for line in f:
                                try:
                                    # Пытаемся парсить каждую строку как JSON
                                    entry = json.loads(line)
                                    log_entries.append(entry)
                                except json.JSONDecodeError:
                                    # Если не получается, парсим как обычный лог
                                    parts = line.strip().split(' | ')
                                    if len(parts) >= 3:
                                        timestamp = parts[0]
                                        command = parts[1]
                                        action = ' '.join(parts[2:])
                                        
                                        log_entries.append({
                                            'timestamp': timestamp,
                                            'command': command,
                                            'action': action,
                                            'result': 'success'  # Предполагаем успешное выполнение
                                        })
                
                except Exception as e:
                    self.logger.error(f"Ошибка при обработке файла {log_file}: {e}", exc_info=True)
            
            self.logger.info(f"Обработано записей логов: {len(log_entries)}")
            return log_entries
            
        except Exception as e:
            self.logger.error(f"Ошибка при обработке логов: {e}", exc_info=True)
            return []
    
    def train(self, log_entries, epochs=3, batch_size=4, 
              learning_rate=5e-5, use_gpu=True):
        """
        Обучение модели на логах
        
        Args:
            log_entries (List[Dict]): Список записей логов
            epochs (int): Количество эпох обучения
            batch_size (int): Размер батча
            learning_rate (float): Скорость обучения
            use_gpu (bool): Использовать ли GPU для обучения
            
        Returns:
            bool: True в случае успешного обучения, False в случае ошибки
        """
        if not self.available:
            self.logger.error("Библиотеки для обучения недоступны")
            return False
        
        if not log_entries:
            self.logger.error("Нет данных для обучения")
            return False
        
        try:
            self.logger.info(f"Начало обучения модели на {len(log_entries)} записях логов")
            
            # Подготовка директории для вывода
            os.makedirs(self.output_dir, exist_ok=True)
            
            # Определение устройства
            device = "cuda" if use_gpu and torch.cuda.is_available() else "cpu"
            self.logger.info(f"Используется устройство для обучения: {device}")
            
            # Загрузка токенизатора и модели
            self.logger.info(f"Загрузка модели из {self.model_path}")
            tokenizer = AutoTokenizer.from_pretrained(self.model_path)
            model = AutoModelForCausalLM.from_pretrained(self.model_path)
            
            # Перемещение модели на устройство
            model = model.to(device)
            
            # Подготовка датасета
            dataset = LogDataset(tokenizer, log_entries)
            
            # Проверка на пустой датасет
            if len(dataset) == 0:
                self.logger.error("Подготовленный датасет пуст")
                return False
            
            # Подготовка коллатора данных
            data_collator = DataCollatorForLanguageModeling(
                tokenizer=tokenizer, 
                mlm=False
            )
            
            # Настройки обучения
            training_args = TrainingArguments(
                output_dir=self.output_dir,
                overwrite_output_dir=True,
                num_train_epochs=epochs,
                per_device_train_batch_size=batch_size,
                save_steps=500,
                save_total_limit=2,
                learning_rate=learning_rate,
                fp16=device == "cuda",
                logging_dir=os.path.join(self.output_dir, 'logs'),
                logging_steps=100,
            )
            
            # Инициализация тренера
            trainer = Trainer(
                model=model,
                args=training_args,
                data_collator=data_collator,
                train_dataset=dataset,
            )
            
            # Запуск обучения
            start_time = time.time()
            self.logger.info("Начало процесса обучения")
            trainer.train()
            
            # Сохранение модели
            trainer.save_model(self.output_dir)
            tokenizer.save_pretrained(self.output_dir)
            
            elapsed_time = time.time() - start_time
            self.logger.info(f"Обучение завершено за {elapsed_time:.2f} секунд")
            self.logger.info(f"Модель сохранена в {self.output_dir}")
            
            return True
            
        except Exception as e:
            self.logger.error(f"Ошибка при обучении модели: {e}", exc_info=True)
            return False
    
    def finetune_model(self, log_path, epochs=3, batch_size=4, 
                       learning_rate=5e-5, use_gpu=True):
        """
        Дообучение модели на основе логов
        
        Args:
            log_path (str): Путь к директории с логами или к конкретному файлу
            epochs (int): Количество эпох обучения
            batch_size (int): Размер батча
            learning_rate (float): Скорость обучения
            use_gpu (bool): Использовать ли GPU для обучения
            
        Returns:
            bool: True в случае успешного обучения, False в случае ошибки
        """
        # Обработка логов
        log_entries = self.process_logs(log_path)
        
        if not log_entries:
            self.logger.warning("Не найдены записи логов для обучения")
            return False
        
        # Обучение модели
        return self.train(
            log_entries=log_entries,
            epochs=epochs,
            batch_size=batch_size,
            learning_rate=learning_rate,
            use_gpu=use_gpu
        )
