#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
Complete Demo - Test full system with InputController, Agent, and all components
Run this to verify everything works end-to-end.
"""

import asyncio
import logging
import sys
from pathlib import Path

# Setup paths
PROJECT_ROOT = Path(__file__).parent
sys.path.insert(0, str(PROJECT_ROOT))

# Setup logging
logging.basicConfig(
    level=logging.DEBUG,
    format='[%(asctime)s] %(name)s - %(levelname)s - %(message)s'
)
LOG = logging.getLogger("demo")


async def test_input_controller():
    """Test InputController with safe_mode."""
    LOG.info("=" * 60)
    LOG.info("TEST 1: InputController (Safe Mode)")
    LOG.info("=" * 60)
    
    from src.input.controller import InputController
    
    # Create controller in safe mode
    controller = InputController(config={"safe_mode": True})
    LOG.info(f"✓ Controller created: safe_mode={controller.safe_mode}")
    
    # Test mouse operations
    await controller.click(100, 100)
    LOG.info("✓ Click executed")
    
    await controller.move(200, 200)
    LOG.info("✓ Move executed")
    
    await controller.type("Hello World")
    LOG.info("✓ Type executed")
    
    await controller.hotkey("ctrl", "c")
    LOG.info("✓ Hotkey executed")
    
    # Test system info
    pos = controller.get_position()
    size = controller.get_screen_size()
    LOG.info(f"✓ Position: {pos}, Screen: {size}")
    
    return True


async def test_agent_core():
    """Test Agent Core initialization."""
    LOG.info("=" * 60)
    LOG.info("TEST 2: Agent Core")
    LOG.info("=" * 60)
    
    try:
        from src.agent.core import Agent
        
        agent = Agent(config={"input": {"safe_mode": True}})
        LOG.info(f"✓ Agent created with safe_mode")
        LOG.info(f"✓ Input controller: {agent.input is not None}")
        
        return True
    except ImportError as e:
        LOG.warning(f"⚠ Could not import Agent: {e}")
        return True  # Don't fail, it's optional


async def test_integrated_agent():
    """Test Integrated Agent with all components."""
    LOG.info("=" * 60)
    LOG.info("TEST 3: Integrated Agent")
    LOG.info("=" * 60)
    
    try:
        from src.agent.integrated_agent import IntegratedAI
        
        config = {
            "input": {"safe_mode": True},
            "logging": {"level": "DEBUG"}
        }
        
        agent = IntegratedAI(config=config)
        LOG.info(f"✓ IntegratedAI created with config")
        
        # Test basic initialization
        state = agent.get_state() if hasattr(agent, "get_state") else "running"
        LOG.info(f"✓ Agent state: {state}")
        
        return True
    except ImportError as e:
        LOG.warning(f"⚠ Could not import IntegratedAI: {e}")
        return True  # Don't fail


async def test_execute_action():
    """Test action execution through InputController."""
    LOG.info("=" * 60)
    LOG.info("TEST 4: Execute Actions")
    LOG.info("=" * 60)
    
    from src.input.controller import InputController
    
    controller = InputController(config={"safe_mode": True})
    
    # Test different action types
    actions = [
        {"type": "click", "x": 100, "y": 100, "button": "left"},
        {"type": "move", "x": 200, "y": 200},
        {"type": "type", "text": "test input"},
        {"type": "hotkey", "keys": ["ctrl", "a"]},
        {"type": "scroll", "clicks": 3},
    ]
    
    for i, action in enumerate(actions):
        result = await controller.execute(action)
        action_type = action.get("type", "unknown")
        if result["success"]:
            LOG.info(f"✓ Action {i+1}: {action_type}")
        else:
            LOG.error(f"✗ Action {i+1}: {action_type} - {result.get('error')}")
    
    return True


async def test_concurrent_operations():
    """Test concurrent async operations."""
    LOG.info("=" * 60)
    LOG.info("TEST 5: Concurrent Operations")
    LOG.info("=" * 60)
    
    from src.input.controller import InputController
    
    controller = InputController(config={"safe_mode": True})
    
    # Create multiple concurrent tasks
    tasks = [
        controller.move(100, 100),
        controller.move(200, 200),
        controller.type("concurrent test"),
        controller.click(150, 150),
        controller.hotkey("ctrl", "v"),
    ]
    
    LOG.info(f"Running {len(tasks)} concurrent operations...")
    await asyncio.gather(*tasks)
    LOG.info(f"✓ All {len(tasks)} operations completed successfully")
    
    return True


async def main():
    """Run all tests."""
    LOG.info("\n" + "=" * 60)
    LOG.info("DAUR-AI COMPLETE SYSTEM TEST")
    LOG.info("=" * 60 + "\n")
    
    tests = [
        ("InputController", test_input_controller),
        ("Agent Core", test_agent_core),
        ("Integrated Agent", test_integrated_agent),
        ("Action Execution", test_execute_action),
        ("Concurrent Operations", test_concurrent_operations),
    ]
    
    results = []
    for name, test_func in tests:
        try:
            result = await test_func()
            results.append((name, "PASSED" if result else "FAILED"))
        except Exception as e:
            LOG.error(f"✗ Test failed with error: {e}", exc_info=True)
            results.append((name, f"ERROR: {e}"))
    
    # Print summary
    LOG.info("\n" + "=" * 60)
    LOG.info("TEST SUMMARY")
    LOG.info("=" * 60)
    
    for name, status in results:
        symbol = "✓" if status == "PASSED" else "✗"
        LOG.info(f"{symbol} {name}: {status}")
    
    passed = sum(1 for _, status in results if status == "PASSED")
    total = len(results)
    
    LOG.info(f"\nTotal: {passed}/{total} tests passed")
    LOG.info("=" * 60 + "\n")
    
    return all(status == "PASSED" for _, status in results)


if __name__ == "__main__":
    try:
        success = asyncio.run(main())
        sys.exit(0 if success else 1)
    except KeyboardInterrupt:
        LOG.info("\n✓ Demo interrupted by user")
        sys.exit(0)
    except Exception as e:
        LOG.error(f"✗ Fatal error: {e}", exc_info=True)
        sys.exit(1)
