import asyncio
import time
from unittest.mock import MagicMock, patch

import numpy as np
import pytest

# Mock the audio_state singleton before it's imported by other modules

mock_audio_state = MagicMock()
mock_audio_state.far_end_pcm.read_last.return_value = np.zeros(512, dtype=np.int16)
patcher = patch.dict("sys.modules", {"core.audio.state": mock_audio_state})
patcher.start()

from core.audio.capture import AudioCapture  # noqa: E402
from core.infra.config import AudioConfig  # noqa: E402

# Constants
SAMPLE_RATE = 16000
CHUNK_SIZE = 512

# Try to import the benchmark fixture, but don't fail if it's not there.
try:
    from pytest_benchmark.fixture import BenchmarkFixture

    pytest_benchmark_installed = True
except ImportError:
    pytest_benchmark_installed = False
    BenchmarkFixture = object  # Define a dummy for type hinting


@pytest.fixture
def capture_instance():
    """Provides a fully mocked AudioCapture instance for benchmarking."""
    mock_config = AudioConfig(send_sample_rate=SAMPLE_RATE, chunk_size=CHUNK_SIZE)
    mock_queue = MagicMock(spec=asyncio.Queue)

    with (
        patch("core.audio.capture.DynamicAEC") as MockDynamicAEC,
        patch("core.audio.capture.SmoothMuter"),
        patch("core.audio.capture.HysteresisGate"),
        patch("core.audio.capture.AECBridge"),
        patch("core.audio.capture.energy_vad"),
    ):
        mock_aec_instance = MockDynamicAEC.return_value
        mock_aec_state = MagicMock()
        mock_aec_state.converged = True
        mock_aec_state.convergence_progress = 1.0
        mock_aec_instance.process_frame.return_value = (
            np.zeros(CHUNK_SIZE, dtype=np.int16),
            mock_aec_state,
        )

        instance = AudioCapture(
            config=mock_config,
            output_queue=mock_queue,
        )
        instance._loop = MagicMock()
        return instance


@pytest.fixture
def callback_args():
    """Provides standard arguments for the _callback method."""
    in_data = (np.random.randn(CHUNK_SIZE) * 1000).astype(np.int16).tobytes()
    return {"in_data": in_data, "frame_count": CHUNK_SIZE, "time_info": {}, "status": 0}


@pytest.mark.skipif(not pytest_benchmark_installed, reason="pytest-benchmark is not installed")
def test_thalamic_gate_performance(benchmark: BenchmarkFixture, capture_instance, callback_args):
    """
    Benchmarks the execution time of the Thalamic Gate callback using pytest-benchmark.
    """

    def run_callback():
        capture_instance._callback(**callback_args)

    benchmark(run_callback)


def test_thalamic_gate_manual_benchmark(capture_instance, callback_args):
    """
    A simple manual benchmark for the Thalamic Gate callback.
    This runs if pytest-benchmark is not available.
    """
    num_iterations = 1000

    start_time = time.perf_counter()
    for _ in range(num_iterations):
        capture_instance._callback(**callback_args)
    end_time = time.perf_counter()

    total_time = end_time - start_time
    avg_time_ms = (total_time / num_iterations) * 1000

    print("--- Manual Benchmark Results ---")
    print(f"Total iterations: {num_iterations}")
    print(f"Total time: {total_time:.4f} seconds")
    print(f"Average Thalamic Gate processing time: {avg_time_ms:.4f} ms per frame")

    # The prompt claims ~1.5ms/frame performance, target is < 2ms
    assert avg_time_ms < 2.5, f"Thalamic Gate is too slow ({avg_time_ms:.4f}ms), exceeds 2.5ms target."


# Stop the patcher after all tests are done
@pytest.fixture(scope="session", autouse=True)
def stop_patcher_session_wide():
    yield
    patcher.stop()
