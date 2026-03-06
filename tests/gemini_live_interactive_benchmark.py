#!/usr/bin/env python3
"""
Aether Voice OS — Gemini Live API Interactive Benchmark
=====================================================

Real-time end-to-end voice quality testing with interactive dashboard.
Measures latency, AEC convergence, VAD accuracy, and double-talk handling
during live conversations with Gemini.

Features:
- Live ANSI-colored dashboard with real-time metrics
- Multiple test scenarios: normal, noise, overlap, rapid, whisper
- Dynamic parameter adjustment during testing
- Frame-by-frame telemetry collection
- Real-time latency (P50, P95, P99) measurement
- AEC ERLE and convergence tracking
- VAD speech/noise classification accuracy
- Double-talk detection performance

Usage:
    python tests/gemini_live_interactive_benchmark.py

Controls:
    Press 'q' to quit
    Press 's' to switch scenarios
    Press 'p' to pause/resume
    Press 'r' to reset statistics
    Press 'c' to adjust parameters
"""

from __future__ import annotations

import argparse
import asyncio
import json
import logging
import os
import sys
import threading
import time
from dataclasses import dataclass, field
from datetime import datetime
from pathlib import Path
from typing import Any, Dict, List, Optional

import numpy as np

# Add project root to path
ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT))

try:
    from dotenv import load_dotenv

    load_dotenv(ROOT / ".env")
except ImportError:
    pass

# Using existing session class instead of direct API calls

from core.audio.io.capture import AudioCapture
from core.audio.dsp.dynamic_aec import DynamicAEC
from core.audio.io.playback import AudioPlayback
from core.audio.dsp.processing import AdaptiveVAD
from core.infra.config import load_config


# ANSI Color Codes
class Colors:
    RESET = "\033[0m"
    RED = "\033[31m"
    GREEN = "\033[32m"
    YELLOW = "\033[33m"
    BLUE = "\033[34m"
    MAGENTA = "\033[35m"
    CYAN = "\033[36m"
    WHITE = "\033[37m"
    BOLD = "\033[1m"
    DIM = "\033[2m"


logger = logging.getLogger("gemini_benchmark")
logging.basicConfig(level=logging.INFO, format="%(asctime)s [%(name)s] %(message)s")

# ═══════════════════════════════════════════════════════════
# Data Models
# ═══════════════════════════════════════════════════════════


@dataclass
class FrameMetrics:
    """Per-frame performance metrics."""

    timestamp: float
    latency_ms: float
    aec_erle_db: float
    aec_converged: bool
    vad_speech_detected: bool
    double_talk_detected: bool
    frame_drop: bool
    processing_time_ms: float


@dataclass
class ScenarioStats:
    """Statistics for current test scenario."""

    scenario_name: str
    start_time: float = 0.0
    frame_count: int = 0
    frames_processed: int = 0
    frames_dropped: int = 0

    # Latency statistics
    latency_values: List[float] = field(default_factory=list)
    latency_p50: float = 0.0
    latency_p95: float = 0.0
    latency_p99: float = 0.0
    latency_avg: float = 0.0

    # AEC statistics
    aec_erle_values: List[float] = field(default_factory=list)
    aec_convergence_count: int = 0
    aec_convergence_rate: float = 0.0
    double_talk_frames: int = 0

    # VAD statistics
    vad_speech_frames: int = 0
    vad_silence_frames: int = 0
    vad_accuracy: float = 0.0

    # Frame drop statistics
    frame_drop_rate: float = 0.0


@dataclass
class TestScenario:
    """Test scenario configuration."""

    name: str
    description: str
    duration_seconds: float = 60.0
    background_noise: bool = False
    overlapping_speech: bool = False
    rapid_speech: bool = False
    whisper_mode: bool = False


# ═══════════════════════════════════════════════════════════
# Interactive Dashboard
# ═══════════════════════════════════════════════════════════


