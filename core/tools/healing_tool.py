"""
Aether Voice OS — Healing Tool.

Part of the "Grounded Healing" suite.
Allows Gemini to autonomously diagnose terminal errors and propose/apply fixes.
"""

import hashlib
import logging
import os
import subprocess
from pathlib import Path
from typing import Any, Optional

from core.tools.vision_tool import take_screenshot

logger = logging.getLogger(__name__)
PROJECT_ROOT = Path(__file__).resolve().parents[2]


def _resolve_project_path(filepath: str) -> Path:
    """Resolve and validate a path so writes stay inside project root."""
    resolved_path = Path(filepath).expanduser().resolve()
    try:
        resolved_path.relative_to(PROJECT_ROOT)
    except ValueError as exc:
        raise ValueError("Path is outside the project root and is not allowed.") from exc
    return resolved_path


def _hash_text(content: str) -> str:
    return hashlib.sha256(content.encode("utf-8")).hexdigest()


def _apply_unified_diff(original_content: str, diff_text: str) -> str:
    """Apply a basic unified diff to original content and return updated content."""
    original_lines = original_content.splitlines(keepends=True)
    diff_lines = diff_text.splitlines(keepends=True)

    if not any(line.startswith("@@") for line in diff_lines):
        # No hunks found; treat payload as full replacement content.
        return diff_text

    result: list[str] = []
    src_index = 0
    i = 0

    while i < len(diff_lines):
        line = diff_lines[i]

        if line.startswith(("---", "+++", "diff ", "index ")):
            i += 1
            continue

        if not line.startswith("@@"):
            i += 1
            continue

        header_parts = line.split(" ")
        if len(header_parts) < 3:
            raise ValueError(f"Invalid hunk header: {line.strip()}")

        old_range = header_parts[1]  # e.g. -12,3
        old_start = int(old_range[1:].split(",")[0])
        target_index = max(old_start - 1, 0)

        result.extend(original_lines[src_index:target_index])
        src_index = target_index
        i += 1

        while i < len(diff_lines) and not diff_lines[i].startswith("@@"):
            hunk_line = diff_lines[i]
            if not hunk_line:
                i += 1
                continue

            prefix = hunk_line[0]
            content = hunk_line[1:]

            if prefix == " ":
                if src_index >= len(original_lines) or original_lines[src_index] != content:
                    raise ValueError("Unified diff context does not match file content.")
                result.append(content)
                src_index += 1
            elif prefix == "-":
                if src_index >= len(original_lines) or original_lines[src_index] != content:
                    raise ValueError("Unified diff removal does not match file content.")
                src_index += 1
            elif prefix == "+":
                result.append(content)
            elif prefix == "\\":
                # `\ No newline at end of file` marker.
                pass
            else:
                raise ValueError(f"Unsupported diff line prefix: {prefix}")
            i += 1

    result.extend(original_lines[src_index:])
    return "".join(result)


def _changed_lines(before: str, after: str) -> dict[str, Any]:
    before_lines = before.splitlines()
    after_lines = after.splitlines()
    max_len = max(len(before_lines), len(after_lines))
    line_numbers = [
        idx + 1
        for idx in range(max_len)
        if (before_lines[idx] if idx < len(before_lines) else None)
        != (after_lines[idx] if idx < len(after_lines) else None)
    ]
    return {"count": len(line_numbers), "line_numbers": line_numbers}


