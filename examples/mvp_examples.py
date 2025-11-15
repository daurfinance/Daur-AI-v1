#!/usr/bin/env python3
"""
Daur AI MVP Examples
Demonstrates all capabilities of the MVP agent
"""

import asyncio
import sys
from pathlib import Path

# Add src to path
sys.path.insert(0, str(Path(__file__).parent.parent / "src"))

from mvp import get_mvp_agent
from mvp.modules.browser.browser_controller import get_browser_controller
from mvp.modules.apps.photoshop_controller import get_photoshop_controller
from mvp.modules.apps.blender_controller import get_blender_controller
from mvp.modules.coding.coding_environment import get_coding_environment
from mvp.modules.emulator.bluestacks_controller import get_bluestacks_controller


def example_1_screen_analysis():
    """Example 1: Analyze current screen"""
    print("\n" + "="*60)
    print("Example 1: Screen Analysis")
    print("="*60)
    
    agent = get_mvp_agent()
    
    # Take screenshot
    screenshot_path = agent.take_screenshot()
    print(f"Screenshot: {screenshot_path}")
    
    # Analyze screen
    analysis = agent.analyze_current_screen()
    
    print(f"\nApp: {analysis['app_name']}")
    print(f"Window: {analysis['window_title']}")
    print(f"Method: {analysis['method_used']}")
    print(f"Time: {analysis['analysis_time']:.2f}s")
    
    if analysis.get('text_content'):
        print(f"\nText (first 200 chars):")
        print(analysis['text_content'][:200])


async def example_2_browser_automation():
    """Example 2: Browser automation"""
    print("\n" + "="*60)
    print("Example 2: Browser Automation")
    print("="*60)
    
    agent = get_mvp_agent()
    
    # Execute browser task
    success = await agent.execute_task(
        "Open Safari and search for 'autonomous AI agents'"
    )
    
    print(f"Task completed: {success}")


def example_3_browser_direct():
    """Example 3: Direct browser control"""
    print("\n" + "="*60)
    print("Example 3: Direct Browser Control")
    print("="*60)
    
    with get_browser_controller('chrome') as browser:
        # Navigate to Google
        browser.navigate("https://www.google.com")
        
        # Search
        browser.search_google("AI automation")
        
        # Get page title
        print(f"Page title: {browser.get_page_title()}")
        
        # Take screenshot
        browser.take_screenshot("/tmp/google_search.png")
        print("Screenshot saved: /tmp/google_search.png")


def example_4_coding():
    """Example 4: Code generation and execution"""
    print("\n" + "="*60)
    print("Example 4: Code Generation")
    print("="*60)
    
    coding = get_coding_environment()
    
    # Create and run project
    result = coding.create_and_run_project(
        project_name="hello_world",
        task_description="Create a Python script that prints 'Hello from Daur AI!' and the current date/time",
        language="python"
    )
    
    print(f"Success: {result['success']}")
    print(f"Project: {result['project_dir']}")
    print(f"\nGenerated Code:\n{result['code']}")
    print(f"\nOutput:\n{result['output']}")
    
    if result.get('error'):
        print(f"Error: {result['error']}")


def example_5_photoshop():
    """Example 5: Photoshop automation"""
    print("\n" + "="*60)
    print("Example 5: Photoshop Automation")
    print("="*60)
    
    ps = get_photoshop_controller()
    
    if not ps.is_available():
        print("Photoshop not available")
        return
    
    # Launch Photoshop
    ps.launch()
    
    # Create new document
    ps.new_document(width=800, height=600)
    
    # Add text
    ps.add_text("Created by Daur AI", x=100, y=100)
    
    # Save
    output_path = "/tmp/daur_ai_test.psd"
    ps.save_file(output_path)
    print(f"Saved: {output_path}")
    
    # Export PNG
    png_path = "/tmp/daur_ai_test.png"
    ps.export_png(png_path)
    print(f"Exported: {png_path}")


def example_6_blender():
    """Example 6: Blender 3D automation"""
    print("\n" + "="*60)
    print("Example 6: Blender 3D Automation")
    print("="*60)
    
    blender = get_blender_controller()
    
    if not blender.is_available():
        print("Blender not available")
        return
    
    # Create cube
    blend_file = "/tmp/daur_cube.blend"
    blender.create_cube(blend_file, size=2.0)
    print(f"Created cube: {blend_file}")
    
    # Render image
    render_output = "/tmp/daur_cube.png"
    blender.render_image(blend_file, render_output)
    print(f"Rendered: {render_output}")


