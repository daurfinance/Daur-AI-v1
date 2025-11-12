#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
Daur AI - Centralized Logging Configuration

This module provides a unified logging configuration for the entire Daur AI system.
All modules should use this centralized logging instead of creating their own loggers.

Features:
- Structured logging with JSON support
- Rotating file handlers with size limits
- Console and file output
- Different log levels for different components
- Performance metrics logging
- Security event logging

Version: 2.0
Date: 2025-11-12
"""

import os
import sys
import logging
import logging.handlers
import json
from datetime import datetime
from pathlib import Path
from typing import Optional, Dict, Any


# Log levels mapping
LOG_LEVELS = {
    'DEBUG': logging.DEBUG,
    'INFO': logging.INFO,
    'WARNING': logging.WARNING,
    'ERROR': logging.ERROR,
    'CRITICAL': logging.CRITICAL
}


class JSONFormatter(logging.Formatter):
    """
    Custom JSON formatter for structured logging.
    
    Outputs log records as JSON objects for easy parsing and analysis.
    """
    
    def format(self, record: logging.LogRecord) -> str:
        """Format log record as JSON."""
        log_data = {
            'timestamp': datetime.fromtimestamp(record.created).isoformat(),
            'level': record.levelname,
            'logger': record.name,
            'message': record.getMessage(),
            'module': record.module,
            'function': record.funcName,
            'line': record.lineno
        }
        
        # Add exception info if present
        if record.exc_info:
            log_data['exception'] = self.formatException(record.exc_info)
        
        # Add extra fields if present
        if hasattr(record, 'extra_data'):
            log_data['extra'] = record.extra_data
        
        return json.dumps(log_data, ensure_ascii=False)


class ColoredFormatter(logging.Formatter):
    """
    Colored console formatter for better readability.
    
    Uses ANSI color codes to highlight different log levels.
    """
    
    # ANSI color codes
    COLORS = {
        'DEBUG': '\033[36m',      # Cyan
        'INFO': '\033[32m',       # Green
        'WARNING': '\033[33m',    # Yellow
        'ERROR': '\033[31m',      # Red
        'CRITICAL': '\033[35m',   # Magenta
        'RESET': '\033[0m'        # Reset
    }
    
    def format(self, record: logging.LogRecord) -> str:
        """Format log record with colors."""
        color = self.COLORS.get(record.levelname, self.COLORS['RESET'])
        reset = self.COLORS['RESET']
        
        # Format timestamp
        timestamp = datetime.fromtimestamp(record.created).strftime('%Y-%m-%d %H:%M:%S')
        
        # Format message
        message = record.getMessage()
        
        # Build colored log line
        log_line = f"{color}[{timestamp}] [{record.levelname:8s}]{reset} {record.name}: {message}"
        
        # Add exception info if present
        if record.exc_info:
            log_line += f"\n{self.formatException(record.exc_info)}"
        
        return log_line


def get_log_directory() -> Path:
    """
    Get the log directory path.
    
    Returns:
        Path: Log directory path
    """
    # Use environment variable if set, otherwise use default
    log_dir = os.getenv('DAUR_AI_LOG_DIR')
    
    if log_dir:
        log_path = Path(log_dir)
    else:
        # Default to ~/.daur_ai/logs
        home_dir = Path.home()
        log_path = home_dir / '.daur_ai' / 'logs'
    
    # Create directory if it doesn't exist
    log_path.mkdir(parents=True, exist_ok=True)
    
    return log_path


def setup_logging(
    log_level: str = 'INFO',
    log_to_file: bool = True,
    log_to_console: bool = True,
    json_format: bool = False,
    component: Optional[str] = None
) -> None:
    """
    Setup centralized logging configuration.
    
    This should be called once at application startup.
    
    Args:
        log_level: Logging level (DEBUG, INFO, WARNING, ERROR, CRITICAL)
        log_to_file: Enable file logging
        log_to_console: Enable console logging
        json_format: Use JSON format for file logs
        component: Component name for specialized logging
    
    Example:
        >>> setup_logging(log_level='DEBUG', json_format=True)
    """
    # Get log level
    level = LOG_LEVELS.get(log_level.upper(), logging.INFO)
    
    # Get root logger
    root_logger = logging.getLogger()
    root_logger.setLevel(level)
    
    # Clear existing handlers
    root_logger.handlers.clear()
    
    # Setup console handler
    if log_to_console:
        console_handler = logging.StreamHandler(sys.stdout)
        console_handler.setLevel(level)
        
        # Use colored formatter for console
        console_formatter = ColoredFormatter()
        console_handler.setFormatter(console_formatter)
        
        root_logger.addHandler(console_handler)
    
    # Setup file handler
    if log_to_file:
        log_dir = get_log_directory()
        
        # Main log file
        log_file = log_dir / f"daur_ai_{datetime.now().strftime('%Y%m%d')}.log"
        
        # Rotating file handler (10MB max, 5 backups)
        file_handler = logging.handlers.RotatingFileHandler(
            log_file,
            maxBytes=10 * 1024 * 1024,  # 10MB
            backupCount=5,
            encoding='utf-8'
        )
        file_handler.setLevel(level)
        
        # Use JSON or standard formatter
        if json_format:
            file_formatter = JSONFormatter()
        else:
            file_formatter = logging.Formatter(
                '%(asctime)s [%(levelname)s] %(name)s: %(message)s',
                datefmt='%Y-%m-%d %H:%M:%S'
            )
        
        file_handler.setFormatter(file_formatter)
        root_logger.addHandler(file_handler)
        
        # Separate error log file
        error_log_file = log_dir / f"daur_ai_errors_{datetime.now().strftime('%Y%m%d')}.log"
        error_handler = logging.handlers.RotatingFileHandler(
            error_log_file,
            maxBytes=10 * 1024 * 1024,
            backupCount=5,
            encoding='utf-8'
        )
        error_handler.setLevel(logging.ERROR)
        error_handler.setFormatter(file_formatter)
        root_logger.addHandler(error_handler)
    
    # Log initialization
    root_logger.info(f"Logging initialized - Level: {log_level}, File: {log_to_file}, Console: {log_to_console}")


def get_logger(name: str) -> logging.Logger:
    """
    Get a logger instance for a specific module.
    
    Args:
        name: Logger name (usually __name__)
    
    Returns:
        logging.Logger: Configured logger instance
    
    Example:
        >>> logger = get_logger(__name__)
        >>> logger.info("Starting process")
    """
    return logging.getLogger(name)


def log_performance(logger: logging.Logger, operation: str, duration: float, **kwargs) -> None:
    """
    Log performance metrics.
    
    Args:
        logger: Logger instance
        operation: Operation name
        duration: Duration in seconds
        **kwargs: Additional metrics
    
    Example:
        >>> logger = get_logger(__name__)
        >>> log_performance(logger, "database_query", 0.234, rows=100)
    """
    metrics = {
        'operation': operation,
        'duration_seconds': duration,
        **kwargs
    }
    
    # Create log record with extra data
    extra = {'extra_data': metrics}
    logger.info(f"Performance: {operation} completed in {duration:.3f}s", extra=extra)


def log_security_event(logger: logging.Logger, event_type: str, details: Dict[str, Any]) -> None:
    """
    Log security-related events.
    
    Args:
        logger: Logger instance
        event_type: Type of security event
        details: Event details
    
    Example:
        >>> logger = get_logger(__name__)
        >>> log_security_event(logger, "login_attempt", {"user": "admin", "success": True})
    """
    security_data = {
        'event_type': event_type,
        'timestamp': datetime.now().isoformat(),
        **details
    }
    
    extra = {'extra_data': security_data}
    logger.warning(f"Security Event: {event_type}", extra=extra)


# Module-level logger for this config module
_logger = None


def _get_module_logger():
    """Get logger for this module."""
    global _logger
    if _logger is None:
        _logger = get_logger(__name__)
    return _logger


# Auto-setup logging with defaults if not already configured
if not logging.getLogger().handlers:
    # Get log level from environment or use INFO
    default_level = os.getenv('DAUR_AI_LOG_LEVEL', 'INFO')
    setup_logging(log_level=default_level)

