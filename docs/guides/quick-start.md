# Quick Start Guide

**Version**: 2.0  
**Last Updated**: 2025-11-12  
**Estimated Time**: 15 minutes

---

## Welcome to Daur AI

This guide will help you get started with Daur AI in just 15 minutes. By the end, you will have installed the system, configured basic settings, and executed your first automation task.

Daur AI is a powerful automation framework that combines computer vision, browser automation, and AI to automate repetitive tasks on your computer. Whether you need to automate web scraping, data entry, testing, or any other repetitive workflow, Daur AI can help.

---

## Prerequisites

Before you begin, ensure your system meets these requirements:

**Operating System**: Ubuntu 22.04 or later (other Linux distributions may work but are not officially supported)

**Python**: Version 3.8 or higher must be installed on your system

**Memory**: At least 4GB RAM is recommended for basic operations, 8GB or more for complex automation tasks

**Disk Space**: Minimum 2GB of free disk space for installation and operation

**Display**: X11 or Wayland display server for GUI automation features

---

## Installation

### Step 1: Clone the Repository

Open your terminal and clone the Daur AI repository to your local machine:

```bash
git clone https://github.com/daurfinance/Daur-AI-v1.git
cd Daur-AI-v1
```

This command downloads the complete Daur AI codebase to a directory named `Daur-AI-v1` in your current location.

### Step 2: Install System Dependencies

Daur AI requires several system-level packages to function properly. Install them using the package manager:

```bash
sudo apt-get update
sudo apt-get install -y \
    python3-pip \
    python3-dev \
    xvfb \
    scrot \
    tesseract-ocr \
    tesseract-ocr-eng \
    libx11-dev \
    libxtst-dev
```

These packages provide essential functionality including Python development tools, virtual display support, screenshot capabilities, OCR (Optical Character Recognition), and X11 libraries for GUI automation.

### Step 3: Install Python Dependencies

Install all required Python packages using pip:

```bash
pip3 install -r requirements.txt
```

This command reads the `requirements.txt` file and installs all necessary Python libraries including PyAutoGUI, OpenCV, Playwright, and various AI model integrations.

### Step 4: Install Playwright Browsers

Playwright requires browser binaries to be installed separately:

```bash
python3 -m playwright install chromium
```

This downloads and installs the Chromium browser that Playwright will use for web automation tasks.

### Step 5: Verify Installation

Run the verification script to ensure everything is installed correctly:

```bash
python3 -c "from src.agent.core import DaurAgent; print('Installation successful!')"
```

If you see "Installation successful!" then the installation is complete and you are ready to proceed.

---

## Basic Configuration

### Configuration File

Create a configuration file to customize Daur AI for your needs. Copy the example configuration:

```bash
cp config.example.json config.json
```

Edit the configuration file with your preferred text editor:

```bash
nano config.json
```

Here is a basic configuration to get started:

```json
{
  "ai": {
    "provider": "openai",
    "model": "gpt-4",
    "api_key": "your-api-key-here"
  },
  "vision": {
    "ocr_enabled": true,
    "ocr_language": "eng",
    "screenshot_format": "png"
  },
  "browser": {
    "headless": false,
    "viewport_width": 1920,
    "viewport_height": 1080
  },
  "logging": {
    "level": "INFO",
    "file": "logs/daur_ai.log"
  }
}
```

**Important**: Replace `your-api-key-here` with your actual OpenAI API key. You can obtain one from the OpenAI platform at https://platform.openai.com/api-keys.

### Environment Variables

Alternatively, you can configure Daur AI using environment variables. This approach is recommended for production deployments as it keeps sensitive information out of configuration files:

```bash
export OPENAI_API_KEY="your-api-key-here"
export DAUR_AI_LOG_LEVEL="INFO"
export DAUR_AI_HEADLESS="false"
```

Add these lines to your `~/.bashrc` or `~/.zshrc` file to make them permanent.

---

## Your First Automation

Now that Daur AI is installed and configured, let's create your first automation script.

### Example 1: Simple Web Navigation

Create a new file called `first_automation.py`:

```python
from src.agent.core import DaurAgent
import asyncio

async def main():
    # Initialize the agent
    agent = DaurAgent({
        "browser": {"headless": False}
    })
    
    print("Starting automation...")
    
    # Execute a simple web navigation task
    result = agent.process_command({
        "action": "navigate_web",
        "url": "https://www.example.com",
        "wait_for": "h1"
    })
    
    print(f"Navigation result: {result}")
    
    # Take a screenshot
    screenshot_result = agent.process_command({
        "action": "take_screenshot",
        "path": "example_screenshot.png"
    })
    
    print(f"Screenshot saved: {screenshot_result}")

if __name__ == "__main__":
    asyncio.run(main())
```

Run the script:

```bash
python3 first_automation.py
```

You should see a browser window open, navigate to example.com, and a screenshot will be saved to your current directory.

