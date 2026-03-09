//! Echo — Acoustic Echo Cancellation (AEC)
//!
//! Handles the subtraction of reference audio (AI output) from microphone input.

use ndarray::Array1;
use numpy::{PyArray1, PyReadonlyArray1};
use pyo3::prelude::*;

#[pyclass]
pub struct DynamicAEC {
    pub filter_size: usize,
    pub weights: Array1<f32>,
}

#[pymethods]
impl DynamicAEC {
    #[new]
    pub fn new(filter_size: usize) -> Self {
        DynamicAEC {
            filter_size,
            weights: Array1::zeros(filter_size),
        }
    }

    pub fn process<'py>(
        &mut self,
        py: Python<'py>,
        mic_input: PyReadonlyArray1<f32>,
        _ref_input: PyReadonlyArray1<f32>,
    ) -> PyResult<Py<PyArray1<f32>>> {
        let mic = mic_input.as_array();
        // Simplified passthrough for now, to be expanded with SIMD NLMS
        let output = mic.to_owned();
        Ok(PyArray1::from_array(py, &output).to_owned())
    }
}
