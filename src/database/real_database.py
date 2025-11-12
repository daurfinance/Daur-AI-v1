#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
Real Database Module for Daur-AI v2.0
Production-grade SQLite database with full schema and CRUD operations
"""

import sqlite3
import json
import logging
from datetime import datetime
from typing import Dict, List, Optional
from contextlib import contextmanager

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class RealDatabase:
    """Production-grade database with full schema and operations"""
    
    def __init__(self, db_path: str = 'daur_ai.db'):
        self.db_path = db_path
        # For in-memory databases, keep a persistent connection
        self._persistent_conn = None
        if db_path == ':memory:':
            self._persistent_conn = sqlite3.connect(db_path, check_same_thread=False)
            self._persistent_conn.row_factory = sqlite3.Row
        self.init_database()
    
    @contextmanager
    def get_connection(self):
        """Context manager for database connections"""
        # Use persistent connection for in-memory databases
        if self._persistent_conn:
            try:
                yield self._persistent_conn
                self._persistent_conn.commit()
            except Exception as e:
                self._persistent_conn.rollback()
                logger.error(f"Database error: {e}")
                raise
        else:
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
    
    def _get_direct_connection(self):
        """Get a direct connection without context manager"""
        if self._persistent_conn:
            return self._persistent_conn
        conn = sqlite3.connect(self.db_path)
        conn.row_factory = sqlite3.Row
        return conn
    
    def init_database(self):
        """Initialize database schema"""
        try:
            conn = self._get_direct_connection()
            cursor = conn.cursor()
            
            # Users table
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS users (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    username TEXT UNIQUE NOT NULL,
                    email TEXT UNIQUE NOT NULL,
                    password_hash TEXT NOT NULL,
                    role TEXT DEFAULT 'user',
                    api_key TEXT UNIQUE,
                    created_at TEXT DEFAULT CURRENT_TIMESTAMP,
                    last_login TEXT,
                    is_active INTEGER DEFAULT 1
                )
            ''')
            
            # Logs table
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS logs (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    timestamp TEXT DEFAULT CURRENT_TIMESTAMP,
                    level TEXT,
                    message TEXT,
                    user_id INTEGER,
                    source TEXT,
                    FOREIGN KEY (user_id) REFERENCES users(id)
                )
            ''')
            
            # Hardware metrics table
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS hardware_metrics (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    timestamp TEXT DEFAULT CURRENT_TIMESTAMP,
                    cpu_percent REAL,
                    memory_percent REAL,
                    disk_percent REAL,
                    gpu_percent REAL,
                    gpu_memory_percent REAL,
                    battery_percent REAL,
                    temperature REAL
                )
            ''')
            
            # Vision analysis table
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS vision_analysis (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    timestamp TEXT DEFAULT CURRENT_TIMESTAMP,
                    image_path TEXT,
                    ocr_text TEXT,
                    ocr_confidence REAL,
                    faces_count INTEGER,
                    faces_data TEXT,
                    barcodes_count INTEGER,
                    barcodes_data TEXT,
                    user_id INTEGER,
                    FOREIGN KEY (user_id) REFERENCES users(id)
                )
            ''')
            
            # User actions table
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS user_actions (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    timestamp TEXT DEFAULT CURRENT_TIMESTAMP,
                    action_type TEXT,
                    action_data TEXT,
                    user_id INTEGER,
                    status TEXT DEFAULT 'completed',
                    FOREIGN KEY (user_id) REFERENCES users(id)
                )
            ''')
            
            # API sessions table
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS api_sessions (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    user_id INTEGER NOT NULL,
                    token TEXT UNIQUE NOT NULL,
                    created_at TEXT DEFAULT CURRENT_TIMESTAMP,
                    expires_at TEXT,
                    is_active INTEGER DEFAULT 1,
                    FOREIGN KEY (user_id) REFERENCES users(id)
                )
            ''')
            
            # Audit log table
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS audit_log (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    timestamp TEXT DEFAULT CURRENT_TIMESTAMP,
                    user_id INTEGER,
                    action TEXT,
                    resource TEXT,
                    details TEXT,
                    ip_address TEXT,
                    FOREIGN KEY (user_id) REFERENCES users(id)
                )
            ''')
            
            # Create indexes for better performance
            try:
                cursor.execute('CREATE INDEX IF NOT EXISTS idx_users_username ON users(username)')
                cursor.execute('CREATE INDEX IF NOT EXISTS idx_logs_timestamp ON logs(timestamp)')
                cursor.execute('CREATE INDEX IF NOT EXISTS idx_hardware_timestamp ON hardware_metrics(timestamp)')
                cursor.execute('CREATE INDEX IF NOT EXISTS idx_vision_timestamp ON vision_analysis(timestamp)')
                cursor.execute('CREATE INDEX IF NOT EXISTS idx_actions_user ON user_actions(user_id)')
            except Exception:
                pass  # Indexes may already exist
            
            conn.commit()
            # Don't close persistent connections
            if not self._persistent_conn:
                conn.close()
            logger.info("Database initialized successfully")
        
        except Exception as e:
            logger.error(f"Error initializing database: {e}")
            try:
                if not self._persistent_conn:
                    conn.close()
            except Exception as e:
                pass
    
    # ===== User Operations =====
    
    def insert_user(self, username: str, email: str, password_hash: str, role: str = 'user') -> Optional[int]:
        """Insert a new user"""
        try:
            with self.get_connection() as conn:
                cursor = conn.cursor()
                cursor.execute('''
                    INSERT INTO users (username, email, password_hash, role, created_at)
                    VALUES (?, ?, ?, ?, ?)
                ''', (username, email, password_hash, role, datetime.now().isoformat()))
                user_id = cursor.lastrowid
                logger.info(f"User inserted: {username} (ID: {user_id})")
                return user_id
        except sqlite3.IntegrityError:
            logger.warning(f"User already exists: {username}")
            return None
        except Exception as e:
            logger.error(f"Error inserting user: {e}")
            return None
    
    def get_user(self, username: str) -> Optional[Dict]:
        """Get user by username"""
        try:
            with self.get_connection() as conn:
                cursor = conn.cursor()
                cursor.execute('SELECT * FROM users WHERE username = ?', (username,))
                row = cursor.fetchone()
                return dict(row) if row else None
        except Exception as e:
            logger.error(f"Error getting user: {e}")
            return None
    
    def get_user_by_id(self, user_id: int) -> Optional[Dict]:
        """Get user by ID"""
        try:
            with self.get_connection() as conn:
                cursor = conn.cursor()
                cursor.execute('SELECT * FROM users WHERE id = ?', (user_id,))
                row = cursor.fetchone()
                return dict(row) if row else None
        except Exception as e:
            logger.error(f"Error getting user by ID: {e}")
            return None
    
    def update_user_login(self, user_id: int) -> bool:
        """Update user last login time"""
        try:
            with self.get_connection() as conn:
                cursor = conn.cursor()
                cursor.execute(
                    'UPDATE users SET last_login = ? WHERE id = ?',
                    (datetime.now().isoformat(), user_id)
                )
                return True
        except Exception as e:
            logger.error(f"Error updating user login: {e}")
            return False
    
    def set_api_key(self, user_id: int, api_key: str) -> bool:
        """Set API key for user"""
        try:
            with self.get_connection() as conn:
                cursor = conn.cursor()
                cursor.execute('UPDATE users SET api_key = ? WHERE id = ?', (api_key, user_id))
                return True
        except Exception as e:
            logger.error(f"Error setting API key: {e}")
            return False
    
    def get_all_users(self, limit: int = 100) -> List[Dict]:
        """Get all users"""
        try:
            with self.get_connection() as conn:
                cursor = conn.cursor()
                cursor.execute('SELECT id, username, email, role, created_at, last_login FROM users LIMIT ?', (limit,))
                return [dict(row) for row in cursor.fetchall()]
        except Exception as e:
            logger.error(f"Error getting all users: {e}")
            return []
    
    # ===== Logging Operations =====
    
    def insert_log(self, level: str, message: str, user_id: Optional[int] = None, source: str = '') -> bool:
        """Insert a log entry"""
        try:
            with self.get_connection() as conn:
                cursor = conn.cursor()
                cursor.execute('''
                    INSERT INTO logs (timestamp, level, message, user_id, source)
                    VALUES (?, ?, ?, ?, ?)
                ''', (datetime.now().isoformat(), level, message, user_id, source))
                return True
        except Exception as e:
            logger.error(f"Error inserting log: {e}")
            return False
    
    def get_logs(self, limit: int = 100, level: Optional[str] = None) -> List[Dict]:
        """Get logs"""
        try:
            with self.get_connection() as conn:
                cursor = conn.cursor()
                if level:
                    cursor.execute(
                        'SELECT * FROM logs WHERE level = ? ORDER BY timestamp DESC LIMIT ?',
                        (level, limit)
                    )
                else:
                    cursor.execute('SELECT * FROM logs ORDER BY timestamp DESC LIMIT ?', (limit,))
                return [dict(row) for row in cursor.fetchall()]
        except Exception as e:
            logger.error(f"Error getting logs: {e}")
            return []
    
    # ===== Hardware Metrics Operations =====
    
    def insert_hardware_metrics(self, cpu_percent: float, memory_percent: float, 
                               disk_percent: float, gpu_percent: float = 0.0,
                               gpu_memory_percent: float = 0.0, battery_percent: float = 0.0,
                               temperature: float = 0.0) -> bool:
        """Insert hardware metrics"""
        try:
            with self.get_connection() as conn:
                cursor = conn.cursor()
                cursor.execute('''
                    INSERT INTO hardware_metrics 
                    (timestamp, cpu_percent, memory_percent, disk_percent, gpu_percent, 
                     gpu_memory_percent, battery_percent, temperature)
                    VALUES (?, ?, ?, ?, ?, ?, ?, ?)
                ''', (datetime.now().isoformat(), cpu_percent, memory_percent, disk_percent,
                      gpu_percent, gpu_memory_percent, battery_percent, temperature))
                return True
        except Exception as e:
            logger.error(f"Error inserting hardware metrics: {e}")
            return False
    
    def get_hardware_metrics(self, limit: int = 100) -> List[Dict]:
        """Get hardware metrics"""
        try:
            with self.get_connection() as conn:
                cursor = conn.cursor()
                cursor.execute('SELECT * FROM hardware_metrics ORDER BY timestamp DESC LIMIT ?', (limit,))
                return [dict(row) for row in cursor.fetchall()]
        except Exception as e:
            logger.error(f"Error getting hardware metrics: {e}")
            return []
    
    def get_hardware_metrics_average(self, hours: int = 1) -> Optional[Dict]:
        """Get average hardware metrics for the last N hours"""
        try:
            with self.get_connection() as conn:
                cursor = conn.cursor()
                cursor.execute('''
                    SELECT 
                        AVG(cpu_percent) as avg_cpu,
                        AVG(memory_percent) as avg_memory,
                        AVG(disk_percent) as avg_disk,
                        AVG(gpu_percent) as avg_gpu,
                        MAX(cpu_percent) as max_cpu,
                        MAX(memory_percent) as max_memory
                    FROM hardware_metrics
                    WHERE timestamp > datetime('now', '-' || ? || ' hours')
                ''', (hours,))
                row = cursor.fetchone()
                return dict(row) if row else None
        except Exception as e:
            logger.error(f"Error getting hardware metrics average: {e}")
            return None
    
    # ===== Vision Analysis Operations =====
    
    def insert_vision_analysis(self, image_path: str, ocr_text: str = '', ocr_confidence: float = 0.0,
                              faces_count: int = 0, faces_data: str = '', 
                              barcodes_count: int = 0, barcodes_data: str = '',
                              user_id: Optional[int] = None) -> bool:
        """Insert vision analysis result"""
        try:
            with self.get_connection() as conn:
                cursor = conn.cursor()
                cursor.execute('''
                    INSERT INTO vision_analysis 
                    (timestamp, image_path, ocr_text, ocr_confidence, faces_count, faces_data,
                     barcodes_count, barcodes_data, user_id)
                    VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
                ''', (datetime.now().isoformat(), image_path, ocr_text, ocr_confidence,
                      faces_count, faces_data, barcodes_count, barcodes_data, user_id))
                return True
        except Exception as e:
            logger.error(f"Error inserting vision analysis: {e}")
            return False
    
    def get_vision_analysis(self, limit: int = 100, user_id: Optional[int] = None) -> List[Dict]:
        """Get vision analysis results"""
        try:
            with self.get_connection() as conn:
                cursor = conn.cursor()
                if user_id:
                    cursor.execute(
                        'SELECT * FROM vision_analysis WHERE user_id = ? ORDER BY timestamp DESC LIMIT ?',
                        (user_id, limit)
                    )
                else:
                    cursor.execute('SELECT * FROM vision_analysis ORDER BY timestamp DESC LIMIT ?', (limit,))
                return [dict(row) for row in cursor.fetchall()]
        except Exception as e:
            logger.error(f"Error getting vision analysis: {e}")
            return []
    
    # ===== User Actions Operations =====
    
    def insert_action(self, action_type: str, action_data: str, user_id: int, status: str = 'completed') -> bool:
        """Insert user action"""
        try:
            with self.get_connection() as conn:
                cursor = conn.cursor()
                cursor.execute('''
                    INSERT INTO user_actions (timestamp, action_type, action_data, user_id, status)
                    VALUES (?, ?, ?, ?, ?)
                ''', (datetime.now().isoformat(), action_type, action_data, user_id, status))
                return True
        except Exception as e:
            logger.error(f"Error inserting action: {e}")
            return False
    
    def get_user_actions(self, user_id: int, limit: int = 100) -> List[Dict]:
        """Get user actions"""
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
    
    # ===== API Session Operations =====
    
    def insert_session(self, user_id: int, token: str, expires_at: str) -> bool:
        """Insert API session"""
        try:
            with self.get_connection() as conn:
                cursor = conn.cursor()
                cursor.execute('''
                    INSERT INTO api_sessions (user_id, token, created_at, expires_at)
                    VALUES (?, ?, ?, ?)
                ''', (user_id, token, datetime.now().isoformat(), expires_at))
                return True
        except Exception as e:
            logger.error(f"Error inserting session: {e}")
            return False
    
    def get_session(self, token: str) -> Optional[Dict]:
        """Get session by token"""
        try:
            with self.get_connection() as conn:
                cursor = conn.cursor()
                cursor.execute('SELECT * FROM api_sessions WHERE token = ? AND is_active = 1', (token,))
                row = cursor.fetchone()
                return dict(row) if row else None
        except Exception as e:
            logger.error(f"Error getting session: {e}")
            return None
    
    def invalidate_session(self, token: str) -> bool:
        """Invalidate a session"""
        try:
            with self.get_connection() as conn:
                cursor = conn.cursor()
                cursor.execute('UPDATE api_sessions SET is_active = 0 WHERE token = ?', (token,))
                return True
        except Exception as e:
            logger.error(f"Error invalidating session: {e}")
            return False
    
    # ===== Audit Log Operations =====
    
    def insert_audit_log(self, user_id: int, action: str, resource: str, 
                        details: str = '', ip_address: str = '') -> bool:
        """Insert audit log entry"""
        try:
            with self.get_connection() as conn:
                cursor = conn.cursor()
                cursor.execute('''
                    INSERT INTO audit_log (timestamp, user_id, action, resource, details, ip_address)
                    VALUES (?, ?, ?, ?, ?, ?)
                ''', (datetime.now().isoformat(), user_id, action, resource, details, ip_address))
                return True
        except Exception as e:
            logger.error(f"Error inserting audit log: {e}")
            return False
    
    def get_audit_log(self, limit: int = 100, user_id: Optional[int] = None) -> List[Dict]:
        """Get audit log entries"""
        try:
            with self.get_connection() as conn:
                cursor = conn.cursor()
                if user_id:
                    cursor.execute(
                        'SELECT * FROM audit_log WHERE user_id = ? ORDER BY timestamp DESC LIMIT ?',
                        (user_id, limit)
                    )
                else:
                    cursor.execute('SELECT * FROM audit_log ORDER BY timestamp DESC LIMIT ?', (limit,))
                return [dict(row) for row in cursor.fetchall()]
        except Exception as e:
            logger.error(f"Error getting audit log: {e}")
            return []
    
    # ===== Statistics Operations =====
    
    def get_statistics(self) -> Dict:
        """Get database statistics"""
        try:
            with self.get_connection() as conn:
                cursor = conn.cursor()
                
                cursor.execute('SELECT COUNT(*) as count FROM users')
                users_count = cursor.fetchone()['count']
                
                cursor.execute('SELECT COUNT(*) as count FROM logs')
                logs_count = cursor.fetchone()['count']
                
                cursor.execute('SELECT COUNT(*) as count FROM vision_analysis')
                analysis_count = cursor.fetchone()['count']
                
                cursor.execute('SELECT COUNT(*) as count FROM user_actions')
                actions_count = cursor.fetchone()['count']
                
                cursor.execute('SELECT COUNT(*) as count FROM hardware_metrics')
                metrics_count = cursor.fetchone()['count']
                
                return {
                    'users': users_count,
                    'logs': logs_count,
                    'vision_analysis': analysis_count,
                    'user_actions': actions_count,
                    'hardware_metrics': metrics_count,
                    'timestamp': datetime.now().isoformat()
                }
        except Exception as e:
            logger.error(f"Error getting statistics: {e}")
            return {}
    
    # ===== Export Operations =====
    
    def export_to_json(self, filepath: str) -> bool:
        """Export database to JSON"""
        try:
            with self.get_connection() as conn:
                cursor = conn.cursor()
                
                data = {
                    'users': [dict(row) for row in cursor.execute('SELECT * FROM users').fetchall()],
                    'logs': [dict(row) for row in cursor.execute('SELECT * FROM logs').fetchall()],
                    'hardware_metrics': [dict(row) for row in cursor.execute('SELECT * FROM hardware_metrics').fetchall()],
                    'vision_analysis': [dict(row) for row in cursor.execute('SELECT * FROM vision_analysis').fetchall()],
                    'user_actions': [dict(row) for row in cursor.execute('SELECT * FROM user_actions').fetchall()],
                    'audit_log': [dict(row) for row in cursor.execute('SELECT * FROM audit_log').fetchall()]
                }
                
                with open(filepath, 'w') as f:
                    json.dump(data, f, indent=2)
                
                logger.info(f"Database exported to {filepath}")
                return True
        except Exception as e:
            logger.error(f"Error exporting database: {e}")
            return False
    
    def cleanup(self):
        """Clean up old data"""
        try:
            with self.get_connection() as conn:
                cursor = conn.cursor()
                
                # Delete logs older than 30 days
                cursor.execute(
                    "DELETE FROM logs WHERE timestamp < datetime('now', '-30 days')"
                )
                
                # Delete hardware metrics older than 7 days
                cursor.execute(
                    "DELETE FROM hardware_metrics WHERE timestamp < datetime('now', '-7 days')"
                )
                
                logger.info("Database cleanup completed")
                return True
        except Exception as e:
            logger.error(f"Error during cleanup: {e}")
            return False


__all__ = ['RealDatabase']

