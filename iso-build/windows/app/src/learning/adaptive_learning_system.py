"""
Система адаптивного обучения AI-агента
Самообучение, анализ обратной связи и улучшение производительности
"""

import json
import time
import logging
import sqlite3
import pickle
import numpy as np
from typing import Dict, List, Optional, Tuple, Any, Union
from dataclasses import dataclass, asdict
from enum import Enum
from collections import defaultdict, deque
import threading
import asyncio
from datetime import datetime, timedelta

class FeedbackType(Enum):
    """Типы обратной связи"""
    SUCCESS = "success"
    FAILURE = "failure"
    PARTIAL_SUCCESS = "partial_success"
    USER_CORRECTION = "user_correction"
    TIMEOUT = "timeout"
    ERROR = "error"

class LearningMode(Enum):
    """Режимы обучения"""
    PASSIVE = "passive"  # Только наблюдение
    ACTIVE = "active"    # Активное обучение
    REINFORCEMENT = "reinforcement"  # Обучение с подкреплением
    SUPERVISED = "supervised"  # Обучение с учителем

@dataclass
class ActionResult:
    """Результат выполнения действия"""
    action_id: str
    command: str
    device_type: str
    parameters: Dict
    success: bool
    execution_time: float
    error_message: Optional[str] = None
    user_feedback: Optional[str] = None
    confidence_score: float = 0.0
    timestamp: float = 0.0

@dataclass
class LearningPattern:
    """Паттерн обучения"""
    pattern_id: str
    context: Dict
    action_sequence: List[Dict]
    success_rate: float
    usage_count: int
    last_used: float
    confidence: float
    tags: List[str]

@dataclass
class AdaptationRule:
    """Правило адаптации"""
    rule_id: str
    condition: Dict
    action: Dict
    priority: int
    success_count: int
    failure_count: int
    enabled: bool = True

