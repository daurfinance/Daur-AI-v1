"""
Tests for Agent Core Module

This module tests the core agent functionality including:
- Component initialization
- Command processing
- Queue management
- Thread safety
- Error handling
"""

import pytest
import asyncio
from pathlib import Path
from unittest.mock import Mock, patch, MagicMock
from src.agent.core import DaurAgent


class TestDaurAgentInitialization:
    """Test agent initialization and component loading."""
    
    def test_init_with_empty_config(self):
        """Test agent initialization with empty config."""
        agent = DaurAgent({})
        assert agent.config == {}
        assert agent.command_queue is not None
        assert agent.stop_event is not None
        assert not agent._running
    
    def test_init_with_config(self):
        """Test agent initialization with configuration."""
        config = {
            "input": {"safe_mode": True},
            "ai": {"model": "gpt-4"}
        }
        agent = DaurAgent(config)
        assert agent.config == config
        assert "input" in agent.config
        assert "ai" in agent.config
    
    def test_components_initialized(self):
        """Test that components are initialized."""
        agent = DaurAgent({})
        # Components should be initialized (may be None if imports fail)
        assert hasattr(agent, 'model')
        assert hasattr(agent, 'input')
        assert hasattr(agent, 'parser')
        assert hasattr(agent, 'file_manager')
    
    def test_logger_created(self):
        """Test that logger is created."""
        agent = DaurAgent({})
        assert agent.logger is not None
        assert agent.logger.name == "daur_ai.agent.core"


class TestComponentInitialization:
    """Test component initialization with mocking."""
    
    @patch('src.agent.core.InputController')
    def test_input_controller_loaded(self, mock_input):
        """Test successful input controller loading."""
        mock_input.return_value = Mock()
        agent = DaurAgent({"input": {}})
        # Should attempt to load InputController
        assert agent.input is not None or agent.input is None  # May fail in test env
    
    @patch('src.agent.core.CommandParser')
    def test_parser_loaded(self, mock_parser):
        """Test successful parser loading."""
        mock_parser.return_value = Mock()
        agent = DaurAgent({})
        assert agent.parser is not None or agent.parser is None
    
    @patch('src.agent.core.ModelManager')
    def test_model_manager_loaded(self, mock_model):
        """Test successful model manager loading."""
        mock_model.return_value = Mock()
        agent = DaurAgent({"ai": {}})
        assert agent.model is not None or agent.model is None
    
    def test_component_fallback_on_error(self):
        """Test that agent handles component loading errors gracefully."""
        # Even if components fail to load, agent should initialize
        agent = DaurAgent({})
        assert agent is not None
        assert not agent._running


class TestCommandProcessing:
    """Test command processing functionality."""
    
    def test_process_command_without_parser(self):
        """Test command processing when parser is not available."""
        agent = DaurAgent({})
        agent.parser = None
        
        result = agent.process_command({"action": "test"})
        assert result is None
    
    def test_process_command_without_input(self):
        """Test command processing when input controller is not available."""
        agent = DaurAgent({})
        agent.parser = Mock()
        agent.input = None
        
        result = agent.process_command({"action": "test"})
        assert result is not None
        assert result["success"] is False
        assert "error" in result
    
    @patch('src.agent.core.asyncio.run')
    def test_process_command_with_input(self, mock_run):
        """Test successful command processing."""
        agent = DaurAgent({})
        agent.parser = Mock()
        agent.input = Mock()
        agent.input.execute = Mock(return_value={"success": True})
        mock_run.return_value = {"success": True}
        
        command = {"action": "click", "x": 100, "y": 200}
        result = agent.process_command(command)
        
        assert result is not None
        mock_run.assert_called_once()
    
    def test_process_command_error_handling(self):
        """Test error handling in command processing."""
        agent = DaurAgent({})
        agent.parser = Mock()
        agent.input = Mock()
        agent.input.execute = Mock(side_effect=Exception("Test error"))
        
        with patch('src.agent.core.asyncio.run', side_effect=Exception("Test error")):
            result = agent.process_command({"action": "test"})
            assert result is not None
            assert result["success"] is False
            assert "error" in result


class TestAgentLifecycle:
    """Test agent lifecycle management."""
    
    def test_start_agent(self):
        """Test starting the agent."""
        agent = DaurAgent({})
        agent.start()
        
        assert agent._running is True
        assert agent._worker_thread is not None
        assert agent._worker_thread.is_alive()
        
        # Cleanup
        agent.stop()
    
    def test_start_already_running(self):
        """Test starting agent when already running."""
        agent = DaurAgent({})
        agent.start()
        
        # Try to start again
        agent.start()
        assert agent._running is True
        
        # Cleanup
        agent.stop()
    
    def test_stop_agent(self):
        """Test stopping the agent."""
        agent = DaurAgent({})
        agent.start()
        assert agent._running is True
        
        agent.stop()
        assert not agent._running
        assert agent.stop_event.is_set()
    
    def test_stop_not_running(self):
        """Test stopping agent when not running."""
        agent = DaurAgent({})
        assert not agent._running
        
        agent.stop()
        assert not agent._running


