import asyncio
import logging
from typing import Any, Callable
try:
    import ujson as json
except ImportError:
    import json

from core.audio.capture import AudioCapture
from core.audio.paralinguistics import ParalinguisticAnalyzer
from core.audio.playback import AudioPlayback
from core.audio.processing import AdaptiveVAD
from core.infra.config import AetherConfig

logger = logging.getLogger(__name__)


class AudioManager:
    """Manages audio lifecycle: capture, playback, and analysis."""

    def __init__(self, config: AetherConfig, gateway: Any, on_affective_data: Callable, event_bus: Optional[Any] = None):
        self._config = config
        self._gateway = gateway
        self._event_bus = event_bus
        self._on_affective_data_callback = on_affective_data

        self._paralinguistics = ParalinguisticAnalyzer(
            sample_rate=self._config.audio.send_sample_rate
        )

        self._vad = AdaptiveVAD(
            window_size_sec=getattr(self._config.audio, "vad_window_sec", 5.0),
            sample_rate=self._config.audio.send_sample_rate,
        )

        self._capture = AudioCapture(
            self._config.audio,
            self._gateway.audio_in_queue,
            vad_engine=self._vad,
            paralinguistic_analyzer=self._paralinguistics,
            on_affective_data=self._on_affective_data_bridge,
        )
        self._capture._on_audio_telemetry = self._gateway.broadcast

        self._playback = AudioPlayback(
            self._config.audio,
            self._gateway.audio_out_queue,
            on_audio_tx=self._gateway.broadcast_binary,
        )

    async def start(self):
        await self._capture.start()
        await self._playback.start()

    async def stop(self):
        await self._capture.stop()
        await self._playback.stop()

    def run_tasks(self, tg: asyncio.TaskGroup):
        tg.create_task(self._capture.run(), name="audio-capture")
        tg.create_task(self._playback.run(), name="audio-playback")

    def interrupt(self):
        self._playback.interrupt()

    def flash_interrupt(self):
        """High-priority alias for barge-in events."""
        logger.info("⚡ FLASH INTERRUPT: Clearing audio pipelines.")
        logger.info("⚡ FLASH INTERRUPT: Clearing audio pipelines.")
        self.interrupt()

    def _on_affective_data_bridge(self, features: Any) -> None:
        """Internal bridge to trigger the shared callback and the EventBus."""
        # 1. Trigger the legacy engine callback (for Firestore/Gateway logging)
        if self._on_affective_data_callback:
            self._on_affective_data_callback(features)

        # 2. Publish to the Neural Event Bus for Tier 2/3 reaction
        if self._event_bus:
            from core.infra.event_bus import AcousticTraitEvent
            import time

            traits = {
                "valence": features.engagement_score,
                "arousal": features.rms_variance / 500.0,
                "energy": features.rms_variance / 1000.0,
            }

            for name, val in traits.items():
                event = AcousticTraitEvent(
                    timestamp=time.time(),
                    source="AudioManager",
                    latency_budget=100, # Sub-100ms requirement
                    trait_name=name,
                    trait_value=val
                )
                asyncio.create_task(self._event_bus.publish(event))
