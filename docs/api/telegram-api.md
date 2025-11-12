# Telegram Bot Integration API

**Version**: 2.0  
**Last Updated**: 2025-11-12  
**Status**: Production Ready

---

## Overview

The Telegram Bot Integration API enables seamless integration of Daur AI with Telegram, allowing users to control automation workflows, receive notifications, and interact with the system through a conversational interface. This API provides comprehensive bot functionality including message handling, command processing, file uploads, and inline keyboards.

---

## Table of Contents

1. [Getting Started](#getting-started)
2. [Bot Configuration](#bot-configuration)
3. [Message Handling](#message-handling)
4. [Command Processing](#command-processing)
5. [File Operations](#file-operations)
6. [Inline Keyboards](#inline-keyboards)
7. [Notifications](#notifications)
8. [Security](#security)
9. [Examples](#examples)

---

## Getting Started

### Creating a Telegram Bot

Before using the Telegram API, you need to create a bot through BotFather:

1. Open Telegram and search for `@BotFather`
2. Send `/newbot` command
3. Follow the prompts to set bot name and username
4. Save the bot token provided by BotFather

### Basic Setup

```python
from src.integrations.telegram_bot import TelegramBot

# Initialize bot with token
bot = TelegramBot(
    token="YOUR_BOT_TOKEN",
    allowed_users=[123456789, 987654321]  # Telegram user IDs
)

# Start bot
bot.start()
print("Bot is running...")
```

---

## Bot Configuration

### Configuration Options

```python
config = {
    "token": "YOUR_BOT_TOKEN",
    "allowed_users": [123456789],  # Whitelist of user IDs
    "enable_voice": True,  # Enable voice message processing
    "enable_files": True,  # Enable file uploads
    "max_file_size_mb": 20,
    "language": "en",
    "timezone": "UTC"
}

bot = TelegramBot(config)
```

### User Authorization

```python
# Add authorized user
bot.add_authorized_user(user_id=123456789, role="admin")

# Remove user
bot.remove_authorized_user(user_id=123456789)

# Check authorization
if bot.is_authorized(user_id=123456789):
    # Process request
    pass
```

---

## Message Handling

### Text Messages

```python
@bot.message_handler(content_types=['text'])
def handle_text(message):
    """Handle incoming text messages."""
    user_id = message.from_user.id
    text = message.text
    
    # Process message
    response = process_user_message(text)
    
    # Send response
    bot.send_message(user_id, response)
```

### Voice Messages

```python
@bot.message_handler(content_types=['voice'])
def handle_voice(message):
    """Handle voice messages."""
    user_id = message.from_user.id
    
    # Download voice file
    file_info = bot.get_file(message.voice.file_id)
    voice_data = bot.download_file(file_info.file_path)
    
    # Transcribe voice to text
    text = transcribe_audio(voice_data)
    
    # Process as text
    response = process_user_message(text)
    bot.send_message(user_id, response)
```

### Photo Messages

```python
@bot.message_handler(content_types=['photo'])
def handle_photo(message):
    """Handle photo uploads."""
    user_id = message.from_user.id
    
    # Get highest resolution photo
    photo = message.photo[-1]
    file_info = bot.get_file(photo.file_id)
    photo_data = bot.download_file(file_info.file_path)
    
    # Process image
    result = analyze_image(photo_data)
    bot.send_message(user_id, f"Image analysis: {result}")
```

---

## Command Processing

### Registering Commands

```python
@bot.command_handler('start')
def cmd_start(message):
    """Handle /start command."""
    welcome_text = """
Welcome to Daur AI Bot! 🤖

Available commands:
/help - Show help
/status - Check system status
/run - Execute automation
/stop - Stop current task
    """
    bot.send_message(message.chat.id, welcome_text)

@bot.command_handler('status')
def cmd_status(message):
    """Handle /status command."""
    status = get_system_status()
    bot.send_message(
        message.chat.id,
        f"System Status: {status['state']}\n"
        f"CPU: {status['cpu']}%\n"
        f"Memory: {status['memory']}%"
    )

@bot.command_handler('run')
def cmd_run(message):
    """Handle /run command with parameters."""
    # Extract parameters
    params = message.text.split()[1:]  # Skip command
    
    if not params:
        bot.send_message(message.chat.id, "Usage: /run <task_name>")
        return
    
    task_name = params[0]
    result = execute_task(task_name)
    bot.send_message(message.chat.id, f"Task result: {result}")
```

---

## File Operations

### Uploading Files

```python
# Send document
with open('/path/to/file.pdf', 'rb') as file:
    bot.send_document(chat_id=user_id, document=file)

# Send photo
with open('/path/to/image.jpg', 'rb') as photo:
    bot.send_photo(chat_id=user_id, photo=photo, caption="Screenshot")

# Send video
with open('/path/to/video.mp4', 'rb') as video:
    bot.send_video(chat_id=user_id, video=video)
```

### Downloading Files

```python
@bot.message_handler(content_types=['document'])
def handle_document(message):
    """Handle document uploads."""
    user_id = message.from_user.id
    
    # Get file info
    file_info = bot.get_file(message.document.file_id)
    file_name = message.document.file_name
    
    # Download file
    file_data = bot.download_file(file_info.file_path)
    
    # Save file
    save_path = f"/uploads/{user_id}/{file_name}"
    with open(save_path, 'wb') as f:
        f.write(file_data)
    
    bot.send_message(user_id, f"File saved: {file_name}")
```

---

## Inline Keyboards

### Creating Keyboards

```python
from telebot import types

def create_menu_keyboard():
    """Create inline keyboard menu."""
    keyboard = types.InlineKeyboardMarkup()
    
    # Add buttons
    keyboard.add(
        types.InlineKeyboardButton("▶️ Start Task", callback_data="start_task"),
        types.InlineKeyboardButton("⏹️ Stop Task", callback_data="stop_task")
    )
    keyboard.add(
        types.InlineKeyboardButton("📊 View Status", callback_data="view_status"),
        types.InlineKeyboardButton("⚙️ Settings", callback_data="settings")
    )
    
    return keyboard

# Send message with keyboard
bot.send_message(
    chat_id=user_id,
    text="Choose an action:",
    reply_markup=create_menu_keyboard()
)
```

### Handling Callbacks

```python
@bot.callback_query_handler(func=lambda call: True)
def handle_callback(call):
    """Handle inline keyboard callbacks."""
    user_id = call.from_user.id
    data = call.data
    
    if data == "start_task":
        result = start_automation_task()
        bot.answer_callback_query(call.id, "Task started!")
        bot.send_message(user_id, f"Task running: {result}")
        
    elif data == "stop_task":
        stop_automation_task()
        bot.answer_callback_query(call.id, "Task stopped!")
        
    elif data == "view_status":
        status = get_system_status()
        bot.send_message(user_id, f"Status: {status}")
        
    elif data == "settings":
        bot.send_message(user_id, "Settings menu", reply_markup=create_settings_keyboard())
```

---

## Notifications

### Sending Notifications

```python
from src.integrations.telegram_notifier import TelegramNotifier

# Initialize notifier
notifier = TelegramNotifier(bot_token="YOUR_TOKEN")

# Send simple notification
notifier.notify(
    user_id=123456789,
    message="Task completed successfully! ✅"
)

# Send notification with details
notifier.notify(
    user_id=123456789,
    message="Automation Report",
    details={
        "Task": "Web Scraping",
        "Status": "Completed",
        "Items": 150,
        "Duration": "5 minutes"
    }
)

# Send alert
notifier.alert(
    user_id=123456789,
    level="warning",
    message="High CPU usage detected: 85%"
)
```

### Scheduled Notifications

```python
from apscheduler.schedulers.background import BackgroundScheduler

scheduler = BackgroundScheduler()

def send_daily_report():
    """Send daily report to users."""
    report = generate_daily_report()
    for user_id in authorized_users:
        notifier.notify(user_id, f"Daily Report:\n{report}")

# Schedule daily report at 9 AM
scheduler.add_job(send_daily_report, 'cron', hour=9)
scheduler.start()
```

---

## Security

### User Authentication

```python
def authenticate_user(user_id):
    """Verify user is authorized."""
    if user_id not in config['allowed_users']:
        return False
    return True

@bot.message_handler(func=lambda m: True)
def handle_all_messages(message):
    """Handle all messages with authentication."""
    if not authenticate_user(message.from_user.id):
        bot.send_message(
            message.chat.id,
            "⛔ Unauthorized. Contact admin for access."
        )
        return
    
    # Process message
    process_message(message)
```

### Rate Limiting

```python
from functools import wraps
from time import time

user_last_request = {}
RATE_LIMIT = 5  # seconds between requests

def rate_limit(func):
    """Rate limiting decorator."""
    @wraps(func)
    def wrapper(message):
        user_id = message.from_user.id
        current_time = time()
        
        if user_id in user_last_request:
            time_diff = current_time - user_last_request[user_id]
            if time_diff < RATE_LIMIT:
                bot.send_message(
                    message.chat.id,
                    f"Please wait {RATE_LIMIT - int(time_diff)} seconds"
                )
                return
        
        user_last_request[user_id] = current_time
        return func(message)
    
    return wrapper

@bot.command_handler('run')
@rate_limit
def cmd_run(message):
    """Rate-limited command."""
    # Process command
    pass
```

---

## Examples

### Complete Bot Implementation

```python
from src.integrations.telegram_bot import TelegramBot
from src.agent.core import DaurAgent
import logging

# Setup logging
logging.basicConfig(level=logging.INFO)

# Initialize bot
bot = TelegramBot(
    token="YOUR_BOT_TOKEN",
    allowed_users=[123456789]
)

# Initialize agent
agent = DaurAgent({})

@bot.command_handler('start')
def cmd_start(message):
    """Welcome message."""
    bot.send_message(
        message.chat.id,
        "Welcome to Daur AI! 🤖\n\n"
        "Send me a task description and I'll automate it for you.\n\n"
        "Commands:\n"
        "/help - Show help\n"
        "/status - System status"
    )

@bot.command_handler('help')
def cmd_help(message):
    """Help command."""
    help_text = """
📖 *Daur AI Bot Help*

*Basic Commands:*
/start - Start the bot
/help - Show this help
/status - Check system status

*Automation:*
Just send me a description of what you want to automate!

Examples:
- "Check my email and summarize new messages"
- "Monitor website for price changes"
- "Extract data from this spreadsheet"
    """
    bot.send_message(message.chat.id, help_text, parse_mode='Markdown')

@bot.command_handler('status')
def cmd_status(message):
    """System status."""
    status = agent.get_status()
    bot.send_message(
        message.chat.id,
        f"🟢 System Online\n"
        f"Active Tasks: {status.get('active_tasks', 0)}\n"
        f"Uptime: {status.get('uptime', 'N/A')}"
    )

@bot.message_handler(content_types=['text'])
def handle_text(message):
    """Handle text messages as automation requests."""
    user_id = message.from_user.id
    text = message.text
    
    # Skip commands
    if text.startswith('/'):
        return
    
    # Send processing message
    processing_msg = bot.send_message(user_id, "🔄 Processing your request...")
    
    try:
        # Execute automation
        result = agent.process_command({
            "action": "execute_natural_language",
            "text": text
        })
        
        # Send result
        bot.edit_message_text(
            f"✅ Task completed!\n\n{result}",
            user_id,
            processing_msg.message_id
        )
        
    except Exception as e:
        bot.edit_message_text(
            f"❌ Error: {str(e)}",
            user_id,
            processing_msg.message_id
        )

# Start bot
if __name__ == '__main__':
    print("Bot started...")
    bot.polling(none_stop=True)
```

### Automation Workflow Bot

```python
@bot.command_handler('automate')
def cmd_automate(message):
    """Start automation workflow."""
    keyboard = types.InlineKeyboardMarkup()
    keyboard.add(
        types.InlineKeyboardButton("🌐 Web Scraping", callback_data="auto_web"),
        types.InlineKeyboardButton("📧 Email", callback_data="auto_email")
    )
    keyboard.add(
        types.InlineKeyboardButton("📊 Data Processing", callback_data="auto_data"),
        types.InlineKeyboardButton("🖥️ Desktop", callback_data="auto_desktop")
    )
    
    bot.send_message(
        message.chat.id,
        "Choose automation type:",
        reply_markup=keyboard
    )

@bot.callback_query_handler(func=lambda call: call.data.startswith('auto_'))
def handle_automation_type(call):
    """Handle automation type selection."""
    automation_type = call.data.replace('auto_', '')
    
    bot.send_message(
        call.message.chat.id,
        f"Selected: {automation_type}\n\n"
        f"Please describe what you want to automate:"
    )
    
    # Set user state for next message
    bot.set_state(call.from_user.id, f"awaiting_description_{automation_type}")

@bot.message_handler(func=lambda m: bot.get_state(m.from_user.id))
def handle_automation_description(message):
    """Handle automation description."""
    state = bot.get_state(message.from_user.id)
    automation_type = state.replace('awaiting_description_', '')
    
    # Execute automation
    result = execute_automation(automation_type, message.text)
    
    bot.send_message(
        message.chat.id,
        f"✅ Automation configured!\n\n{result}"
    )
    
    # Clear state
    bot.delete_state(message.from_user.id)
```

---

## See Also

- [Agent Core API](./agent-api.md) - Core automation functionality
- [System API](./system-api.md) - System integration
- [Security API](./security-api.md) - Authentication and authorization

---

**Last Updated**: 2025-11-12  
**Version**: 2.0  
**Author**: Manus AI

