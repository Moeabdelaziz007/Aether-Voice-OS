//! Aether Cortex — Neural Signal Layer for Aether Voice OS
//!
//! Biologically inspired audio DSP engine, built in Rust for zero-latency
//! signal processing. The architecture mirrors the human auditory cortex:
//!
//! - `cochlea`   — Circular buffer (the ear's spiral organ)
//! - `synapse`   — Voice Activity Detection (neural firing threshold)  
//! - `axon`      — Zero-crossing detection (clean signal propagation)
//! - `thalamus`  — Spectral noise reduction (sensory filtering)
//!
//! All modules expose Python bindings via PyO3, serving as drop-in
//! replacements for the NumPy implementations in `core/audio/processing.py`.

mod cochlea;
mod synapse;
mod axon;
mod thalamus;

use pyo3::prelude::*;

/// The Aether Cortex Python module — neural signal processing at native speed.
///
/// Exposes biologically-named DSP primitives that map 1:1 to Python equivalents:
///   - `CochlearBuffer`   → replaces `RingBuffer`
///   - `energy_vad()`     → replaces `energy_vad()`
///   - `find_zero_crossing()` → replaces `find_zero_crossing()`
///   - `spectral_denoise()` → new capability (noise reduction)
#[pymodule]
fn aether_cortex(m: &Bound<'_, PyModule>) -> PyResult<()> {
    // === Cochlea: The Spiral Buffer ===
    m.add_class::<cochlea::CochlearBuffer>()?;

    // === Synapse: Neural Activation (VAD) ===
    m.add_function(wrap_pyfunction!(synapse::energy_vad, m)?)?;

    // === Axon: Clean Signal Propagation (Zero-Crossing) ===
    m.add_function(wrap_pyfunction!(axon::find_zero_crossing, m)?)?;

    // === Thalamus: Sensory Filter (Noise Reduction) ===
    m.add_function(wrap_pyfunction!(thalamus::spectral_denoise, m)?)?;

    // Module metadata
    m.add("__version__", "0.1.0")?;
    m.add("__backend__", "rust")?;

    Ok(())
}
