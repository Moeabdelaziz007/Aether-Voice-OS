//! Aether Cortex — Neural Signal Layer for Aether Voice OS
//!
//! Consolidated biologically inspired audio DSP engine.

mod axon;
mod cochlea;
mod echo;
mod synapse;
mod thalamus;
mod zcr;

use pyo3::prelude::*;

#[pymodule]
fn aether_cortex(m: &Bound<'_, PyModule>) -> PyResult<()> {
    m.add_class::<cochlea::CochlearBuffer>()?;
    m.add_class::<echo::DynamicAEC>()?;
    m.add_function(wrap_pyfunction!(synapse::energy_vad, m)?)?;
    m.add_function(wrap_pyfunction!(axon::find_zero_crossing, m)?)?;
    m.add_function(wrap_pyfunction!(thalamus::spectral_denoise, m)?)?;
    m.add_function(wrap_pyfunction!(zcr::calculate_zcr, m)?)?;

    m.add("__version__", "0.2.0")?;
    m.add("__backend__", "rust-consolidated")?;

    Ok(())
}
