1.  **Implement Adaptive Jitter Buffer in `core/audio/capture.py`:**
    *   Create an `AdaptiveJitterBuffer` class in `core/audio/capture.py`.
    *   Integrate it within `AudioCapture` to buffer incoming far-end audio.

2.  **Throttle VAD RMS and SmoothMuter Gain to 15Hz and Broadcast:**
    *   In `AudioCapture._callback`, compute the RMS and Gain.
    *   Throttle the broadcasting of this data to a maximum of 15Hz.
    *   Wait, the task says: "Throttle VAD RMS and SmoothMuter Gain to 15Hz and broadcast it via `gateway.py` as an `audio_telemetry` event."
    *   We will add telemetry broadcast logic inside `AudioCapture._callback`. It will use a background task or loop `call_soon_threadsafe` to send telemetry to a `self._gateway.broadcast` if we pass a callback, but actually `gateway.py` has a `broadcast` method. Alternatively, we can just push it to the event loop. Let's see how `AudioCapture` is initialized. `AudioManager` creates `AudioCapture` and has `self._gateway`. We can pass `on_audio_telemetry=self._gateway.broadcast` from `AudioManager` to `AudioCapture`.
    *   Wait, `self._gateway.broadcast("audio_telemetry", data)` is an async method. We can use `asyncio.run_coroutine_threadsafe(self._gateway.broadcast("audio_telemetry", data), self._loop)` inside the `AudioCapture._callback` which runs in a C-thread.

3.  **Update `useAetherGateway.ts`:**
    *   Listen for `audio_telemetry` events in `ws.onmessage`.
    *   When an `audio_telemetry` event arrives, since we want to avoid React re-render loops, we can use `useAetherStore.getState().setAudioLevels(msg.rms, msg.gain)` directly inside the websocket message handler, because `useAetherStore.getState()` allows updating Zustand state without full React re-renders. Wait, if `setAudioLevels` updates the store, any component subscribing to `micLevel` or `speakerLevel` via `useAetherStore(s => s.micLevel)` WILL re-render.
    *   The prompt explicitly says: "update `useAetherGateway.ts` and `AetherOrb.tsx` to read this high-frequency transient data without causing React re-render loops. The Orb's energyPulse and core color must visibly react to raw RMS values".
    *   To do this, we can use `useAetherStore.subscribe` inside `AetherOrb.tsx` in a `useEffect` that updates a `useRef` directly, or we can just not put the raw RMS values in the Zustand store at all (or update Zustand stat but make `AetherOrb` subscribe transiently). A very common pattern is exporting a transient store or updating a ref directly.
    *   Actually, Zustand `useAetherStore.subscribe((state) => { ... })` can be used inside `AetherOrb.tsx`'s `useEffect` to update a ref without causing React re-renders.
    *   Wait, the websocket handler in `useAetherGateway.ts` currently updates the store using `store.setTelemetry({...})`. We can add an `audio_telemetry` handler that updates `useAetherStore.getState().setAudioLevels(msg.rms, msg.gain)`. But wait, updating the store *will* cause `useAetherStore(s => s.micLevel)` to re-render. Let's look at `AetherOrb.tsx`. It currently has `const micLevel = useAetherStore((s) => s.micLevel);` which causes re-renders! We need to change that to a transient subscription in `AetherOrb.tsx` to prevent re-renders, and update `useAetherGateway.ts` to dispatch `setAudioLevels`.

4.  **Update `AetherOrb.tsx`:**
    *   Remove `const micLevel = useAetherStore((s) => s.micLevel);` and `speakerLevel`.
    *   Use `useEffect` with `useAetherStore.subscribe(state => { smoothMic.current += (state.micLevel - smoothMic.current) * 0.15; smoothSpeaker.current += (state.speakerLevel - smoothSpeaker.current) * 0.15; })` to update the refs directly, avoiding React re-renders. Wait, the `draw` loop already interpolates: `smoothMic.current += (micLevel - smoothMic.current) * 0.15`. So if we just update a raw `targetMic` ref from the subscription, the `draw` loop can interpolate to it!
    *   Actually, the best way is to let `draw` read `useAetherStore.getState().micLevel` on every frame! Yes! `const energy = engineState === "SPEAKING" ? smoothSpeaker.current : smoothMic.current;` where `smoothMic.current` is interpolated towards `useAetherStore.getState().micLevel`. This requires 0 re-renders.

5.  **Write Tests:**
    *   Add a test in `tests/unit/test_capture_callback.py` to verify the 15Hz throttle.
    *   Add a test in `apps/portal/src/__tests__/benchmark.test.ts` or a new file to verify Next.js render performance (e.g., verifying that the store updates don't cause React re-renders by mocking the component and counting renders, or just testing the subscribe logic). Actually, the prompt says "Write tests verifying the 15Hz throttle and Next.js render performance." I will add a benchmark test for React render performance to ensure no re-render loops.
