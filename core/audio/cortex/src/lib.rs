use ndarray::Array1;
use numpy::{PyArray1, PyReadonlyArray1};
use pyo3::prelude::*;
use pyo3::types::PyDict;

#[pyclass]
struct CochlearBuffer {
    capacity: usize,
    buffer: Vec<i16>,
    write_pos: usize,
    count: usize,
}

#[pymethods]
impl CochlearBuffer {
    #[new]
    fn new(capacity: usize) -> Self {
        CochlearBuffer {
            capacity,
            buffer: vec![0; capacity],
            write_pos: 0,
            count: 0,
        }
    }

    fn write(&mut self, data: Vec<i16>) {
        let n = data.len();
        if n >= self.capacity {
            self.buffer.copy_from_slice(&data[n - self.capacity..]);
            self.write_pos = 0;
            self.count = self.capacity;
        } else {
            for val in data {
                self.buffer[self.write_pos] = val;
                self.write_pos = (self.write_pos + 1) % self.capacity;
                self.count = std::cmp::min(self.count + 1, self.capacity);
            }
        }
    }

    fn read_last(&self, n: usize) -> Vec<i16> {
        let n = std::cmp::min(n, self.count);
        if n == 0 {
            return vec![];
        }
        let mut result = Vec::with_capacity(n);
        let start = (self.write_pos + self.capacity - n) % self.capacity;
        if start + n <= self.capacity {
            result.extend_from_slice(&self.buffer[start..start + n]);
        } else {
            result.extend_from_slice(&self.buffer[start..]);
            result.extend_from_slice(&self.buffer[..n - (self.capacity - start)]);
        }
        result
    }

    fn clear(&mut self) {
        self.write_pos = 0;
        self.count = 0;
    }

    fn count(&self) -> usize {
        self.count
    }
}

#[pyfunction]
fn energy_vad(audio: PyReadonlyArray1<f32>, threshold: f32) -> bool {
    let array = audio.as_array();
    if array.is_empty() {
        return false;
    }
    let sum_sq: f32 = array.iter().map(|&x| x * x).sum();
    let mean_sq = sum_sq / array.len() as f32;
    mean_sq.sqrt() > threshold
}

#[pyfunction]
fn find_zero_crossing(audio: PyReadonlyArray1<f32>) -> usize {
    let array = audio.as_array();
    if array.len() < 2 {
        return 0;
    }
    let mut crossings = 0;
    for i in 0..array.len() - 1 {
        if (array[i] >= 0.0 && array[i + 1] < 0.0) || (array[i] < 0.0 && array[i + 1] >= 0.0) {
            crossings += 1;
        }
    }
    crossings
}

#[pyfunction]
fn spectral_denoise<'py>(
    py: Python<'py>,
    audio: PyReadonlyArray1<i16>,
    noise_floor: f32,
) -> PyResult<&'py PyDict> {
    let array = audio.as_array();
    let n = array.len();

    if n == 0 {
        let dict = PyDict::new(py);
        let empty_samples: Vec<i16> = Vec::new();
        dict.set_item("samples", PyArray1::from_slice(py, &empty_samples))?;
        dict.set_item("noise_level", 0.0)?;
        dict.set_item("gate_active", true)?;
        dict.set_item("sample_count", 0)?;
        return Ok(dict);
    }

    let sum_sq: f32 = array.iter().map(|&x| (x as f32).powi(2)).sum();
    let energy = (sum_sq / n as f32).sqrt() / 32768.0;
    let gate_active = energy < noise_floor;

    let samples = if gate_active {
        let gain = if noise_floor > 0.0 {
            (energy / noise_floor).powi(2)
        } else {
            0.0
        };
        array
            .iter()
            .map(|&x| (x as f32 * gain) as i16)
            .collect::<Vec<i16>>()
    } else {
        array.to_vec()
    };

    let dict = PyDict::new(py);
    dict.set_item("samples", PyArray1::from_slice(py, &samples))?;
    dict.set_item("noise_level", energy)?;
    dict.set_item("gate_active", gate_active)?;
    dict.set_item("sample_count", n)?;

    Ok(dict)
}

#[pyclass]
struct DynamicAEC {
    filter_size: usize,
    weights: Array1<f32>,
}

#[pymethods]
impl DynamicAEC {
    #[new]
    fn new(filter_size: usize) -> Self {
        DynamicAEC {
            filter_size,
            weights: Array1::zeros(filter_size),
        }
    }

    fn process<'py>(
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

#[pymodule]
fn aether_cortex(_py: Python<'_>, m: &PyModule) -> PyResult<()> {
    m.add_class::<CochlearBuffer>()?;
    m.add_class::<DynamicAEC>()?;
    m.add_function(wrap_pyfunction!(energy_vad, m)?)?;
    m.add_function(wrap_pyfunction!(find_zero_crossing, m)?)?;
    m.add_function(wrap_pyfunction!(spectral_denoise, m)?)?;
    Ok(())
}
