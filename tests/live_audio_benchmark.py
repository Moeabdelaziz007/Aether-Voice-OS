#!/usr/bin/env python3
"""
Aether Voice OS — Live Audio Benchmark

Runs real-time audio pipeline tests and captures performance metrics.

Test Scenarios:
1. Single speaker (clean)
2. Overlapping speech (simulated echo)
3. Background noise
4. Rapid commands
5. Silence gaps

Usage:
    python tests/live_audio_benchmark.py --duration 30 --scenario all
"""

from __future__ import annotations

import argparse
import asyncio
import logging
import sys
import time
from pathlib import Path

# Add project root to path
ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT))

if True:
    from core.audio.capture import AudioCapture
    from core.audio.paralinguistics import ParalinguisticAnalyzer
    from core.audio.playback import AudioPlayback
    from core.audio.processing import AdaptiveVAD, SilentAnalyzer
    from core.audio.telemetry import AudioTelemetryLogger
    from core.infra.config import load_config

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s │ %(levelname)-7s │ %(name)-28s │ %(message)s",
    datefmt="%H:%M:%S",
)
logger = logging.getLogger(__name__)


class LiveAudioBenchmark:
    """
    Live audio pipeline benchmark runner.

    Captures real microphone input and measures:
    - End-to-end latency
    - AEC performance (ERLE, convergence)
    - VAD accuracy
    - Frame drops
    - Jitter
    """

    def __init__(
        self,
        duration_sec: float = 30.0,
        scenario: str = "all",
        output_dir: str = "telemetry_logs",
    ):
        self._duration = duration_sec
        self._scenario = scenario
        self._output_dir = Path(output_dir)
        self._output_dir.mkdir(parents=True, exist_ok=True)

        self._config = load_config()
        self._telemetry: AudioTelemetryLogger = None
        self._capture: AudioCapture = None
        self._playback: AudioPlayback = None
        self._running = False

    async def setup(self) -> None:
        """Initialize audio components."""
        logger.info("🚀 Setting up Live Audio Benchmark...")

        # Create telemetry logger
        session_id = f"benchmark_{int(time.time() * 1000)}"
        self._telemetry = AudioTelemetryLogger(
            session_id=session_id, log_to_file=True, log_dir=str(self._output_dir)
        )

        # Create queues
        audio_in_queue = asyncio.Queue(maxsize=self._config.audio.mic_queue_max)
        audio_out_queue = asyncio.Queue(maxsize=15)

        # Create VAD engine
        vad_engine = AdaptiveVAD(
            window_size_sec=5.0, sample_rate=self._config.audio.send_sample_rate
        )

        # Create analyzers
        silent_analyzer = SilentAnalyzer(
            sample_rate=self._config.audio.send_sample_rate
        )
        para_analyzer = ParalinguisticAnalyzer()

        # Create capture
        self._capture = AudioCapture(
            config=self._config.audio,
            output_queue=audio_in_queue,
            analyzer=silent_analyzer,
            vad_engine=vad_engine,
            paralinguistic_analyzer=para_analyzer,
        )

        # Attach telemetry logger
        self._capture.set_telemetry_logger(self._telemetry)

        # Create playback
        self._playback = AudioPlayback(
            config=self._config.audio,
            input_queue=audio_out_queue,
        )

        logger.info(f"📊 Session ID: {session_id}")
        logger.info(f"⏱️ Duration: {self._duration}s")
        logger.info(f"📁 Output: {self._output_dir}")

    async def run(self) -> dict:
        """Run the benchmark and return metrics."""
        logger.info("=" * 60)
        logger.info("  LIVE AUDIO BENCHMARK — STARTING")
        logger.info("=" * 60)

        self._running = True
        start_time = time.time()

        try:
            # Start audio components
            await self._capture.start()
            await self._playback.start()

            logger.info("🎙️ Microphone active — SPEAK NOW!")
            logger.info(f"⏱️ Recording for {self._duration} seconds...")

            # Run for specified duration
            while self._running and (time.time() - start_time) < self._duration:
                # Print periodic stats
                await asyncio.sleep(5.0)
                stats = self._telemetry.get_real_time_stats()
                logger.info(
                    f"📊 Stats: "
                    f"latency={stats.get('latency_avg_ms', 0):.1f}ms avg, "
                    f"frames={stats.get('frames_processed', 0)}, "
                    f"dropped={stats.get('frames_dropped', 0)}, "
                    f"AEC={'✓' if stats.get('aec_converged') else '○'}"
                )

        except KeyboardInterrupt:
            logger.info("⏹️ Benchmark interrupted by user")
        finally:
            await self.teardown()

        # Get final metrics
        metrics = self._telemetry.get_session_metrics()
        return self._format_metrics(metrics)

    def _format_metrics(self, metrics) -> dict:
        """Format metrics for display."""
        return {
            "session_id": metrics.session_id,
            "duration_sec": metrics.end_time - metrics.start_time
            if metrics.end_time
            else 0,
            "total_frames": metrics.total_frames,
            "frames_dropped": metrics.frames_dropped,
            "drop_rate": (
                metrics.frames_dropped / metrics.total_frames * 100
                if metrics.total_frames > 0
                else 0
            ),
            "latency": {
                "p50_ms": round(metrics.latency_p50_ms, 2),
                "p95_ms": round(metrics.latency_p95_ms, 2),
                "p99_ms": round(metrics.latency_p99_ms, 2),
                "avg_ms": round(metrics.latency_avg_ms, 2),
                "max_ms": round(metrics.latency_max_ms, 2),
            },
            "aec": {
                "erle_avg_db": round(metrics.erle_avg_db, 2),
                "convergence_rate": round(metrics.aec_convergence_rate * 100, 1),
                "double_talk_frames": metrics.double_talk_frames,
            },
            "vad": {
                "speech_ratio": round(metrics.speech_ratio * 100, 1),
                "speech_frames": metrics.frames_speech,
                "silence_frames": metrics.frames_silence,
            },
            "jitter_ms": round(metrics.jitter_ms, 2),
        }

    async def teardown(self) -> None:
        """Clean up audio components."""
        logger.info("🛑 Stopping benchmark...")
        self._running = False

        if self._capture:
            await self._capture.stop()
        if self._playback:
            await self._playback.stop()

        # Save reports
        if self._telemetry:
            report_path = self._telemetry.save_session_report()
            csv_path = self._telemetry.save_detailed_log()
            logger.info(f"📄 Session report: {report_path}")
            logger.info(f"📄 Detailed log: {csv_path}")

    def print_summary(self, metrics: dict) -> None:
        """Print formatted summary."""
        print("\n" + "=" * 60)
        print("  BENCHMARK SUMMARY")
        print("=" * 60)
        print(f"\n📊 Session: {metrics['session_id']}")
        print(f"⏱️ Duration: {metrics['duration_sec']:.1f}s")
        print(
            f"🎬 Frames: {metrics['total_frames']} ({metrics['frames_dropped']} dropped, {metrics['drop_rate']:.1f}%)"
        )

        print("\n⚡ Latency:")
        print(f"   p50: {metrics['latency']['p50_ms']:.1f}ms")
        print(f"   p95: {metrics['latency']['p95_ms']:.1f}ms")
        print(f"   p99: {metrics['latency']['p99_ms']:.1f}ms")
        print(f"   avg: {metrics['latency']['avg_ms']:.1f}ms")
        print(f"   max: {metrics['latency']['max_ms']:.1f}ms")

        print("\n🔊 AEC Performance:")
        print(f"   ERLE avg: {metrics['aec']['erle_avg_db']:.1f}dB")
        print(f"   Convergence: {metrics['aec']['convergence_rate']:.1f}%")
        print(f"   Double-talk frames: {metrics['aec']['double_talk_frames']}")

        print("\n🎤 VAD Stats:")
        print(f"   Speech ratio: {metrics['vad']['speech_ratio']:.1f}%")
        print(f"   Speech frames: {metrics['vad']['speech_frames']}")
        print(f"   Silence frames: {metrics['vad']['silence_frames']}")

        print(f"\n📈 Jitter: {metrics['jitter_ms']:.2f}ms")
        print("=" * 60)


async def main():
    parser = argparse.ArgumentParser(
        description="Aether Voice OS — Live Audio Benchmark"
    )
    parser.add_argument(
        "--duration",
        type=float,
        default=30.0,
        help="Benchmark duration in seconds (default: 30)",
    )
    parser.add_argument(
        "--scenario",
        type=str,
        default="all",
        choices=["all", "single_speaker", "noise", "rapid"],
        help="Test scenario to run (default: all)",
    )
    parser.add_argument(
        "--output",
        type=str,
        default="telemetry_logs",
        help="Output directory for logs (default: telemetry_logs)",
    )

    args = parser.parse_args()

    benchmark = LiveAudioBenchmark(
        duration_sec=args.duration, scenario=args.scenario, output_dir=args.output
    )

    await benchmark.setup()
    metrics = await benchmark.run()
    benchmark.print_summary(metrics)

    return metrics


if __name__ == "__main__":
    asyncio.run(main())
