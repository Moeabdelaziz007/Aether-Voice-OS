"""Aether Voice OS — Legacy Dynamic AEC Entry Point."""
from core.audio.aec.engine import AECState, DynamicAEC
from core.audio.aec.filters import FrequencyDomainNLMS
from core.audio.aec.detectors import DoubleTalkDetector, DelayEstimator
from core.audio.aec.buffer import BoundedBuffer
