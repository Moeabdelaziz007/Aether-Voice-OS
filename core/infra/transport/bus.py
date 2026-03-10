"""
Aether Voice OS — Global State Bus.

Provides a distributed messaging and state storage layer using Redis.
Enables real-time synchronization between multiple Aether Gateway nodes.
"""

from __future__ import annotations

import asyncio
import logging
from typing import Any, Callable, Dict, Optional, Set

try:
    import redis.asyncio as redis

    REDIS_AVAILABLE = True
except ImportError:
    REDIS_AVAILABLE = False

try:
    import msgpack

    MSGPACK_AVAILABLE = True
except ImportError:
    MSGPACK_AVAILABLE = False

logger = logging.getLogger(__name__)


class GlobalBus:
    """
    Distributed State Bus and PubSub manager using Redis.
    """

    def __init__(
        self,
        host: str = "localhost",
        port: int = 6379,
        db: int = 0,
        password: Optional[str] = None,
        prefix: str = "aether:",
    ) -> None:
        self._host = host
        self._port = port
        self._db = db
        self._password = password
        self._prefix = prefix
        self._client: Optional[redis.Redis] = None
        self._pubsub: Optional[redis.PubSub] = None
        self._subscriptions: Dict[str, Set[Callable]] = {}
        self._running = False
        self._listen_task: Optional[asyncio.Task] = None

    @property
    def is_connected(self) -> bool:
        return self._client is not None

    async def connect(self) -> bool:
        """Establish connection to Redis."""
        if not REDIS_AVAILABLE:
            logger.error("A2A [BUS] Redis package not installed.")
            return False

        try:
            self._client = redis.Redis(
                host=self._host,
                port=self._port,
                db=self._db,
                password=self._password,
                decode_responses=False,
            )
            # Ping to verify with safety timeout
            await asyncio.wait_for(self._client.ping(), timeout=5.0)
            self._running = True
            logger.info(
                "✦ A2A [BUS] Connected to Global State Bus (Redis: %s:%d)",
                self._host,
                self._port,
            )
            return True
        except Exception as e:
            logger.error("A2A [BUS] Connection failed: %s", e)
            self._client = None
            return False

    async def disconnect(self) -> None:
        """Close Redis connection."""
        self._running = False
        if self._listen_task:
            self._listen_task.cancel()
            try:
                await self._listen_task
            except asyncio.CancelledError:
                pass

        if self._client:
            await self._client.close()
            self._client = None
            logger.info("A2A [BUS] Disconnected.")

    async def publish(self, channel: str, message: Any) -> int:
        """Publish a message to a specific channel."""
        if not self._client:
            return 0

        full_channel = f"{self._prefix}pubsub:{channel}"

        # Use msgpack for binary serialization to reduce CPU overhead
        if MSGPACK_AVAILABLE:
            payload = msgpack.packb(message, use_bin_type=True)
        else:
            import json

            payload = json.dumps(message).encode("utf-8")

        try:
            receivers = await self._client.publish(full_channel, payload)
            return receivers
        except Exception as e:
            logger.error("A2A [BUS] Publish error on %s: %s", full_channel, e)
            return 0

    async def subscribe(self, channel: str, callback: Callable[[Any], Any]) -> None:
        """Subscribe to a channel and register a callback."""
        if not self._client:
            return

        full_channel = f"{self._prefix}pubsub:{channel}"

        if full_channel not in self._subscriptions:
            self._subscriptions[full_channel] = set()
            if self._pubsub is None:
                self._pubsub = self._client.pubsub()
            await self._pubsub.subscribe(full_channel)

            # Start listener if not running
            if not self._listen_task or self._listen_task.done():
                self._listen_task = asyncio.create_task(self._listen_loop())

        self._subscriptions[full_channel].add(callback)
        logger.debug("A2A [BUS] Subscribed to %s", full_channel)

    async def _listen_loop(self) -> None:
        """Background loop to route PubSub messages to callbacks."""
        if not self._pubsub:
            return

        while self._running:
            try:
                message = await self._pubsub.get_message(ignore_subscribe_messages=True, timeout=1.0)
                if message and message["type"] == b"message":
                    channel = message["channel"]
                    if isinstance(channel, bytes):
                        channel = channel.decode("utf-8")

                    raw_data = message["data"]
                    if MSGPACK_AVAILABLE:
                        try:
                            data = msgpack.unpackb(raw_data, raw=False)
                        except msgpack.ExtraData:
                            import json

                            data = json.loads(raw_data.decode("utf-8"))
                        except Exception:
                            # Fallback if somehow it's json or plain text
                            try:
                                import json

                                data = json.loads(raw_data.decode("utf-8"))
                            except Exception:
                                data = raw_data
                    else:
                        import json

                        data = json.loads(raw_data.decode("utf-8"))

                    callbacks = self._subscriptions.get(channel, set())
                    for cb in callbacks:
                        try:
                            if asyncio.iscoroutinefunction(cb):
                                await cb(data)
                            else:
                                cb(data)
                        except Exception as e:
                            logger.error("A2A [BUS] Callback error on %s: %s", channel, e)
            except asyncio.CancelledError:
                break
            except Exception as e:
                logger.error("A2A [BUS] Listen loop error: %s", e)
                await asyncio.sleep(1.0)

    async def set_state(self, key: str, value: Any, ex: Optional[int] = None) -> bool:
        """Store state in global storage."""
        if not self._client:
            return False

        full_key = f"{self._prefix}state:{key}"
        try:
            if MSGPACK_AVAILABLE:
                payload = msgpack.packb(value, use_bin_type=True)
            else:
                import json

                payload = json.dumps(value).encode("utf-8")

            await self._client.set(full_key, payload, ex=ex)
            return True
        except Exception as e:
            logger.error("A2A [BUS] State set error for %s: %s", full_key, e)
            return False

    async def get_state(self, key: str) -> Optional[Any]:
        """Retrieve state from global storage."""
        if not self._client:
            return None

        full_key = f"{self._prefix}state:{key}"
        try:
            data = await self._client.get(full_key)
            if not data:
                return None

            if MSGPACK_AVAILABLE:
                try:
                    return msgpack.unpackb(data, raw=False)
                except Exception:
                    pass

            # Fallback for older JSON entries
            import json

            return json.loads(data.decode("utf-8"))
        except Exception as e:
            logger.error("A2A [BUS] State get error for %s: %s", full_key, e)
            return None

    async def delete_state(self, key: str) -> bool:
        """Delete state from global storage."""
        if not self._client:
            return False

        full_key = f"{self._prefix}state:{key}"
        try:
            await self._client.delete(full_key)
            return True
        except Exception as e:
            logger.error("A2A [BUS] State delete error for %s: %s", full_key, e)
            return False
