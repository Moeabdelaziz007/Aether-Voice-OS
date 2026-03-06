"""
Demo for Dynamic Acoustic Echo Cancellation (AEC)

This example generates a simulated far-end (speaker) signal and a
near-end (microphone) signal that contains an echoed version of the
far-end plus local noise. It then processes it frame-by-frame through
the DynamicAEC to demonstrate echo cancellation and ERLE tracking.
"""

import time

import numpy as np

from core.audio.dynamic_aec import DynamicAEC


def run_aec_demo():
    print("Initializing Dynamic AEC...")
    sample_rate = 16000
    frame_size = 512
    aec = DynamicAEC(
        sample_rate=sample_rate,
        frame_size=frame_size,
        filter_length_ms=100.0,
        step_size=0.5,
    )

    # Generate 5 seconds of simulated audio
    duration = 5.0
    num_samples = int(duration * sample_rate)

    # Far-end: 440Hz Sine wave (AI talking)
    t = np.linspace(0, duration, num_samples, endpoint=False)
    far_end_full = (np.sin(2 * np.pi * 440 * t) * 10000).astype(np.int16)

    # Near-end: Echo of Far-end (delayed by 50ms, attenuated) + random noise (user room)
    delay_samples = int(0.05 * sample_rate)
    echo = np.zeros_like(far_end_full)
    echo[delay_samples:] = (far_end_full[:-delay_samples] * 0.4).astype(np.int16)
    noise = np.random.normal(0, 500, num_samples).astype(np.int16)
    near_end_full = echo + noise

    print(f"Processing {duration}s of audio in {frame_size}-sample chunks...")

    start_time = time.time()
    for i in range(0, num_samples - frame_size, frame_size):
        far_chunk = far_end_full[i : i + frame_size]
        near_chunk = near_end_full[i : i + frame_size]

        cleaned, state = aec.process_frame(near_chunk, far_chunk)

        # Print progress every second of audio
        if i % sample_rate == 0 and i > 0:
            print(
                f"Processed {i / sample_rate:.1f}s | "
                f"ERLE: {state.erle_db:.1f}dB | "
                f"Converged: {state.converged} | "
                f"Delay Est: {state.estimated_delay_ms:.1f}ms"
            )

    elapsed = time.time() - start_time
    print(
        f"Finished processing in {elapsed:.2f}s ({duration / elapsed:.1f}x real-time)"
    )


if __name__ == "__main__":
    run_aec_demo()
