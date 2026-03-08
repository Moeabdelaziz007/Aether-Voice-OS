import asyncio
import json
import logging
import time
from collections import deque
from dataclasses import asdict, dataclass
from datetime import datetime
from pathlib import Path
from typing import Any, Dict, Optional

import numpy as np
import structlog

from core.infra.event_bus import EventBus, TelemetryEvent

logger = structlog.get_logger("AetherOS.Telemetry")

def log_audio_metrics(
    rms: float,
    zcr: float,
    aec_erle: float,
    aec_converged: bool,
    queue_size: int,
):
    """Structured logging for audio metrics"""
    logger.info(
        "audio_metrics",
        rms=rms,
        zcr=zcr,
        aec_erle=aec_erle,
        aec_converged=aec_converged,
        queue_size=queue_size,
        latency_budget_ms=32,  # target
    )

# ==========================================
# 🌌 Audio Telemetry Engine
# Calculating paralinguistic features at 15Hz
# to power the Aether HUD visualization.
# ==========================================


class AudioTelemetry:
    """
    Analyzes PCM audio segments and broadcasts
    mathematical paralinguistics into the Tier 3 Telemetry bus.
    """

    def __init__(self, event_bus: EventBus, interval_sec: float = 0.066):  # ~15Hz
        self._bus = event_bus
        self._interval = interval_sec
        self._running = False
        self._loop_task: Optional[asyncio.Task] = None

        # Internal Analysis Accumulator
        self._current_buffer = bytearray()

    def feed_audio(self, pcm_data: bytes):
        """Accumulate audio for the next analysis window."""
        self._current_buffer.extend(pcm_data)

    async def start(self):
        """Start the telemetry broadcast loop."""
        if self._running:
            return
        self._running = True
        self._loop_task = asyncio.create_task(self._analysis_loop())
        logger.info("[Telemetry] Broadcast loop started at 15Hz.")

    async def stop(self):
        """Stop the telemetry broadcast loop."""
        self._running = False
        if self._loop_task:
            self._loop_task.cancel()
        logger.info("[Telemetry] Broadcast loop stopped.")

    async def _analysis_loop(self):
        """Periodic analysis and event emission."""
        while self._running:
            start_time = time.time()

            if self._current_buffer:
                # 1. Convert bytearray to numpy
                audio_np = (
                    np.frombuffer(self._current_buffer, dtype=np.int16).astype(
                        np.float32
                    )
                    / 32768.0
                )
                self._current_buffer = bytearray()  # Clear after read

                # 2. Calculate Paralinguistics
                # A. Volume (RMS)
                volume = np.sqrt(np.mean(audio_np**2)) if len(audio_np) > 0 else 0

                # B. Pitch (Simplified via zero-crossing rate)
                zero_crossings = np.nonzero(np.diff(np.sign(audio_np)))[0]
                pitch_est = (
                    len(zero_crossings) / (len(audio_np) / 16000) / 2
                    if len(audio_np) > 0
                    else 0
                )

                # C. Spectral Centroid (Brightness/Timbre)
                spectrum = np.abs(np.fft.rfft(audio_np))
                freqs = np.fft.rfftfreq(len(audio_np), 1 / 16000)
                centroid = (
                    np.sum(freqs * spectrum) / np.sum(spectrum)
                    if np.sum(spectrum) > 0
                    else 0
                )

                # 3. Publish to Tier 3
                await self._bus.publish(
                    TelemetryEvent(
                        timestamp=time.time(),
                        source="AudioTelemetry",
                        latency_budget=200,  # Telemetry can tolerate more lag
                        metric_name="paralinguistics",
                        value=volume,
                        metadata={
                            "volume": float(volume),
                            "pitch_hz": float(pitch_est),
                            "spectral_centroid": float(centroid),
                        },
                    )
                )

            # Maintain constant frequency
            elapsed = time.time() - start_time
            await asyncio.sleep(max(0, self._interval - elapsed))


# ═══════════════════════════════════════════════════════════
# 🌌 Audio Telemetry Logger — Performance Metrics Collector
# Captures real-time audio pipeline performance for analysis
# ═══════════════════════════════════════════════════════════


@dataclass
class FrameMetrics:
    """Metrics for a single audio frame."""

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
    """Aggregated metrics for an audio session."""

    session_id: str
    start_time: float
    end_time: Optional[float] = None
    total_frames: int = 0
    frames_dropped: int = 0
    frames_speech: int = 0
    frames_silence: int = 0

    # Latency Stats
    latency_p50_ms: float = 0.0
    latency_p95_ms: float = 0.0
    latency_p99_ms: float = 0.0
    latency_avg_ms: float = 0.0
    latency_max_ms: float = 0.0

    # AEC Stats
    erle_avg_db: float = 0.0
    aec_convergence_rate: float = 0.0
    double_talk_frames: int = 0

    # VAD Stats
    vad_accuracy: float = 0.0  # Requires ground truth
    speech_ratio: float = 0.0

    # Jitter
    jitter_ms: float = 0.0


