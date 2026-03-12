import numpy as np
import logging

logger = logging.getLogger(__name__)

class FrequencyDomainNLMS:
    """Frequency-domain Normalized Least Mean Squares adaptive filter."""
    def __init__(self, filter_length: int = 1024, step_size: float = 0.5, regularization: float = 1e-4, leakage: float = 0.999) -> None:
        self.filter_length = filter_length
        self.step_size = step_size
        self.regularization = regularization
        self.leakage = leakage
        self.block_size = filter_length
        self.n_fft = 2 * filter_length
        self.W = np.zeros(self.n_fft // 2 + 1, dtype=np.complex128)
        self.input_buffer = np.zeros(self.n_fft, dtype=np.float64)
        self.output_buffer = np.zeros(self.block_size, dtype=np.float64)
        self.power_estimate = np.ones(self.n_fft // 2 + 1) * 1e-6
        self.alpha = 0.9
        self._error_full = np.zeros(self.n_fft, dtype=np.float64)

    def process(self, far_end: np.ndarray, near_end: np.ndarray) -> tuple[np.ndarray, np.ndarray]:
        far_end = np.asarray(far_end).flatten()[:self.block_size]
        near_end = np.asarray(near_end).flatten()[:self.block_size]
        self.input_buffer[:self.block_size] = self.input_buffer[self.block_size:]
        self.input_buffer[self.block_size:] = far_end
        X = np.fft.rfft(self.input_buffer)
        Y = self.W * X
        y_full = np.fft.irfft(Y)
        estimated_echo = y_full[self.block_size:]
        error_signal = near_end - estimated_echo
        self._error_full.fill(0.0)
        self._error_full[self.block_size:] = error_signal
        E = np.fft.rfft(self._error_full)
        X_mag_sq = np.abs(X) ** 2
        self.power_estimate = self.alpha * self.power_estimate + (1 - self.alpha) * X_mag_sq
        mu = self.step_size / (self.power_estimate + self.regularization)
        gradient = mu * np.conj(X) * E
        self.W = self.leakage * self.W + gradient
        return error_signal, estimated_echo

    def get_filter_energy(self) -> float:
        time_weights = np.fft.irfft(self.W)
        return float(np.sum(time_weights**2))

    def reset(self) -> None:
        self.W.fill(0)
        self.input_buffer.fill(0)
        self.output_buffer.fill(0)
        self.power_estimate.fill(1e-6)
        self._error_full.fill(0)

    def pre_train(self, far_end_signal: np.ndarray, near_end_signal: np.ndarray, iterations: int = 3) -> float:
        if len(far_end_signal) < self.block_size * 2: return 0.0
        total_erle = []
        for _ in range(iterations):
            for i in range(0, len(far_end_signal) - self.block_size, self.block_size):
                far_block, near_block = far_end_signal[i:i + self.block_size], near_end_signal[i:i + self.block_size]
                error, _ = self.process(far_block, near_block)
                echo_power, error_power = np.mean(near_block**2), np.mean(error**2)
                if error_power > 1e-10: total_erle.append(10 * np.log10(echo_power / error_power))
        avg_erle = np.mean(total_erle) if total_erle else 0.0
        logger.info(f"AEC pre-training complete: ERLE={avg_erle:.1f}dB")
        return avg_erle
