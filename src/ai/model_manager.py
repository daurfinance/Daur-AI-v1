#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
Daur-AI: Менеджер AI-моделей
Модуль для загрузки, инициализации и использования локальных моделей ИИ

Версия: 1.0
Дата: 09.05.2025
"""

import os
import time
import json
import logging
import threading
from typing import Dict, List, Any, Optional, Union, Tuple

# Попытка импорта различных библиотек для работы с моделями ИИ
try:
    import torch
    HAS_TORCH = True
except ImportError:
    HAS_TORCH = False
    
try:
    from transformers import AutoModelForCausalLM, AutoTokenizer, pipeline
    HAS_TRANSFORMERS = True
except ImportError:
    HAS_TRANSFORMERS = False

try:
    from llama_cpp import Llama
    HAS_LLAMA_CPP = True
except ImportError:
    HAS_LLAMA_CPP = False


class AIModelManager:
    """
    Менеджер для загрузки и использования локальных моделей ИИ
    Поддерживает различные форматы моделей (GGUF, GGML, PyTorch и т.д.)
    """
    
    def __init__(self, model_path: str, timeout: int = 30, 
                 context_length: int = 4096, n_threads: int = None,
                 use_gpu: bool = True, device: str = None):
        """
        Инициализация менеджера моделей
        
        Args:
            model_path (str): Путь к модели или директории с моделями
            timeout (int): Таймаут для инференса модели в секундах
            context_length (int): Длина контекста для модели
            n_threads (int, optional): Количество потоков для CPU-инференса
            use_gpu (bool): Использовать ли GPU (если доступен)
            device (str, optional): Устройство для запуска модели (cuda:0, cpu и т.д.)
        """
        self.logger = logging.getLogger('daur_ai.ai')
        self.model_path = model_path
        self.timeout = timeout
        self.context_length = context_length
        self.use_gpu = use_gpu
        
        # Определение устройства
        if device:
            self.device = device
        elif use_gpu and HAS_TORCH and torch.cuda.is_available():
            self.device = "cuda:0"
            self.logger.info("Используется CUDA для инференса")
        else:
            self.device = "cpu"
            self.logger.info("Используется CPU для инференса")
        
        # Определение количества потоков
        if n_threads is None:
            import multiprocessing
            self.n_threads = max(1, multiprocessing.cpu_count() - 1)
        else:
            self.n_threads = n_threads
            
        # Атрибуты для моделей
        self.model = None
        self.tokenizer = None
        self.model_type = None
        self.is_loaded = False
        self.loading_lock = threading.Lock()
        
        # Проверка доступности модели
        if not os.path.exists(model_path):
            self.logger.error(f"Путь к модели не существует: {model_path}")
            raise FileNotFoundError(f"Путь к модели не существует: {model_path}")
        
        # Автоопределение типа модели
        self._detect_model_type()
        
        # Загрузка модели (ленивая загрузка)
        self.logger.info(f"Менеджер AI-моделей инициализирован, тип модели: {self.model_type}")
    
    def _detect_model_type(self):
        """
        Автоопределение типа модели по расширению или структуре папки
        """
        if os.path.isfile(self.model_path):
            # Определение по расширению файла
            ext = os.path.splitext(self.model_path)[1].lower()
            
            if ext in ['.gguf', '.ggml']:
                self.model_type = "llama_cpp"
                self.logger.info(f"Обнаружена модель формата {ext}")
                
            elif ext in ['.bin', '.pt', '.pth']:
                self.model_type = "pytorch"
                self.logger.info(f"Обнаружена модель формата PyTorch: {ext}")
                
            else:
                self.logger.warning(f"Неизвестное расширение модели: {ext}")
                # Попытка определения по наличию библиотек
                if HAS_LLAMA_CPP:
                    self.model_type = "llama_cpp"
                elif HAS_TRANSFORMERS and HAS_TORCH:
                    self.model_type = "transformers"
                else:
                    self.logger.error("Не удалось определить тип модели")
                    raise ValueError("Неподдерживаемый формат модели")
        
        else:
            # Это директория, попытка определить тип модели по структуре
            if os.path.exists(os.path.join(self.model_path, 'config.json')):
                self.model_type = "transformers"
                self.logger.info("Обнаружена модель формата Transformers")
            else:
                self.logger.warning("Не удалось определить тип модели по структуре директории")
                # Попытка определения по наличию библиотек
                if HAS_TRANSFORMERS and HAS_TORCH:
                    self.model_type = "transformers"
                elif HAS_LLAMA_CPP:
                    self.model_type = "llama_cpp"
                else:
                    self.logger.error("Не удалось определить тип модели")
                    raise ValueError("Неподдерживаемый формат модели")

    def load_model(self):
        """
        Загрузка модели в память
        
        Returns:
            bool: True если загрузка прошла успешно, иначе False
        """
        if self.is_loaded:
            return True
        
        with self.loading_lock:
            if self.is_loaded:  # Повторная проверка в случае конкурентного доступа
                return True
            
            self.logger.info(f"Загрузка модели из {self.model_path}")
            start_time = time.time()
            
            try:
                if self.model_type == "llama_cpp":
                    if not HAS_LLAMA_CPP:
                        self.logger.error("Библиотека llama-cpp-python не установлена")
                        return False
                    
                    self.model = Llama(
                        model_path=self.model_path,
                        n_ctx=self.context_length,
                        n_threads=self.n_threads,
                        n_gpu_layers=-1 if self.use_gpu else 0
                    )
                
                elif self.model_type == "transformers":
                    if not (HAS_TRANSFORMERS and HAS_TORCH):
                        self.logger.error("Библиотеки transformers или PyTorch не установлены")
                        return False
                    
                    # Загрузка токенизатора и модели
                    self.tokenizer = AutoTokenizer.from_pretrained(
                        self.model_path, 
                        trust_remote_code=True
                    )
                    
                    self.model = AutoModelForCausalLM.from_pretrained(
                        self.model_path,
                        device_map=self.device if self.use_gpu else "cpu",
                        torch_dtype=torch.float16 if self.use_gpu else torch.float32,
                        low_cpu_mem_usage=True,
                        trust_remote_code=True
                    )
                
                else:
                    self.logger.error(f"Неподдерживаемый тип модели: {self.model_type}")
                    return False
                
                self.is_loaded = True
                load_time = time.time() - start_time
                self.logger.info(f"Модель успешно загружена за {load_time:.2f} секунд")
                return True
                
            except Exception as e:
                self.logger.error(f"Ошибка загрузки модели: {e}", exc_info=True)
                return False
    
    def unload_model(self):
        """Выгрузка модели из памяти"""
        if not self.is_loaded:
            return
        
        with self.loading_lock:
            if not self.is_loaded:
                return
            
            self.logger.info("Выгрузка модели из памяти")
            
            try:
                if self.model_type == "transformers":
                    # Явное освобождение памяти для PyTorch моделей
                    if HAS_TORCH:
                        if hasattr(self.model, "to"):
                            self.model = self.model.to("cpu")
                        
                        import gc
                        del self.model
                        del self.tokenizer
                        gc.collect()
                        
                        if torch.cuda.is_available():
                            torch.cuda.empty_cache()
                
                # Для других типов моделей
                elif self.model_type == "llama_cpp":
                    del self.model
                
                self.model = None
                self.tokenizer = None
                self.is_loaded = False
                self.logger.info("Модель успешно выгружена из памяти")
                
            except Exception as e:
                self.logger.error(f"Ошибка при выгрузке модели: {e}", exc_info=True)

    def generate_text(self, prompt: str, max_tokens: int = 256, 
                    temperature: float = 0.7, top_p: float = 0.95) -> Union[str, None]:
        """
        Генерация текста с использованием загруженной модели
        
        Args:
            prompt (str): Входной текст-запрос для модели
            max_tokens (int): Максимальное количество токенов для генерации
            temperature (float): Температура семплирования (0.0-1.0)
            top_p (float): Параметр Top-p для семплирования (0.0-1.0)
            
        Returns:
            str: Сгенерированный текст или None в случае ошибки
        """
        if not self.is_loaded and not self.load_model():
            self.logger.error("Не удалось загрузить модель для генерации текста")
            return None
        
        self.logger.debug(f"Запрос на генерацию текста: {prompt[:50]}...")
        
        # Установка таймера для обработки зависаний
        result = [None]
        exception = [None]
        
        def _generate():
            try:
                if self.model_type == "llama_cpp":
                    output = self.model(
                        prompt=prompt,
                        max_tokens=max_tokens,
                        temperature=temperature,
                        top_p=top_p,
                        echo=False
                    )
                    result[0] = output['choices'][0]['text']
                    
                elif self.model_type == "transformers":
                    inputs = self.tokenizer(prompt, return_tensors="pt").to(self.device)
                    
                    with torch.no_grad():
                        outputs = self.model.generate(
                            **inputs,
                            max_length=min(inputs['input_ids'].shape[1] + max_tokens, self.context_length),
                            temperature=temperature if temperature > 0 else 1.0,
                            top_p=top_p,
                            do_sample=temperature > 0,
                            pad_token_id=self.tokenizer.eos_token_id
                        )
                    
                    result[0] = self.tokenizer.decode(
                        outputs[0][inputs['input_ids'].shape[1]:], 
                        skip_special_tokens=True
                    )
            
            except Exception as e:
                exception[0] = str(e)
                self.logger.error(f"Ошибка при генерации текста: {e}", exc_info=True)
        
        # Запуск в отдельном потоке с таймером
        thread = threading.Thread(target=_generate)
        thread.daemon = True
        thread.start()
        thread.join(timeout=self.timeout)
        
        if thread.is_alive():
            self.logger.error(f"Таймаут генерации после {self.timeout} секунд")
            return f"ERROR: Таймаут генерации после {self.timeout} секунд"
        
        if exception[0]:
            return f"ERROR: {exception[0]}"
        
        generated_text = result[0]
        self.logger.debug(f"Текст сгенерирован: {generated_text[:50]}...")
        
        return generated_text

    def parse_command(self, command_text: str) -> List[Dict[str, Any]]:
        """
        Парсинг команды пользователя в структурированный формат
        используя возможности модели ИИ
        
        Args:
            command_text (str): Текстовая команда от пользователя
            
        Returns:
            List[Dict[str, Any]]: Список действий в формате словарей
        """
        prompt_template = """
        Преобразуй следующую команду на естественном языке в структурированный JSON-формат.
        Команда: "{command}"
        
        Возможные типы действий:
        - input_click - клик мышью (координаты или имя элемента)
        - input_dblclick - двойной клик
        - input_move - перемещение мыши
        - input_type - ввод текста
        - input_key - нажатие клавиши на клавиатуре
        - app_open - открытие приложения
        - app_close - закрытие приложения
        - app_switch - переключение на приложение
        - file_create - создание файла
        - file_read - чтение файла
        - file_write - запись в файл
        - file_delete - удаление файла
        - system_exec - выполнение системной команды
        - wait - ожидание указанного времени
        
        Формат результата - список объектов JSON, каждый должен содержать:
        - action: тип действия из перечисленных выше
        - params: объект с параметрами, зависящими от типа действия
        
        Возвращай только JSON, без дополнительных пояснений или текста.
        """
        
        try:
            # Подготавливаем запрос для модели
            formatted_prompt = prompt_template.format(command=command_text)
            
            # Получаем ответ от модели
            response = self.generate_text(formatted_prompt, max_tokens=512, temperature=0.2)
            
            if not response or response.startswith("ERROR:"):
                self.logger.error(f"Ошибка при парсинге команды: {response}")
                return []
            
            # Извлекаем JSON из ответа
            json_match = re.search(r'\[.*\]', response, re.DOTALL)
            if not json_match:
                self.logger.warning("Не удалось найти JSON в ответе модели")
                return []
            
            json_str = json_match.group(0)
            actions = json.loads(json_str)
            
            # Валидация результата
            if not isinstance(actions, list):
                self.logger.warning(f"Неверный формат ответа: ожидался список, получено {type(actions)}")
                return []
            
            self.logger.debug(f"Команда успешно разобрана: {actions}")
            return actions
            
        except json.JSONDecodeError as e:
            self.logger.error(f"Ошибка декодирования JSON: {e}")
            return []
        except Exception as e:
            self.logger.error(f"Ошибка при парсинге команды: {e}", exc_info=True)
            return []
    
    def cleanup(self):
        """Очистка ресурсов"""
        self.unload_model()
        self.logger.info("Очистка ресурсов AIModelManager завершена")

    def __del__(self):
        """Деструктор класса"""
        self.cleanup()
