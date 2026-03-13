#!/usr/bin/env python3
"""
Aether Voice OS — Live Audio Dashboard

Real-time monitoring dashboard for voice agent performance.
Displays: Latency, ERLE, VAD, AEC Convergence, Frame Drops, Jitter

Usage:
    python tests/live_dashboard.py --duration 60
"""

from __future__ import annotations

import argparse
import asyncio
import logging
import sys
import time
from collections import deque
from dataclasses import dataclass
from pathlib import Path
from typing import Optional

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT))

if True:
    from core.audio.capture import AudioCapture
    from core.audio.paralinguistics import ParalinguisticAnalyzer
    from core.audio.playback import AudioPlayback
    from core.audio.processing import AdaptiveVAD, SilentAnalyzer
    from core.audio.state import audio_state
    from core.audio.telemetry import AudioTelemetryLogger
    from core.infra.config import load_config

logging.basicConfig(level=logging.WARNING, format="")


class Colors:
    RESET = "\033[0m"
    BOLD = "\033[1m"
    DIM = "\033[2m"
    RED = "\033[91m"
    GREEN = "\033[92m"
    YELLOW = "\033[93m"
    BLUE = "\033[94m"
    MAGENTA = "\033[95m"
    CYAN = "\033[96m"
    WHITE = "\033[97m"
    BG_RED = "\033[41m"
    BG_GREEN = "\033[42m"
    BG_YELLOW = "\033[43m"


@dataclass
class DashboardMetrics:
    latency_current_ms: float = 0.0
    latency_avg_ms: float = 0.0
    latency_p95_ms: float = 0.0
    latency_max_ms: float = 0.0
    erle_db: float = 0.0
    aec_converged: bool = False
    aec_convergence_rate: float = 0.0
    double_talk: bool = False
    vad_is_speech: bool = False
    rms_energy: float = 0.0
    speech_ratio: float = 0.0
    frames_total: int = 0
    frames_dropped: int = 0
    jitter_ms: float = 0.0
    session_time_sec: float = 0.0
    queue_pressure: float = 0.0


