# 🧪 Testing Guide

## Running Tests

### Quick Test (5 complete system tests)
```bash
python run_demo.py
```

### Unit Tests (21 InputController tests)
```bash
pytest tests/test_input_controller_full.py -v
```

### All Tests
```bash
pytest tests/ -v
```

### With Coverage
```bash
pytest tests/ --cov=src --cov-report=html
```

## Test Suites

### 1. InputController Tests (`test_input_controller_full.py`)
- ✓ Mouse operations (click, move, drag, scroll)
- ✓ Keyboard operations (key press, type, hotkey)
- ✓ Clipboard operations (get, set)
- ✓ System info (position, screen size)
- ✓ Action execution (execute method)
- ✓ Configuration tests
- ✓ Async/concurrent operations

**Status**: 21/21 PASSED ✅

### 2. Integration Tests (`run_demo.py`)
- ✓ InputController (Safe Mode)
- ✓ Agent Core
- ✓ Integrated Agent
- ✓ Action Execution
- ✓ Concurrent Operations

**Status**: 5/5 PASSED ✅

## Safe Mode Testing

For CI/CD and safe testing without real input:

```python
# Enable safe_mode
controller = InputController(config={"safe_mode": True})

# All operations are logged but not executed
await controller.click(100, 100)  # Logged: [SAFE] Click 1x left at (100,100)
await controller.type("test")     # Logged: [SAFE] Type: test
```

## Continuous Integration

### GitHub Actions Example
```yaml
name: Tests
on: [push, pull_request]
jobs:
  test:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v2
      - uses: actions/setup-python@v2
        with:
          python-version: 3.11
      - run: pip install -r requirements.txt pytest pytest-asyncio
      - run: python run_demo.py
      - run: pytest tests/ -v
```

## Test Patterns

### Testing Async Code
```python
import pytest

@pytest.mark.asyncio
async def test_my_async_function():
    controller = InputController(config={"safe_mode": True})
    await controller.click(100, 100)
    assert controller.safe_mode is True
```

### Testing with Fixtures
```python
@pytest.fixture
def controller():
    return InputController(config={"safe_mode": True})

@pytest.mark.asyncio
async def test_with_fixture(controller):
    await controller.type("test")
    # test assertions
```

### Testing Concurrent Operations
```python
@pytest.mark.asyncio
async def test_concurrent():
    controller = InputController(config={"safe_mode": True})
    tasks = [
        controller.move(100, 100),
        controller.type("test"),
        controller.click(200, 200),
    ]
    await asyncio.gather(*tasks)
    # test assertions
```

## Performance Benchmarks

```bash
# Run with timing
python -m pytest tests/ -v --durations=10
```

Expected results with safe_mode:
- Single operation: <1ms
- 10 operations: <5ms
- 100 operations: <50ms

## Debugging Tests

### Verbose Output
```bash
pytest tests/ -vv
```

### Show Print Statements
```bash
pytest tests/ -s
```

### Stop on First Failure
```bash
pytest tests/ -x
```

### Run Specific Test
```bash
pytest tests/test_input_controller_full.py::test_click_safe_mode -v
```

### Run with Logging
```bash
pytest tests/ -v --log-cli-level=DEBUG
```

## Coverage Report

```bash
pytest tests/ --cov=src --cov-report=term-missing
```

Target: >90% coverage

## Known Issues & Workarounds

### Issue: Tests hang on macOS
**Solution**: Use safe_mode or ensure accessibility permissions are granted

### Issue: Permission denied on Linux
**Solution**: 
```bash
sudo usermod -a -G input $USER
```

### Issue: Screen capture fails
**Solution**: Some desktop environments need special permissions

## Contributing Tests

When adding new features:

1. Write test before code (TDD)
2. Use fixtures for reusable setup
3. Use parametrize for multiple test cases
4. Keep tests independent (no shared state)
5. Aim for >90% coverage

Example:
```python
@pytest.mark.parametrize("button", ["left", "right", "middle"])
@pytest.mark.asyncio
async def test_click_buttons(controller, button):
    await controller.click(100, 100, button=button)
    assert controller.safe_mode is True
```

## Test Command Reference

| Command | Purpose |
|---------|---------|
| `python run_demo.py` | Quick integration test |
| `pytest tests/ -v` | Run all unit tests |
| `pytest tests/ -k "test_click"` | Run specific tests |
| `pytest tests/ --cov=src` | Generate coverage report |
| `pytest tests/ -x` | Stop on first failure |
| `pytest tests/ -n auto` | Parallel test execution |

## Success Criteria

✅ All 21 unit tests passing
✅ All 5 integration tests passing
✅ >90% code coverage
✅ All manual tests working
✅ No warnings or errors in logs
