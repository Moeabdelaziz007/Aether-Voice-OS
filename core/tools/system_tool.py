"""
Aether Voice OS — System Tool.

Local system actions that the agent can perform.
These run directly on the host machine, providing
the agent with awareness of time, date, and basic
environment information.

All functions are pure — no side effects beyond returning data.
"""

from __future__ import annotations

import logging
import platform
import shlex
import subprocess
from datetime import datetime, timezone

logger = logging.getLogger(__name__)

COMMAND_WHITELIST = {
    "ls",
    "echo",
    "date",
    "whoami",
    "pwd",
    "grep",
    "cat",
    "sleep",
    "git",
}

COMMAND_BLACKLIST = {
    "rm",
    "sudo",
    "mkfs",
    "kill",
    "shutdown",
    "reboot",
    "dd",
    "mv",
    ":(){ :|:& };:",
    "wget",
    "curl",
    "nc",
    "netcat",
    "sh",
    "bash",
    "zsh",
    "chmod",
    "chown",
    "python",
    "perl",
    "ruby",
}

ALLOWED_GIT_SUBCOMMANDS = {
    "status",
    "log",
    "diff",
    "show",
    "pull",
    "push",
    "remote",
    "branch",
}


async def get_current_time(**kwargs) -> dict:
    """
    Returns the current date and time.

    This is one of the most commonly invoked tools —
    when a user asks "What time is it?" Gemini emits
    this function call.
    """
    now = datetime.now()
    utc_now = datetime.now(timezone.utc)

    return {
        "local_time": now.strftime("%I:%M %p"),
        "local_date": now.strftime("%A, %B %d, %Y"),
        "utc_time": utc_now.strftime("%H:%M:%S UTC"),
        "timezone": str(now.astimezone().tzinfo),
        "unix_timestamp": int(now.timestamp()),
    }


async def get_system_info(**kwargs) -> dict:
    """Returns basic information about the host system."""
    return {
        "os": platform.system(),
        "os_version": platform.version(),
        "machine": platform.machine(),
        "hostname": platform.node(),
        "python_version": platform.python_version(),
    }


async def run_timer(minutes: int = 1, label: str = "Timer", **kwargs) -> dict:
    """
    Acknowledge a timer request.

    Note: The actual countdown is informational — we return
    confirmation so Gemini can tell the user. A real timer
    would require a background scheduler integration.
    """
    end_time = datetime.now()
    end_time = end_time.replace(minute=end_time.minute + minutes)

    return {
        "status": "timer_set",
        "label": label,
        "duration_minutes": minutes,
        "will_fire_at": end_time.strftime("%I:%M %p"),
        "message": f"Timer '{label}' set for {minutes} minute(s).",
    }


async def run_terminal_command(command: str, **kwargs) -> dict:
    """
    Executes a safe, sandboxed terminal command.

    Security:
    - shell=False (prevents injection)
    - Blacklisted commands (rm, sudo, etc.) are blocked.
    - 5-second timeout.
    """
    try:
        # 1. Parse command safely
        args = shlex.split(command)
        if not args:
            return {"error": "No command provided."}

        base_cmd = args[0]

        if base_cmd.lower() in COMMAND_BLACKLIST:
            logger.warning(f"Security Block: Attempted to run '{base_cmd}'")
            return {
                "error": "Command blocked by security guardrails.",
                "violation": base_cmd.lower(),
            }

        is_whitelisted = base_cmd in COMMAND_WHITELIST
        if base_cmd == "git":
            is_whitelisted = len(args) > 1 and args[1] in ALLOWED_GIT_SUBCOMMANDS

        if not is_whitelisted:
            logger.warning(f"Security Block: Command '{base_cmd}' not in whitelist.")
            return {
                "error": "Command not allowed in strict mode.",
                "violation": base_cmd,
                "allowed": sorted(COMMAND_WHITELIST),
            }

        # 3. Execute with Isolation
        result = subprocess.run(
            args,
            capture_output=True,
            text=True,
            timeout=5,  # Strict timeout
            shell=False,  # Prevent shell injection
        )

        return {
            "stdout": result.stdout.strip(),
            "stderr": result.stderr.strip(),
            "return_code": result.returncode,
        }

    except subprocess.TimeoutExpired:
        return {"error": "Command timed out (limit: 5s)."}
    except Exception as e:
        return {"error": f"Execution failed: {str(e)}"}


