"""
Aether Voice OS — Health Check System

Monitors system health and triggers recovery actions.
"""

from __future__ import annotations

import asyncio
import logging
import time
from dataclasses import dataclass
from enum import Enum
from typing import Callable, Optional

logger = logging.getLogger("AetherOS.HealthCheck")


class HealthStatus(Enum):
    HEALTHY = "healthy"
    DEGRADED = "degraded"
    UNHEALTHY = "unhealthy"
    UNKNOWN = "unknown"


@dataclass
class ComponentHealth:
    name: str
    status: HealthStatus
    last_check: float
    latency_ms: float = 0.0
    error_message: str = ""
    consecutive_failures: int = 0


class HealthChecker:
    """
    Periodic health monitoring for system components.
    
    Monitors:
    - Gemini API connectivity
    - Audio pipeline latency
    - AEC convergence
    - Memory/queue pressure
    """

    def __init__(
        self,
        check_interval: float = 30.0,
        failure_threshold: int = 3,
        on_unhealthy: Optional[Callable[[str], None]] = None,
    ):
        self._interval = check_interval
        self._threshold = failure_threshold
        self._on_unhealthy = on_unhealthy
        
        self._components: dict[str, ComponentHealth] = {}
        self._running = False
        self._task: Optional[asyncio.Task] = None

    def register_component(
        self,
        name: str,
        check_fn: Callable[[], Coroutine[None, None, tuple[bool, float, str]]],
    ) -> None:
        """Register a component for health monitoring."""
        self._components[name] = ComponentHealth(
            name=name,
            status=HealthStatus.UNKNOWN,
            last_check=0.0,
            check_fn=check_fn,
        )

    async def start(self) -> None:
        """Start health monitoring."""
        if self._running:
            return
        self._running = True
        self._task = asyncio.create_task(self._monitor_loop())
        logger.info("🏥 Health checker started")

    async def stop(self) -> None:
        """Stop health monitoring."""
        self._running = False
        if self._task:
            self._task.cancel()
            try:
                await self._task
            except asyncio.CancelledError:
                pass
        logger.info("🏥 Health checker stopped")

    async def _monitor_loop(self) -> None:
        """Main monitoring loop."""
        while self._running:
            for name, component in self._components.items():
                try:
                    is_healthy, latency, msg = await component.check_fn()
                    component.last_check = time.time()
                    component.latency_ms = latency
                    
                    if is_healthy:
                        component.status = HealthStatus.HEALTHY
                        component.consecutive_failures = 0
                        component.error_message = ""
                    else:
                        component.consecutive_failures += 1
                        component.error_message = msg
                        
                        if component.consecutive_failures >= self._threshold:
                            component.status = HealthStatus.UNHEALTHY
                            logger.error(
                                f"❌ {name} unhealthy: {msg} "
                                f"({component.consecutive_failures} failures)"
                            )
                            if self._on_unhealthy:
                                self._on_unhealthy(name)
                        else:
                            component.status = HealthStatus.DEGRADED
                            logger.warning(
                                f"⚠️ {name} degraded: {msg}"
                            )
                            
                except Exception as e:
                    component.status = HealthStatus.UNKNOWN
                    component.error_message = str(e)
                    logger.error(f"❌ Health check error for {name}: {e}")
            
            await asyncio.sleep(self._interval)

    def get_health(self, name: str) -> Optional[ComponentHealth]:
        """Get health status for a component."""
        return self._components.get(name)

    def get_all_health(self) -> dict[str, ComponentHealth]:
        """Get all component health statuses."""
        return dict(self._components)

    def is_healthy(self) -> bool:
        """Check if all components are healthy."""
        return all(
            c.status == HealthStatus.HEALTHY
            for c in self._components.values()
        )


# Pre-built health check functions
async def check_gemini_api() -> tuple[bool, float, str]:
    """Check Gemini API connectivity."""
    import os
    import httpx
    
    api_key = os.getenv("GOOGLE_API_KEY")
    if not api_key:
        return False, 0.0, "API key not configured"
    
    start = time.perf_counter()
    try:
        async with httpx.AsyncClient(timeout=10.0) as client:
            response = await client.get(
                "https://generativelanguage.googleapis.com/v1beta/models",
                headers={"x-goog-api-key": api_key},
            )
        latency = (time.perf_counter() - start) * 1000
        
        if response.status_code == 200:
            return True, latency, "OK"
        return False, latency, f"HTTP {response.status_code}"
    except Exception as e:
        latency = (time.perf_counter() - start) * 1000
        return False, latency, str(e)


async def check_audio_pipeline(
    latency_threshold_ms: float = 20.0,
) -> tuple[bool, float, str]:
    """Check audio pipeline health via telemetry."""
    from core.audio.state import audio_state
    
    latency = getattr(audio_state, "last_latency_ms", 0.0)
    
    if latency > latency_threshold_ms:
        return False, latency, f"High latency: {latency:.1f}ms"
    return True, latency, "OK"


async def check_aec_convergence() -> tuple[bool, float, str]:
    """Check AEC convergence status."""
    from core.audio.state import audio_state
    
    converged = getattr(audio_state, "aec_converged", False)
    erle = getattr(audio_state, "aec_erle_db", 0.0)
    
    if converged:
        return True, 0.0, f"Converged (ERLE: {erle:.1f}dB)"
    return True, 0.0, "Not yet converged"


from typing import Coroutine
