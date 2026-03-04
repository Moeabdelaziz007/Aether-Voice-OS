with open('core/audio/capture.py', 'r') as f:
    content = f.read()

content = content.replace(
    "    def __init__(self, target_latency_ms: float = 60.0, max_latency_ms: float = 200.0, sample_rate: int = 16000) -> None:",
    "    def __init__(\n        self,\n        target_latency_ms: float = 60.0,\n        max_latency_ms: float = 200.0,\n        sample_rate: int = 16000\n    ) -> None:"
)

content = content.replace(
    '            if getattr(self, "_on_audio_telemetry", None) and self._loop and not self._loop.is_closed():',
    '            if getattr(self, "_on_audio_telemetry", None) and \\\n               self._loop and not self._loop.is_closed():'
)

with open('core/audio/capture.py', 'w') as f:
    f.write(content)

with open('tests/unit/test_telemetry.py', 'r') as f:
    content = f.read()

content = content.replace(
    "        capture._dynamic_aec.process_frame.return_value = (np.zeros(512, dtype=np.int16), Mock(converged=False, convergence_progress=0.0, erle_db=0.0, estimated_delay_ms=0, double_talk_detected=False))",
    "        capture._dynamic_aec.process_frame.return_value = (\n            np.zeros(512, dtype=np.int16),\n            Mock(converged=False, convergence_progress=0.0, erle_db=0.0, estimated_delay_ms=0, double_talk_detected=False)\n        )"
)

content = content.replace(
    "        with patch('core.audio.capture.asyncio.run_coroutine_threadsafe', side_effect=mock_run_coroutine_threadsafe):",
    "        with patch(\n            'core.audio.capture.asyncio.run_coroutine_threadsafe',\n            side_effect=mock_run_coroutine_threadsafe\n        ):"
)

with open('tests/unit/test_telemetry.py', 'w') as f:
    f.write(content)
