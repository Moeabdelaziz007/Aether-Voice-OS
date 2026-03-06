with open("core/ai/hive.py", "r") as f:
    content = f.read()

# Fix the missing parameter in __init__
content = content.replace(
    "api_key: Optional[str] = None,\n    ) -> None:",
    "api_key: Optional[str] = None,\n        enable_deep_handover: bool = True,\n        ai_config: Optional[Any] = None,\n    ) -> None:",
)

with open("core/ai/hive.py", "w") as f:
    f.write(content)