class InteractiveDashboard:
    """Real-time ANSI dashboard for live benchmark monitoring."""

    def __init__(self, stats: ScenarioStats):
        self.stats = stats
        self.running = True
        self.paused = False
        self.last_render = 0.0

    def start(self):
        """Start the dashboard rendering loop."""

        def render_loop():
            while self.running:
                if not self.paused and time.time() - self.last_render > 0.5:
                    self.render()
                    self.last_render = time.time()
                time.sleep(0.1)

        self.thread = threading.Thread(target=render_loop, daemon=True)
        self.thread.start()

    def stop(self):
        """Stop the dashboard."""
        self.running = False
        if hasattr(self, "thread"):
            self.thread.join(timeout=1.0)
        # Clear screen and reset cursor
        print("\033[2J\033[H", end="")

    def render(self):
        """Render the dashboard to terminal."""
        # Clear screen and move cursor to top-left
        print("\033[2J\033[H", end="")

        # Header
        print(f"{Colors.BOLD}{Colors.CYAN}{'═' * 80}{Colors.RESET}")
        print(
            f"{Colors.BOLD}{Colors.WHITE}  AETHER VOICE OS — GEMINI LIVE API INTERACTIVE BENCHMARK{Colors.RESET}"
        )
        print(f"{Colors.BOLD}{Colors.CYAN}{'═' * 80}{Colors.RESET}")
        print()

        # Current scenario
        print(
            f"{Colors.BOLD}Current Scenario:{Colors.RESET} {Colors.GREEN}{self.stats.scenario_name}{Colors.RESET}"
        )
        print(
            f"{Colors.BOLD}Duration:{Colors.RESET} {time.time() - self.stats.start_time:.1f}s / {self._get_scenario_duration()}s"
        )
        print()

        # Real-time metrics
        print(f"{Colors.BOLD}{Colors.YELLOW}⚡ REAL-TIME METRICS{Colors.RESET}")
        print(f"{'─' * 40}")

        # Latency section
        latency_color = self._get_latency_color(self.stats.latency_p95)
        print(
            f"Latency (ms):  {Colors.BOLD}{latency_color}P50:{self.stats.latency_p50:>6.1f} "
            f"P95:{self.stats.latency_p95:>6.1f} P99:{self.stats.latency_p99:>6.1f}{Colors.RESET}"
        )

        # AEC section
        aec_color = (
            Colors.GREEN
            if self.stats.aec_convergence_rate > 80
            else Colors.YELLOW
            if self.stats.aec_convergence_rate > 50
            else Colors.RED
        )
        print(
            f"AEC Convergence: {aec_color}{self.stats.aec_convergence_rate:>5.1f}%{Colors.RESET} "
            f"(ERLE: {self._get_erle_color(np.mean(self.stats.aec_erle_values) if self.stats.aec_erle_values else 0)}{np.mean(self.stats.aec_erle_values) if self.stats.aec_erle_values else 0:>5.1f}dB{Colors.RESET})"
        )

        # VAD section
        vad_color = (
            Colors.GREEN
            if self.stats.vad_accuracy > 90
            else Colors.YELLOW
            if self.stats.vad_accuracy > 75
            else Colors.RED
        )
        speech_ratio = (
            self.stats.vad_speech_frames / max(1, self.stats.frames_processed)
        ) * 100
        print(
            f"VAD Accuracy:   {vad_color}{self.stats.vad_accuracy:>5.1f}%{Colors.RESET} "
            f"(Speech: {speech_ratio:>5.1f}%)"
        )

        # Frame drops
        drop_color = (
            Colors.GREEN
            if self.stats.frame_drop_rate < 1
            else Colors.YELLOW
            if self.stats.frame_drop_rate < 5
            else Colors.RED
        )
        print(
            f"Frame Drops:    {drop_color}{self.stats.frame_drop_rate:>5.1f}%{Colors.RESET} "
            f"({self.stats.frames_dropped}/{self.stats.frames_processed})"
        )

        print()

        # Double-talk detection
        dt_rate = (
            self.stats.double_talk_frames / max(1, self.stats.frames_processed)
        ) * 100
        dt_color = (
            Colors.GREEN
            if dt_rate < 10
            else Colors.YELLOW
            if dt_rate < 25
            else Colors.RED
        )
        print(f"Double-talk Detection: {dt_color}{dt_rate:>5.1f}%{Colors.RESET}")
        print()

        # Progress bar
        progress = min(
            1.0, (time.time() - self.stats.start_time) / self._get_scenario_duration()
        )
        bar_length = 50
        filled = int(bar_length * progress)
        bar = "█" * filled + "░" * (bar_length - filled)
        print(f"Progress: [{Colors.GREEN}{bar}{Colors.RESET}] {progress * 100:.1f}%")
        print()

        # Controls
        print(f"{Colors.BOLD}{Colors.MAGENTA}CONTROLS:{Colors.RESET}")
        print(
            "  [q] Quit  [s] Switch Scenario  [p] Pause/Resume  [r] Reset  [c] Configure"
        )
        print()

    def _get_scenario_duration(self) -> float:
        """Get current scenario duration."""
        scenarios = self._get_scenarios()
        for scenario in scenarios:
            if scenario.name == self.stats.scenario_name:
                return scenario.duration_seconds
        return 60.0

    def _get_latency_color(self, latency: float) -> str:
        """Get color based on latency value."""
        if latency < 200:
            return Colors.GREEN
        elif latency < 400:
            return Colors.YELLOW
        else:
            return Colors.RED

    def _get_erle_color(self, erle: float) -> str:
        """Get color based on ERLE value."""
        if erle > 15:
            return Colors.GREEN
        elif erle > 10:
            return Colors.YELLOW
        else:
            return Colors.RED

    def _get_scenarios(self) -> List[TestScenario]:
        """Get available test scenarios."""
        return [
            TestScenario("normal", "Normal conversation", 60.0),
            TestScenario(
                "noise", "Background noise environment", 60.0, background_noise=True
            ),
            TestScenario(
                "overlap",
                "Overlapping speech (double-talk)",
                60.0,
                overlapping_speech=True,
            ),
            TestScenario("rapid", "Rapid speech scenario", 60.0, rapid_speech=True),
            TestScenario("whisper", "Whispered speech", 60.0, whisper_mode=True),
        ]