class AdaptiveLearningSystem:
    """Система адаптивного обучения AI-агента"""
    
    def __init__(self, db_path: str = "learning_data.db"):
        self.logger = logging.getLogger(__name__)
        self.db_path = db_path
        
        # Режим обучения
        self.learning_mode = LearningMode.ACTIVE
        self.learning_enabled = True
        
        # История действий
        self.action_history = deque(maxlen=10000)
        self.feedback_history = deque(maxlen=5000)
        
        # Паттерны и правила
        self.learned_patterns = {}
        self.adaptation_rules = {}
        
        # Статистика
        self.learning_stats = {
            'total_actions': 0,
            'successful_actions': 0,
            'failed_actions': 0,
            'patterns_learned': 0,
            'rules_created': 0,
            'adaptations_made': 0,
            'learning_sessions': 0
        }
        
        # Настройки обучения
        self.min_pattern_confidence = 0.7
        self.max_patterns = 1000
        self.learning_rate = 0.1
        self.adaptation_threshold = 0.8
        
        # Контекстная информация
        self.current_context = {}
        self.context_history = deque(maxlen=1000)
        
        # Блокировки для многопоточности
        self.learning_lock = threading.Lock()
        
        # Инициализация
        self._initialize_database()
        self._load_learning_data()
    
    def _initialize_database(self):
        """Инициализирует базу данных для хранения данных обучения"""
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            # Таблица результатов действий
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS action_results (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    action_id TEXT UNIQUE,
                    command TEXT,
                    device_type TEXT,
                    parameters TEXT,
                    success BOOLEAN,
                    execution_time REAL,
                    error_message TEXT,
                    user_feedback TEXT,
                    confidence_score REAL,
                    timestamp REAL
                )
            ''')
            
            # Таблица паттернов
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS learning_patterns (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    pattern_id TEXT UNIQUE,
                    context TEXT,
                    action_sequence TEXT,
                    success_rate REAL,
                    usage_count INTEGER,
                    last_used REAL,
                    confidence REAL,
                    tags TEXT
                )
            ''')
            
            # Таблица правил адаптации
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS adaptation_rules (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    rule_id TEXT UNIQUE,
                    condition TEXT,
                    action TEXT,
                    priority INTEGER,
                    success_count INTEGER,
                    failure_count INTEGER,
                    enabled BOOLEAN
                )
            ''')
            
            # Таблица статистики
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS learning_stats (
                    key TEXT PRIMARY KEY,
                    value REAL
                )
            ''')
            
            conn.commit()
            conn.close()
            
            self.logger.info("База данных обучения инициализирована")
            
        except Exception as e:
            self.logger.error(f"Ошибка инициализации базы данных: {e}")
    
    def _load_learning_data(self):
        """Загружает данные обучения из базы данных"""
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            # Загрузка паттернов
            cursor.execute('SELECT * FROM learning_patterns')
            for row in cursor.fetchall():
                pattern = LearningPattern(
                    pattern_id=row[1],
                    context=json.loads(row[2]),
                    action_sequence=json.loads(row[3]),
                    success_rate=row[4],
                    usage_count=row[5],
                    last_used=row[6],
                    confidence=row[7],
                    tags=json.loads(row[8])
                )
                self.learned_patterns[pattern.pattern_id] = pattern
            
            # Загрузка правил адаптации
            cursor.execute('SELECT * FROM adaptation_rules')
            for row in cursor.fetchall():
                rule = AdaptationRule(
                    rule_id=row[1],
                    condition=json.loads(row[2]),
                    action=json.loads(row[3]),
                    priority=row[4],
                    success_count=row[5],
                    failure_count=row[6],
                    enabled=bool(row[7])
                )
                self.adaptation_rules[rule.rule_id] = rule
            
            # Загрузка статистики
            cursor.execute('SELECT * FROM learning_stats')
            for row in cursor.fetchall():
                self.learning_stats[row[0]] = row[1]
            
            conn.close()
            
            self.logger.info(f"Загружено {len(self.learned_patterns)} паттернов и {len(self.adaptation_rules)} правил")
            
        except Exception as e:
            self.logger.error(f"Ошибка загрузки данных обучения: {e}")
    
    def record_action_result(self, result: ActionResult):
        """Записывает результат выполнения действия"""
        try:
            with self.learning_lock:
                # Добавление в историю
                self.action_history.append(result)
                
                # Обновление статистики
                self.learning_stats['total_actions'] += 1
                if result.success:
                    self.learning_stats['successful_actions'] += 1
                else:
                    self.learning_stats['failed_actions'] += 1
                
                # Сохранение в базу данных
                self._save_action_result(result)
                
                # Анализ для обучения
                if self.learning_enabled:
                    self._analyze_for_learning(result)
            
        except Exception as e:
            self.logger.error(f"Ошибка записи результата действия: {e}")
    
    def _save_action_result(self, result: ActionResult):
        """Сохраняет результат действия в базу данных"""
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            cursor.execute('''
                INSERT OR REPLACE INTO action_results 
                (action_id, command, device_type, parameters, success, execution_time, 
                 error_message, user_feedback, confidence_score, timestamp)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            ''', (
                result.action_id,
                result.command,
                result.device_type,
                json.dumps(result.parameters),
                result.success,
                result.execution_time,
                result.error_message,
                result.user_feedback,
                result.confidence_score,
                result.timestamp
            ))
            
            conn.commit()
            conn.close()
            
        except Exception as e:
            self.logger.error(f"Ошибка сохранения результата действия: {e}")
    
    def _analyze_for_learning(self, result: ActionResult):
        """Анализирует результат для обучения"""
        try:
            # Поиск паттернов
            self._identify_patterns(result)
            
            # Обновление существующих паттернов
            self._update_patterns(result)
            
            # Создание правил адаптации
            self._create_adaptation_rules(result)
            
            # Адаптация поведения
            self._adapt_behavior(result)
            
        except Exception as e:
            self.logger.error(f"Ошибка анализа для обучения: {e}")
    
    def _identify_patterns(self, result: ActionResult):
        """Идентифицирует новые паттерны поведения"""
        try:
            # Анализ последовательности действий
            recent_actions = list(self.action_history)[-5:]  # Последние 5 действий
            
            if len(recent_actions) >= 3:
                # Создание паттерна из последовательности
                pattern_context = {
                    'device_types': [a.device_type for a in recent_actions],
                    'commands': [a.command for a in recent_actions],
                    'success_pattern': [a.success for a in recent_actions],
                    'time_pattern': [a.execution_time for a in recent_actions]
                }
                
                # Проверка на уникальность паттерна
                pattern_signature = self._generate_pattern_signature(pattern_context)
                
                if pattern_signature not in self.learned_patterns:
                    # Создание нового паттерна
                    new_pattern = LearningPattern(
                        pattern_id=pattern_signature,
                        context=pattern_context,
                        action_sequence=[asdict(a) for a in recent_actions],
                        success_rate=sum(a.success for a in recent_actions) / len(recent_actions),
                        usage_count=1,
                        last_used=time.time(),
                        confidence=0.5,  # Начальная уверенность
                        tags=self._generate_pattern_tags(pattern_context)
                    )
                    
                    if new_pattern.success_rate >= self.min_pattern_confidence:
                        self.learned_patterns[pattern_signature] = new_pattern
                        self.learning_stats['patterns_learned'] += 1
                        self._save_pattern(new_pattern)
                        
                        self.logger.info(f"Новый паттерн изучен: {pattern_signature}")
            
        except Exception as e:
            self.logger.error(f"Ошибка идентификации паттернов: {e}")
    
    def _generate_pattern_signature(self, context: Dict) -> str:
        """Генерирует уникальную подпись паттерна"""
        try:
            # Создание хеша на основе контекста
            context_str = json.dumps(context, sort_keys=True)
            import hashlib
            return hashlib.md5(context_str.encode()).hexdigest()[:16]
            
        except Exception as e:
            self.logger.error(f"Ошибка генерации подписи паттерна: {e}")
            return f"pattern_{int(time.time())}"
    
    def _generate_pattern_tags(self, context: Dict) -> List[str]:
        """Генерирует теги для паттерна"""
        tags = []
        
        try:
            # Теги на основе типов устройств
            device_types = context.get('device_types', [])
            for device_type in set(device_types):
                tags.append(f"device:{device_type}")
            
            # Теги на основе команд
            commands = context.get('commands', [])
            for command in set(commands):
                if len(command) > 0:
                    tags.append(f"command:{command[:20]}")
            
            # Теги на основе успешности
            success_pattern = context.get('success_pattern', [])
            if all(success_pattern):
                tags.append("all_success")
            elif any(success_pattern):
                tags.append("partial_success")
            else:
                tags.append("all_failure")
            
            return tags
            
        except Exception as e:
            self.logger.error(f"Ошибка генерации тегов: {e}")
            return []
    
    def _update_patterns(self, result: ActionResult):
        """Обновляет существующие паттерны"""
        try:
            for pattern_id, pattern in self.learned_patterns.items():
                # Проверка соответствия контексту
                if self._matches_pattern_context(result, pattern):
                    # Обновление статистики паттерна
                    pattern.usage_count += 1
                    pattern.last_used = time.time()
                    
                    # Обновление коэффициента успешности
                    old_success_rate = pattern.success_rate
                    new_success_rate = (old_success_rate * (pattern.usage_count - 1) + (1 if result.success else 0)) / pattern.usage_count
                    pattern.success_rate = new_success_rate
                    
                    # Обновление уверенности
                    pattern.confidence = min(1.0, pattern.confidence + self.learning_rate * (1 if result.success else -0.5))
                    
                    # Сохранение обновленного паттерна
                    self._save_pattern(pattern)
            
        except Exception as e:
            self.logger.error(f"Ошибка обновления паттернов: {e}")
    
    def _matches_pattern_context(self, result: ActionResult, pattern: LearningPattern) -> bool:
        """Проверяет соответствие результата контексту паттерна"""
        try:
            context = pattern.context
            
            # Проверка типа устройства
            if 'device_types' in context:
                if result.device_type not in context['device_types']:
                    return False
            
            # Проверка команды
            if 'commands' in context:
                if result.command not in context['commands']:
                    return False
            
            return True
            
        except Exception as e:
            self.logger.error(f"Ошибка проверки соответствия паттерну: {e}")
            return False
    
    def _create_adaptation_rules(self, result: ActionResult):
        """Создает правила адаптации на основе результатов"""
        try:
            # Создание правила для неуспешных действий
            if not result.success and result.error_message:
                rule_condition = {
                    'device_type': result.device_type,
                    'command_pattern': result.command[:50],
                    'error_type': result.error_message[:100]
                }
                
                rule_action = {
                    'type': 'retry_with_modification',
                    'modifications': self._suggest_modifications(result),
                    'max_retries': 3
                }
                
                rule_id = f"error_rule_{result.device_type}_{int(time.time())}"
                
                new_rule = AdaptationRule(
                    rule_id=rule_id,
                    condition=rule_condition,
                    action=rule_action,
                    priority=5,
                    success_count=0,
                    failure_count=1,
                    enabled=True
                )
                
                self.adaptation_rules[rule_id] = new_rule
                self.learning_stats['rules_created'] += 1
                self._save_adaptation_rule(new_rule)
                
                self.logger.info(f"Создано правило адаптации: {rule_id}")
            
        except Exception as e:
            self.logger.error(f"Ошибка создания правил адаптации: {e}")
    
    def _suggest_modifications(self, result: ActionResult) -> Dict:
        """Предлагает модификации для неуспешного действия"""
        modifications = {}
        
        try:
            # Анализ ошибки и предложение изменений
            if result.error_message:
                error_msg = result.error_message.lower()
                
                if 'timeout' in error_msg:
                    modifications['increase_timeout'] = True
                    modifications['timeout_multiplier'] = 2.0
                
                if 'not found' in error_msg or 'element' in error_msg:
                    modifications['retry_with_delay'] = True
                    modifications['delay_seconds'] = 2.0
                
                if 'permission' in error_msg or 'access' in error_msg:
                    modifications['use_elevated_privileges'] = True
                
                if 'network' in error_msg or 'connection' in error_msg:
                    modifications['retry_network'] = True
                    modifications['network_retry_count'] = 3
            
            return modifications
            
        except Exception as e:
            self.logger.error(f"Ошибка предложения модификаций: {e}")
            return {}
    
    def _adapt_behavior(self, result: ActionResult):
        """Адаптирует поведение на основе результата"""
        try:
            # Применение правил адаптации
            applicable_rules = self._find_applicable_rules(result)
            
            for rule in applicable_rules:
                if rule.enabled:
                    self._apply_adaptation_rule(rule, result)
                    self.learning_stats['adaptations_made'] += 1
            
        except Exception as e:
            self.logger.error(f"Ошибка адаптации поведения: {e}")
    
    def _find_applicable_rules(self, result: ActionResult) -> List[AdaptationRule]:
        """Находит применимые правила адаптации"""
        applicable_rules = []
        
        try:
            for rule in self.adaptation_rules.values():
                if self._rule_matches_result(rule, result):
                    applicable_rules.append(rule)
            
            # Сортировка по приоритету
            applicable_rules.sort(key=lambda r: r.priority, reverse=True)
            
            return applicable_rules
            
        except Exception as e:
            self.logger.error(f"Ошибка поиска применимых правил: {e}")
            return []
    
    def _rule_matches_result(self, rule: AdaptationRule, result: ActionResult) -> bool:
        """Проверяет соответствие правила результату"""
        try:
            condition = rule.condition
            
            # Проверка типа устройства
            if 'device_type' in condition:
                if condition['device_type'] != result.device_type:
                    return False
            
            # Проверка паттерна команды
            if 'command_pattern' in condition:
                if condition['command_pattern'] not in result.command:
                    return False
            
            # Проверка типа ошибки
            if 'error_type' in condition and result.error_message:
                if condition['error_type'] not in result.error_message:
                    return False
            
            return True
            
        except Exception as e:
            self.logger.error(f"Ошибка проверки соответствия правила: {e}")
            return False
    
    def _apply_adaptation_rule(self, rule: AdaptationRule, result: ActionResult):
        """Применяет правило адаптации"""
        try:
            action = rule.action
            
            # Обновление статистики правила
            if result.success:
                rule.success_count += 1
            else:
                rule.failure_count += 1
            
            # Отключение неэффективных правил
            total_applications = rule.success_count + rule.failure_count
            if total_applications >= 10:
                success_rate = rule.success_count / total_applications
                if success_rate < 0.3:  # Менее 30% успешности
                    rule.enabled = False
                    self.logger.info(f"Правило {rule.rule_id} отключено из-за низкой эффективности")
            
            # Сохранение обновленного правила
            self._save_adaptation_rule(rule)
            
            self.logger.info(f"Применено правило адаптации: {rule.rule_id}")
            
        except Exception as e:
            self.logger.error(f"Ошибка применения правила адаптации: {e}")
    
    def get_learning_recommendations(self, context: Dict) -> List[Dict]:
        """Возвращает рекомендации на основе изученных паттернов"""
        recommendations = []
        
        try:
            # Поиск релевантных паттернов
            relevant_patterns = self._find_relevant_patterns(context)
            
            for pattern in relevant_patterns:
                if pattern.confidence >= self.min_pattern_confidence:
                    recommendation = {
                        'pattern_id': pattern.pattern_id,
                        'confidence': pattern.confidence,
                        'success_rate': pattern.success_rate,
                        'recommended_actions': pattern.action_sequence[-3:],  # Последние 3 действия
                        'tags': pattern.tags,
                        'usage_count': pattern.usage_count
                    }
                    recommendations.append(recommendation)
            
            # Сортировка по уверенности и успешности
            recommendations.sort(key=lambda r: (r['confidence'], r['success_rate']), reverse=True)
            
            return recommendations[:5]  # Топ-5 рекомендаций
            
        except Exception as e:
            self.logger.error(f"Ошибка получения рекомендаций: {e}")
            return []
    
    def _find_relevant_patterns(self, context: Dict) -> List[LearningPattern]:
        """Находит релевантные паттерны для контекста"""
        relevant_patterns = []
        
        try:
            for pattern in self.learned_patterns.values():
                relevance_score = self._calculate_pattern_relevance(pattern, context)
                if relevance_score > 0.5:
                    relevant_patterns.append(pattern)
            
            return relevant_patterns
            
        except Exception as e:
            self.logger.error(f"Ошибка поиска релевантных паттернов: {e}")
            return []
    
    def _calculate_pattern_relevance(self, pattern: LearningPattern, context: Dict) -> float:
        """Вычисляет релевантность паттерна для контекста"""
        try:
            relevance_score = 0.0
            
            # Сравнение контекстов
            pattern_context = pattern.context
            
            # Совпадение типов устройств
            if 'device_type' in context and 'device_types' in pattern_context:
                if context['device_type'] in pattern_context['device_types']:
                    relevance_score += 0.3
            
            # Совпадение команд
            if 'command' in context and 'commands' in pattern_context:
                for pattern_command in pattern_context['commands']:
                    if context['command'] in pattern_command or pattern_command in context['command']:
                        relevance_score += 0.4
                        break
            
            # Бонус за высокую успешность
            relevance_score += pattern.success_rate * 0.2
            
            # Бонус за частое использование
            if pattern.usage_count > 10:
                relevance_score += 0.1
            
            return min(1.0, relevance_score)
            
        except Exception as e:
            self.logger.error(f"Ошибка вычисления релевантности паттерна: {e}")
            return 0.0
    
    def _save_pattern(self, pattern: LearningPattern):
        """Сохраняет паттерн в базу данных"""
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            cursor.execute('''
                INSERT OR REPLACE INTO learning_patterns 
                (pattern_id, context, action_sequence, success_rate, usage_count, 
                 last_used, confidence, tags)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?)
            ''', (
                pattern.pattern_id,
                json.dumps(pattern.context),
                json.dumps(pattern.action_sequence),
                pattern.success_rate,
                pattern.usage_count,
                pattern.last_used,
                pattern.confidence,
                json.dumps(pattern.tags)
            ))
            
            conn.commit()
            conn.close()
            
        except Exception as e:
            self.logger.error(f"Ошибка сохранения паттерна: {e}")
    
    def _save_adaptation_rule(self, rule: AdaptationRule):
        """Сохраняет правило адаптации в базу данных"""
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            cursor.execute('''
                INSERT OR REPLACE INTO adaptation_rules 
                (rule_id, condition, action, priority, success_count, failure_count, enabled)
                VALUES (?, ?, ?, ?, ?, ?, ?)
            ''', (
                rule.rule_id,
                json.dumps(rule.condition),
                json.dumps(rule.action),
                rule.priority,
                rule.success_count,
                rule.failure_count,
                rule.enabled
            ))
            
            conn.commit()
            conn.close()
            
        except Exception as e:
            self.logger.error(f"Ошибка сохранения правила адаптации: {e}")
    
    def get_learning_statistics(self) -> Dict:
        """Возвращает статистику обучения"""
        try:
            stats = dict(self.learning_stats)
            
            # Дополнительная статистика
            stats.update({
                'patterns_count': len(self.learned_patterns),
                'rules_count': len(self.adaptation_rules),
                'active_rules_count': len([r for r in self.adaptation_rules.values() if r.enabled]),
                'success_rate': (stats['successful_actions'] / max(1, stats['total_actions'])) * 100,
                'learning_mode': self.learning_mode.value,
                'learning_enabled': self.learning_enabled,
                'action_history_size': len(self.action_history),
                'feedback_history_size': len(self.feedback_history)
            })
            
            return stats
            
        except Exception as e:
            self.logger.error(f"Ошибка получения статистики обучения: {e}")
            return {}
    
    def set_learning_mode(self, mode: LearningMode):
        """Устанавливает режим обучения"""
        self.learning_mode = mode
        self.logger.info(f"Режим обучения изменен на: {mode.value}")
    
    def enable_learning(self, enabled: bool = True):
        """Включает/выключает обучение"""
        self.learning_enabled = enabled
        self.logger.info(f"Обучение {'включено' if enabled else 'выключено'}")
    
    def reset_learning_data(self):
        """Сбрасывает все данные обучения"""
        try:
            with self.learning_lock:
                # Очистка памяти
                self.learned_patterns.clear()
                self.adaptation_rules.clear()
                self.action_history.clear()
                self.feedback_history.clear()
                
                # Сброс статистики
                for key in self.learning_stats:
                    self.learning_stats[key] = 0
                
                # Очистка базы данных
                conn = sqlite3.connect(self.db_path)
                cursor = conn.cursor()
                
                cursor.execute('DELETE FROM action_results')
                cursor.execute('DELETE FROM learning_patterns')
                cursor.execute('DELETE FROM adaptation_rules')
                cursor.execute('DELETE FROM learning_stats')
                
                conn.commit()
                conn.close()
                
                self.logger.info("Все данные обучения сброшены")
            
        except Exception as e:
            self.logger.error(f"Ошибка сброса данных обучения: {e}")
    
    def export_learning_data(self, filepath: str) -> bool:
        """Экспортирует данные обучения в файл"""
        try:
            export_data = {
                'patterns': {pid: asdict(pattern) for pid, pattern in self.learned_patterns.items()},
                'rules': {rid: asdict(rule) for rid, rule in self.adaptation_rules.items()},
                'statistics': self.learning_stats,
                'export_timestamp': time.time()
            }
            
            with open(filepath, 'w', encoding='utf-8') as f:
                json.dump(export_data, f, indent=2, ensure_ascii=False)
            
            self.logger.info(f"Данные обучения экспортированы в: {filepath}")
            return True
            
        except Exception as e:
            self.logger.error(f"Ошибка экспорта данных обучения: {e}")
            return False
    
    def import_learning_data(self, filepath: str) -> bool:
        """Импортирует данные обучения из файла"""
        try:
            with open(filepath, 'r', encoding='utf-8') as f:
                import_data = json.load(f)
            
            # Импорт паттернов
            if 'patterns' in import_data:
                for pid, pattern_data in import_data['patterns'].items():
                    pattern = LearningPattern(**pattern_data)
                    self.learned_patterns[pid] = pattern
                    self._save_pattern(pattern)
            
            # Импорт правил
            if 'rules' in import_data:
                for rid, rule_data in import_data['rules'].items():
                    rule = AdaptationRule(**rule_data)
                    self.adaptation_rules[rid] = rule
                    self._save_adaptation_rule(rule)
            
            # Импорт статистики
            if 'statistics' in import_data:
                self.learning_stats.update(import_data['statistics'])
            
            self.logger.info(f"Данные обучения импортированы из: {filepath}")
            return True
            
        except Exception as e:
            self.logger.error(f"Ошибка импорта данных обучения: {e}")
            return False
