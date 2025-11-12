import pytest
from typing import Generator
import os
import tempfile
from pathlib import Path

@pytest.fixture
def temp_workspace() -> Generator[Path, None, None]:
    """Создает временную рабочую директорию для тестов."""
    with tempfile.TemporaryDirectory() as temp_dir:
        yield Path(temp_dir)

@pytest.fixture
def mock_config(temp_workspace: Path) -> dict:
    """Создает тестовую конфигурацию."""
    return {
        "workspace_dir": str(temp_workspace),
        "ai": {
            "model": "test_model",
            "temperature": 0.7,
            "max_tokens": 1000
        },
        "vision": {
            "confidence_threshold": 0.8,
            "max_retries": 3
        },
        "system": {
            "max_parallel_tasks": 4,
            "timeout": 30
        }
    }

def test_temp_workspace(temp_workspace: Path):
    """Проверяет создание временной директории."""
    assert temp_workspace.exists()
    assert temp_workspace.is_dir()
    
    # Создаем тестовый файл
    test_file = temp_workspace / "test.txt"
    test_file.write_text("test content")
    
    assert test_file.exists()
    assert test_file.read_text() == "test content"

def test_mock_config(mock_config: dict):
    """Проверяет тестовую конфигурацию."""
    assert "workspace_dir" in mock_config
    assert "ai" in mock_config
    assert "vision" in mock_config
    assert "system" in mock_config
    
    assert isinstance(mock_config["ai"]["temperature"], float)
    assert isinstance(mock_config["vision"]["confidence_threshold"], float)
    assert isinstance(mock_config["system"]["max_parallel_tasks"], int)