from __future__ import annotations

import time
import uuid
from dataclasses import dataclass, field

from websockets.asyncio.server import ServerConnection


@dataclass
class ClientSession:
    client_id: str
    ws: ServerConnection
    capabilities: list[str]
    session_id: str = field(default_factory=lambda: str(uuid.uuid4()))
    last_pong: float = field(default_factory=time.monotonic)
    connected_at: float = field(default_factory=time.monotonic)
