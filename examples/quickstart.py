#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
Quick Start Example - Simple agent automation demonstration
"""

import asyncio
import logging
from src.input.controller import InputController

logging.basicConfig(level=logging.INFO)
LOG = logging.getLogger("quickstart")


async def main():
    LOG.info("🚀 Daur-AI Quick Start Example")
    LOG.info("-" * 50)
    
    # Initialize controller
    LOG.info("1️⃣  Initializing InputController...")
    controller = InputController(config={
        "safe_mode": False,  # Set to True for safe testing
        "keyboard_delay": 0.01
    })
    LOG.info("   ✓ Controller ready")
    
    # Example 1: Mouse automation
    LOG.info("\n2️⃣  Mouse automation:")
    await controller.move(100, 100)
    LOG.info("   ✓ Moved to (100, 100)")
    
    await controller.click(100, 100, clicks=1)
    LOG.info("   ✓ Clicked")
    
    # Example 2: Keyboard automation
    LOG.info("\n3️⃣  Keyboard automation:")
    await controller.type("Hello, Daur-AI!")
    LOG.info("   ✓ Typed text")
    
    await controller.hotkey("ctrl", "a")
    LOG.info("   ✓ Selected all (Ctrl+A)")
    
    # Example 3: Clipboard
    LOG.info("\n4️⃣  Clipboard operations:")
    await controller.clipboard_set("Copied by Daur-AI")
    LOG.info("   ✓ Clipboard set")
    
    content = await controller.clipboard_get()
    LOG.info(f"   ✓ Clipboard read: {content}")
    
    # Example 4: System info
    LOG.info("\n5️⃣  System info:")
    pos = controller.get_position()
    size = controller.get_screen_size()
    LOG.info(f"   ✓ Mouse position: {pos}")
    LOG.info(f"   ✓ Screen size: {size}")
    
    LOG.info("\n✅ Quick start completed!")
    LOG.info("-" * 50)


if __name__ == "__main__":
    asyncio.run(main())