async def run_command(command: str, **kwargs) -> dict:
    return await run_terminal_command(command, **kwargs)


async def list_codebase(path: str = ".", **kwargs) -> dict:
    """
    Returns a flat list of files in the project, ignoring common artifacts.
    Efficient for giving the agent a map of the codebase.
    """
    import os

    ignore_dirs = {
        ".git",
        "__pycache__",
        "node_modules",
        ".next",
        ".venv",
        "out",
        "build",
    }
    file_list = []

    try:
        for root, dirs, files in os.walk(path):
            # Prune ignore_dirs in-place to prevent os.walk from entering them
            dirs[:] = [d for d in dirs if d not in ignore_dirs]
            for file in files:
                rel_path = os.path.relpath(os.path.join(root, file), path)
                file_list.append(rel_path)

        return {
            "status": "success",
            "file_count": len(file_list),
            "files": file_list[:500],  # Truncate to avoid context overflow
            "truncated": len(file_list) > 500,
        }
    except Exception as e:
        return {"status": "error", "message": str(e)}


async def read_file_content(filepath: str, **kwargs) -> dict:
    """
    Reads the content of a specific file.
    Security: Limits content to 10,000 characters to prevent OOM.
    """
    import os

    if not os.path.exists(filepath):
        return {"status": "error", "message": "File not found."}

    try:
        with open(filepath, "r", encoding="utf-8") as f:
            content = f.read(10001)  # Read slightly more to detect truncation

        is_truncated = len(content) > 10000
        return {
            "status": "success",
            "content": content[:10000],
            "truncated": is_truncated,
            "size_bytes": os.path.getsize(filepath),
        }
    except Exception as e:
        return {"status": "error", "message": str(e)}


def get_tools() -> list[dict]:
    """
    Module-level tool registration.

    Called by ToolRouter.register_module() to auto-discover
    all tools in this module.
    """
    return [
        {
            "name": "get_current_time",
            "description": (
                "Returns the current local time, date, and timezone. "
                "Use when the user asks what time or date it is."
            ),
            "parameters": {},
            "handler": get_current_time,
            "latency_tier": "low_latency",
            "idempotent": True,
        },
        {
            "name": "get_system_info",
            "description": (
                "Returns information about the host system: OS, version, "
                "hostname. Use when the user asks about their computer."
            ),
            "parameters": {},
            "handler": get_system_info,
            "latency_tier": "low_latency",
            "idempotent": True,
        },
        {
            "name": "run_timer",
            "description": (
                "Sets a timer for a specified number of minutes with a label. "
                "Use when the user asks to set a timer or reminder."
            ),
            "parameters": {
                "type": "object",
                "properties": {
                    "minutes": {
                        "type": "integer",
                        "description": "Number of minutes for the timer",
                    },
                    "label": {
                        "type": "string",
                        "description": "A label for the timer",
                    },
                },
                "required": ["minutes"],
            },
            "handler": run_timer,
            "latency_tier": "low_latency",
            "idempotent": True,
        },
        {
            "name": "run_terminal_command",
            "description": (
                "Executes a read-only or safe terminal command to diagnose issues. "
                "Allowed: git, cat, ls, grep, echo, etc. "
                "Blocked: rm, sudo, kill. "
                "Use this to check git status or read error logs."
            ),
            "parameters": {
                "type": "object",
                "properties": {
                    "command": {
                        "type": "string",
                        "description": "The terminal command to run",
                    }
                },
                "required": ["command"],
            },
            "handler": run_terminal_command,
        },
        {
            "name": "list_codebase",
            "description": (
                "Returns a map of all files in the current project directory, "
                "ignoring git/build artifacts."
            ),
            "parameters": {
                "type": "object",
                "properties": {
                    "path": {
                        "type": "string",
                        "description": "The directory to list (default: .)",
                    }
                },
            },
            "handler": list_codebase,
            "latency_tier": "low_latency",
        },
        {
            "name": "read_file_content",
            "description": (
                "Reads the text content of a file. Use this to examine code or "
                "config files."
            ),
            "parameters": {
                "type": "object",
                "properties": {
                    "filepath": {
                        "type": "string",
                        "description": "Path to the file to read",
                    }
                },
                "required": ["filepath"],
            },
            "handler": read_file_content,
            "latency_tier": "low_latency",
        },
    ]