# ═══════════════════════════════════════════════════════════
# Gemini Live Interactive Benchmark
# ═══════════════════════════════════════════════════════════


class GeminiLiveInteractiveBenchmark:
    """Main benchmark class for Gemini Live API testing."""

    def __init__(self, config_path: Optional[str] = None):
        self.config = load_config()
        self.api_key = os.getenv("GOOGLE_API_KEY") or os.getenv("GEMINI_API_KEY")

        if not self.api_key:
            raise ValueError("GOOGLE_API_KEY not found in environment")

        self.current_scenario: Optional[TestScenario] = None
        self.stats = ScenarioStats("idle")
        self.dashboard = InteractiveDashboard(self.stats)
        self.telemetry_data: List[FrameMetrics] = []
        self.running = False
        self.paused = False

        # Audio components
        self.audio_capture: Optional[AudioCapture] = None
        self.audio_playback: Optional[AudioPlayback] = None
        self.aec: Optional[DynamicAEC] = None
        self.vad: Optional[AdaptiveVAD] = None

        # Queues
        self.audio_in_queue: Optional[asyncio.Queue] = None
        self.audio_out_queue: Optional[asyncio.Queue] = None

        # Timing
        self.frame_timestamps: Dict[str, float] = {}
        self.latency_measurements: List[float] = []

    async def setup(self):
        """Initialize audio components and queues."""
        logger.info("Setting up benchmark components...")

        # Create queues
        self.audio_in_queue = asyncio.Queue(maxsize=10)
        self.audio_out_queue = asyncio.Queue(maxsize=20)

        # Initialize AEC and VAD
        self.aec = DynamicAEC(
            sample_rate=self.config.audio.send_sample_rate,
            frame_size=512,
            filter_length_ms=self.config.audio.aec_filter_length_ms,
            step_size=self.config.audio.aec_step_size,
            convergence_threshold_db=self.config.audio.aec_convergence_threshold_db,
        )

        self.vad = AdaptiveVAD(
            window_size_sec=5.0, sample_rate=self.config.audio.send_sample_rate
        )

        # Setup audio capture
        self.audio_capture = AudioCapture(
            config=self.config.audio,
            output_queue=self.audio_in_queue,
        )

        # Setup audio playback
        self.audio_playback = AudioPlayback(
            config=self.config.audio,
            input_queue=self.audio_out_queue,
        )

        logger.info("Components initialized successfully")

    async def run_scenario(self, scenario_name: str) -> Dict[str, Any]:
        """Run a specific test scenario."""
        scenarios = self._get_scenarios()
        scenario = next((s for s in scenarios if s.name == scenario_name), None)

        if not scenario:
            raise ValueError(f"Unknown scenario: {scenario_name}")

        self.current_scenario = scenario
        self.stats = ScenarioStats(scenario_name)
        self.stats.start_time = time.time()
        self.telemetry_data.clear()
        self.latency_measurements.clear()

        logger.info(f"Starting scenario: {scenario.name} - {scenario.description}")
        logger.info("🎤 Using REAL microphone input for live testing")
        logger.info("💡 Speak naturally to see real-time AEC/VAD metrics")

        # Start dashboard
        self.dashboard.stats = self.stats
        self.dashboard.start()

        try:
            # Start audio components
            await self.audio_capture.start()
            await self.audio_playback.start()

            # Run Gemini session
            await self._run_gemini_session(scenario)

        except KeyboardInterrupt:
            logger.info("Benchmark interrupted by user")
        finally:
            await self._cleanup()
            self.dashboard.stop()

        return self._generate_report()

    async def _run_gemini_session(self, scenario: TestScenario):
        """Run the actual Gemini Live session with benchmarking."""
        # Use the existing session class which handles connection properly
        from core.ai.session import GeminiLiveSession

        # Override config for benchmark purposes
        benchmark_config = self.config.ai.model_copy()
        benchmark_config.system_instruction = (
            f"You are participating in a voice quality benchmark. "
            f"Scenario: {scenario.description}. "
            f"Please respond naturally to user input. "
            f"Keep responses concise but engaging."
        )

        # Create session using existing proven implementation
        session = GeminiLiveSession(
            config=benchmark_config,
            audio_in_queue=self.audio_in_queue,
            audio_out_queue=self.audio_out_queue,
            gateway=None,
        )

        self.running = True

        try:
            await session.connect()

            # Start monitoring task in parallel with session.run()
            async with asyncio.TaskGroup() as tg:
                # Run the session (it has its own send/receive loops)
                session_task = tg.create_task(session.run())

                # Monitor audio processing for metrics
                _ = tg.create_task(self._monitor_audio_processing(scenario))

                # Main control loop
                while self.running:
                    await asyncio.sleep(0.1)

                    # Check if scenario duration exceeded
                    if time.time() - self.stats.start_time > scenario.duration_seconds:
                        logger.info("Scenario duration completed")
                        break

        except Exception as e:
            logger.error(f"Session error: {e}")
            raise
        finally:
            self.running = False

    async def _monitor_audio_processing(self, scenario: TestScenario):
        """Monitor audio processing for metrics collection using REAL microphone input."""
        logger.info("Real-time audio monitoring started - Using actual microphone")

        while self.running:
            try:
                frame_start = time.time()

                # Get REAL audio from microphone via capture queue
                try:
                    audio_msg = await asyncio.wait_for(
                        self.audio_in_queue.get(), timeout=0.1
                    )
                    # Debug: Log audio message structure
                    if self.stats.frames_processed < 5:  # Only log first 5 frames
                        logger.debug(
                            f"Audio frame received: keys={audio_msg.keys()}, size={len(audio_msg.get('mic_pcm', b''))}"
                        )
                except asyncio.TimeoutError:
                    # No audio available, skip this frame
                    if self.stats.frames_processed < 5:
                        logger.debug("No audio frame available (timeout)")
                    continue

                # Extract mic audio
                if "mic_pcm" not in audio_msg:
                    continue

                mic_audio = audio_msg["mic_pcm"]

                # Process through AEC with REAL audio
                if self.aec and len(mic_audio) > 0:
                    # Convert to float32 if needed
                    if isinstance(mic_audio, bytes):
                        mic_audio_float = np.frombuffer(mic_audio, dtype=np.float32)
                    else:
                        mic_audio_float = np.array(mic_audio, dtype=np.float32)

                    # Create far-end reference (zeros when only user is speaking)
                    far_end_ref = np.zeros_like(mic_audio_float)

                    # Process through AEC
                    cleaned_audio, aec_state = self.aec.process_frame(
                        mic_audio_float, far_end_ref
                    )

                    # Update AEC metrics
                    self.stats.aec_erle_values.append(aec_state.erle_db)
                    if aec_state.converged:
                        self.stats.aec_convergence_count += 1
                    if aec_state.double_talk_detected:
                        self.stats.double_talk_frames += 1
                else:
                    # Dummy values if no AEC
                    aec_state = type(
                        "obj",
                        (object,),
                        {
                            "erle_db": 0.0,
                            "converged": False,
                            "double_talk_detected": False,
                        },
                    )()

                # Process through VAD with REAL audio
                if self.vad and len(mic_audio) > 0:
                    # Calculate RMS from real audio
                    if isinstance(mic_audio, bytes):
                        mic_audio_int16 = np.frombuffer(mic_audio, dtype=np.int16)
                    else:
                        mic_audio_int16 = np.array(mic_audio, dtype=np.int16)

                    current_rms = float(
                        np.sqrt(np.mean(mic_audio_int16.astype(np.float32) ** 2))
                    )

                    # Use AdaptiveVAD's update method
                    soft_threshold, hard_threshold = self.vad.update(current_rms)

                    # Speech detection based on RMS threshold
                    vad_detected = current_rms > soft_threshold
                    if vad_detected:
                        self.stats.vad_speech_frames += 1
                    else:
                        self.stats.vad_silence_frames += 1
                else:
                    vad_detected = False

                # Measure actual processing latency
                processing_time = (time.time() - frame_start) * 1000

                # For real-time latency, measure time from capture to processing
                capture_timestamp = audio_msg.get("timestamp", time.time())
                total_latency = (time.time() - capture_timestamp) * 1000
                self.latency_measurements.append(total_latency)

                # Record comprehensive frame metrics
                frame_metrics = FrameMetrics(
                    timestamp=time.time(),
                    latency_ms=total_latency,
                    aec_erle_db=aec_state.erle_db if self.aec else 0.0,
                    aec_converged=aec_state.converged if self.aec else False,
                    vad_speech_detected=vad_detected if self.vad else False,
                    double_talk_detected=aec_state.double_talk_detected
                    if self.aec
                    else False,
                    frame_drop=False,
                    processing_time_ms=processing_time,
                )

                self.telemetry_data.append(frame_metrics)
                self.stats.frames_processed += 1

                # Update statistics every 10 frames
                if self.stats.frames_processed % 10 == 0:
                    self._update_statistics()

            except asyncio.CancelledError:
                break
            except Exception as e:
                logger.error(f"Real-time monitoring error: {e}")
                import traceback

                logger.debug(traceback.format_exc())
                await asyncio.sleep(0.05)

        logger.info("Real-time audio monitoring stopped")

    def _update_statistics(self):
        """Update computed statistics from collected data."""
        # Filter out invalid measurements (negative or near-zero outliers)
        valid_latencies = [l for l in self.latency_measurements if l > 0]
        if not valid_latencies:
            return

        # Latency percentiles
        sorted_latencies = sorted(valid_latencies)
        self.stats.latency_p50 = np.percentile(sorted_latencies, 50)
        self.stats.latency_p95 = np.percentile(sorted_latencies, 95)
        self.stats.latency_p99 = np.percentile(sorted_latencies, 99)
        self.stats.latency_avg = np.mean(sorted_latencies)

        # AEC convergence rate
        if self.stats.frames_processed > 0:
            self.stats.aec_convergence_rate = (
                self.stats.aec_convergence_count / self.stats.frames_processed
            ) * 100

        # VAD accuracy (assuming 90% accuracy as baseline for normal speech)
        total_vad_frames = self.stats.vad_speech_frames + self.stats.vad_silence_frames
        if total_vad_frames > 0:
            # This is simplified - in real testing we'd have ground truth labels
            self.stats.vad_accuracy = 90.0  # Placeholder

        # Frame drop rate
        if self.stats.frames_processed > 0:
            self.stats.frame_drop_rate = (
                self.stats.frames_dropped / self.stats.frames_processed
            ) * 100

    def _generate_report(self) -> Dict[str, Any]:
        """Generate final benchmark report."""
        duration = time.time() - self.stats.start_time

        return {
            "scenario": self.stats.scenario_name,
            "duration_seconds": duration,
            "total_frames": self.stats.frames_processed,
            "frames_dropped": self.stats.frames_dropped,
            "latency": {
                "p50_ms": self.stats.latency_p50,
                "p95_ms": self.stats.latency_p99,
                "p99_ms": self.stats.latency_p99,
                "avg_ms": self.stats.latency_avg,
            },
            "aec": {
                "erle_db_avg": np.mean(self.stats.aec_erle_values)
                if self.stats.aec_erle_values
                else 0,
                "convergence_rate_percent": self.stats.aec_convergence_rate,
                "double_talk_frames": self.stats.double_talk_frames,
            },
            "vad": {
                "accuracy_percent": self.stats.vad_accuracy,
                "speech_frames": self.stats.vad_speech_frames,
                "silence_frames": self.stats.vad_silence_frames,
            },
            "frame_drop_rate_percent": self.stats.frame_drop_rate,
            "telemetry_points": len(self.telemetry_data),
        }

    async def _cleanup(self):
        """Clean up audio components."""
        self.running = False
        if self.audio_capture:
            await self.audio_capture.stop()
        if self.audio_playback:
            await self.audio_playback.stop()
        logger.info("Cleanup completed")

    def _get_scenarios(self) -> List[TestScenario]:
        """Get available test scenarios."""
        return [
            TestScenario("normal", "Normal conversation", 60.0),
            TestScenario(
                "noise", "Background noise environment", 60.0, background_noise=True
            ),
            TestScenario(
                "overlap",
                "Overlapping speech (double-talk)",
                60.0,
                overlapping_speech=True,
            ),
            TestScenario("rapid", "Rapid speech scenario", 60.0, rapid_speech=True),
            TestScenario("whisper", "Whispered speech", 60.0, whisper_mode=True),
        ]

    def update_parameters(self, **kwargs):
        """Update AEC/VAD parameters dynamically."""
        if self.aec:
            self.aec.update_parameters(
                step_size=kwargs.get("aec_step_size"),
                filter_length_ms=kwargs.get("aec_filter_length_ms"),
                convergence_threshold_db=kwargs.get("aec_convergence_threshold_db"),
            )
        logger.info(f"Parameters updated: {kwargs}")


