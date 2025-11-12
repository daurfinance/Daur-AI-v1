"""
Advanced Rate Limiting and DDoS Protection for Daur-AI v2.0
Продвинутое ограничение частоты запросов и защита от DDoS

Поддерживает:
- Ограничение частоты запросов по IP
- Ограничение частоты запросов по пользователю
- Обнаружение DDoS атак
- Блокировка подозрительных IP
- Адаптивная защита
- Анализ трафика
"""

import time
import logging
import threading
from typing import Dict, List, Tuple, Optional
from collections import defaultdict, deque
from dataclasses import dataclass
from datetime import datetime, timedelta
from enum import Enum

# Настройка логирования
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class ThreatLevel(Enum):
    """Уровни угрозы"""
    SAFE = "safe"
    WARNING = "warning"
    CRITICAL = "critical"


@dataclass
class RateLimitRule:
    """Правило ограничения частоты"""
    name: str
    max_requests: int
    time_window: int  # в секундах
    action: str = "block"  # block, delay, challenge


@dataclass
class IPInfo:
    """Информация об IP адресе"""
    ip: str
    requests: deque  # времена последних запросов
    blocked: bool = False
    threat_level: ThreatLevel = ThreatLevel.SAFE
    last_request: float = 0
    total_requests: int = 0
    suspicious_patterns: int = 0


class AdvancedRateLimiter:
    """Продвинутое ограничение частоты запросов"""
    
    def __init__(self, max_history: int = 10000):
        """
        Инициализация ограничителя
        
        Args:
            max_history: Максимальный размер истории
        """
        self.rules: Dict[str, RateLimitRule] = {}
        self.ip_tracker: Dict[str, IPInfo] = {}
        self.user_tracker: Dict[str, deque] = defaultdict(lambda: deque(maxlen=1000))
        self.blocked_ips: set = set()
        self.whitelist_ips: set = set()
        self.lock = threading.Lock()
        self.max_history = max_history
        
        # Правила по умолчанию
        self._setup_default_rules()
        
        logger.info("Advanced Rate Limiter initialized")
    
    def _setup_default_rules(self):
        """Установить правила по умолчанию"""
        # Общее ограничение: 1000 запросов в минуту
        self.add_rule(RateLimitRule(
            name="global",
            max_requests=1000,
            time_window=60,
            action="block"
        ))
        
        # API: 100 запросов в минуту
        self.add_rule(RateLimitRule(
            name="api",
            max_requests=100,
            time_window=60,
            action="block"
        ))
        
        # Логин: 10 попыток в час
        self.add_rule(RateLimitRule(
            name="login",
            max_requests=10,
            time_window=3600,
            action="block"
        ))
        
        # Регистрация: 5 попыток в час
        self.add_rule(RateLimitRule(
            name="register",
            max_requests=5,
            time_window=3600,
            action="block"
        ))
    
    def add_rule(self, rule: RateLimitRule) -> bool:
        """Добавить правило"""
        with self.lock:
            self.rules[rule.name] = rule
            logger.info(f"Rate limit rule added: {rule.name}")
            return True
    
    def check_limit(self, rule_name: str, identifier: str, 
                    ip_address: str = None) -> Tuple[bool, Optional[str]]:
        """
        Проверить ограничение
        
        Args:
            rule_name: Имя правила
            identifier: Идентификатор (IP или user_id)
            ip_address: IP адрес (опционально)
        
        Returns:
            (allowed, reason)
        """
        with self.lock:
            # Проверяем белый список
            if ip_address and ip_address in self.whitelist_ips:
                return True, None
            
            # Проверяем черный список
            if ip_address and ip_address in self.blocked_ips:
                return False, f"IP {ip_address} is blocked"
            
            # Получаем правило
            if rule_name not in self.rules:
                logger.warning(f"Rule not found: {rule_name}")
                return True, None
            
            rule = self.rules[rule_name]
            
            # Получаем трекер
            if rule_name.startswith("ip_"):
                tracker = self.ip_tracker.get(identifier, deque(maxlen=rule.max_requests * 2))
            else:
                tracker = self.user_tracker[identifier]
            
            # Текущее время
            now = time.time()
            
            # Удаляем старые запросы
            while tracker and tracker[0] < now - rule.time_window:
                tracker.popleft()
            
            # Проверяем лимит
            if len(tracker) >= rule.max_requests:
                logger.warning(f"Rate limit exceeded for {identifier} on rule {rule_name}")
                
                # Блокируем IP если нужно
                if ip_address:
                    self.blocked_ips.add(ip_address)
                    logger.warning(f"IP blocked: {ip_address}")
                
                return False, f"Rate limit exceeded for {rule_name}"
            
            # Добавляем текущий запрос
            tracker.append(now)
            
            # Обновляем трекер
            if rule_name.startswith("ip_"):
                self.ip_tracker[identifier] = tracker
            else:
                self.user_tracker[identifier] = tracker
            
            return True, None
    
    def is_ip_blocked(self, ip_address: str) -> bool:
        """Проверить, заблокирован ли IP"""
        with self.lock:
            return ip_address in self.blocked_ips
    
    def block_ip(self, ip_address: str, reason: str = "") -> bool:
        """Заблокировать IP"""
        with self.lock:
            self.blocked_ips.add(ip_address)
            logger.warning(f"IP blocked: {ip_address}. Reason: {reason}")
            return True
    
    def unblock_ip(self, ip_address: str) -> bool:
        """Разблокировать IP"""
        with self.lock:
            if ip_address in self.blocked_ips:
                self.blocked_ips.remove(ip_address)
                logger.info(f"IP unblocked: {ip_address}")
                return True
            return False
    
    def whitelist_ip(self, ip_address: str) -> bool:
        """Добавить IP в белый список"""
        with self.lock:
            self.whitelist_ips.add(ip_address)
            logger.info(f"IP whitelisted: {ip_address}")
            return True
    
    def get_blocked_ips(self) -> List[str]:
        """Получить список заблокированных IP"""
        with self.lock:
            return list(self.blocked_ips)
    
    def get_statistics(self) -> Dict:
        """Получить статистику"""
        with self.lock:
            return {
                'total_ips_tracked': len(self.ip_tracker),
                'total_users_tracked': len(self.user_tracker),
                'blocked_ips': len(self.blocked_ips),
                'whitelisted_ips': len(self.whitelist_ips),
                'rules_count': len(self.rules)
            }