def example_7_bluestacks():
    """Example 7: BlueStacks emulator control"""
    print("\n" + "="*60)
    print("Example 7: BlueStacks Control")
    print("="*60)
    
    bs = get_bluestacks_controller()
    
    if not bs.is_available():
        print("ADB not available. Install Android SDK Platform Tools")
        return
    
    # Connect to BlueStacks
    if not bs.connect_bluestacks():
        print("Failed to connect to BlueStacks")
        return
    
    # Get screen size
    width, height = bs.get_screen_size()
    print(f"Screen size: {width}x{height}")
    
    # List installed apps
    packages = bs.list_packages()
    print(f"Installed apps: {len(packages)}")
    
    # Take screenshot
    screenshot_path = "/tmp/bluestacks_screenshot.png"
    bs.take_screenshot(screenshot_path)
    print(f"Screenshot: {screenshot_path}")
    
    # Example: Open WhatsApp
    # bs.open_whatsapp()


def example_8_chat():
    """Example 8: Chat with agent"""
    print("\n" + "="*60)
    print("Example 8: Chat with Agent")
    print("="*60)
    
    agent = get_mvp_agent()
    
    questions = [
        "What can you do?",
        "How do I open Safari?",
        "Can you control Photoshop?"
    ]
    
    for question in questions:
        print(f"\nUser: {question}")
        response = agent.chat(question)
        print(f"Agent: {response}")


def example_9_statistics():
    """Example 9: Vision statistics"""
    print("\n" + "="*60)
    print("Example 9: Vision Statistics")
    print("="*60)
    
    agent = get_mvp_agent()
    
    # Do some screen analyses
    for i in range(3):
        agent.analyze_current_screen()
    
    # Get statistics
    stats = agent.get_status()['statistics']
    
    print(f"\nTotal Analyses: {stats['total_analyses']}")
    print(f"Accessibility API: {stats.get('accessibility_percentage', 0):.1f}%")
    print(f"OCR: {stats.get('ocr_percentage', 0):.1f}%")
    print(f"Vision Model: {stats.get('vision_model_percentage', 0):.1f}%")


async def example_10_complex_task():
    """Example 10: Complex multi-step task"""
    print("\n" + "="*60)
    print("Example 10: Complex Task")
    print("="*60)
    
    agent = get_mvp_agent()
    
    # Complex task with multiple steps
    success = await agent.execute_task(
        "Open Chrome, go to github.com, and search for 'AI automation'"
    )
    
    print(f"Task completed: {success}")


def main():
    """Run all examples"""
    print("\n" + "="*60)
    print("Daur AI MVP Examples")
    print("="*60)
    
    examples = [
        ("Screen Analysis", example_1_screen_analysis),
        ("Browser Automation", example_2_browser_automation),
        ("Direct Browser Control", example_3_browser_direct),
        ("Code Generation", example_4_coding),
        ("Photoshop Automation", example_5_photoshop),
        ("Blender 3D", example_6_blender),
        ("BlueStacks Control", example_7_bluestacks),
        ("Chat with Agent", example_8_chat),
        ("Vision Statistics", example_9_statistics),
        ("Complex Task", example_10_complex_task),
    ]
    
    print("\nAvailable examples:")
    for i, (name, _) in enumerate(examples, 1):
        print(f"  {i}. {name}")
    
    print("\nRun specific example: python mvp_examples.py <number>")
    print("Run all examples: python mvp_examples.py all")
    
    if len(sys.argv) > 1:
        arg = sys.argv[1]
        
        if arg == "all":
            # Run all examples
            for name, func in examples:
                try:
                    if asyncio.iscoroutinefunction(func):
                        asyncio.run(func())
                    else:
                        func()
                except Exception as e:
                    print(f"Error in {name}: {e}")
        else:
            # Run specific example
            try:
                index = int(arg) - 1
                if 0 <= index < len(examples):
                    name, func = examples[index]
                    print(f"\nRunning: {name}\n")
                    
                    if asyncio.iscoroutinefunction(func):
                        asyncio.run(func())
                    else:
                        func()
                else:
                    print(f"Invalid example number: {arg}")
            except ValueError:
                print(f"Invalid argument: {arg}")


if __name__ == "__main__":
    main()

