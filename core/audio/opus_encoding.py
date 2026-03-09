import logging
import numpy as np

try:
    import opuslib
    HAS_OPUS = True
except ImportError:
    HAS_OPUS = False

logger = logging.getLogger("AetherOS.Audio.Opus")

class OpusEncoder:
    """
    Wrapper for Opus encoding (RFC 6716).
    Optimized for Voice/VOIP at 24kHz or 168kHz.
    """

    def __init__(self, sample_rate: int = 16000, channels: int = 1, bitrate: int = 32000):
        self.sample_rate = sample_rate
        self.channels = channels
        self.bitrate = bitrate
        self._encoder = None

        if HAS_OPUS:
            try:
                # APPLICATION_VOIP for low-latency
                self._encoder = opuslib.Encoder(sample_rate, channels, 'voip')
                self._encoder.bitrate = bitrate
                logger.info(f"Opus Encoder initialized: {sample_rate}Hz, {bitrate}bps")
            except Exception as e:
                logger.warning(f"Failed to initialize Opus encoder: {e}. Falling back to PCM.")
        else:
            logger.warning("Opus library not found. Using raw PCM fallback.")

    def encode(self, pcm_chunk: bytes) -> bytes:
        """Encode PCM bytes to Opus packet."""
        if not self._encoder:
            return pcm_chunk # Fallback to PCM

        try:
            # Opus expects frames of 2.5, 5, 10, 20, 40, 60 ms
            # For 16kHz, 20ms = 320 samples
            # Assuming incoming chunk matches the expected frame size
            return self._encoder.encode(pcm_chunk, self.sample_rate // 50) 
        except Exception as e:
            logger.error(f"Opus encode error: {e}")
            return pcm_chunk

class OpusDecoder:
    """Wrapper for Opus decoding."""
    def __init__(self, sample_rate: int = 16000, channels: int = 1):
        self.sample_rate = sample_rate
        self.channels = channels
        self._decoder = None

        if HAS_OPUS:
            try:
                self._decoder = opuslib.Decoder(sample_rate, channels)
                logger.info(f"Opus Decoder initialized: {sample_rate}Hz")
            except Exception as e:
                logger.warning(f"Failed to initialize Opus decoder: {e}")
        else:
            logger.warning("Opus library not found. Returning raw data.")

    def decode(self, opus_packet: bytes) -> bytes:
        if not self._decoder:
            return opus_packet

        try:
            return self._decoder.decode(opus_packet, self.sample_rate // 50)
        except Exception as e:
            logger.error(f"Opus decode error: {e}")
            return b"\x00" * (self.sample_rate // 50 * 2) # Return silence on error
