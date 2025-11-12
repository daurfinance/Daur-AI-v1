# Agent Core API

The Agent Core is the central orchestration system for Daur AI. It coordinates all AI operations, task planning, execution, and monitoring.

## Overview

The `AgentCore` class provides the primary interface for interacting with Daur AI. It manages task execution, state management, and coordination between all subsystems including vision, input control, and browser automation.

## Class: AgentCore

### Initialization

```python
from src.agent.agent_core import AgentCore
from src.config import AgentConfig

# Basic initialization
agent = AgentCore()

# With custom configuration
config = AgentConfig(
    model="gpt-4",
    max_tokens=4096,
    temperature=0.7,
    timeout=300
)
agent = AgentCore(config=config)

# Initialize the agent
await agent.initialize()
```

### Core Methods

#### execute_task()

Execute a natural language task with full autonomy.

**Signature:**
```python
async def execute_task(
    self,
    task: str,
    context: Optional[Dict[str, Any]] = None,
    max_steps: int = 50
) -> TaskResult
```

**Parameters:**
- `task` (str): Natural language description of the task to execute
- `context` (dict, optional): Additional context or parameters for the task
- `max_steps` (int): Maximum number of steps before timeout (default: 50)

**Returns:**
- `TaskResult`: Object containing execution results, status, and metadata

**Example:**
```python
result = await agent.execute_task(
    task="Open Chrome, navigate to GitHub, and create a new repository named 'test-repo'",
    context={"github_token": "ghp_xxx"},
    max_steps=100
)

print(f"Status: {result.status}")
print(f"Output: {result.output}")
print(f"Steps taken: {result.steps_count}")
```

**Raises:**
- `AgentException`: If task execution fails
- `TimeoutError`: If max_steps is exceeded
- `ValidationError`: If task description is invalid

---

#### plan_task()

Generate an execution plan for a task without executing it.

**Signature:**
```python
async def plan_task(
    self,
    task: str,
    context: Optional[Dict[str, Any]] = None
) -> TaskPlan
```

**Parameters:**
- `task` (str): Natural language description of the task
- `context` (dict, optional): Additional context for planning

**Returns:**
- `TaskPlan`: Structured plan with steps, dependencies, and estimated duration

**Example:**
```python
plan = await agent.plan_task("Research competitors and create comparison report")

for step in plan.steps:
    print(f"{step.order}. {step.description} (Est: {step.estimated_time}s)")
```

---

#### get_status()

Get current agent status and active tasks.

**Signature:**
```python
def get_status(self) -> AgentStatus
```

**Returns:**
- `AgentStatus`: Current state, active tasks, and resource usage

**Example:**
```python
status = agent.get_status()
print(f"State: {status.state}")
print(f"Active tasks: {status.active_tasks}")
print(f"CPU usage: {status.cpu_percent}%")
print(f"Memory usage: {status.memory_mb}MB")
```

---

#### pause_task()

Pause the currently executing task.

**Signature:**
```python
async def pause_task(self, task_id: str) -> bool
```

**Parameters:**
- `task_id` (str): ID of the task to pause

**Returns:**
- `bool`: True if successfully paused

**Example:**
```python
task_id = result.task_id
await agent.pause_task(task_id)
```

---

#### resume_task()

Resume a paused task.

**Signature:**
```python
async def resume_task(self, task_id: str) -> bool
```

**Parameters:**
- `task_id` (str): ID of the task to resume

**Returns:**
- `bool`: True if successfully resumed

**Example:**
```python
await agent.resume_task(task_id)
```

---

#### cancel_task()

Cancel a running or paused task.

**Signature:**
```python
async def cancel_task(self, task_id: str) -> bool
```

**Parameters:**
- `task_id` (str): ID of the task to cancel

**Returns:**
- `bool`: True if successfully cancelled

**Example:**
```python
await agent.cancel_task(task_id)
```

---

#### shutdown()

Gracefully shutdown the agent and cleanup resources.

**Signature:**
```python
async def shutdown(self) -> None
```

**Example:**
```python
await agent.shutdown()
```

---

## Data Classes

### TaskResult

Result object returned by `execute_task()`.