class DDoSDetector:
    """Обнаружение DDoS атак"""
    
    def __init__(self, window_size: int = 60, threshold: int = 1000):
        """
        Инициализация детектора
        
        Args:
            window_size: Размер временного окна в секундах
            threshold: Порог для обнаружения атаки
        """
        self.window_size = window_size
        self.threshold = threshold
        self.request_history: deque = deque(maxlen=threshold * 2)
        self.ip_request_count: Dict[str, int] = defaultdict(int)
        self.lock = threading.Lock()
        self.under_attack = False
        self.attack_start_time: Optional[float] = None
        
        logger.info(f"DDoS Detector initialized (threshold: {threshold})")
    
    def record_request(self, ip_address: str) -> bool:
        """Записать запрос"""
        with self.lock:
            now = time.time()
            self.request_history.append((ip_address, now))
            self.ip_request_count[ip_address] += 1
            
            # Удаляем старые записи
            while self.request_history and self.request_history[0][1] < now - self.window_size:
                old_ip, _ = self.request_history.popleft()
                self.ip_request_count[old_ip] -= 1
                if self.ip_request_count[old_ip] <= 0:
                    del self.ip_request_count[old_ip]
            
            return True
    
    def detect_attack(self) -> bool:
        """Обнаружить атаку"""
        with self.lock:
            request_count = len(self.request_history)
            
            # Проверяем общее количество запросов
            if request_count > self.threshold:
                if not self.under_attack:
                    self.under_attack = True
                    self.attack_start_time = time.time()
                    logger.critical(f"DDoS ATTACK DETECTED! Requests: {request_count}")
                return True
            else:
                if self.under_attack:
                    duration = time.time() - self.attack_start_time
                    logger.info(f"DDoS attack ended. Duration: {duration}s")
                    self.under_attack = False
                return False
    
    def get_suspicious_ips(self, top_n: int = 10) -> List[Tuple[str, int]]:
        """Получить подозрительные IP"""
        with self.lock:
            sorted_ips = sorted(
                self.ip_request_count.items(),
                key=lambda x: x[1],
                reverse=True
            )
            return sorted_ips[:top_n]
    
    def get_threat_level(self) -> ThreatLevel:
        """Получить уровень угрозы"""
        with self.lock:
            request_count = len(self.request_history)
            
            if request_count > self.threshold * 1.5:
                return ThreatLevel.CRITICAL
            elif request_count > self.threshold * 0.75:
                return ThreatLevel.WARNING
            else:
                return ThreatLevel.SAFE
    
    def get_statistics(self) -> Dict:
        """Получить статистику"""
        with self.lock:
            return {
                'total_requests': len(self.request_history),
                'unique_ips': len(self.ip_request_count),
                'under_attack': self.under_attack,
                'threat_level': self.get_threat_level().value,
                'top_ips': self.get_suspicious_ips(5)
            }


class SecurityMonitor:
    """Комплексный монитор безопасности"""
    
    def __init__(self):
        """Инициализация"""
        self.rate_limiter = AdvancedRateLimiter()
        self.ddos_detector = DDoSDetector()
        self.lock = threading.Lock()
        
        logger.info("Security Monitor initialized")
    
    def check_request(self, ip_address: str, user_id: Optional[str] = None,
                     endpoint: str = "api") -> Tuple[bool, Optional[str]]:
        """
        Проверить безопасность запроса
        
        Args:
            ip_address: IP адрес
            user_id: ID пользователя (опционально)
            endpoint: Endpoint (api, login, register)
        
        Returns:
            (allowed, reason)
        """
        # Записываем в DDoS детектор
        self.ddos_detector.record_request(ip_address)
        
        # Проверяем DDoS
        if self.ddos_detector.detect_attack():
            suspicious_ips = self.ddos_detector.get_suspicious_ips(1)
            if suspicious_ips and suspicious_ips[0][0] == ip_address:
                return False, "Possible DDoS attack detected"
        
        # Проверяем rate limit
        allowed, reason = self.rate_limiter.check_limit(endpoint, ip_address, ip_address)
        
        if not allowed:
            return False, reason
        
        return True, None
    
    def get_security_status(self) -> Dict:
        """Получить статус безопасности"""
        return {
            'rate_limiter': self.rate_limiter.get_statistics(),
            'ddos_detector': self.ddos_detector.get_statistics(),
            'threat_level': self.ddos_detector.get_threat_level().value
        }
