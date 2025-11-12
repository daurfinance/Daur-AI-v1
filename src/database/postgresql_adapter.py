"""
PostgreSQL Adapter for Daur-AI v2.0
Адаптер PostgreSQL с пулингом соединений

Поддерживает:
- Подключение к PostgreSQL
- Пулинг соединений
- Миграции
- Транзакции
- Полная совместимость с SQLite API
"""

import logging
import os
from typing import Optional, List, Dict, Any
from contextlib import contextmanager
from dataclasses import dataclass

# Настройка логирования
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Попытка импортировать psycopg2
try:
    import psycopg2
    from psycopg2 import pool, sql
    PSYCOPG2_AVAILABLE = True
except ImportError:
    PSYCOPG2_AVAILABLE = False
    logger.warning("psycopg2 not available. Install with: pip install psycopg2-binary")


@dataclass
class PostgreSQLConfig:
    """Конфигурация PostgreSQL"""
    host: str = "localhost"
    port: int = 5432
    database: str = "daur_ai"
    user: str = "postgres"
    password: str = "postgres"
    min_connections: int = 2
    max_connections: int = 10


class PostgreSQLAdapter:
    """Адаптер PostgreSQL с пулингом"""
    
    def __init__(self, config: Optional[PostgreSQLConfig] = None):
        """
        Инициализация адаптера
        
        Args:
            config: Конфигурация PostgreSQL
        """
        if not PSYCOPG2_AVAILABLE:
            raise ImportError("psycopg2 is required. Install with: pip install psycopg2-binary")
        
        self.config = config or PostgreSQLConfig()
        self.connection_pool = None
        self.initialized = False
        
        self._init_pool()
        logger.info(f"PostgreSQL Adapter initialized: {self.config.host}:{self.config.port}/{self.config.database}")
    
    def _init_pool(self):
        """Инициализировать пул соединений"""
        try:
            self.connection_pool = psycopg2.pool.SimpleConnectionPool(
                self.config.min_connections,
                self.config.max_connections,
                host=self.config.host,
                port=self.config.port,
                database=self.config.database,
                user=self.config.user,
                password=self.config.password
            )
            self.initialized = True
            logger.info(f"Connection pool created: {self.config.min_connections}-{self.config.max_connections} connections")
        except Exception as e:
            logger.error(f"Failed to create connection pool: {e}")
            self.initialized = False
    
    @contextmanager
    def get_connection(self):
        """Получить соединение из пула"""
        if not self.initialized:
            raise RuntimeError("PostgreSQL adapter not initialized")
        
        conn = None
        try:
            conn = self.connection_pool.getconn()
            yield conn
            conn.commit()
        except Exception as e:
            if conn:
                conn.rollback()
            logger.error(f"Database error: {e}")
            raise
        finally:
            if conn:
                self.connection_pool.putconn(conn)
    
    def execute(self, query: str, params: tuple = None) -> List[Dict]:
        """Выполнить запрос"""
        with self.get_connection() as conn:
            with conn.cursor() as cur:
                cur.execute(query, params or ())
                
                # Если это SELECT запрос
                if cur.description:
                    columns = [desc[0] for desc in cur.description]
                    rows = cur.fetchall()
                    return [dict(zip(columns, row)) for row in rows]
                
                return []
    
    def execute_one(self, query: str, params: tuple = None) -> Optional[Dict]:
        """Выполнить запрос и получить одну строку"""
        results = self.execute(query, params)
        return results[0] if results else None
    
    def insert(self, table: str, data: Dict) -> int:
        """Вставить данные"""
        columns = list(data.keys())
        values = list(data.values())
        
        query = sql.SQL("INSERT INTO {} ({}) VALUES ({}) RETURNING id").format(
            sql.Identifier(table),
            sql.SQL(", ").join(map(sql.Identifier, columns)),
            sql.SQL(", ").join(["%s"] * len(columns))
        )
        
        result = self.execute_one(query.as_string(psycopg2.extensions.connection()), tuple(values))
        return result['id'] if result else None
    
    def update(self, table: str, data: Dict, where: Dict) -> int:
        """Обновить данные"""
        set_clause = ", ".join([f"{k} = %s" for k in data.keys()])
        where_clause = " AND ".join([f"{k} = %s" for k in where.keys()])
        
        query = f"UPDATE {table} SET {set_clause} WHERE {where_clause}"
        params = tuple(list(data.values()) + list(where.values()))
        
        with self.get_connection() as conn:
            with conn.cursor() as cur:
                cur.execute(query, params)
                return cur.rowcount
    
    def delete(self, table: str, where: Dict) -> int:
        """Удалить данные"""
        where_clause = " AND ".join([f"{k} = %s" for k in where.keys()])
        query = f"DELETE FROM {table} WHERE {where_clause}"
        params = tuple(where.values())
        
        with self.get_connection() as conn:
            with conn.cursor() as cur:
                cur.execute(query, params)
                return cur.rowcount
    
    def select(self, table: str, where: Dict = None, limit: int = None) -> List[Dict]:
        """Выбрать данные"""
        query = f"SELECT * FROM {table}"
        params = []
        
        if where:
            where_clause = " AND ".join([f"{k} = %s" for k in where.keys()])
            query += f" WHERE {where_clause}"
            params = list(where.values())
        
        if limit:
            query += f" LIMIT {limit}"
        
        return self.execute(query, tuple(params))
    
    def init_database(self):
        """Инициализировать базу данных"""
        try:
            with self.get_connection() as conn:
                with conn.cursor() as cur:
                    # Создаём таблицы
                    cur.execute("""
                        CREATE TABLE IF NOT EXISTS users (
                            id SERIAL PRIMARY KEY,
                            username VARCHAR(255) UNIQUE NOT NULL,
                            email VARCHAR(255) UNIQUE NOT NULL,
                            password_hash VARCHAR(255) NOT NULL,
                            role VARCHAR(50) DEFAULT 'user',
                            api_key VARCHAR(255) UNIQUE,
                            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                        )
                    """)
                    
                    cur.execute("""
                        CREATE TABLE IF NOT EXISTS logs (
                            id SERIAL PRIMARY KEY,
                            user_id INTEGER REFERENCES users(id),
                            action VARCHAR(255),
                            details TEXT,
                            timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                        )
                    """)
                    
                    cur.execute("""
                        CREATE TABLE IF NOT EXISTS hardware_metrics (
                            id SERIAL PRIMARY KEY,
                            cpu_percent FLOAT,
                            memory_percent FLOAT,
                            disk_percent FLOAT,
                            gpu_percent FLOAT,
                            battery_percent FLOAT,
                            network_bytes_sent BIGINT,
                            timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                        )
                    """)
                    
                    cur.execute("""
                        CREATE TABLE IF NOT EXISTS vision_analysis (
                            id SERIAL PRIMARY KEY,
                            user_id INTEGER REFERENCES users(id),
                            analysis_type VARCHAR(50),
                            result TEXT,
                            confidence FLOAT,
                            timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                        )
                    """)
                    
                    logger.info("Database initialized successfully")
                    return True
        
        except Exception as e:
            logger.error(f"Error initializing database: {e}")
            return False
    
    def close(self):
        """Закрыть пул соединений"""
        if self.connection_pool:
            self.connection_pool.closeall()
            logger.info("Connection pool closed")


