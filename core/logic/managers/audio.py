import logging
import asyncio
from typing import Optional, Any, Callable
from core.audio.capture import AudioCapture
from core.audio.playback import AudioPlayback
from core.audio.processing import AdaptiveVAD
from core.audio.paralinguistics import ParalinguisticAnalyzer, ParalinguisticFeatures
from core.infra.config import AetherConfig

logger = logging.getLogger(__name__)

class AudioManager:
    """Manages audio lifecycle: capture, playback, and analysis."""
    
    def __init__(self, config: AetherConfig, gateway: Any, on_affective_data: Callable):
        self._config = config
        self._gateway = gateway
        
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
            on_affective_data=on_affective_data,
        )
        
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
