#!/usr/bin/env python3
"""
Daur AI MVP Chat Interface
Interactive chat with autonomous agent using local LLM
"""

import asyncio
import logging
import sys
from pathlib import Path

# Add src to path
sys.path.insert(0, str(Path(__file__).parent / "src"))

from mvp import get_mvp_agent


# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)

logger = logging.getLogger(__name__)


def print_banner():
    """Print welcome banner"""
    banner = """
╔═══════════════════════════════════════════════════════════╗
║                                                           ║
║              🤖 Daur AI MVP Agent 🤖                      ║
║                                                           ║
║         Autonomous AI with 100% Local LLM                 ║
║                                                           ║
║  Powered by: Ollama + Llama 3.2 + LLaVA                  ║
║  Cost: $0 (Free!)                                         ║
║                                                           ║
╚═══════════════════════════════════════════════════════════╝

Capabilities:
  • Browser Control (Chrome, Safari)
  • Creative Apps (Photoshop, Blender, Canva, Word)
  • Local Coding (Create, Save, Run)
  • BlueStacks Emulator
  • Free Screen Analysis (OCR + Accessibility + Vision)

Commands:
  /task <description>  - Execute a task
  /status              - Show agent status
  /screenshot          - Take and analyze screenshot
  /help                - Show help
  /quit                - Exit

Type your message or command...
"""
    print(banner)


async def main():
    """Main chat loop"""
    print_banner()
    
    # Initialize agent
    logger.info("Initializing MVP agent...")
    agent = get_mvp_agent()
    
    print("\n✓ Agent ready!\n")
    
    while True:
        try:
            # Get user input
            user_input = input("You: ").strip()
            
            if not user_input:
                continue
            
            # Handle commands
            if user_input.startswith('/'):
                command_parts = user_input[1:].split(maxsplit=1)
                command = command_parts[0].lower()
                args = command_parts[1] if len(command_parts) > 1 else ""
                
                if command == 'quit' or command == 'exit':
                    print("\n👋 Goodbye!\n")
                    break
                
                elif command == 'help':
                    print("\nCommands:")
                    print("  /task <description>  - Execute a task")
                    print("  /status              - Show agent status")
                    print("  /screenshot          - Take and analyze screenshot")
                    print("  /help                - Show this help")
                    print("  /quit                - Exit")
                    print()
                
                elif command == 'status':
                    status = agent.get_status()
                    print("\n📊 Agent Status:")
                    print(f"  Current Task: {status['current_task'] or 'None'}")
                    print(f"  Progress: {status['current_step']}/{status['total_steps']}")
                    
                    stats = status['statistics']
                    if stats.get('total_analyses', 0) > 0:
                        print(f"\n📈 Vision Statistics:")
                        print(f"  Total Analyses: {stats['total_analyses']}")
                        print(f"  Accessibility API: {stats.get('accessibility_percentage', 0):.1f}%")
                        print(f"  OCR: {stats.get('ocr_percentage', 0):.1f}%")
                        print(f"  Vision Model: {stats.get('vision_model_percentage', 0):.1f}%")
                    print()
                
                elif command == 'screenshot':
                    print("\n📸 Taking screenshot...")
                    screenshot_path = agent.take_screenshot()
                    
                    if screenshot_path:
                        print(f"✓ Screenshot saved: {screenshot_path}")
                        
                        print("\n🔍 Analyzing screen...")
                        analysis = agent.analyze_current_screen()
                        
                        print(f"\nApp: {analysis.get('app_name', 'Unknown')}")
                        print(f"Window: {analysis.get('window_title', 'Unknown')}")
                        print(f"Method: {analysis.get('method_used', 'Unknown')}")
                        print(f"Time: {analysis.get('analysis_time', 0):.2f}s")
                        
                        if analysis.get('text_content'):
                            print(f"\nText (first 200 chars):")
                            print(analysis['text_content'][:200])
                    else:
                        print("✗ Failed to take screenshot")
                    print()
                
                elif command == 'task':
                    if not args:
                        print("Usage: /task <description>")
                        continue
                    
                    print(f"\n🚀 Starting task: {args}\n")
                    
                    success = await agent.execute_task(args)
                    
                    if success:
                        print("\n✓ Task completed successfully!\n")
                    else:
                        print("\n✗ Task failed\n")
                
                else:
                    print(f"Unknown command: {command}")
                    print("Type /help for available commands")
            
            else:
                # Regular chat
                print("\nAgent: ", end="", flush=True)
                response = agent.chat(user_input)
                print(response)
                print()
        
        except KeyboardInterrupt:
            print("\n\n👋 Goodbye!\n")
            break
        
        except Exception as e:
            logger.error(f"Error: {e}", exc_info=True)
            print(f"\n✗ Error: {e}\n")


if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        print("\n\n👋 Goodbye!\n")

