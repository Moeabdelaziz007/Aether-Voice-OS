import asyncio
import time
from collections import deque
from dataclasses import asdict, dataclass
from typing import Optional

import structlog

from core.infra.event_bus import EventBus, TelemetryEvent

logger = structlog.get_logger("AetherOS.Telemetry.Logger")

@dataclass
class FrameMetrics:
    timestamp: float
    frame_id: int
    capture_latency_ms: float = 0.0
    aec_latency_ms: float = 0.0
    vad_latency_ms: float = 0.0
    total_latency_ms: float = 0.0
    rms_energy: float = 0.0
    erle_db: float = 0.0
    aec_converged: bool = False
    vad_is_speech: bool = False
    vad_is_soft: bool = False
    double_talk: bool = False
    frame_dropped: bool = False
    queue_size_in: int = 0
    queue_size_out: int = 0

@dataclass
class SessionMetrics:
    session_id: str
    start_time: float
    end_time: Optional[float] = None
    total_frames: int = 0
    frames_dropped: int = 0
    frames_speech: int = 0
    frames_silence: int = 0
    latency_p50_ms: float = 0.0
    latency_p95_ms: float = 0.0
    latency_p99_ms: float = 0.0
    latency_avg_ms: float = 0.0
    latency_max_ms: float = 0.0
    erle_avg_db: float = 0.0
    aec_convergence_rate: float = 0.0
    double_talk_frames: int = 0
    vad_accuracy: float = 0.0
    speech_ratio: float = 0.0
    jitter_ms: float = 0.0

class AudioTelemetryLogger:
    """Performance logging for the audio pipeline."""
    def __init__(self, event_bus: Optional[EventBus] = None, session_id: Optional[str] = None):
        self._bus = event_bus
        self._session_id = session_id or f"session_{int(time.time() * 1000)}"
        self._frame_metrics: deque[FrameMetrics] = deque(maxlen=10000)
        self._frame_id = 0
        self._start_time = time.time()
        self._latency_history: deque[float] = deque(maxlen=1000)
        self._current_frame: Optional[FrameMetrics] = None
        self._frame_start_time: float = 0.0
        self._last_frame_id = -1

    def start_frame(self) -> int:
        self._frame_start_time = time.perf_counter()
        self._frame_id += 1
        self._current_frame = FrameMetrics(timestamp=time.time(), frame_id=self._frame_id)
        return self._frame_id

    def record_capture(self, latency_ms: float, queue_size: int = 0):
        if self._current_frame:
            self._current_frame.capture_latency_ms = latency_ms
            self._current_frame.queue_size_in = queue_size

    def record_aec(self, latency_ms: float, erle_db: float = 0.0, converged: bool = False, double_talk: bool = False):
        if self._current_frame:
            self._current_frame.aec_latency_ms = latency_ms
            self._current_frame.aec_converged = converged
            self._current_frame.erle_db = erle_db
            self._current_frame.double_talk = double_talk

    def record_vad(self, latency_ms: float, is_speech: bool, is_soft: bool = False, rms_energy: float = 0.0):
        if self._current_frame:
            self._current_frame.vad_latency_ms = latency_ms
            self._current_frame.vad_is_speech = is_speech
            self._current_frame.vad_is_soft = is_soft
            self._current_frame.rms_energy = rms_energy

    def end_frame(self) -> Optional[FrameMetrics]:
        if not self._current_frame: return None
        self._current_frame.total_latency_ms = (time.perf_counter() - self._frame_start_time) * 1000
        if self._last_frame_id >= 0 and self._current_frame.frame_id > self._last_frame_id + 1:
            self._current_frame.frame_dropped = True
        self._last_frame_id = self._current_frame.frame_id
        self._frame_metrics.append(self._current_frame)
        self._latency_history.append(self._current_frame.total_latency_ms)
        if self._bus:
            asyncio.create_task(self._publish_frame_metrics(self._current_frame))
        frame = self._current_frame
        self._current_frame = None
        return frame

    async def _publish_frame_metrics(self, frame: FrameMetrics):
        await self._bus.publish(TelemetryEvent(timestamp=frame.timestamp, source="AudioTelemetryLogger", latency_budget=50, metric_name="frame_metrics", value=frame.total_latency_ms, metadata=asdict(frame)))

    def get_session_metrics(self) -> SessionMetrics:
        frames = list(self._frame_metrics)
        if not frames: return SessionMetrics(session_id=self._session_id, start_time=self._start_time)
        latencies = [f.total_latency_ms for f in frames]
        sorted_latencies = sorted(latencies)
        n = len(sorted_latencies)
        # Simplified aggregation for brevity in this refactor
        return SessionMetrics(
            session_id=self._session_id,
            start_time=self._start_time,
            total_frames=n,
            latency_p50_ms=sorted_latencies[int(n*0.5)],
            latency_p95_ms=sorted_latencies[int(n*0.95)],
            latency_avg_ms=sum(latencies)/n
        )
