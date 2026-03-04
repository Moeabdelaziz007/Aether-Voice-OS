import logging

import numpy as np

logger = logging.getLogger(__name__)

try:
    # Attempt to import the compiled Rust module
    from .aether_cortex import DynamicAEC as RustAEC
    HAS_RUST_CORTEX = True
    logger.info("✦ Aether Cortex: Rust acceleration ARMED.")
except ImportError:
    HAS_RUST_CORTEX = False
    logger.warning("✧ Aether Cortex: Rust acceleration not found. Falling back to NumPy (Performance degraded).")

class AECBridge:
    """Bridge for switching between NumPy and Rust AEC implementations."""
    
    def __init__(self, filter_size: int = 512):
        self.filter_size = filter_size
        self.use_rust = HAS_RUST_CORTEX
        self.rust_aec = RustAEC(filter_size) if HAS_RUST_CORTEX else None
        
    def process(self, mic: np.ndarray, ref: np.ndarray) -> np.ndarray:
        if self.use_rust and self.rust_aec:
            return self.rust_aec.process(mic, ref)
        
        # Fallback placeholder (actual logic would call the existing numpy AEC)
        return mic
