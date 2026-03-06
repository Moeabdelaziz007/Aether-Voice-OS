use pyo3::prelude::*;
use numpy::{PyArray1, PyReadonlyArray1};

/// Calculate Zero-Crossing Rate for a PCM chunk.
/// Returns ZCR as a float between 0.0 and 1.0.
#[pyfunction]
pub fn calculate_zcr(pcm_data: PyReadonlyArray1<i16>) -> f64 {
    let slice = pcm_data.as_slice().unwrap();

    if slice.len() < 2 {
        return 0.0;
    }

    let mut crossings = 0usize;

    for i in 1..slice.len() {
        let prev = slice[i - 1];
        let curr = slice[i];

        // Crossing when sign differs
        if (prev >= 0) != (curr >= 0) {
            crossings += 1;
        }
    }

    crossings as f64 / slice.len() as f64
}
