import asyncio
import logging
from typing import Any, Callable, Optional

from core.audio.capture import AudioCapture
from core.audio.paralinguistics import ParalinguisticAnalyzer
from core.audio.playback import AudioPlayback
from core.audio.processing import AdaptiveVAD
from core.infra.config import AetherConfig

logger = logging.getLogger(__name__)


class AudioManager:
    """Manages audio lifecycle: capture, playback, and analysis."""

    def __init__(
        self,
        config: AetherConfig,
        gateway: Any,
        on_affective_data: Callable,
        event_bus: Optional[Any] = None,
    ):
        self._config = config
        self._gateway = gateway
        self._event_bus = event_bus
        self._on_affective_data_callback = on_affective_data

        # Components (initialized in start, not __init__)
        self._capture: Optional[AudioCapture] = None
        self._playback: Optional[AudioPlayback] = None
        self._paralinguistics: Optional[ParalinguisticAnalyzer] = None
        self._vad: Optional[AdaptiveVAD] = None

        # Task references
        self._capture_task: Optional[asyncio.Task] = None
        self._playback_task: Optional[asyncio.Task] = None

        self._running = False

    async def start(self) -> None:
        """Initialize and start audio components."""
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

        await self._capture.start()
        await self._playback.start()
        self._running = True

    async def restart(self) -> None:
        """Restart audio pipeline after failure."""
        logger.warning("AudioManager: Restarting pipeline...")

        # 1. Stop existing
        await self.stop()

        # 2. Clear queues
        self._clear_queues()

        # 3. Recreate components
        self._capture = None
        self._playback = None
        self._paralinguistics = None
        self._vad = None

        # 4. Start fresh
        await self.start()

        logger.info("AudioManager: Restart complete")

    async def stop(self) -> None:
        """Stop audio components gracefully."""
        self._running = False

        if self._capture:
            await self._capture.stop()

        if self._playback:
            await self._playback.stop()

        # Cancel tasks if running
        if self._capture_task and not self._capture_task.done():
            self._capture_task.cancel()
            try:
                await self._capture_task
            except asyncio.CancelledError:
                pass

        if self._playback_task and not self._playback_task.done():
            self._playback_task.cancel()
            try:
                await self._playback_task
            except asyncio.CancelledError:
                pass

    def _clear_queues(self) -> None:
        """Clear all audio queues."""
        if hasattr(self._gateway, "audio_in_queue"):
            # Clear mic queue
            while not self._gateway.audio_in_queue.empty():
                try:
                    self._gateway.audio_in_queue.get_nowait()
                except asyncio.QueueEmpty:
                    break

        if hasattr(self._gateway, "audio_out_queue"):
            # Clear speaker queue
            while not self._gateway.audio_out_queue.empty():
                try:
                    self._gateway.audio_out_queue.get_nowait()
                except asyncio.QueueEmpty:
                    break

    def run_tasks(self, tg: asyncio.TaskGroup):
        """Add audio tasks to TaskGroup."""
        if self._capture:
            self._capture_task = tg.create_task(
                self._capture.run(), name="audio-capture"
            )
        if self._playback:
            self._playback_task = tg.create_task(
                self._playback.run(), name="audio-playback"
            )

    def interrupt(self):
        if self._playback:
            self._playback.interrupt()

    def flash_interrupt(self):
        """High-priority alias for barge-in events."""
        logger.info("⚡ FLASH INTERRUPT: Clearing audio pipelines.")
        self.interrupt()

    def reset_aec(self) -> None:
        """Reset AEC filter."""
        if self._capture and hasattr(self._capture, "_dynamic_aec"):
            self._capture._dynamic_aec.reset()
            logger.info("AEC filter reset via AudioManager")

    def _on_affective_data_bridge(self, features: Any) -> None:
        """Internal bridge to trigger the shared callback and the EventBus."""
        # 1. Trigger the legacy engine callback (for Firestore/Gateway logging)
        if self._on_affective_data_callback:
            self._on_affective_data_callback(features)

        # 2. Publish to the Neural Event Bus for Tier 2/3 reaction
        if self._event_bus:
            import time

            from core.infra.event_bus import AcousticTraitEvent

            traits = {
                "valence": features.engagement_score,
                "arousal": features.rms_variance / 500.0,
                "energy": features.rms_variance / 1000.0,
            }

            for name, val in traits.items():
                event = AcousticTraitEvent(
                    timestamp=time.time(),
                    source="AudioManager",
                    latency_budget=100,  # Sub-100ms requirement
                    trait_name=name,
                    trait_value=val,
                )
                asyncio.create_task(self._event_bus.publish(event))
