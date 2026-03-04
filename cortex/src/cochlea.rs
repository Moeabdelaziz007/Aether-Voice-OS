//! Cochlea — The Spiral Buffer
//!
//! Named after the cochlea in the inner ear: a coiled, fluid-filled structure
//! that converts sound vibrations into neural signals. Like its biological
//! counterpart, this buffer continuously receives raw audio waves and provides
//! windowed access to recent history — enabling downstream neurons (VAD,
//! zero-crossing) to analyze the signal without blocking the stream.
//!
//! Key design properties:
//! - O(1) writes via circular indexing (no allocations in hot path)
//! - Power-of-2 capacity for branchless modulo (bitwise AND masking)
//! - Contiguous read_last via single/split memcpy
//! - Fixed memory footprint — no GC pressure, no Python object overhead

use pyo3::prelude::*;

/// CochlearBuffer — lock-free circular buffer for PCM int16 audio.
///
/// Drop-in replacement for `core.audio.processing.RingBuffer`.
/// The capacity is automatically rounded UP to the nearest power of 2
/// for branchless index masking (capacity & (pos - 1) instead of pos % capacity).
#[pyclass]
pub struct CochlearBuffer {
    /// Pre-allocated sample storage
    buf: Vec<i16>,
    /// Bitmask for branchless modulo: capacity - 1 (works because capacity is pow2)
    mask: usize,
    /// Next write position (monotonically increasing, masked on access)
    write_pos: usize,
    /// Number of valid samples currently stored
    count: usize,
    /// Total capacity (always a power of 2)
    capacity: usize,
}

#[pymethods]
impl CochlearBuffer {
    /// Create a new CochlearBuffer with the given capacity.
    ///
    /// The actual capacity is rounded up to the nearest power of 2
    /// for O(1) index computation.
    #[new]
    fn new(capacity_samples: usize) -> Self {
        // Round up to nearest power of 2
        let capacity = capacity_samples.next_power_of_two();
        CochlearBuffer {
            buf: vec![0i16; capacity],
            mask: capacity - 1,
            write_pos: 0,
            count: 0,
            capacity,
        }
    }

    /// Number of valid samples currently in the buffer.
    #[getter]
    fn count(&self) -> usize {
        self.count
    }

    /// Total buffer capacity (power-of-2 aligned).
    #[getter]
    fn capacity(&self) -> usize {
        self.capacity
    }

    /// Append PCM samples to the buffer.
    ///
    /// If data exceeds remaining capacity, oldest samples are overwritten
    /// (circular behavior). This mirrors cochlear hair cells being stimulated
    /// by new vibrations while previous signals decay.
    fn write(&mut self, data: Vec<i16>) {
        let n = data.len();
        if n == 0 {
            return;
        }

        if n >= self.capacity {
            // Data larger than buffer — keep only the last `capacity` samples
            // Like the cochlea discarding old vibrations when overwhelmed
            let start = n - self.capacity;
            self.buf.copy_from_slice(&data[start..]);
            self.write_pos = 0;
            self.count = self.capacity;
            return;
        }

        // Write with wrap-around using branchless masking
        for (i, &sample) in data.iter().enumerate() {
            let pos = (self.write_pos + i) & self.mask;
            self.buf[pos] = sample;
        }

        self.write_pos = (self.write_pos + n) & self.mask;
        self.count = std::cmp::min(self.count + n, self.capacity);
    }

    /// Read the last `n` samples from the buffer (newest data).
    ///
    /// Returns a contiguous copy, safe to use after further writes.
    /// Analogous to reading the most recent neural impulses from the
    /// auditory nerve before they decay.
    fn read_last(&self, n: usize) -> Vec<i16> {
        let n = std::cmp::min(n, self.count);
        if n == 0 {
            return Vec::new();
        }

        let mut result = Vec::with_capacity(n);

        // Calculate start position (n samples before write_pos)
        // Using wrapping arithmetic with mask for branchless indexing
        let start = (self.write_pos.wrapping_sub(n)) & self.mask;

        if start + n <= self.capacity {
            // Contiguous read — single memcpy
            result.extend_from_slice(&self.buf[start..start + n]);
        } else {
            // Split read — wraps around the boundary
            let tail_len = self.capacity - start;
            result.extend_from_slice(&self.buf[start..]);
            result.extend_from_slice(&self.buf[..n - tail_len]);
        }

        result
    }

    /// Reset the buffer without deallocating memory.
    ///
    /// The cochlea remains structurally intact but silent —
    /// ready to receive new signals immediately.
    fn clear(&mut self) {
        self.write_pos = 0;
        self.count = 0;
    }
}

#[cfg(test)]
mod tests {
    use super::*;

    #[test]
    fn test_basic_write_and_read() {
        let mut buf = CochlearBuffer::new(100);
        let data: Vec<i16> = (0..50).collect();
        buf.write(data.clone());
        assert_eq!(buf.count(), 50);
        let result = buf.read_last(50);
        assert_eq!(result, data);
    }

    #[test]
    fn test_wrap_around() {
        let mut buf = CochlearBuffer::new(16); // Rounds to 16 (already pow2)
        buf.write((0..12).collect());
        buf.write((12..24).collect());
        // Buffer is 16 capacity, wrote 24 total → last 16 samples: [8..24)
        let result = buf.read_last(16);
        let expected: Vec<i16> = (8..24).collect();
        assert_eq!(result, expected);
    }

    #[test]
    fn test_overflow_large_write() {
        let mut buf = CochlearBuffer::new(8); // Rounds to 8
        let data: Vec<i16> = (0..20).collect();
        buf.write(data);
        assert_eq!(buf.count(), 8);
        let result = buf.read_last(8);
        let expected: Vec<i16> = (12..20).collect();
        assert_eq!(result, expected);
    }

    #[test]
    fn test_read_more_than_available() {
        let mut buf = CochlearBuffer::new(100);
        buf.write((0..10).collect());
        let result = buf.read_last(50);
        assert_eq!(result.len(), 10);
    }

    #[test]
    fn test_empty_operations() {
        let buf = CochlearBuffer::new(100);
        assert_eq!(buf.read_last(10).len(), 0);

        let mut buf2 = CochlearBuffer::new(100);
        buf2.write(vec![]);
        assert_eq!(buf2.count(), 0);
    }

    #[test]
    fn test_clear() {
        let mut buf = CochlearBuffer::new(100);
        buf.write((0..50).collect());
        buf.clear();
        assert_eq!(buf.count(), 0);
        assert_eq!(buf.read_last(10).len(), 0);
    }

    #[test]
    fn test_power_of_two_rounding() {
        let buf = CochlearBuffer::new(5);
        assert_eq!(buf.capacity(), 8); // 5 → next pow2 = 8

        let buf2 = CochlearBuffer::new(16);
        assert_eq!(buf2.capacity(), 16); // Already pow2

        let buf3 = CochlearBuffer::new(1000);
        assert_eq!(buf3.capacity(), 1024); // 1000 → 1024
    }
}
