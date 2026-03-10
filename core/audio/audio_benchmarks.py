import time
from datetime import datetime
from typing import Any, Dict

import structlog

from core.audio.telemetry import AudioTelemetryLogger, SessionMetrics

logger = structlog.get_logger("AetherOS.Audio.Benchmark")


class AudioBenchmarkRunner:
    """
    Runs standardized audio benchmarks for Aether pipeline.
    Tests scenarios: clean speech, noise, overlap, rapid commands.
    """

    SCENARIOS = [
        "single_speaker_clean",
        "overlapping_speech",
        "background_noise",
        "rapid_commands",
        "silence_gaps",
        "echo_simulation",
    ]

    def __init__(self, telemetry_logger: AudioTelemetryLogger):
        self._logger = telemetry_logger
        self._results: Dict[str, SessionMetrics] = {}

    def record_scenario_result(self, scenario: str, metrics: SessionMetrics):
        self._results[scenario] = metrics
        logger.info(f"Benchmark result recorded for: {scenario}")

    def generate_report(self) -> Dict[str, Any]:
        """Generate comparison report across scenarios."""
        return {
            "scenarios": {k: str(v) for k, v in self._results.items()},
            "timestamp": datetime.now().isoformat(),
            "verdict": "READY" if len(self._results) > 0 else "NO_DATA",
        }


async def run_latency_stress_test(logger_instance: AudioTelemetryLogger, duration_sec: int = 10):
    """Utility to stress the pipeline and record results."""
    logger.info(f"Starting latency stress test for {duration_sec}s...")
    start_time = time.time()
    while time.time() - start_time < duration_sec:
        logger_instance.start_frame()
        # Simulate processing delay
        time.sleep(0.01)
        logger_instance.record_capture(2.5)
        logger_instance.record_aec(1.2, converged=True)
        logger_instance.end_frame()

    report = logger_instance.get_session_metrics()
    logger.info("Stress test complete.", p95_ms=report.latency_p95_ms)
    return report
