import pytest
from typing import Generator
import os
import tempfile
import subprocess
import time
from pathlib import Path

# Xvfb display configuration
XVFB_DISPLAY = ":99"
XVFB_RESOLUTION = "1920x1080x24"

@pytest.fixture(scope="session")
def xvfb_display():
    """
    Start Xvfb virtual display for headless GUI testing.
    
    This fixture starts an Xvfb server at the beginning of the test session
    and stops it at the end. All GUI tests can use this display.
    """
    # Check if we're already running in a display environment
    if os.environ.get("DISPLAY"):
        # Already have a display, no need for Xvfb
        yield os.environ.get("DISPLAY")
        return
    
    # Start Xvfb
    xvfb_process = subprocess.Popen(
        ["Xvfb", XVFB_DISPLAY, "-screen", "0", XVFB_RESOLUTION],
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE
    )
    
    # Set DISPLAY environment variable
    os.environ["DISPLAY"] = XVFB_DISPLAY
    
    # Wait for Xvfb to start
    time.sleep(2)
    
    # Verify Xvfb is running
    try:
        subprocess.run(
            ["xdpyinfo", "-display", XVFB_DISPLAY],
            check=True,
            capture_output=True,
            timeout=5
        )
    except (subprocess.CalledProcessError, subprocess.TimeoutExpired):
        xvfb_process.kill()
        pytest.skip("Xvfb failed to start")
    
    yield XVFB_DISPLAY
    
    # Cleanup: stop Xvfb
    xvfb_process.terminate()
    try:
        xvfb_process.wait(timeout=5)
    except subprocess.TimeoutExpired:
        xvfb_process.kill()
    
    # Clean up environment
    if "DISPLAY" in os.environ:
        del os.environ["DISPLAY"]


@pytest.fixture
def gui_environment(xvfb_display):
    """
    Fixture for tests that require GUI/display.
    
    Usage:
        @pytest.mark.gui
        def test_something(gui_environment):
            # Test code that needs display
            pass
    """
    return xvfb_display


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