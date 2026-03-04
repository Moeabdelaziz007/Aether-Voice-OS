### 📘 Project Best Practices

#### 1. Project Purpose
Aether Voice OS is a real-time, bidirectional **voice AI system**. It captures microphone audio at **16kHz PCM16** via PyAudio callbacks, performs local DSP (AEC/VAD/paralinguistics) to improve interaction quality and responsiveness, and streams audio to/from **Gemini Live** (native audio) over an async session. It also integrates tool calling, monitoring/telemetry, and a UI gateway.

#### 2. Project Structure
- **`core/`** — Primary Python backend.
  - **`core/audio/`** — Real-time audio pipeline.
    - `capture.py`: PyAudio mic capture callback (“Thalamic Gate”) + muting/gating + local analysis.
    - `playback.py`: PyAudio speaker callback; drains queues on barge-in.
    - `dynamic_aec.py`: Adaptive echo cancellation (delay estimation + frequency-domain NLMS + double-talk detection).
    - `processing.py`: Pure compute utilities (RingBuffer, VAD, zero-crossing search).
    - `paralinguistics.py`: Lightweight affective features (pitch, centroid, transients, zen mode).
    - `spectral.py`: STFT, coherence, GCC-PHAT delay estimation, ERLE.
    - `state.py`: Shared `audio_state` singleton and hysteresis gate.
  - **`core/ai/`** — Gemini Live session + AI orchestration.
    - `session.py`: Bidirectional Live API loops, tool call dispatching, interruption handling.
    - `thalamic.py`: Higher-level gating/backchannel hooks.
  - **`core/infra/`** — Configuration, telemetry, transport.
    - `config.py`: Pydantic settings (`AetherConfig`, `AudioConfig`, `AIConfig`).
    - `telemetry.py`: OpenTelemetry traces + usage recording.
    - `transport/`: Gateway / websocket / session state.
  - **`core/tools/`** — ToolRouter and tool implementations.
- **`apps/portal/`** — Next.js UI (frontend).
- **`cortex/`** — Rust DSP acceleration backend (`aether_cortex`) mirrored by Python fallbacks.
- **`tests/`** — Pytest test suites.
  - `tests/unit/`: unit tests for DSP, capture, session, etc.
  - `tests/integration/`, `tests/e2e/`: higher-level tests.

**Entry points / runtime:**
- `core/engine.py`, `core/server.py` are typical orchestration/serving layers.
- Configuration is loaded via `core/infra/config.py::load_config()` and `.env` files.

#### 3. Test Strategy
- **Framework:** `pytest` (with `pytest-asyncio` for async tests).
- **Test layout:**
  - Unit tests in `tests/unit/test_*.py`.
  - Prefer DSP unit tests using **numpy synthetic signals** (sines, delayed echoes, controlled noise).
- **Mocking guidelines:**
  - Mock external I/O and SDKs: PyAudio (`pyaudio.Stream`), Gemini client/session (`google.genai`), gateways.
  - For audio callback tests, mock `core.audio.state.audio_state` before importing modules that reference it.
  - Use deterministic randomness via `np.random.default_rng(seed)`.
- **Unit vs integration:**
  - **Unit tests**: validate pure compute (`processing.py`, `spectral.py`, NLMS behavior) and callback logic with mocks.
  - **Integration tests**: validate end-to-end audio pipeline behavior (queues, session loops) without real devices.
- **Coverage expectations:**
  - Target **>80% coverage** on the audio pipeline modules:
    - `core/audio/capture.py`, `dynamic_aec.py`, `processing.py`, `paralinguistics.py`, `spectral.py`.

#### 4. Code Style
- **Typing:**
  - Use Python type hints consistently (`np.ndarray`, `NDArray[np.int16]`, `Optional[...]`, `tuple[...]`).
  - Prefer explicit return types for public methods.
- **Async + threading:**
  - PyAudio callbacks run on a C-thread; avoid blocking, heavy allocations, or async operations directly.
  - Use `loop.call_soon_threadsafe(...)` for interaction with asyncio.
  - Prefer bounded queues and explicit overflow policy to keep latency bounded.
- **Naming conventions:**
  - Modules: `snake_case.py`
  - Classes: `PascalCase`
  - Functions/methods: `snake_case`
  - Constants: `UPPER_SNAKE_CASE`
- **Documentation:**
  - Use module docstrings to explain purpose and runtime constraints (hot path vs cold path).
  - For DSP logic, add short comments describing signal processing assumptions.
- **Error handling:**
  - Use domain-specific exceptions from `core/utils/errors.py` when possible.
  - In hot paths (callbacks), prefer best-effort handling + counters/logging rather than raising.

#### 5. Common Patterns
- **Hot-path vs cold-path separation**
  - Keep DSP and gating inside callback minimal.
  - Push complex operations to the asyncio side when feasible.
- **Best-effort telemetry**
  - Maintain cheap integer counters for overflow/drops (e.g., `audio_state.capture_queue_drops`).
  - Add structured logging but rate-limit in hot paths.
- **Fallback strategy (Rust-first)**
  - Modules like `processing.py` may dispatch to Rust (`aether_cortex`) if present.
  - Tests should be robust to backend differences by asserting semantic behavior.
- **Queue overflow policy**
  - Drop **oldest** items on overflow to keep output “fresh” and latency bounded.

#### 6. Do's and Don'ts
- ✅ Do keep PyAudio callback code **non-blocking** and low-allocation.
- ✅ Do use bounded buffers/queues with clear overflow behavior.
- ✅ Do prefer deterministic numpy-based synthetic audio for tests.
- ✅ Do ensure sample-rate assumptions are explicit (capture 16kHz, Gemini playback 24kHz).

- ❌ Don’t allocate large temporary arrays per callback iteration (e.g., avoid `np.where(np.diff(np.sign(...)))`).
- ❌ Don’t call async functions directly from callback threads.
- ❌ Don’t rely on wall-clock time in DSP tests; use frame counts.
- ❌ Don’t silently swallow systematic overflows—increment counters and add observability.

#### 7. Tools & Dependencies
- **NumPy**: primary DSP math and synthetic test signal generation.
- **PyAudio**: low-level capture/playback via callback streams.
- **google-genai SDK**: Gemini Live sessions (`google.genai`, `google.genai.types`).
- **Pydantic / pydantic-settings**: configuration models (`AIConfig`, `AudioConfig`).
- **OpenTelemetry**: tracing + usage telemetry (`core/infra/telemetry.py`).
- **pytest / pytest-asyncio**: unit and async tests.
- **Rust acceleration (`aether_cortex`)**: optional high-performance backend.

**Setup notes:**
- Environment variables are loaded from `.env` via Pydantic settings (`load_config()` supports fallback if `.env` cannot be read).

#### 8. Other Notes
- **Sample rates:**
  - Capture: **16kHz** PCM16 mono.
  - Playback: Gemini output is **24kHz** PCM16; playback resamples to 16kHz for AEC reference via linear interpolation.
- **AEC behavior:**
  - `DynamicAEC` adapts on block boundaries (filter-length blocks). Tests must run enough frames to fill blocks.
- **State sharing:**
  - `audio_state` is a shared singleton updated from both callback threads and asyncio tasks; treat it as concurrent state.
- **Performance constraints:**
  - Anything in capture/playback callbacks should be treated as real-time code: no blocking, minimal allocations, and predictable runtime.
