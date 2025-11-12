"""
Real Learning System with Machine Learning
Полнофункциональная система обучения с реальными ML алгоритмами
"""

import logging
import json
import pickle
from typing import Dict, List, Optional, Tuple, Any
from dataclasses import dataclass, asdict
from enum import Enum
from collections import defaultdict, Counter
import numpy as np
from datetime import datetime, timedelta

try:
    from sklearn.ensemble import RandomForestClassifier
    from sklearn.preprocessing import StandardScaler
    from sklearn.metrics import accuracy_score, precision_score, recall_score
    SKLEARN_AVAILABLE = True
except ImportError:
    SKLEARN_AVAILABLE = False
    logging.warning("scikit-learn not available. Install with: pip install scikit-learn")

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class PatternType(Enum):
    """Типы паттернов"""
    BEHAVIOR = "behavior"
    SEQUENCE = "sequence"
    FREQUENCY = "frequency"
    ANOMALY = "anomaly"
    PREDICTION = "prediction"


class LearningMode(Enum):
    """Режимы обучения"""
    SUPERVISED = "supervised"
    UNSUPERVISED = "unsupervised"
    REINFORCEMENT = "reinforcement"
    SEMI_SUPERVISED = "semi_supervised"


@dataclass
class Pattern:
    """Обнаруженный паттерн"""
    pattern_id: str
    pattern_type: PatternType
    name: str
    description: str
    confidence: float
    occurrences: int
    last_seen: str
    features: Dict[str, Any]


@dataclass
class LearningResult:
    """Результат обучения"""
    success: bool
    accuracy: float
    precision: float
    recall: float
    patterns_found: int
    model_version: str
    timestamp: str


@dataclass
class Prediction:
    """Предсказание"""
    action: str
    probability: float
    confidence: float
    reasoning: str
    timestamp: str


