import numpy as np

SAMPLE_RATE = 16000

def _sine(
    freq_hz: float, n: int, amp: float = 0.8, sr: int = SAMPLE_RATE
) -> np.ndarray:
    t = np.arange(n, dtype=np.float64) / sr
    return amp * np.sin(2.0 * np.pi * freq_hz * t)

n = 4096
delay = 200

x = _sine(440.0, n)
y = np.zeros_like(x)
y[delay:] = x[: n - delay]

def improved_gcc_phat(x, y, max_delay=1000):
    n = min(len(x), len(y))
    x = x[:n]
    y = y[:n]
    n_fft = 2 ** int(np.ceil(np.log2(2 * n - 1)))
    X = np.fft.fft(x, n_fft)
    Y = np.fft.fft(y, n_fft)
    R = X * np.conj(Y)
    R_magnitude = np.abs(R)
    eps = 1e-10
    R_phat = R / (R_magnitude + eps)
    cc = np.fft.ifft(R_phat)
    cc = np.real(cc)

    # Actually need to concatenate the ends if we don't use fftshift
    # because negative delays are at the end of the array
    cc = np.concatenate((cc[-max_delay:], cc[:max_delay+1]))

    peak_idx = np.argmax(np.abs(cc))
    delay_est = peak_idx - max_delay
    return delay_est

print("Improved:", improved_gcc_phat(x, y))
