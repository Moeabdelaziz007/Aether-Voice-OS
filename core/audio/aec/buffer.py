import threading

import numpy as np


class BoundedBuffer:
    """A thread-safe preallocated ring buffer for audio samples."""
    def __init__(self, max_samples: int):
        self.max_samples = max_samples
        self._buf = np.zeros(max_samples, dtype=np.float64)
        self._write = 0
        self._count = 0
        self._lock = threading.Lock()

    def append(self, data: np.ndarray):
        with self._lock:
            n = len(data)
            if n == 0: return
            if n >= self.max_samples:
                data = data[-self.max_samples:]
                n = self.max_samples
            end = self._write + n
            if end <= self.max_samples:
                self._buf[self._write:end] = data
            else:
                first = self.max_samples - self._write
                self._buf[self._write:] = data[:first]
                self._buf[:end - self.max_samples] = data[first:]
            self._write = end % self.max_samples
            self._count = min(self._count + n, self.max_samples)

    def pop_left(self, n: int) -> np.ndarray:
        with self._lock:
            if self._count < n: return np.array([], dtype=np.float64)
            read_start = (self._write - self._count) % self.max_samples
            end = read_start + n
            if end <= self.max_samples:
                extracted = self._buf[read_start:end].copy()
            else:
                first = self.max_samples - read_start
                extracted = np.concatenate([self._buf[read_start:], self._buf[:n - first]])
            self._count -= n
            return extracted

    def clear(self):
        with self._lock:
            self._write = 0
            self._count = 0

    def __len__(self):
        return self._count
