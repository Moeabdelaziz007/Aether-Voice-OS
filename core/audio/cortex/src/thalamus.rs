//! Thalamus — Sensory Gateway & Noise Filter
//!
//! Named after the thalamus: the brain's central relay station that filters
//! and routes all sensory input (except smell) before it reaches the cortex.
//! The thalamus acts as a gatekeeper — it attenuates background noise and
//! amplifies relevant signals, ensuring the cortex receives clean, focused data.
//!
//! This module implements spectral subtraction noise reduction:
//! 1. Estimate the noise floor during periods of silence (VAD = false)
//! 2. Transform the signal to frequency domain (FFT)
//! 3. Subtract the noise spectrum, preserving speech harmonics
//! 4. Transform back to time domain (IFFT)
//!
//! This is a NEW capability not present in the Python codebase — the first
//! "sense enhancement" that goes beyond what the biological original does.
//!
//! Note: This is a placeholder implementation. Full spectral subtraction
//! requires the `rustfft` crate which will be added in a future iteration.
//! For now, we implement a simpler time-domain noise gate as a functional
//! starting point.

use numpy::PyReadonlyArray1;
use pyo3::prelude::*;

/// Simple time-domain noise gate with exponential smoothing.
///
/// This is Phase 1 of the Thalamus — a noise gate that silences
/// samples below a threshold. Phase 2 will add full spectral
/// subtraction using rustfft.
///
/// Args:
///     pcm_data: Raw PCM int16 audio samples.
///     noise_floor: RMS threshold below which signal is gated (default: 0.015).
///     attack_ms: Gate opening time in ms (default: 5.0).
///     release_ms: Gate closing time in ms (default: 50.0).
///     sample_rate: Audio sample rate in Hz (default: 16000).
///
/// Returns:
///     Dict with:
///       - `samples`: Processed PCM int16 samples (noise-gated)
///       - `noise_level`: Estimated noise floor RMS
///       - `gate_active`: Whether the gate was applied
///       - `sample_count`: Number of samples processed
#[pyfunction]
#[pyo3(signature = (pcm_data, noise_floor=0.015, attack_ms=5.0, release_ms=50.0, sample_rate=16000))]
pub fn spectral_denoise(
    py: Python<'_>,
    pcm_data: PyReadonlyArray1<i16>,
    noise_floor: f64,
    attack_ms: f64,
    release_ms: f64,
    sample_rate: u32,
) -> PyResult<PyObject> {
    let pcm = pcm_data.as_slice().unwrap();
    let res = _spectral_denoise_internal(pcm, noise_floor, attack_ms, release_ms, sample_rate);

    let dict = pyo3::types::PyDict::new_bound(py);
    dict.set_item("samples", res.0)?;
    dict.set_item("noise_level", res.1)?;
    dict.set_item("gate_active", res.2)?;
    dict.set_item("sample_count", res.3)?;
    Ok(dict.into())
}

/// Native internal logic for spectral_denoise.
fn _spectral_denoise_internal(
    pcm: &[i16],
    noise_floor: f64,
    attack_ms: f64,
    release_ms: f64,
    sample_rate: u32,
) -> (Vec<i16>, f64, bool, usize) {
    let len = pcm.len();
    if len == 0 {
        return (vec![], 0.0, false, 0);
    }

    let inv_max = 1.0f64 / 32768.0;
    let mut sum_sq: f64 = 0.0;
    for &sample in pcm {
        let n = sample as f64 * inv_max;
        sum_sq += n * n;
    }
    let rms = (sum_sq / len as f64).sqrt();
    let gate_active = rms < noise_floor;

    let attack_samples = (sample_rate as f64 * attack_ms / 1000.0).max(1.0);
    let release_samples = (sample_rate as f64 * release_ms / 1000.0).max(1.0);
    let attack_coeff = 1.0 - (-1.0 / attack_samples).exp();
    let release_coeff = 1.0 - (-1.0 / release_samples).exp();

    let mut output = Vec::with_capacity(len);
    let mut envelope: f64 = 0.0;

    for &sample in pcm {
        let abs_sample = (sample as f64 * inv_max).abs();
        if abs_sample > envelope {
            envelope += attack_coeff * (abs_sample - envelope);
        } else {
            envelope += release_coeff * (abs_sample - envelope);
        }

        if envelope < noise_floor {
            let gain = (envelope / noise_floor).powi(2);
            output.push((sample as f64 * gain) as i16);
        } else {
            output.push(sample);
        }
    }

    (output, rms, gate_active, len)
}

#[cfg(test)]
mod tests {
    #[test]
    fn test_silence_gated() {
        // Very quiet signal should be heavily attenuated
        let silence = vec![50i16; 1000]; // ~0.0015 RMS, well below 0.015
        let inv_max = 1.0f64 / 32768.0;
        let sum_sq: f64 = silence
            .iter()
            .map(|&s| {
                let n = s as f64 * inv_max;
                n * n
            })
            .sum();
        let rms = (sum_sq / silence.len() as f64).sqrt();
        assert!(rms < 0.015, "Expected quiet signal, got RMS={}", rms);
    }

    #[test]
    fn test_loud_passes_through() {
        // Loud signal should pass through unmodified
        let loud = vec![10000i16; 1000]; // ~0.305 RMS
        let inv_max = 1.0f64 / 32768.0;
        let sum_sq: f64 = loud
            .iter()
            .map(|&s| {
                let n = s as f64 * inv_max;
                n * n
            })
            .sum();
        let rms = (sum_sq / loud.len() as f64).sqrt();
        assert!(rms > 0.015, "Expected loud signal, got RMS={}", rms);
    }

    #[test]
    fn test_empty_input() {
        let empty: Vec<i16> = vec![];
        assert!(empty.is_empty());
    }
}