async def diagnose_and_repair(context: Optional[str] = None, **kwargs) -> dict[str, Any]:
    """
    Takes a snapshot of the screen and terminal, analyzes the error,
    and returns a diagnosis with a proposed fix.
    """
    logger.info("Healing Tool: Initiating Grounded Diagnosis...")

    # 1. Capture Visual Context
    screenshot_result = await take_screenshot()
    if "error" in screenshot_result:
        return {"error": f"Failed to capture visual context: {screenshot_result['error']}"}

    # 2. Capture Terminal Context (Last 50 lines of common log files or current dir)
    terminal_context = ""
    try:
        # Attempt to get recent git/build output
        result = subprocess.run(
            ["tail", "-n", "50", ".aether/logs/session.log"],
            capture_output=True,
            text=True,
            timeout=2,
        )
        if result.returncode == 0:
            terminal_context = result.stdout
        else:
            # Fallback: Just return current directory status
            result = subprocess.run(["ls", "-la"], capture_output=True, text=True, timeout=2)
            terminal_context = f"No log file found. Current Dir:\n{result.stdout}"
    except Exception:
        terminal_context = "Could not retrieve terminal context."

    # 3. Return payload for Gemini to process
    return {
        "status": "analysis_ready",
        "visual_data": screenshot_result["data"],
        "terminal_output": terminal_context,
        "hint": ("Analyze the screenshot for red text or crash logs. Cross-reference with terminal output."),
        "message": "Grounded context gathered. Ready for repair proposal.",
    }


async def apply_repair(filepath: str, diff: str, **kwargs) -> dict[str, Any]:
    """
    Applies a specific code fix (diff) to a file.
    Always creates a backup before modification.
    """
    try:
        safe_path = _resolve_project_path(filepath)
    except ValueError as e:
        return {"error": str(e)}

    if not os.path.exists(safe_path):
        return {"error": f"File {filepath} not found."}

    backup_path = safe_path.with_suffix(f"{safe_path.suffix}.bak")
    try:
        # Create backup
        with open(safe_path, "r", encoding="utf-8") as f:
            original_content = f.read()

        with open(backup_path, "w", encoding="utf-8") as f:
            f.write(original_content)

        updated_content = _apply_unified_diff(original_content, diff)

        with open(safe_path, "w", encoding="utf-8") as f:
            f.write(updated_content)

        with open(safe_path, "r", encoding="utf-8") as f:
            persisted_content = f.read()

        if persisted_content != updated_content:
            raise RuntimeError("Validation failed: persisted content mismatch.")

        before_hash = _hash_text(original_content)
        after_hash = _hash_text(persisted_content)
        changed_lines = _changed_lines(original_content, persisted_content)

        if before_hash == after_hash:
            status = "no_changes"
            message = f"No changes applied to {safe_path}."
        else:
            status = "success"
            message = f"Repair applied to {safe_path}. Backup created at {backup_path}."

        return {
            "status": status,
            "backup": str(backup_path),
            "changed_lines": changed_lines,
            "hash": {"before": before_hash, "after": after_hash},
            "message": message,
        }
    except Exception as e:
        try:
            if backup_path.exists():
                with open(backup_path, "r", encoding="utf-8") as f:
                    backup_content = f.read()
                with open(safe_path, "w", encoding="utf-8") as f:
                    f.write(backup_content)
        except Exception as rollback_error:
            return {
                "error": f"Repair failed: {str(e)}",
                "rollback_error": str(rollback_error),
            }
        return {"error": f"Repair failed: {str(e)}", "rollback": "applied"}


def get_tools() -> list[dict]:
    """
    Module-level tool registration.
    """
    return [
        {
            "name": "diagnose_and_repair",
            "description": (
                "Call this when a terminal error occurs or when the user says "
                "'it's broken' or 'fix this'. It captures screen and terminal "
                "state to provide full context for a diagnosis."
            ),
            "parameters": {
                "type": "object",
                "properties": {
                    "context": {
                        "type": "string",
                        "description": "Optional user context about what happened.",
                    }
                },
            },
            "handler": diagnose_and_repair,
        },
        {
            "name": "apply_repair",
            "description": (
                "Applies a code fix to a specific file. Use after 'diagnose_and_repair' identifies the fix."
            ),
            "parameters": {
                "type": "object",
                "properties": {
                    "filepath": {
                        "type": "string",
                        "description": "The absolute path to the file to fix.",
                    },
                    "diff": {
                        "type": "string",
                        "description": "The new content or diff to apply.",
                    },
                },
                "required": ["filepath", "diff"],
            },
            "handler": apply_repair,
        },
    ]