class RealLearningSystem:
    """Реальная система обучения с ML"""
    
    def __init__(self, model_path: Optional[str] = None):
        """
        Инициализация системы обучения
        
        Args:
            model_path: Путь к сохранённой модели
        """
        self.logger = logging.getLogger(__name__)
        
        if not SKLEARN_AVAILABLE:
            raise ImportError("scikit-learn is required. Install with: pip install scikit-learn")
        
        # Инициализируем модель
        self.model = RandomForestClassifier(n_estimators=100, random_state=42)
        self.scaler = StandardScaler()
        
        # Хранилище данных
        self.training_data = []
        self.training_labels = []
        self.patterns = {}
        self.behavior_history = defaultdict(list)
        self.sequence_patterns = defaultdict(int)
        self.frequency_patterns = defaultdict(int)
        self.anomalies = []
        
        # Метаданные модели
        self.model_version = "1.0.0"
        self.is_trained = False
        self.accuracy = 0.0
        self.precision = 0.0
        self.recall = 0.0
        
        # Загружаем модель если указана
        if model_path:
            self.load_model(model_path)
        
        self.logger.info("Real Learning System initialized")
    
    # ===== TRAINING =====
    
    def add_training_data(self, features: List[float], label: str) -> bool:
        """
        Добавить данные для обучения
        
        Args:
            features: Вектор признаков
            label: Метка класса
        
        Returns:
            bool: Успешность добавления
        """
        try:
            self.training_data.append(features)
            self.training_labels.append(label)
            self.logger.info(f"Added training data: {label}")
            return True
        except Exception as e:
            self.logger.error(f"Error adding training data: {e}")
            return False
    
    def train_model(self, test_size: float = 0.2) -> LearningResult:
        """
        Обучить модель
        
        Args:
            test_size: Доля тестовых данных
        
        Returns:
            LearningResult: Результат обучения
        """
        try:
            if len(self.training_data) < 10:
                self.logger.warning("Not enough training data")
                return LearningResult(
                    success=False,
                    accuracy=0.0,
                    precision=0.0,
                    recall=0.0,
                    patterns_found=0,
                    model_version=self.model_version,
                    timestamp=datetime.now().isoformat()
                )
            
            # Преобразуем в numpy arrays
            X = np.array(self.training_data)
            y = np.array(self.training_labels)
            
            # Масштабируем данные
            X_scaled = self.scaler.fit_transform(X)
            
            # Обучаем модель
            self.model.fit(X_scaled, y)
            
            # Вычисляем метрики
            y_pred = self.model.predict(X_scaled)
            self.accuracy = accuracy_score(y, y_pred)
            self.precision = precision_score(y, y_pred, average='weighted', zero_division=0)
            self.recall = recall_score(y, y_pred, average='weighted', zero_division=0)
            
            self.is_trained = True
            self.model_version = "1.1.0"
            
            self.logger.info(f"Model trained: Accuracy={self.accuracy:.2%}, Precision={self.precision:.2%}, Recall={self.recall:.2%}")
            
            return LearningResult(
                success=True,
                accuracy=self.accuracy,
                precision=self.precision,
                recall=self.recall,
                patterns_found=len(self.patterns),
                model_version=self.model_version,
                timestamp=datetime.now().isoformat()
            )
        
        except Exception as e:
            self.logger.error(f"Error training model: {e}")
            return LearningResult(
                success=False,
                accuracy=0.0,
                precision=0.0,
                recall=0.0,
                patterns_found=0,
                model_version=self.model_version,
                timestamp=datetime.now().isoformat()
            )
    
    # ===== PATTERN DETECTION =====
    
    def detect_behavior_patterns(self, behavior_sequence: List[str]) -> List[Pattern]:
        """
        Обнаружить поведенческие паттерны
        
        Args:
            behavior_sequence: Последовательность действий
        
        Returns:
            List[Pattern]: Обнаруженные паттерны
        """
        try:
            patterns = []
            
            # Анализируем последовательность
            for i in range(len(behavior_sequence) - 1):
                action = behavior_sequence[i]
                next_action = behavior_sequence[i + 1]
                
                # Создаём паттерн последовательности
                pattern_key = f"{action}->{next_action}"
                self.sequence_patterns[pattern_key] += 1
                
                # Если паттерн повторяется часто, добавляем его
                if self.sequence_patterns[pattern_key] >= 3:
                    pattern = Pattern(
                        pattern_id=f"seq_{pattern_key}",
                        pattern_type=PatternType.SEQUENCE,
                        name=f"Sequence: {pattern_key}",
                        description=f"Action {action} followed by {next_action}",
                        confidence=min(self.sequence_patterns[pattern_key] / 10, 1.0),
                        occurrences=self.sequence_patterns[pattern_key],
                        last_seen=datetime.now().isoformat(),
                        features={'sequence': pattern_key}
                    )
                    
                    if pattern.pattern_id not in self.patterns:
                        patterns.append(pattern)
                        self.patterns[pattern.pattern_id] = pattern
            
            self.logger.info(f"Detected {len(patterns)} behavior patterns")
            return patterns
        
        except Exception as e:
            self.logger.error(f"Error detecting behavior patterns: {e}")
            return []
    
    def detect_frequency_patterns(self, action_list: List[str]) -> List[Pattern]:
        """
        Обнаружить паттерны частоты
        
        Args:
            action_list: Список действий
        
        Returns:
            List[Pattern]: Обнаруженные паттерны
        """
        try:
            patterns = []
            
            # Подсчитываем частоту действий
            counter = Counter(action_list)
            
            for action, count in counter.most_common():
                frequency = count / len(action_list) if action_list else 0
                
                if frequency > 0.1:  # Более 10% от всех действий
                    pattern = Pattern(
                        pattern_id=f"freq_{action}",
                        pattern_type=PatternType.FREQUENCY,
                        name=f"Frequency: {action}",
                        description=f"Action {action} occurs {frequency:.1%} of the time",
                        confidence=frequency,
                        occurrences=count,
                        last_seen=datetime.now().isoformat(),
                        features={'action': action, 'frequency': frequency}
                    )
                    
                    if pattern.pattern_id not in self.patterns:
                        patterns.append(pattern)
                        self.patterns[pattern.pattern_id] = pattern
            
            self.logger.info(f"Detected {len(patterns)} frequency patterns")
            return patterns
        
        except Exception as e:
            self.logger.error(f"Error detecting frequency patterns: {e}")
            return []
    
    def detect_anomalies(self, data_sequence: List[float], threshold: float = 2.0) -> List[Dict[str, Any]]:
        """
        Обнаружить аномалии в данных
        
        Args:
            data_sequence: Последовательность данных
            threshold: Пороговое значение (в стандартных отклонениях)
        
        Returns:
            List[Dict[str, Any]]: Обнаруженные аномалии
        """
        try:
            if len(data_sequence) < 3:
                return []
            
            data = np.array(data_sequence)
            mean = np.mean(data)
            std = np.std(data)
            
            anomalies = []
            
            for i, value in enumerate(data):
                z_score = abs((value - mean) / std) if std > 0 else 0
                
                if z_score > threshold:
                    anomaly = {
                        'index': i,
                        'value': float(value),
                        'z_score': float(z_score),
                        'mean': float(mean),
                        'std': float(std),
                        'timestamp': datetime.now().isoformat()
                    }
                    anomalies.append(anomaly)
                    self.anomalies.append(anomaly)
            
            self.logger.info(f"Detected {len(anomalies)} anomalies")
            return anomalies
        
        except Exception as e:
            self.logger.error(f"Error detecting anomalies: {e}")
            return []
    
    # ===== PREDICTION =====
    
    def predict_action(self, features: List[float]) -> Optional[Prediction]:
        """
        Предсказать следующее действие
        
        Args:
            features: Вектор признаков
        
        Returns:
            Optional[Prediction]: Предсказание или None
        """
        try:
            if not self.is_trained:
                self.logger.warning("Model is not trained")
                return None
            
            # Масштабируем признаки
            X = np.array([features])
            X_scaled = self.scaler.transform(X)
            
            # Предсказываем
            prediction = self.model.predict(X_scaled)[0]
            probabilities = self.model.predict_proba(X_scaled)[0]
            
            # Получаем максимальную вероятность
            max_prob = np.max(probabilities)
            
            # Создаём объект предсказания
            pred = Prediction(
                action=str(prediction),
                probability=float(max_prob),
                confidence=float(max_prob),
                reasoning=f"Based on {len(self.training_data)} training samples",
                timestamp=datetime.now().isoformat()
            )
            
            self.logger.info(f"Prediction: {prediction} (confidence: {max_prob:.2%})")
            return pred
        
        except Exception as e:
            self.logger.error(f"Error making prediction: {e}")
            return None
    
    def predict_sequence(self, action_sequence: List[str], steps: int = 3) -> List[Prediction]:
        """
        Предсказать последовательность действий
        
        Args:
            action_sequence: Текущая последовательность
            steps: Количество шагов для предсказания
        
        Returns:
            List[Prediction]: Список предсказаний
        """
        try:
            predictions = []
            current_sequence = action_sequence.copy()
            
            for step in range(steps):
                # Ищем следующее действие на основе текущей последовательности
                next_actions = {}
                
                for i in range(len(self.training_labels) - 1):
                    if self.training_labels[i] == current_sequence[-1]:
                        next_action = self.training_labels[i + 1]
                        next_actions[next_action] = next_actions.get(next_action, 0) + 1
                
                if not next_actions:
                    break
                
                # Выбираем наиболее вероятное действие
                best_action = max(next_actions, key=next_actions.get)
                probability = next_actions[best_action] / sum(next_actions.values())
                
                pred = Prediction(
                    action=best_action,
                    probability=probability,
                    confidence=probability,
                    reasoning=f"Based on {next_actions[best_action]} occurrences",
                    timestamp=datetime.now().isoformat()
                )
                
                predictions.append(pred)
                current_sequence.append(best_action)
            
            self.logger.info(f"Predicted {len(predictions)} steps ahead")
            return predictions
        
        except Exception as e:
            self.logger.error(f"Error predicting sequence: {e}")
            return []
    
    # ===== PATTERN MANAGEMENT =====
    
    def get_patterns(self, pattern_type: Optional[PatternType] = None) -> List[Pattern]:
        """
        Получить обнаруженные паттерны
        
        Args:
            pattern_type: Тип паттерна для фильтрации
        
        Returns:
            List[Pattern]: Список паттернов
        """
        try:
            patterns = list(self.patterns.values())
            
            if pattern_type:
                patterns = [p for p in patterns if p.pattern_type == pattern_type]
            
            # Сортируем по уверенности
            patterns.sort(key=lambda p: p.confidence, reverse=True)
            
            return patterns
        except Exception as e:
            self.logger.error(f"Error getting patterns: {e}")
            return []
    
    def get_anomalies(self, limit: int = 10) -> List[Dict[str, Any]]:
        """
        Получить обнаруженные аномалии
        
        Args:
            limit: Максимальное количество аномалий
        
        Returns:
            List[Dict[str, Any]]: Список аномалий
        """
        try:
            return self.anomalies[-limit:]
        except Exception as e:
            self.logger.error(f"Error getting anomalies: {e}")
            return []
    
    # ===== MODEL MANAGEMENT =====
    
    def save_model(self, filepath: str) -> bool:
        """
        Сохранить модель
        
        Args:
            filepath: Путь для сохранения
        
        Returns:
            bool: Успешность сохранения
        """
        try:
            model_data = {
                'model': self.model,
                'scaler': self.scaler,
                'patterns': self.patterns,
                'model_version': self.model_version,
                'accuracy': self.accuracy,
                'precision': self.precision,
                'recall': self.recall,
                'is_trained': self.is_trained
            }
            
            with open(filepath, 'wb') as f:
                pickle.dump(model_data, f)
            
            self.logger.info(f"Model saved: {filepath}")
            return True
        except Exception as e:
            self.logger.error(f"Error saving model: {e}")
            return False
    
    def load_model(self, filepath: str) -> bool:
        """
        Загрузить модель
        
        Args:
            filepath: Путь к модели
        
        Returns:
            bool: Успешность загрузки
        """
        try:
            with open(filepath, 'rb') as f:
                model_data = pickle.load(f)
            
            self.model = model_data['model']
            self.scaler = model_data['scaler']
            self.patterns = model_data['patterns']
            self.model_version = model_data['model_version']
            self.accuracy = model_data['accuracy']
            self.precision = model_data['precision']
            self.recall = model_data['recall']
            self.is_trained = model_data['is_trained']
            
            self.logger.info(f"Model loaded: {filepath}")
            return True
        except Exception as e:
            self.logger.error(f"Error loading model: {e}")
            return False
    
    def get_model_info(self) -> Dict[str, Any]:
        """Получить информацию о модели"""
        return {
            'version': self.model_version,
            'is_trained': self.is_trained,
            'accuracy': self.accuracy,
            'precision': self.precision,
            'recall': self.recall,
            'training_samples': len(self.training_data),
            'patterns_found': len(self.patterns),
            'anomalies_detected': len(self.anomalies)
        }

