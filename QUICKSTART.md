# 🚀 Quick Start Guide - Daur AI MVP

Get started with Daur AI MVP in 5 minutes!

---

## ⚡ Installation (One Command)

```bash
curl -fsSL https://raw.githubusercontent.com/daurfinance/Daur-AI-v1/mvp/install_mvp.sh | bash
```

**Time:** 10-15 minutes  
**Space:** ~10GB

---

## 🎮 Basic Usage

### 1. Start Interactive Chat

```bash
cd Daur-AI-v1
python3 mvp_chat.py
```

### 2. Try Commands

```
/task open Safari and search for "AI automation"
/screenshot
/status
/help
```

---

## 📝 Simple Examples

### Example 1: Screen Analysis

```python
from src.mvp import get_mvp_agent

agent = get_mvp_agent()

# Analyze current screen
analysis = agent.analyze_current_screen()
print(f"App: {analysis['app_name']}")
print(f"Window: {analysis['window_title']}")
```

### Example 2: Browser Automation

```python
from src.mvp import get_mvp_agent
import asyncio

agent = get_mvp_agent()

async def search():
    await agent.execute_task("Open Safari and search for 'AI agents'")

asyncio.run(search())
```

### Example 3: Code Generation

```python
from src.mvp.modules.coding.coding_environment import get_coding_environment

coding = get_coding_environment()

# Generate and run code
result = coding.create_and_run_project(
    project_name="hello",
    task_description="Print hello world with current time",
    language="python"
)

print(result['output'])
```

---

## 🔧 Configuration

### Change Models (for faster/slower computers)

Edit `src/mvp/core/ollama_client.py`:

```python
# Fast computers (8GB RAM)
default_model = "llama3.2:3b"
vision_model = "llava"

# Powerful computers (16GB+ RAM)
default_model = "llama3.2:11b"
vision_model = "llama3.2-vision:11b"
```

---

## 📚 More Examples

Run example scripts:

```bash
# See all examples
python3 examples/mvp_examples.py

# Run specific example
python3 examples/mvp_examples.py 1  # Screen analysis
python3 examples/mvp_examples.py 4  # Code generation

# Run all examples
python3 examples/mvp_examples.py all
```

---

## 🐛 Troubleshooting

### Ollama not running

```bash
ollama serve
```

### Models not found

```bash
ollama pull llama3.2:3b
ollama pull llava
```

### Python dependencies

```bash
pip3 install -r requirements-mvp.txt
```

---

## 📖 Full Documentation

See [MVP_README.md](MVP_README.md) for complete documentation.

---

## 🎉 You're Ready!

```bash
python3 mvp_chat.py
```

Type `/task open Safari` to test! 🚀