class LiveDashboard:
    LATENCY_GOOD = 5.0
    LATENCY_WARN = 10.0
    ERLE_GOOD = 15.0
    ERLE_WARN = 10.0
    JITTER_GOOD = 2.0
    JITTER_WARN = 5.0

    def __init__(self, duration_sec: float = 60.0):
        self._duration = duration_sec
        self._config = load_config()
        self._telemetry: Optional[AudioTelemetryLogger] = None
        self._capture: Optional[AudioCapture] = None
        self._playback: Optional[AudioPlayback] = None
        self._running = False
        self._start_time = 0.0
        self._latency_history: deque = deque(maxlen=60)
        self._erle_history: deque = deque(maxlen=60)
        self._rms_history: deque = deque(maxlen=60)
        self._metrics = DashboardMetrics()

    async def setup(self) -> None:
        session_id = f"dashboard_{int(time.time() * 1000)}"
        self._telemetry = AudioTelemetryLogger(
            session_id=session_id, log_to_file=True, log_dir="telemetry_logs"
        )
        audio_in_queue = asyncio.Queue(maxsize=self._config.audio.mic_queue_max)
        audio_out_queue = asyncio.Queue(maxsize=15)
        vad_engine = AdaptiveVAD(
            window_size_sec=5.0, sample_rate=self._config.audio.send_sample_rate
        )
        silent_analyzer = SilentAnalyzer(
            sample_rate=self._config.audio.send_sample_rate
        )
        para_analyzer = ParalinguisticAnalyzer()
        self._capture = AudioCapture(
            config=self._config.audio,
            output_queue=audio_in_queue,
            analyzer=silent_analyzer,
            vad_engine=vad_engine,
            paralinguistic_analyzer=para_analyzer,
        )
        self._capture.set_telemetry_logger(self._telemetry)
        self._playback = AudioPlayback(
            config=self._config.audio, input_queue=audio_out_queue
        )

    async def run(self) -> None:
        self._running = True
        self._start_time = time.time()
        await self._capture.start()
        await self._playback.start()
        print("\033[2J\033[H", end="")
        print("\033[?25l", end="")
        try:
            await asyncio.create_task(self._display_loop())
        except KeyboardInterrupt:
            pass
        finally:
            self._running = False
            print("\033[?25h", end="")
            await self.teardown()

    async def _display_loop(self) -> None:
        while self._running:
            self._update_metrics()
            self._render()
            await asyncio.sleep(0.1)

    def _update_metrics(self) -> None:
        if not self._telemetry:
            return
        stats = self._telemetry.get_real_time_stats()
        session = self._telemetry.get_session_metrics()
        self._metrics.latency_current_ms = stats.get("latency_current_ms", 0)
        self._metrics.latency_avg_ms = stats.get("latency_avg_ms", 0)
        self._metrics.frames_total = stats.get("frames_processed", 0)
        self._metrics.frames_dropped = stats.get("frames_dropped", 0)
        self._metrics.aec_converged = stats.get("aec_converged", False)
        self._metrics.vad_is_speech = stats.get("speech_active", False)
        self._metrics.latency_p95_ms = session.latency_p95_ms
        self._metrics.latency_max_ms = session.latency_max_ms
        self._metrics.erle_db = session.erle_avg_db
        self._metrics.aec_convergence_rate = session.aec_convergence_rate
        self._metrics.speech_ratio = session.speech_ratio
        self._metrics.jitter_ms = session.jitter_ms
        self._metrics.double_talk = getattr(audio_state, "double_talk", False)
        self._metrics.rms_energy = getattr(audio_state, "last_rms", 0)
        self._metrics.session_time_sec = time.time() - self._start_time
        if self._metrics.latency_current_ms > 0:
            self._latency_history.append(self._metrics.latency_current_ms)
        if self._metrics.erle_db > 0:
            self._erle_history.append(self._metrics.erle_db)
        self._rms_history.append(self._metrics.rms_energy)

    def _color_latency(self, val: float) -> str:
        if val < self.LATENCY_GOOD:
            return f"{Colors.GREEN}{val:.1f}{Colors.RESET}"
        elif val < self.LATENCY_WARN:
            return f"{Colors.YELLOW}{val:.1f}{Colors.RESET}"
        return f"{Colors.RED}{val:.1f}{Colors.RESET}"

    def _color_erle(self, val: float) -> str:
        if val >= self.ERLE_GOOD:
            return f"{Colors.GREEN}{val:.1f}{Colors.RESET}"
        elif val >= self.ERLE_WARN:
            return f"{Colors.YELLOW}{val:.1f}{Colors.RESET}"
        return f"{Colors.RED}{val:.1f}{Colors.RESET}"

    def _color_jitter(self, val: float) -> str:
        if val < self.JITTER_GOOD:
            return f"{Colors.GREEN}{val:.1f}{Colors.RESET}"
        elif val < self.JITTER_WARN:
            return f"{Colors.YELLOW}{val:.1f}{Colors.RESET}"
        return f"{Colors.RED}{val:.1f}{Colors.RESET}"

    def _sparkline(self, data: deque, width: int = 30, height: int = 5) -> str:
        if not data:
            return " " * width
        bars = ["▁", "▂", "▃", "▄", "▅", "▆", "▇", "█"]
        vals = list(data)[-width:]
        max_val = max(vals) if max(vals) > 0 else 1
        normalized = [int(v / max_val * (len(bars) - 1)) for v in vals]
        return "".join(bars[min(i, len(bars) - 1)] for i in normalized)

    def _render(self) -> None:
        print("\033[H", end="")
        m = self._metrics
        remain = max(0, self._duration - m.session_time_sec)
        status = (
            f"{Colors.BG_GREEN} LIVE {Colors.RESET}"
            if m.frames_total > 0
            else f"{Colors.BG_YELLOW} WAITING {Colors.RESET}"
        )
        header = f"""
{Colors.BOLD}{"═" * 70}{Colors.RESET}
{Colors.BOLD}  🎙️  AETHER VOICE OS — LIVE DASHBOARD  {status}{Colors.BOLD}
{"═" * 70}{Colors.RESET}
  ⏱️  Session: {m.session_time_sec:.1f}s / {self._duration:.0f}s    "
  ⏳ Remaining: {remain:.1f}s    🎬 Frames: {m.frames_total}
"""
        latency_section = f"""
{Colors.BOLD}┌{"─" * 30} LATENCY {"─" * 30}┐{Colors.RESET}
│                                                                  │
│  Current: {self._color_latency(m.latency_current_ms):>8} ms    "
  Avg: {self._color_latency(m.latency_avg_ms):>8} ms    "
  P95: {self._color_latency(m.latency_p95_ms):>8} ms    "
  Max: {self._color_latency(m.latency_max_ms):>8} ms    │
│                                                                  │
│  Graph: {Colors.CYAN}{self._sparkline(self._latency_history)}{Colors.RESET}  │
│                                                                  │
{Colors.BOLD}└{"─" * 68}┘{Colors.RESET}
"""
        aec_vad_section = f"""
{Colors.BOLD}┌{"─" * 30} AEC / VAD {"─" * 29}┐{Colors.RESET}
│                                                                  │
│  ERLE: {self._color_erle(m.erle_db):>8} dB    "
  Convergence: {Colors.GREEN if m.aec_converged else Colors.RED}"
  {m.aec_convergence_rate * 100:.0f}%{Colors.RESET}    "
  Double-Talk: {Colors.YELLOW if m.double_talk else Colors.GREEN}"
  {"⚡" if m.double_talk else "○"}{Colors.RESET}            │
│                                                                  │
│  VAD Status: {Colors.GREEN if m.vad_is_speech else Colors.DIM}"
  {"🗣️ SPEAKING" if m.vad_is_speech else "🔇 SILENT"}{Colors.RESET}    "
  RMS: {m.rms_energy:.4f}        │
│                                                                  │
{Colors.BOLD}└{"─" * 68}┘{Colors.RESET}
"""
        system_section = f"""
{Colors.BOLD}┌{"─" * 30} SYSTEM {"─" * 31}┐{Colors.RESET}
│                                                                  │
│  Jitter: {self._color_jitter(m.jitter_ms):>8} ms    "
  Frames Dropped: {Colors.RED if m.frames_dropped > 0 else Colors.GREEN}"
  {m.frames_dropped}{Colors.RESET}    "
  Speech Ratio: {m.speech_ratio * 100:.1f}%          │
│                                                                  │
{Colors.BOLD}└{"─" * 68}┘{Colors.RESET}
"""
        print(header + latency_section + aec_vad_section + system_section)

    async def teardown(self) -> None:
        if self._capture:
            await self._capture.stop()
        if self._playback:
            await self._playback.stop()
        if self._telemetry:
            self._telemetry.save_session_report()
            self._telemetry.save_detailed_log()


async def main():
    parser = argparse.ArgumentParser(description="Aether Live Dashboard")
    parser.add_argument(
        "--duration", type=float, default=60.0, help="Duration in seconds"
    )
    args = parser.parse_args()
    dashboard = LiveDashboard(duration_sec=args.duration)
    await dashboard.setup()
    await dashboard.run()


if __name__ == "__main__":
    asyncio.run(main())
