import os
import json
import time
from typing import Any, Dict, List, Optional

class WorkingBuffer:
    """
    Temporary buffer for raw exchanges in the 'Danger Zone' (>60% context).
    Ensures safe recovery during context compaction.
    """

    def __init__(self, workspace_path: str):
        self.buffer_file = os.path.join(workspace_path, "WORKING-BUFFER.md")
        self.threshold = 0.6
        self.is_active = False

    def check_threshold(self, context_usage: float):
        """Activates buffer if context exceeds threshold."""
        if context_usage > self.threshold and not self.is_active:
            self.is_active = True
            self._init_buffer()
        elif context_usage <= self.threshold:
            self.is_active = False

    def _init_buffer(self):
        with open(self.buffer_file, "w") as f:
            f.write(f"# Working Buffer (Active: {time.ctime()})\n")

    async def append_exchange(self, user_msg: str, agent_summary: str):
        """Appends a raw exchange to the buffer."""
        if not self.is_active:
            return

        entry = f"\n---\n**Human**: {user_msg}\n**Aether**: {agent_summary}\n"
        await asyncio.to_thread(self._sync_append, entry)

    def _sync_append(self, entry: str):
        with open(self.buffer_file, "a") as f:
            f.write(entry)

    async def read_buffer(self) -> str:
        """Reads the entire buffer for recovery."""
        return await asyncio.to_thread(self._sync_read_buffer)

    def _sync_read_buffer(self) -> str:
        if os.path.exists(self.buffer_file):
            with open(self.buffer_file, "r") as f:
                return f.read()
        return ""

    async def clear(self):
        """Clears the buffer after successful recovery."""
        await asyncio.to_thread(self._sync_clear)

    def _sync_clear(self):
        if os.path.exists(self.buffer_file):
            os.remove(self.buffer_file)
        self.is_active = False
