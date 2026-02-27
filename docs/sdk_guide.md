# 🛠️ Aether SDK Guide: Building Custom Tools

## 📡 The Neural Dispatcher Pattern

Aether OS uses a **Neural Dispatcher** (powered by `ToolRouter`) to bridge Gemini's intentions with Python execution. Every tool must follow the ADK (Aether Development Kit) standard.

## 🏗️ Anatomoy of a Tool

A tool consists of two parts:

1. **The Declaration:** A JSON schema (OpenAPI compatible) that tells Gemini *what* the tool does.
2. **The Handler:** An `async` Python function that executes the logic.

## ✍️ Example: Weather Tool (`my_weather_tool.py`)

```python
import asyncio

# 1. THE DECLARATION
def get_tools():
    return [{
        "name": "get_weather",
        "description": "Get current weather for a specific city.",
        "parameters": {
            "type": "object",
            "properties": {
                "city": {"type": "string", "description": "Name of the city"}
            },
            "required": ["city"]
        },
        "handler": handle_get_weather  # This is crucial for the Router
    }]

# 2. THE HANDLER
async def handle_get_weather(city: str) -> dict:
    """Executes the weather lookup."""
    # Simulation: Replace with real API call (e.g., OpenWeatherMap)
    await asyncio.sleep(0.5)
    return {
        "city": city,
        "temp": "22°C",
        "condition": "Cloudy",
        "status": "success"
    }
```

## 🔄 Registration Flow

To activate your tool, register it in `core/engine.py`:

```python
from core.tools import my_weather_tool

# Inside AetherEngine._register_tools()
self._router.register_module(my_weather_tool)
```

## 🧪 Testing Tools

Aether supports "Dry Run" tool testing without requiring a live voice session:

```python
from core.tools.router import ToolRouter
from google.genai import types

router = ToolRouter()
router.register_module(my_weather_tool)

# Simulate a Gemini call
fc = types.FunctionCall(name="get_weather", args={"city": "Cairo"})
result = await router.dispatch(fc)
print(result) # {'city': 'Cairo', 'temp': '22°C', ...}
```

## 🛡️ Expert Tips

1. **Semantic Clarity:** Gemini relies on descriptions to decide when to call a tool. Be extremely clear about the tool's purpose.
2. **Error Handling:** Always return a dictionary with a `status` field (`success` or `error`). Never allow a handler to crash the main engine loop.
3. **Async Everything:** Use `aiohttp` or `httpx` for network calls. Synchronous/Blocking calls will cause audio stuttering.
4. **Output Truncation:** Gemini ignores tool results that are too long. Aim for <500 tokens in the return dict.
