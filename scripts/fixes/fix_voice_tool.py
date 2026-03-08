with open("core/tools/voice_tool.py", "r") as f:
    content = f.read()

content = content.replace(
    "self._capture = AudioCaptureself._config.audio, self._audio_in)",
    "self._capture = AudioCapture(self._config.audio, self._audio_in)",
)
content = content.replace(
    "self._playback = AudioPlaybackself._config.audio, self._audio_out)",
    "self._playback = AudioPlayback(self._config.audio, self._audio_out)",
)
content = content.replace("mock_gateway = MagicMock)", "mock_gateway = MagicMock()")
content = content.replace(
    'raise RuntimeError"Call setup() before execute()")',
    'raise RuntimeError("Call setup() before execute()")',
)


with open("core/tools/voice_tool.py", "w") as f:
    f.write(content)
