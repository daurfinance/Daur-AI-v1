"""
Core configuration file.

Default configuration for Daur-AI
"""

DEFAULT_CONFIG = {
    "ai": {
        "model": "simple",  # simple, enhanced, or ollama
        "temperature": 0.7,
        "max_tokens": 1000
    },
    "input": {
        "mode": "simple",  # simple or advanced
        "delay": 0.1,
        "safe_mode": True
    },
    "parser": {
        "mode": "simple",  # simple or enhanced
        "language": "ru"
    },
    "system": {
        "debug": False,
        "log_level": "INFO",
        "workspace_dir": "workspace"
    }
}