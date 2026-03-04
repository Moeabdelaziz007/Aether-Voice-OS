with open("core/audio/capture.py", "r") as f:
    content = f.read()


# Block 1
s1 = """        # How many samples remain to reach the target, based on a linear ramp
        # of length `self._ramp_samples` for a full-scale delta of 1.0.
        delta = target - start
        remaining = int(np.ceil(abs(delta) * self._ramp_samples))

<<<<<<< HEAD
        if ramp_len > 0:
            ramp = np.linspace(
                self._current_gain + step,         # Start one step ahead
                self._current_gain + (step * ramp_len),
                ramp_len,
                dtype=np.float32,
            )

            # If we are finishing the ramp in this chunk, make SURE the last value is exactly target
            if ramp_len == steps_needed:
                ramp[-1] = self._target_gain

            gains[:ramp_len] = ramp
            self._current_gain = float(ramp[-1])

        # Fill the rest of the chunk with whatever the current gain is
        if ramp_len < chunk_len:
            gains[ramp_len:] = self._target_gain
            self._current_gain = self._target_gain

        # Optional: Keep a very tiny snap just for IEEE float math drift
        if abs(self._current_gain - self._target_gain) < 1e-4:
            self._current_gain = self._target_gain
=======
        if remaining <= 0:
            self._current_gain = target
            gains = np.full(chunk_len, target, dtype=np.float32)
        else:
            ramp_len = min(chunk_len, remaining)
>>>>>>> origin/main

            # Use endpoint=True so the last sample of the ramp hits the exact
            # intermediate value (or the target if ramp completes in this chunk).
            ramp = np.linspace(
                start,
                start + delta * (ramp_len / remaining),
                ramp_len,
                dtype=np.float32,
            )"""

r1 = """        # How many samples remain to reach the target, based on a linear ramp
        # of length `self._ramp_samples` for a full-scale delta of 1.0.
        delta = target - start
        remaining = int(np.ceil(abs(delta) * self._ramp_samples))

        if remaining <= 0:
            self._current_gain = target
            gains = np.full(chunk_len, target, dtype=np.float32)
        else:
            ramp_len = min(chunk_len, remaining)

            # Use endpoint=True so the last sample of the ramp hits the exact
            # intermediate value (or the target if ramp completes in this chunk).
            ramp = np.linspace(
                start,
                start + delta * (ramp_len / remaining),
                ramp_len,
                dtype=np.float32,
            )"""

s2 = """<<<<<<< HEAD
        if len(processed_chunk) > 1:
            s1 = processed_chunk[:-1].astype(np.int32)
            s2 = processed_chunk[1:].astype(np.int32)
            signs = s1 * s2
            audio_state.last_zcr = float(np.count_nonzero(signs < 0)) / len(processed_chunk)
=======
        # Low-allocation ZCR (zero-crossing rate) calculation.
        # Count sign changes without building diff/sign/where intermediate arrays.
        if len(processed_chunk) > 1:
            prev = processed_chunk[:-1]
            curr = processed_chunk[1:]
            # Crossing when sign differs or either is zero.
            crossings = ((prev >= 0) != (curr >= 0)) | (prev == 0) | (curr == 0)
<<<<<<< ours
            audio_state.last_zcr = float(np.count_nonzero(crossings) / len(processed_chunk))
>>>>>>> origin/main
=======
            audio_state.last_zcr = float(
                np.count_nonzero(crossings) / len(processed_chunk)
            )
>>>>>>> theirs"""

r2 = """        # Low-allocation ZCR (zero-crossing rate) calculation.
        # Count sign changes without building diff/sign/where intermediate arrays.
        if len(processed_chunk) > 1:
            prev = processed_chunk[:-1]
            curr = processed_chunk[1:]
            # Crossing when sign differs or either is zero.
            crossings = ((prev >= 0) != (curr >= 0)) | (prev == 0) | (curr == 0)
            audio_state.last_zcr = float(
                np.count_nonzero(crossings) / len(processed_chunk)
            )"""

content = content.replace(s1, r1)
content = content.replace(s2, r2)

with open("core/audio/capture.py", "w") as f:
    f.write(content)