### Example 2: Screen Text Recognition

Create another file called `ocr_example.py`:

```python
from src.vision.screen_recognition import ScreenRecognition

# Initialize screen recognition
screen = ScreenRecognition()

# Capture and analyze screen
result = screen.analyze_screen()

print("Text found on screen:")
for text in result['text']:
    print(f"  - {text}")

print(f"\nTotal elements detected: {len(result['elements'])}")
```

Run the script:

```bash
python3 ocr_example.py
```

This script captures your current screen and extracts all visible text using OCR technology.

### Example 3: Browser Automation

Create a file called `browser_example.py`:

```python
from src.browser.browser_automation import BrowserAutomation
import asyncio

async def main():
    # Initialize browser
    browser = BrowserAutomation(headless=False)
    await browser.init()
    
    # Navigate to a website
    await browser.navigate("https://github.com")
    
    # Find and click search button
    search_button = await browser.find_element("button[aria-label='Search']")
    if search_button:
        await browser.click("button[aria-label='Search']")
        print("Clicked search button")
    
    # Type search query
    await browser.type_text("input[type='text']", "automation")
    
    # Wait a moment
    await asyncio.sleep(2)
    
    # Take screenshot
    await browser.take_screenshot("github_search.png")
    print("Screenshot saved")
    
    # Close browser
    await browser.close()

if __name__ == "__main__":
    asyncio.run(main())
```

Run the script:

```bash
python3 browser_example.py
```

This demonstrates browser automation capabilities including navigation, element interaction, and screenshot capture.

---

## Understanding the Basics

### Agent Architecture

Daur AI uses an agent-based architecture where the **DaurAgent** class serves as the central coordinator. The agent manages different components including vision systems, browser automation, input control, and AI models.

When you create a DaurAgent instance, it initializes all necessary subsystems and provides a unified interface for automation tasks. The agent processes commands through the `process_command()` method, which accepts a dictionary specifying the action and parameters.

### Command Structure

Commands in Daur AI follow a consistent structure:

```python
command = {
    "action": "action_name",
    "param1": "value1",
    "param2": "value2"
}

result = agent.process_command(command)
```

The `action` field specifies what operation to perform, while additional fields provide parameters for that operation. The agent returns a result dictionary containing the outcome and any relevant data.

### Common Actions

Here are some frequently used actions:

**navigate_web**: Opens a URL in the browser and optionally waits for specific elements to load

**click_element**: Clicks on a screen element identified by text, image, or coordinates

**type_text**: Types text into the currently focused input field

**take_screenshot**: Captures the current screen or browser viewport

**extract_text**: Uses OCR to extract text from the screen or a specific region

**wait_for_element**: Waits until a specific element appears on screen

---

## Next Steps

Now that you have completed the quick start guide, you are ready to explore more advanced features:

**Web Automation Tutorial**: Learn how to build complex web scraping and automation workflows. See [Web Automation Guide](./web-automation.md) for detailed instructions.

**Desktop Automation**: Automate desktop applications using computer vision and input control. Read the [Desktop Automation Guide](./desktop-automation.md) to get started.

**AI Integration**: Leverage AI models to make your automation smarter and more adaptive. Check out the [AI Integration Guide](./ai-integration.md) for examples.

**API Reference**: Explore the complete API documentation to understand all available features. Visit the [API Documentation](../api/README.md) for comprehensive reference material.

**Best Practices**: Learn how to write robust, maintainable automation scripts. See [Best Practices](./best-practices.md) for expert tips.

---

## Troubleshooting

### Common Issues

**Import Errors**: If you encounter import errors, ensure all dependencies are installed correctly by running `pip3 install -r requirements.txt` again.

**Display Errors**: If you see "Cannot open display" errors, make sure you have X11 running or use Xvfb for headless operation: `xvfb-run python3 your_script.py`

**Permission Errors**: Some operations may require additional permissions. Run scripts with appropriate privileges or adjust file permissions as needed.

**Browser Not Found**: If Playwright cannot find browsers, reinstall them with `python3 -m playwright install chromium`

### Getting Help

If you encounter issues not covered here, consult the following resources:

**Documentation**: Check the comprehensive documentation in the `docs/` directory for detailed information on all features.

**GitHub Issues**: Search existing issues or create a new one at https://github.com/daurfinance/Daur-AI-v1/issues

**Community**: Join our community discussions to ask questions and share experiences.

**Logs**: Check the log files in the `logs/` directory for detailed error messages and debugging information.

---

## Summary

Congratulations! You have successfully installed Daur AI, configured basic settings, and executed your first automation tasks. You now have a solid foundation to build more complex automation workflows.

Remember that automation is an iterative process. Start with simple tasks, test thoroughly, and gradually build up to more complex workflows. The Daur AI documentation provides extensive resources to support your automation journey.

---

**Last Updated**: 2025-11-12  
**Version**: 2.0  
**Author**: Manus AI