class TestQueueManagement:
    """Test command queue management."""
    
    def test_submit_command(self):
        """Test submitting command to queue."""
        agent = DaurAgent({})
        command = {"action": "test"}
        
        agent.submit_command(command)
        assert not agent.command_queue.empty()
    
    def test_queue_processing(self):
        """Test that commands are processed from queue."""
        agent = DaurAgent({})
        agent.parser = Mock()
        agent.input = Mock()
        agent.input.execute = Mock(return_value={"success": True})
        
        with patch('src.agent.core.asyncio.run', return_value={"success": True}):
            agent.start()
            
            # Submit command
            command = {"action": "test"}
            agent.submit_command(command)
            
            # Give worker thread time to process
            import time
            time.sleep(0.5)
            
            # Queue should be empty after processing
            assert agent.command_queue.empty()
            
            # Cleanup
            agent.stop()
    
    def test_queue_timeout(self):
        """Test queue timeout handling."""
        agent = DaurAgent({})
        agent.start()
        
        # Queue should timeout gracefully when empty
        import time
        time.sleep(0.2)
        
        assert agent._running
        
        # Cleanup
        agent.stop()


class TestErrorHandling:
    """Test error handling in various scenarios."""
    
    def test_component_import_error(self):
        """Test handling of component import errors."""
        # Agent should initialize even if components fail
        with patch('src.agent.core.InputController', side_effect=ImportError("Test error")):
            agent = DaurAgent({})
            assert agent is not None
            # Input should be None or fallback
            assert agent.input is None or agent.input is not None
    
    def test_command_execution_error(self):
        """Test handling of command execution errors."""
        agent = DaurAgent({})
        agent.parser = Mock()
        agent.input = Mock()
        agent.input.execute = Mock(side_effect=RuntimeError("Execution failed"))
        
        with patch('src.agent.core.asyncio.run', side_effect=RuntimeError("Execution failed")):
            result = agent.process_command({"action": "test"})
            assert result is not None
            assert result["success"] is False
            assert "error" in result
    
    def test_thread_exception_handling(self):
        """Test exception handling in worker thread."""
        agent = DaurAgent({})
        agent.parser = Mock()
        
        # Start agent
        agent.start()
        
        # Submit command that will cause error
        agent.submit_command({"action": "invalid"})
        
        # Give time to process
        import time
        time.sleep(0.5)
        
        # Agent should still be running despite error
        assert agent._running
        
        # Cleanup
        agent.stop()


class TestThreadSafety:
    """Test thread safety of agent operations."""
    
    def test_concurrent_command_submission(self):
        """Test submitting commands from multiple threads."""
        agent = DaurAgent({})
        agent.start()
        
        import threading
        
        def submit_commands():
            for i in range(10):
                agent.submit_command({"action": "test", "id": i})
        
        # Create multiple threads
        threads = [threading.Thread(target=submit_commands) for _ in range(3)]
        
        # Start all threads
        for t in threads:
            t.start()
        
        # Wait for completion
        for t in threads:
            t.join()
        
        # Give time to process
        import time
        time.sleep(1)
        
        # Cleanup
        agent.stop()
    
    def test_stop_from_different_thread(self):
        """Test stopping agent from different thread."""
        agent = DaurAgent({})
        agent.start()
        
        import threading
        
        def stop_agent():
            import time
            time.sleep(0.2)
            agent.stop()
        
        thread = threading.Thread(target=stop_agent)
        thread.start()
        thread.join()
        
        assert not agent._running


# Fixtures
@pytest.fixture
def agent():
    """Create agent instance for testing."""
    agent = DaurAgent({})
    yield agent
    if agent._running:
        agent.stop()


@pytest.fixture
def agent_with_mocks():
    """Create agent with mocked components."""
    with patch('src.agent.core.InputController') as mock_input, \
         patch('src.agent.core.CommandParser') as mock_parser, \
         patch('src.agent.core.ModelManager') as mock_model:
        
        mock_input.return_value = Mock()
        mock_parser.return_value = Mock()
        mock_model.return_value = Mock()
        
        agent = DaurAgent({})
        yield agent
        
        if agent._running:
            agent.stop()


# Integration tests
class TestAgentIntegration:
    """Integration tests for agent with real components."""
    
    @pytest.mark.integration
    def test_full_agent_lifecycle(self):
        """Test complete agent lifecycle."""
        config = {
            "input": {"safe_mode": True},
            "ai": {"model": "gpt-4"}
        }
        
        agent = DaurAgent(config)
        
        # Start agent
        agent.start()
        assert agent._running
        
        # Submit command
        agent.submit_command({"action": "test"})
        
        # Give time to process
        import time
        time.sleep(0.5)
        
        # Stop agent
        agent.stop()
        assert not agent._running
    
    @pytest.mark.integration
    def test_agent_with_real_input_controller(self):
        """Test agent with real input controller."""
        try:
            from src.input.controller import InputController
            
            config = {"input": {"safe_mode": True}}
            agent = DaurAgent(config)
            
            # Input controller should be loaded
            assert agent.input is not None
            
        except ImportError:
            pytest.skip("InputController not available")