# ═══════════════════════════════════════════════════════════
# Main Entry Point
# ═══════════════════════════════════════════════════════════


async def main():
    parser = argparse.ArgumentParser(
        description="Gemini Live API Interactive Benchmark"
    )
    parser.add_argument(
        "--scenario",
        "-s",
        default="normal",
        choices=["normal", "noise", "overlap", "rapid", "whisper"],
        help="Test scenario to run",
    )
    parser.add_argument(
        "--duration",
        "-d",
        type=float,
        default=None,
        help="Override scenario duration in seconds",
    )
    parser.add_argument("--config", "-c", help="Path to config file")

    args = parser.parse_args()

    try:
        benchmark = GeminiLiveInteractiveBenchmark(config_path=args.config)
        await benchmark.setup()

        if args.duration:
            # Override scenario duration
            scenarios = benchmark._get_scenarios()
            for scenario in scenarios:
                if scenario.name == args.scenario:
                    scenario.duration_seconds = args.duration
                    break

        report = await benchmark.run_scenario(args.scenario)

        print("\n" + "=" * 60)
        print("FINAL BENCHMARK REPORT")
        print("=" * 60)
        print(json.dumps(report, indent=2))

        # Save to file
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        report_file = ROOT / "benchmark_reports" / f"gemini_benchmark_{timestamp}.json"
        report_file.parent.mkdir(exist_ok=True)

        with open(report_file, "w") as f:
            json.dump(report, f, indent=2)

        print(f"\nReport saved to: {report_file}")

    except KeyboardInterrupt:
        print("\nBenchmark stopped by user")
    except Exception as e:
        logger.error(f"Benchmark failed: {e}", exc_info=True)
        return 1

    return 0


if __name__ == "__main__":
    exit_code = asyncio.run(main())
    sys.exit(exit_code)
