"""Core agent implementation with component initialization."""
import asyncio
import logging
from typing import Dict, Any, Optional
from queue import Queue, Empty
from threading import Event, Thread


class DaurAgent:
    """Core agent coordinating components and executing commands."""

    def __init__(self, config: Dict[str, Any]):
        self.config = config or {}
        self.logger = logging.getLogger("daur_ai.agent.core")
        self.command_queue = Queue()
        self.stop_event = Event()

        # Components
        self.model = None
        self.input = None
        self.parser = None
        self.file_manager = None

        # Internal state
        self._worker_thread = None
        self._running = False

        self.init_components()

    def init_components(self) -> None:
        """Initialize all components with fallbacks."""
        # Input controller
        input_config = self.config.get("input", {})
        try:
            from src.input.controller import InputController
            self.input = InputController(input_config)
            self.logger.info("✓ InputController loaded")
        except Exception as e:
            self.logger.warning(f"✗ InputController failed: {e}")
            try:
                from src.input.simple_controller import SimpleInputController
                self.input = SimpleInputController()
                self.logger.info("✓ SimpleInputController loaded")
            except (ImportError, AttributeError, Exception) as e:
                self.logger.error(f"✗ No input controller available: {e}")
                self.input = None

        # Command parser
        try:
            from src.parser.command_parser import CommandParser
            self.parser = CommandParser()
            self.logger.info("✓ CommandParser loaded")
        except Exception as e:
            self.logger.warning(f"✗ CommandParser failed: {e}")
            self.parser = None

        # File manager
        try:
            from src.files.manager import FileManager
            self.file_manager = FileManager()
            self.logger.info("✓ FileManager loaded")
        except Exception as e:
            self.logger.warning(f"✗ FileManager failed: {e}")
            self.file_manager = None

        # Model manager
        try:
            from src.ai.model_manager import ModelManager
            self.model = ModelManager(self.config.get("ai", {}))
            self.logger.info("✓ ModelManager loaded")
        except Exception as e:
            self.logger.warning(f"✗ ModelManager failed: {e}")
            self.model = None

    def process_command(self, command: Dict[str, Any]) -> Any:
        """Process a single command."""
        if not self.parser:
            self.logger.error("Parser not available")
            return None

        try:
            self.logger.debug(f"Processing: {command}")
            # Parse and execute command through input controller
            if self.input:
                return asyncio.run(self.input.execute(command))
            return {"success": False, "error": "No input controller"}
        except Exception as e:
            self.logger.error(f"Command failed: {e}")
            return {"success": False, "error": str(e)}

    def start(self) -> None:
        """Start the agent's worker thread."""
        if self._running:
            self.logger.warning("Agent already running")
            return

        self._running = True
        self._worker_thread = Thread(target=self._process_queue, daemon=True)
        self._worker_thread.start()
        self.logger.info("Agent started")

    def _process_queue(self) -> None:
        """Worker thread: processes queued commands."""
        self.logger.debug("Command worker started")
        while self._running and not self.stop_event.is_set():
            try:
                command = self.command_queue.get(timeout=0.5)
                self.process_command(command)
            except Empty:
                continue
            except Exception as e:
                self.logger.error(f"Worker error: {e}")

    def stop(self) -> None:
        """Stop the agent."""
        self._running = False
        self.stop_event.set()
        if self._worker_thread:
            self._worker_thread.join(timeout=2)
        self.logger.info("Agent stopped")

    def submit_command(self, command: Dict[str, Any]) -> None:
        """Submit a command to the queue."""
        self.command_queue.put(command)

    def cleanup(self) -> None:
        """Clean up resources."""
        self.stop()
        if hasattr(self, "input") and self.input:
            if hasattr(self.input, "cleanup"):
                self.input.cleanup()
        if hasattr(self, "model") and self.model:
            if hasattr(self.model, "cleanup"):
                self.model.cleanup()
        self.logger.info("Agent cleaned up")


# Exported name for backwards compatibility
Agent = DaurAgent
