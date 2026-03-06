# Voice + Live Voice: Quality and Speed Recommendations

## Better Sound Quality

1. **Adaptive noise profiling per environment**
   - Capture a 2-3 second baseline noise profile at session start.
   - Continuously update profile in low-speech windows to improve denoise stability.
2. **Multi-band dynamics chain**
   - Add a lightweight compressor/limiter for 200-3.5kHz speech band while keeping low-latency.
   - Keep peak limiter at output stage to avoid clipping on bursty TTS segments.
3. **Short lookahead de-esser for harsh sibilance**
   - Apply only to synthesized playback path to keep user microphone path natural.
4. **Comfort noise injection during gate silence**
   - When gate closes aggressively, add very low-level comfort noise to avoid perceptual "dead air" artifacts.

## Faster Live Voice Response

1. **Early partial hypothesis routing**
   - Forward partial intent/transcript as soon as confidence threshold is crossed to reduce perceived latency.
2. **Queue pressure backoff policy**
   - Dynamically lower output chunk size or skip low-priority commentary when `gemini_output_queue_drops` rises.
3. **Frame-size adaptation (10/20/30ms)**
   - Under CPU pressure, increase frame size to reduce callback overhead.
   - Under interruption-heavy sessions, decrease frame size for snappier barge-in.
4. **Pre-warmed tool pathways**
   - Keep high-frequency tools hot (cached auth/context) to reduce function-call turnaround.

## Creative Ideas

1. **Emotion-aware response voicing**
   - Modulate TTS prosody and pacing from paralinguistic confidence signals.
2. **"Whisper mode" collaboration**
   - Auto-switch to low-volume, concise responses in meetings using environmental speech density.
3. **Contextual sonic earcons**
   - Use tiny branded non-verbal cues (success, waiting, handoff) to reduce cognitive load.
4. **Adaptive persona timbre presets**
   - Let users pick coding/deep-focus/coach styles that alter cadence and verbosity.

## Validation Targets (Suggested)

- End-to-end P95 latency: **< 220 ms**
- Barge-in reaction: **< 120 ms** to mute/drain
- Output queue drops: **< 0.1%** over 30-minute session
- VAD false-positive rate in silence: **< 5%**
- Noisy speech detection rate (15 dB SNR): **> 70%**