class PostgreSQLDatabase:
    """Полная база данных на PostgreSQL"""
    
    def __init__(self, config: Optional[PostgreSQLConfig] = None):
        """Инициализация"""
        self.adapter = PostgreSQLAdapter(config)
        self.adapter.init_database()
    
    # Методы пользователей
    def insert_user(self, username: str, email: str, password_hash: str, role: str = "user") -> int:
        """Вставить пользователя"""
        return self.adapter.insert("users", {
            "username": username,
            "email": email,
            "password_hash": password_hash,
            "role": role
        })
    
    def get_user_by_username(self, username: str) -> Optional[Dict]:
        """Получить пользователя по имени"""
        return self.adapter.execute_one(
            "SELECT * FROM users WHERE username = %s",
            (username,)
        )
    
    def get_user_by_id(self, user_id: int) -> Optional[Dict]:
        """Получить пользователя по ID"""
        return self.adapter.execute_one(
            "SELECT * FROM users WHERE id = %s",
            (user_id,)
        )
    
    # Методы логирования
    def insert_log(self, user_id: int, action: str, details: str = "") -> int:
        """Вставить лог"""
        return self.adapter.insert("logs", {
            "user_id": user_id,
            "action": action,
            "details": details
        })
    
    def get_logs(self, user_id: int = None, limit: int = 100) -> List[Dict]:
        """Получить логи"""
        if user_id:
            return self.adapter.execute(
                "SELECT * FROM logs WHERE user_id = %s ORDER BY timestamp DESC LIMIT %s",
                (user_id, limit)
            )
        else:
            return self.adapter.execute(
                "SELECT * FROM logs ORDER BY timestamp DESC LIMIT %s",
                (limit,)
            )
    
    # Методы метрик
    def insert_hardware_metrics(self, cpu: float, memory: float, disk: float,
                               gpu: float = 0, battery: float = 0, 
                               network_sent: int = 0) -> int:
        """Вставить метрики"""
        return self.adapter.insert("hardware_metrics", {
            "cpu_percent": cpu,
            "memory_percent": memory,
            "disk_percent": disk,
            "gpu_percent": gpu,
            "battery_percent": battery,
            "network_bytes_sent": network_sent
        })
    
    def get_hardware_metrics(self, limit: int = 100) -> List[Dict]:
        """Получить метрики"""
        return self.adapter.execute(
            "SELECT * FROM hardware_metrics ORDER BY timestamp DESC LIMIT %s",
            (limit,)
        )
    
    def get_average_metrics(self, hours: int = 1) -> Optional[Dict]:
        """Получить средние метрики за период"""
        return self.adapter.execute_one(
            """
            SELECT 
                AVG(cpu_percent) as avg_cpu,
                AVG(memory_percent) as avg_memory,
                AVG(disk_percent) as avg_disk,
                MAX(cpu_percent) as max_cpu,
                MAX(memory_percent) as max_memory
            FROM hardware_metrics
            WHERE timestamp > NOW() - INTERVAL '%s hours'
            """,
            (hours,)
        )
    
    # Методы анализа видения
    def insert_vision_analysis(self, user_id: int, analysis_type: str,
                              result: str, confidence: float = 0.0) -> int:
        """Вставить анализ видения"""
        return self.adapter.insert("vision_analysis", {
            "user_id": user_id,
            "analysis_type": analysis_type,
            "result": result,
            "confidence": confidence
        })
    
    def get_vision_analysis(self, user_id: int = None, limit: int = 100) -> List[Dict]:
        """Получить анализы видения"""
        if user_id:
            return self.adapter.execute(
                "SELECT * FROM vision_analysis WHERE user_id = %s ORDER BY timestamp DESC LIMIT %s",
                (user_id, limit)
            )
        else:
            return self.adapter.execute(
                "SELECT * FROM vision_analysis ORDER BY timestamp DESC LIMIT %s",
                (limit,)
            )
    
    def close(self):
        """Закрыть соединение"""
        self.adapter.close()