class AudioTelemetryLogger:
    """
    Comprehensive audio pipeline performance logger.

    Captures:
    - End-to-end latency per frame
    - Frame drops and queue pressure
    - AEC performance (ERLE, convergence)
    - VAD accuracy
    - Jitter analysis

    Outputs:
    - Real-time metrics to EventBus
    - Session summary JSON on stop()
    - Optional: Continuous CSV logging
    """

    def __init__(
        self,
        event_bus: Optional[EventBus] = None,
        session_id: Optional[str] = None,
        log_to_file: bool = True,
        log_dir: str = "telemetry_logs",
    ):
        self._bus = event_bus
        self._session_id = session_id or f"session_{int(time.time() * 1000)}"
        self._log_to_file = log_to_file
        self._log_dir = Path(log_dir)

        # Frame storage
        self._frame_metrics: deque[FrameMetrics] = deque(maxlen=10000)
        self._frame_id = 0
        self._start_time = time.time()

        # Latency tracking
        self._latency_history: deque[float] = deque(maxlen=1000)

        # Current frame timing
        self._current_frame: Optional[FrameMetrics] = None
        self._frame_start_time: float = 0.0

        # Drop tracking
        self._last_frame_id = -1

        # Create log directory
        if self._log_to_file:
            self._log_dir.mkdir(parents=True, exist_ok=True)

        logger.info(f"📊 AudioTelemetryLogger initialized: session={self._session_id}")

    # ── Frame Lifecycle ─────────────────────────────────────

    def start_frame(self) -> int:
        """Start timing a new frame. Returns frame_id."""
        self._frame_start_time = time.perf_counter()
        self._frame_id += 1
        self._current_frame = FrameMetrics(
            timestamp=time.time(), frame_id=self._frame_id
        )
        return self._frame_id

    def record_capture(self, latency_ms: float, queue_size: int = 0):
        """Record capture stage metrics."""
        if self._current_frame:
            self._current_frame.capture_latency_ms = latency_ms
            self._current_frame.queue_size_in = queue_size

    def record_aec(
        self,
        latency_ms: float,
        erle_db: float = 0.0,
        converged: bool = False,
        double_talk: bool = False,
    ):
        """Record AEC stage metrics."""
        if self._current_frame:
            self._current_frame.aec_latency_ms = latency_ms
            self._current_frame.aec_converged = converged
            self._current_frame.erle_db = erle_db
            self._current_frame.double_talk = double_talk

    def record_vad(
        self,
        latency_ms: float,
        is_speech: bool,
        is_soft: bool = False,
        rms_energy: float = 0.0,
    ):
        """Record VAD stage metrics."""
        if self._current_frame:
            self._current_frame.vad_latency_ms = latency_ms
            self._current_frame.vad_is_speech = is_speech
            self._current_frame.vad_is_soft = is_soft
            self._current_frame.rms_energy = rms_energy

    def record_output(self, queue_size: int = 0):
        """Record output queue status."""
        if self._current_frame:
            self._current_frame.queue_size_out = queue_size

    def end_frame(self) -> Optional[FrameMetrics]:
        """Finalize frame timing and store metrics."""
        if not self._current_frame:
            return None

        # Calculate total latency
        total_time = time.perf_counter() - self._frame_start_time
        self._current_frame.total_latency_ms = total_time * 1000

        # Check for frame drops (skipped frame IDs)
        if (
            self._last_frame_id >= 0
            and self._current_frame.frame_id > self._last_frame_id + 1
        ):
            self._current_frame.frame_dropped = True
        self._last_frame_id = self._current_frame.frame_id

        # Store metrics
        self._frame_metrics.append(self._current_frame)
        self._latency_history.append(self._current_frame.total_latency_ms)

        # Publish to event bus
        if self._bus:
            asyncio.create_task(self._publish_frame_metrics(self._current_frame))

        frame = self._current_frame
        self._current_frame = None
        return frame

    # ── Metrics Analysis ─────────────────────────────────────

    def get_session_metrics(self) -> SessionMetrics:
        """Calculate aggregated session metrics."""
        frames = list(self._frame_metrics)
        if not frames:
            return SessionMetrics(
                session_id=self._session_id, start_time=self._start_time
            )

        latencies = [f.total_latency_ms for f in frames]
        erle_values = [f.erle_db for f in frames if f.erle_db > 0]

        # Calculate percentiles
        sorted_latencies = sorted(latencies)
        n = len(sorted_latencies)

        metrics = SessionMetrics(
            session_id=self._session_id,
            start_time=self._start_time,
            end_time=time.time(),
            total_frames=len(frames),
            frames_dropped=sum(1 for f in frames if f.frame_dropped),
            frames_speech=sum(1 for f in frames if f.vad_is_speech),
            frames_silence=sum(1 for f in frames if not f.vad_is_speech),
            latency_p50_ms=sorted_latencies[int(n * 0.5)] if n > 0 else 0,
            latency_p95_ms=sorted_latencies[int(n * 0.95)] if n > 0 else 0,
            latency_p99_ms=sorted_latencies[int(n * 0.99)] if n > 0 else 0,
            latency_avg_ms=sum(latencies) / n if n > 0 else 0,
            latency_max_ms=max(latencies) if latencies else 0,
            erle_avg_db=sum(erle_values) / len(erle_values) if erle_values else 0,
            aec_convergence_rate=sum(1 for f in frames if f.aec_converged) / n
            if n > 0
            else 0,
            double_talk_frames=sum(1 for f in frames if f.double_talk),
            speech_ratio=sum(1 for f in frames if f.vad_is_speech) / n if n > 0 else 0,
        )

        # Calculate jitter (variation in latency)
        if len(latencies) > 1:
            diffs = [
                abs(latencies[i + 1] - latencies[i]) for i in range(len(latencies) - 1)
            ]
            metrics.jitter_ms = sum(diffs) / len(diffs)

        return metrics

    def get_real_time_stats(self) -> Dict[str, Any]:
        """Get current real-time statistics."""
        if not self._latency_history:
            return {"status": "no_data"}

        latencies = list(self._latency_history)
        recent = latencies[-100:]  # Last 100 frames

        return {
            "session_id": self._session_id,
            "frames_processed": len(self._frame_metrics),
            "latency_current_ms": latencies[-1] if latencies else 0,
            "latency_avg_ms": sum(recent) / len(recent) if recent else 0,
            "latency_max_ms": max(recent) if recent else 0,
            "frames_dropped": sum(1 for f in self._frame_metrics if f.frame_dropped),
            "aec_converged": any(
                f.aec_converged for f in list(self._frame_metrics)[-100:]
            ),
            "speech_active": any(
                f.vad_is_speech for f in list(self._frame_metrics)[-10:]
            ),
        }

    # ── Output ──────────────────────────────────────────────

    async def _publish_frame_metrics(self, frame: FrameMetrics):
        """Publish frame metrics to event bus."""
        if self._bus:
            await self._bus.publish(
                TelemetryEvent(
                    timestamp=frame.timestamp,
                    source="AudioTelemetryLogger",
                    latency_budget=50,
                    metric_name="frame_metrics",
                    value=frame.total_latency_ms,
                    metadata=asdict(frame),
                )
            )

    def save_session_report(self) -> Path:
        """Save session metrics to JSON file."""
        metrics = self.get_session_metrics()
        filepath = self._log_dir / f"session_{self._session_id}.json"

        with open(filepath, "w") as f:
            json.dump(asdict(metrics), f, indent=2, default=str)

        logger.info(f"📊 Session report saved: {filepath}")
        return filepath

    def save_detailed_log(self) -> Path:
        """Save detailed frame-by-frame log to CSV."""
        import csv

        filepath = self._log_dir / f"frames_{self._session_id}.csv"
        frames = list(self._frame_metrics)

        if not frames:
            return filepath

        with open(filepath, "w", newline="") as f:
            writer = csv.DictWriter(f, fieldnames=asdict(frames[0]).keys())
            writer.writeheader()
            for frame in frames:
                writer.writerow(asdict(frame))

        logger.info(f"📊 Detailed log saved: {filepath} ({len(frames)} frames)")
        return filepath

    # ── Context Manager ─────────────────────────────────────

    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        if self._log_to_file:
            self.save_session_report()
            self.save_detailed_log()
        return False


