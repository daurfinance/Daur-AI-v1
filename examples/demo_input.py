#!/usr/bin/env python3
"""Demo for InputController usage.

This script demonstrates basic usage of the InputController. It asks for
confirmation before performing any real input actions to avoid accidental
clicks/typing.
"""
import sys
import time
import logging

from src.input.controller import InputController


def confirm(prompt: str) -> bool:
    ans = input(f"{prompt} [y/N]: ")
    return ans.strip().lower() in ("y", "yes")


def main():
    logging.basicConfig(level=logging.INFO)
    cfg = {
        "mouse_speed": 1.0,
        "keyboard_delay": 0.02,
        "safe_mode": False,
    }

    ic = InputController(cfg)

    print("This demo will perform a typing action and take a screenshot.")
    if not confirm("Continue and allow real input actions?"):
        print("Aborted by user")
        return

    try:
        # Start controller (no-op for current implementation)
        import asyncio
        asyncio.run(ic.start())

        # Type some text
        res = asyncio.run(ic.execute({"subtype": "type", "text": "Hello from Daur-AI demo!"}))
        print("Type result:", res)

        # Take screenshot
        path = f"demo_screenshot_{int(time.time())}.png"
        res = asyncio.run(ic.execute({"subtype": "screenshot", "path": path}))
        print("Screenshot saved to:", res.get("path") if isinstance(res, dict) else res)

    finally:
        try:
            asyncio.run(ic.stop())
        except Exception:
            pass


if __name__ == '__main__':
    main()
