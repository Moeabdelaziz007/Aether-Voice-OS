import numpy as np
from core.audio.spectral import gcc_phat

def _sine(freq, n, sr=16000):
    t = np.arange(n) / sr
    return np.sin(2 * np.pi * freq * t)

n = 4096
delay = 200

# Create a clear signal, not just a sine wave (which is periodic and gives multiple peaks)
x = np.random.randn(n)
y = np.zeros_like(x)
y[delay:] = x[: n - delay]

est, conf = gcc_phat(x, y, sample_rate=16000, max_delay=1000)
print("est:", est, "conf:", conf)
