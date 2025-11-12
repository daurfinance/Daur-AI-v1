#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
Daur AI - Centralized Application Configuration

This module provides unified configuration management for the entire Daur AI system.
Configuration can be loaded from environment variables, config files, or defaults.

Features:
- Environment variable support
- YAML/JSON config file loading
- Type-safe configuration access
- Validation and defaults
- Runtime configuration updates

Version: 2.0
Date: 2025-11-12
"""

import os
import json
from pathlib import Path
from typing import Any, Dict, Optional
from dataclasses import dataclass, field


@dataclass
class AIConfig:
    """AI model configuration."""
    model_provider: str = "openai"  # openai, ollama, anthropic
    model_name: str = "gpt-4"
    max_tokens: int = 4096
    temperature: float = 0.7
    timeout: int = 300
    retry_attempts: int = 3


@dataclass
class VisionConfig:
    """Vision system configuration."""
    ocr_engine: str = "tesseract"  # tesseract, easyocr
    ocr_language: str = "eng"
    confidence_threshold: float = 0.7
    enable_gpu: bool = False
    max_image_size: int = 1920


@dataclass
class BrowserConfig:
    """Browser automation configuration."""
    browser_type: str = "chromium"  # chromium, firefox, webkit
    headless: bool = True
    viewport_width: int = 1920
    viewport_height: int = 1080
    timeout: int = 30000  # milliseconds
    user_agent: Optional[str] = None


@dataclass
class InputConfig:
    """Input control configuration."""
    safe_mode: bool = False
    mouse_speed: float = 1.0
    keyboard_delay: float = 0.1
    human_like_typing: bool = True
    platform: Optional[str] = None  # auto-detect if None


@dataclass
class SecurityConfig:
    """Security configuration."""
    enable_rbac: bool = True
    enable_encryption: bool = True
    jwt_secret: Optional[str] = None
    session_timeout: int = 3600  # seconds
    max_login_attempts: int = 5
    rate_limit_requests: int = 100
    rate_limit_window: int = 60  # seconds


@dataclass
class BillingConfig:
    """Billing system configuration."""
    stripe_api_key: Optional[str] = None
    stripe_webhook_secret: Optional[str] = None
    enable_billing: bool = False
    currency: str = "USD"
    trial_period_days: int = 14


@dataclass
class TelegramConfig:
    """Telegram bot configuration."""
    bot_token: Optional[str] = None
    enable_telegram: bool = False
    allowed_users: list = field(default_factory=list)
    enable_voice: bool = True
    enable_file_processing: bool = True


@dataclass
class DatabaseConfig:
    """Database configuration."""
    database_url: Optional[str] = None
    pool_size: int = 10
    max_overflow: int = 20
    echo_sql: bool = False


@dataclass
class LoggingConfig:
    """Logging configuration."""
    log_level: str = "INFO"
    log_to_file: bool = True
    log_to_console: bool = True
    json_format: bool = False
    log_dir: Optional[str] = None


@dataclass
class AppConfig:
    """
    Main application configuration.
    
    This class holds all configuration for the Daur AI system.
    Configuration is loaded from environment variables and config files.
    """
    
    # Component configurations
    ai: AIConfig = field(default_factory=AIConfig)
    vision: VisionConfig = field(default_factory=VisionConfig)
    browser: BrowserConfig = field(default_factory=BrowserConfig)
    input: InputConfig = field(default_factory=InputConfig)
    security: SecurityConfig = field(default_factory=SecurityConfig)
    billing: BillingConfig = field(default_factory=BillingConfig)
    telegram: TelegramConfig = field(default_factory=TelegramConfig)
    database: DatabaseConfig = field(default_factory=DatabaseConfig)
    logging: LoggingConfig = field(default_factory=LoggingConfig)
    
    # General settings
    environment: str = "production"  # development, staging, production
    debug: bool = False
    data_dir: Optional[str] = None
    
    def __post_init__(self):
        """Initialize configuration from environment variables."""
        self._load_from_env()
        self._load_from_file()
        self._validate()
    
    def _load_from_env(self):
        """Load configuration from environment variables."""
        # General settings
        self.environment = os.getenv('DAUR_AI_ENV', self.environment)
        self.debug = os.getenv('DAUR_AI_DEBUG', '').lower() in ('true', '1', 'yes')
        self.data_dir = os.getenv('DAUR_AI_DATA_DIR', self.data_dir)
        
        # AI configuration
        self.ai.model_provider = os.getenv('DAUR_AI_MODEL_PROVIDER', self.ai.model_provider)
        self.ai.model_name = os.getenv('DAUR_AI_MODEL_NAME', self.ai.model_name)
        
        if os.getenv('DAUR_AI_MAX_TOKENS'):
            self.ai.max_tokens = int(os.getenv('DAUR_AI_MAX_TOKENS'))
        
        if os.getenv('DAUR_AI_TEMPERATURE'):
            self.ai.temperature = float(os.getenv('DAUR_AI_TEMPERATURE'))
        
        # Vision configuration
        self.vision.ocr_engine = os.getenv('DAUR_AI_OCR_ENGINE', self.vision.ocr_engine)
        self.vision.ocr_language = os.getenv('DAUR_AI_OCR_LANGUAGE', self.vision.ocr_language)
        self.vision.enable_gpu = os.getenv('DAUR_AI_VISION_GPU', '').lower() in ('true', '1', 'yes')
        
        # Browser configuration
        self.browser.browser_type = os.getenv('DAUR_AI_BROWSER_TYPE', self.browser.browser_type)
        self.browser.headless = os.getenv('DAUR_AI_BROWSER_HEADLESS', 'true').lower() in ('true', '1', 'yes')
        
        # Security configuration
        self.security.jwt_secret = os.getenv('JWT_SECRET', self.security.jwt_secret)
        self.security.enable_rbac = os.getenv('DAUR_AI_ENABLE_RBAC', 'true').lower() in ('true', '1', 'yes')
        
        # Billing configuration
        self.billing.stripe_api_key = os.getenv('STRIPE_API_KEY', self.billing.stripe_api_key)
        self.billing.stripe_webhook_secret = os.getenv('STRIPE_WEBHOOK_SECRET', self.billing.stripe_webhook_secret)
        self.billing.enable_billing = bool(self.billing.stripe_api_key)
        
        # Telegram configuration
        self.telegram.bot_token = os.getenv('TELEGRAM_BOT_TOKEN', self.telegram.bot_token)
        self.telegram.enable_telegram = bool(self.telegram.bot_token)
        
        # Database configuration
        self.database.database_url = os.getenv('DATABASE_URL', self.database.database_url)
        
        # Logging configuration
        self.logging.log_level = os.getenv('DAUR_AI_LOG_LEVEL', self.logging.log_level)
        self.logging.log_dir = os.getenv('DAUR_AI_LOG_DIR', self.logging.log_dir)
    
    def _load_from_file(self):
        """Load configuration from config file if it exists."""
        config_file = os.getenv('DAUR_AI_CONFIG_FILE')
        
        if not config_file:
            # Try default locations
            possible_locations = [
                Path.cwd() / 'config.json',
                Path.home() / '.daur_ai' / 'config.json',
                Path('/etc/daur_ai/config.json')
            ]
            
            for location in possible_locations:
                if location.exists():
                    config_file = str(location)
                    break
        
        if config_file and Path(config_file).exists():
            try:
                with open(config_file, 'r') as f:
                    config_data = json.load(f)
                
                # Update configuration from file
                self._update_from_dict(config_data)
            except Exception as e:
                print(f"Warning: Failed to load config file {config_file}: {e}")
    
    def _update_from_dict(self, data: Dict[str, Any]):
        """Update configuration from dictionary."""
        for key, value in data.items():
            if hasattr(self, key) and isinstance(value, dict):
                # Update nested config
                config_obj = getattr(self, key)
                for sub_key, sub_value in value.items():
                    if hasattr(config_obj, sub_key):
                        setattr(config_obj, sub_key, sub_value)
            elif hasattr(self, key):
                setattr(self, key, value)
    
    def _validate(self):
        """Validate configuration."""
        # Validate AI config
        if self.ai.temperature < 0 or self.ai.temperature > 2:
            raise ValueError("AI temperature must be between 0 and 2")
        
        if self.ai.max_tokens < 1:
            raise ValueError("AI max_tokens must be positive")
        
        # Validate vision config
        if self.vision.confidence_threshold < 0 or self.vision.confidence_threshold > 1:
            raise ValueError("Vision confidence_threshold must be between 0 and 1")
        
        # Validate security config
        if self.security.session_timeout < 60:
            raise ValueError("Security session_timeout must be at least 60 seconds")
        
        # Validate billing config
        if self.billing.enable_billing and not self.billing.stripe_api_key:
            raise ValueError("Billing enabled but no Stripe API key provided")
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert configuration to dictionary."""
        return {
            'ai': self.ai.__dict__,
            'vision': self.vision.__dict__,
            'browser': self.browser.__dict__,
            'input': self.input.__dict__,
            'security': self.security.__dict__,
            'billing': self.billing.__dict__,
            'telegram': self.telegram.__dict__,
            'database': self.database.__dict__,
            'logging': self.logging.__dict__,
            'environment': self.environment,
            'debug': self.debug,
            'data_dir': self.data_dir
        }
    
    def save_to_file(self, file_path: str):
        """Save configuration to file."""
        with open(file_path, 'w') as f:
            json.dump(self.to_dict(), f, indent=2)


# Global configuration instance
_config: Optional[AppConfig] = None


def get_config() -> AppConfig:
    """
    Get the global configuration instance.
    
    Returns:
        AppConfig: Global configuration object
    
    Example:
        >>> config = get_config()
        >>> print(config.ai.model_name)
        gpt-4
    """
    global _config
    
    if _config is None:
        _config = AppConfig()
    
    return _config


def reload_config():
    """
    Reload configuration from environment and files.
    
    This can be used to pick up configuration changes at runtime.
    """
    global _config
    _config = AppConfig()
    return _config

