"""
Production-Grade Database Module for Daur-AI v2.0
"""

import sqlite3
import json
import logging
from datetime import datetime
from typing import Dict, List, Optional
from contextlib import contextmanager

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class ProductionDatabase:
    """Полнофункциональная база данных"""
    
    def __init__(self, db_path: str = 'daur_ai.db'):
        self.db_path = db_path
        self.init_database()
    
    @contextmanager
    def get_connection(self):
        """Контекстный менеджер для подключения"""
        conn = sqlite3.connect(self.db_path)
        conn.row_factory = sqlite3.Row
        try:
            yield conn
            conn.commit()
        except Exception as e:
            conn.rollback()
            logger.error(f"Database error: {e}")
            raise
        finally:
            conn.close()
    
    def init_database(self):
        """Инициализировать базу данных"""
        try:
            with self.get_connection() as conn:
                cursor = conn.cursor()
                
                # Таблица пользователей
                cursor.execute('''
                    CREATE TABLE IF NOT EXISTS users (
                        id INTEGER PRIMARY KEY,
                        username TEXT UNIQUE NOT NULL,
                        email TEXT UNIQUE NOT NULL,
                        role TEXT DEFAULT 'user',
                        created_at TEXT,
                        last_login TEXT
                    )
                ''')
                
                # Таблица логов
                cursor.execute('''
                    CREATE TABLE IF NOT EXISTS logs (
                        id INTEGER PRIMARY KEY,
                        timestamp TEXT,
                        level TEXT,
                        message TEXT,
                        user_id INTEGER,
                        FOREIGN KEY (user_id) REFERENCES users(id)
                    )
                ''')
                
                # Таблица метрик оборудования
                cursor.execute('''
                    CREATE TABLE IF NOT EXISTS hardware_metrics (
                        id INTEGER PRIMARY KEY,
                        timestamp TEXT,
                        cpu_percent REAL,
                        memory_percent REAL,
                        disk_percent REAL,
                        gpu_percent REAL
                    )
                ''')
                
                # Таблица анализов изображений
                cursor.execute('''
                    CREATE TABLE IF NOT EXISTS vision_analysis (
                        id INTEGER PRIMARY KEY,
                        timestamp TEXT,
                        image_path TEXT,
                        ocr_text TEXT,
                        faces_count INTEGER,
                        barcodes_count INTEGER,
                        user_id INTEGER,
                        FOREIGN KEY (user_id) REFERENCES users(id)
                    )
                ''')
                
                # Таблица действий пользователя
                cursor.execute('''
                    CREATE TABLE IF NOT EXISTS user_actions (
                        id INTEGER PRIMARY KEY,
                        timestamp TEXT,
                        action_type TEXT,
                        action_data TEXT,
                        user_id INTEGER,
                        FOREIGN KEY (user_id) REFERENCES users(id)
                    )
                ''')
                
                logger.info("Database initialized successfully")
        
        except Exception as e:
            logger.error(f"Error initializing database: {e}")
    
    def insert_user(self, username: str, email: str, role: str = 'user') -> bool:
        """Добавить пользователя"""
        try:
            with self.get_connection() as conn:
                cursor = conn.cursor()
                cursor.execute('''
                    INSERT INTO users (username, email, role, created_at)
                    VALUES (?, ?, ?, ?)
                ''', (username, email, role, datetime.now().isoformat()))
                logger.info(f"User inserted: {username}")
                return True
        except sqlite3.IntegrityError:
            logger.warning(f"User already exists: {username}")
            return False
        except Exception as e:
            logger.error(f"Error inserting user: {e}")
            return False
    
    def get_user(self, username: str) -> Optional[Dict]:
        """Получить пользователя"""
        try:
            with self.get_connection() as conn:
                cursor = conn.cursor()
                cursor.execute('SELECT * FROM users WHERE username = ?', (username,))
                row = cursor.fetchone()
                return dict(row) if row else None
        except Exception as e:
            logger.error(f"Error getting user: {e}")
            return None
    
    def insert_log(self, level: str, message: str, user_id: Optional[int] = None) -> bool:
        """Добавить лог"""
        try:
            with self.get_connection() as conn:
                cursor = conn.cursor()
                cursor.execute('''
                    INSERT INTO logs (timestamp, level, message, user_id)
                    VALUES (?, ?, ?, ?)
                ''', (datetime.now().isoformat(), level, message, user_id))
                return True
        except Exception as e:
            logger.error(f"Error inserting log: {e}")
            return False
    
    def insert_hardware_metric(self, cpu: float, memory: float, disk: float, gpu: float = 0) -> bool:
        """Добавить метрику оборудования"""
        try:
            with self.get_connection() as conn:
                cursor = conn.cursor()
                cursor.execute('''
                    INSERT INTO hardware_metrics (timestamp, cpu_percent, memory_percent, disk_percent, gpu_percent)
                    VALUES (?, ?, ?, ?, ?)
                ''', (datetime.now().isoformat(), cpu, memory, disk, gpu))
                return True
        except Exception as e:
            logger.error(f"Error inserting hardware metric: {e}")
            return False
    
    def insert_vision_analysis(self, image_path: str, ocr_text: str, faces: int, barcodes: int, user_id: Optional[int] = None) -> bool:
        """Добавить анализ изображения"""
        try:
            with self.get_connection() as conn:
                cursor = conn.cursor()
                cursor.execute('''
                    INSERT INTO vision_analysis (timestamp, image_path, ocr_text, faces_count, barcodes_count, user_id)
                    VALUES (?, ?, ?, ?, ?, ?)
                ''', (datetime.now().isoformat(), image_path, ocr_text, faces, barcodes, user_id))
                return True
        except Exception as e:
            logger.error(f"Error inserting vision analysis: {e}")
            return False
    
    def insert_user_action(self, action_type: str, action_data: Dict, user_id: Optional[int] = None) -> bool:
        """Добавить действие пользователя"""
        try:
            with self.get_connection() as conn:
                cursor = conn.cursor()
                cursor.execute('''
                    INSERT INTO user_actions (timestamp, action_type, action_data, user_id)
                    VALUES (?, ?, ?, ?)
                ''', (datetime.now().isoformat(), action_type, json.dumps(action_data), user_id))
                return True
        except Exception as e:
            logger.error(f"Error inserting user action: {e}")
            return False
    
    def get_logs(self, limit: int = 100) -> List[Dict]:
        """Получить логи"""
        try:
            with self.get_connection() as conn:
                cursor = conn.cursor()
                cursor.execute('SELECT * FROM logs ORDER BY timestamp DESC LIMIT ?', (limit,))
                return [dict(row) for row in cursor.fetchall()]
        except Exception as e:
            logger.error(f"Error getting logs: {e}")
            return []
    
    def get_hardware_metrics(self, limit: int = 100) -> List[Dict]:
        """Получить метрики оборудования"""
        try:
            with self.get_connection() as conn:
                cursor = conn.cursor()
                cursor.execute('SELECT * FROM hardware_metrics ORDER BY timestamp DESC LIMIT ?', (limit,))
                return [dict(row) for row in cursor.fetchall()]
        except Exception as e:
            logger.error(f"Error getting hardware metrics: {e}")
            return []
    
    def get_vision_analysis(self, limit: int = 100) -> List[Dict]:
        """Получить анализы изображений"""
        try:
            with self.get_connection() as conn:
                cursor = conn.cursor()
                cursor.execute('SELECT * FROM vision_analysis ORDER BY timestamp DESC LIMIT ?', (limit,))
                return [dict(row) for row in cursor.fetchall()]
        except Exception as e:
            logger.error(f"Error getting vision analysis: {e}")
            return []
    
    def get_user_actions(self, user_id: int, limit: int = 100) -> List[Dict]:
        """Получить действия пользователя"""
        try:
            with self.get_connection() as conn:
                cursor = conn.cursor()
                cursor.execute('''
                    SELECT * FROM user_actions 
                    WHERE user_id = ? 
                    ORDER BY timestamp DESC 
                    LIMIT ?
                ''', (user_id, limit))
                return [dict(row) for row in cursor.fetchall()]
        except Exception as e:
            logger.error(f"Error getting user actions: {e}")
            return []
    
    def get_statistics(self) -> Dict:
        """Получить статистику"""
        try:
            with self.get_connection() as conn:
                cursor = conn.cursor()
                
                cursor.execute('SELECT COUNT(*) as count FROM users')
                users_count = cursor.fetchone()['count']
                
                cursor.execute('SELECT COUNT(*) as count FROM logs')
                logs_count = cursor.fetchone()['count']
                
                cursor.execute('SELECT COUNT(*) as count FROM vision_analysis')
                analysis_count = cursor.fetchone()['count']
                
                return {
                    'users': users_count,
                    'logs': logs_count,
                    'vision_analysis': analysis_count,
                    'timestamp': datetime.now().isoformat()
                }
        except Exception as e:
            logger.error(f"Error getting statistics: {e}")
            return {}
    
    def export_to_json(self, filepath: str) -> bool:
        """Экспортировать базу данных в JSON"""
        try:
            with self.get_connection() as conn:
                cursor = conn.cursor()
                
                data = {
                    'users': [dict(row) for row in cursor.execute('SELECT * FROM users').fetchall()],
                    'logs': [dict(row) for row in cursor.execute('SELECT * FROM logs').fetchall()],
                    'hardware_metrics': [dict(row) for row in cursor.execute('SELECT * FROM hardware_metrics').fetchall()],
                    'vision_analysis': [dict(row) for row in cursor.execute('SELECT * FROM vision_analysis').fetchall()],
                    'user_actions': [dict(row) for row in cursor.execute('SELECT * FROM user_actions').fetchall()]
                }
                
                with open(filepath, 'w') as f:
                    json.dump(data, f, indent=2)
                
                logger.info(f"Database exported to {filepath}")
                return True
        except Exception as e:
            logger.error(f"Error exporting database: {e}")
            return False


__all__ = ['ProductionDatabase']

