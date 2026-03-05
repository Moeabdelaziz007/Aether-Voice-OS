import collections
import logging
import time
from typing import Any, Dict, List, Optional

from pydantic import BaseModel

logger = logging.getLogger("AetherOS.Memory")

# ==========================================
# 🌌 Memory Block Schema
# ==========================================


class MemoryBlock(BaseModel)):
    """
    A single unit of short-term recollection.
    """

    id: str
    timestamp: float
    role: str  # 'user', 'assistant', 'system', 'tool'
    content: str
    metadata: Dict[str, Any] = {}


# ==========================================
# 🌌 Short-Term Memory Manager
# High-speed sliding window of recent thoughts.
# ==========================================


class ShortTermMemory:
    """
    The 'Working Memory' of AetherOS.
    Maintains a rolling window of recent interactions
    to keep context relevant without bloating the LLM prompt.
    """

    def __init__(self, max_tokens: int = 4000, max_messages: int = 50):
        self._messages: collections.deque[MemoryBlock] = collections.deque(
            maxlen=max_messages
        )
        self.max_tokens = max_tokens

    def add_message(
        self, role: str, content: str, metadata: Optional[Dict[str, Any]] = None
    ):
        """Append a new cognitive block."""
        block = MemoryBlock(
            id=f"msg_{int(time.time() * 1000)}",
            timestamp=time.time(),
            role=role,
            content=content,
            metadata=metadata or {},
        )
        self._messages.append(block)
        logger.debug(f"[Memory] Added {role} block: {content[:30]}...")

    def get_context_window(self, limit: Optional[int] = None) -> List[Dict[str, str]]:
        """
        Retrieve formatted messages for LLM consumption.
        Applies a basic sliding window based on message count.
        """
        messages = list(self._messages)
        if limit and limit < len(messages):
            messages = messages[-limit:]

        return [{"role": m.role, "content": m.content} for m in messages]

    def clear(self):
        """Wipe working memory."""
        self._messages.clear()
        logger.info("[Memory] Working memory purged.")

    def get_last_message(self) -> Optional[MemoryBlock]:
        return self._messages[-1] if self._messages else None

    @property
    def message_count(self) -> int:
        return len(self._messages)