**Attributes:**
- `task_id` (str): Unique identifier for the task
- `status` (str): Execution status ("success", "failed", "cancelled")
- `output` (Any): Task output or result
- `steps_count` (int): Number of steps executed
- `duration` (float): Execution time in seconds
- `error` (Optional[str]): Error message if failed
- `metadata` (dict): Additional execution metadata

---

### TaskPlan

Execution plan returned by `plan_task()`.

**Attributes:**
- `task_id` (str): Unique identifier for the plan
- `steps` (List[PlanStep]): Ordered list of execution steps
- `estimated_duration` (float): Total estimated time in seconds
- `dependencies` (List[str]): External dependencies required
- `risks` (List[str]): Potential risks or challenges

---

### AgentStatus

Current agent status returned by `get_status()`.

**Attributes:**
- `state` (str): Current state ("idle", "running", "paused", "error")
- `active_tasks` (List[str]): List of active task IDs
- `cpu_percent` (float): CPU usage percentage
- `memory_mb` (float): Memory usage in megabytes
- `uptime` (float): Time since initialization in seconds

---

## Configuration

### AgentConfig

Configuration object for agent initialization.

**Attributes:**
- `model` (str): AI model to use (default: "gpt-4")
- `max_tokens` (int): Maximum tokens per request (default: 4096)
- `temperature` (float): Model temperature (default: 0.7)
- `timeout` (int): Default task timeout in seconds (default: 300)
- `retry_attempts` (int): Number of retry attempts on failure (default: 3)
- `log_level` (str): Logging level (default: "INFO")

**Example:**
```python
config = AgentConfig(
    model="gpt-4-turbo",
    max_tokens=8192,
    temperature=0.5,
    timeout=600,
    retry_attempts=5,
    log_level="DEBUG"
)
```

---

## Error Handling

The Agent Core uses specific exception types for different error scenarios:

```python
from src.exceptions import (
    AgentException,
    TaskExecutionError,
    PlanningError,
    ValidationError
)

try:
    result = await agent.execute_task(task)
except TaskExecutionError as e:
    print(f"Task execution failed: {e}")
except PlanningError as e:
    print(f"Task planning failed: {e}")
except ValidationError as e:
    print(f"Invalid task description: {e}")
except AgentException as e:
    print(f"General agent error: {e}")
```

---

## Best Practices

**Task Descriptions**  
Provide clear, specific task descriptions with all necessary context. The more detailed the description, the better the execution quality.

**Resource Management**  
Always call `shutdown()` when done to properly cleanup resources and prevent memory leaks.

**Error Handling**  
Implement proper error handling for production use. The agent can encounter various failure modes that should be handled gracefully.

**Monitoring**  
Regularly check agent status during long-running tasks to monitor resource usage and detect potential issues early.

**Timeouts**  
Set appropriate timeouts based on task complexity. Complex tasks may require higher `max_steps` values.

---

## Examples

### Complete Task Execution

```python
import asyncio
from src.agent.agent_core import AgentCore
from src.config import AgentConfig

async def main():
    # Initialize agent
    config = AgentConfig(model="gpt-4", timeout=600)
    agent = AgentCore(config=config)
    await agent.initialize()
    
    try:
        # Execute task
        result = await agent.execute_task(
            task="Research the top 5 AI companies and create a comparison spreadsheet",
            max_steps=200
        )
        
        if result.status == "success":
            print(f"Task completed in {result.duration}s")
            print(f"Output: {result.output}")
        else:
            print(f"Task failed: {result.error}")
            
    finally:
        # Cleanup
        await agent.shutdown()

asyncio.run(main())
```

### Task Planning and Monitoring

```python
async def plan_and_execute():
    agent = AgentCore()
    await agent.initialize()
    
    # First, plan the task
    plan = await agent.plan_task("Automate monthly report generation")
    print(f"Plan has {len(plan.steps)} steps")
    print(f"Estimated duration: {plan.estimated_duration}s")
    
    # Review and approve plan
    if input("Execute plan? (y/n): ").lower() == 'y':
        result = await agent.execute_task("Automate monthly report generation")
        
        # Monitor progress
        while result.status == "running":
            status = agent.get_status()
            print(f"Progress: {status.active_tasks}")
            await asyncio.sleep(5)
    
    await agent.shutdown()
```

---

*API Version: 2.0.0*  
*Last Updated: 2025-11-12*