# ═══════════════════════════════════════════════════════════
# 🌌 Benchmark Runner — Automated Performance Testing
# ═══════════════════════════════════════════════════════════


class AudioBenchmarkRunner:
    """
    Runs standardized audio benchmarks for Aether pipeline.

    Test Scenarios:
    - Single speaker (clean)
    - Overlapping speech
    - Background noise
    - Rapid commands
    - Silence gaps
    """

    SCENARIOS = [
        "single_speaker_clean",
        "overlapping_speech",
        "background_noise",
        "rapid_commands",
        "silence_gaps",
        "echo_simulation",
    ]

    def __init__(self, logger_instance: AudioTelemetryLogger):
        self._logger = logger_instance
        self._results: Dict[str, SessionMetrics] = {}

    def run_all_scenarios(self) -> Dict[str, SessionMetrics]:
        """Run all benchmark scenarios."""
        results = {}
        for scenario in self.SCENARIOS:
            logger.info(f"🏃 Running benchmark: {scenario}")
            # Benchmarks would be run here with actual audio
            # This is a placeholder for the benchmark framework
        return results

    def generate_report(self) -> Dict[str, Any]:
        """Generate comparison report across scenarios."""
        return {
            "scenarios": {k: asdict(v) for k, v in self._results.items()},
            "timestamp": datetime.now().isoformat(),
        }
