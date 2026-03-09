import os
from datetime import datetime
from typing import List


class WALProtocol:
    """
    Write-Ahead Logging for AetherOS.
    Ensures critical session details are persisted to SESSION-STATE.md
    BEFORE the model responds, preventing context amnesia.
    """

    def __init__(self, workspace_path: str):
        self.state_file = os.path.join(workspace_path, "SESSION-STATE.md")
        self.triggers = ["correction", "preference", "decision", "value", "identity"]

    async def on_interaction(self, input_text: str, detected_traits: List[str]):
        """Analyze interaction and write to WAL if critical details are detected."""
        if any(trigger in detected_traits for trigger in self.triggers):
            await self._write_to_state(input_text, detected_traits)

    async def _write_to_state(self, detail: str, traits: List[str]):
        """Persists the detail to the markdown state file."""
        timestamp = datetime.now().isoformat()
        entry = f"\n### [WAL] {timestamp}\n- **Traits**: {', '.join(traits)}\n- **Detail**: {detail}\n"

        await asyncio.to_thread(self._sync_write, entry)

    def _sync_write(self, entry: str):
        with open(self.state_file, "a") as f:
            f.write(entry)

    async def get_last_critical_details(self) -> str:
        """Reads the last few entries from the state file."""
        return await asyncio.to_thread(self._sync_read)

    def _sync_read(self) -> str:
        try:
            with open(self.state_file, "r") as f:
                content = f.read()
                return content[-500:]
        except FileNotFoundError:
            return ""
