import logging
from typing import Optional, Tuple

from core.ai.genetic import AgentDNA

logger = logging.getLogger(__name__)


class VoiceAgent:
    """
    Handles raw audio streams, latency tracking, and baseline emotion extraction.
    Designed for Native Audio Gemini API.
    """

    def __init__(self, dna: Optional[AgentDNA] = None):
        self.is_streaming = False
        self.current_latency_ms = 0
        self.dna = dna or AgentDNA()

    def apply_dna(self, dna: AgentDNA):
        """Update the agent's DNA trait configuration."""
        self.dna = dna
        logger.info("[AGENT] DNA updated: %s", self.__class__.__name__)

    def build_dna_prompt(self, base_instructions: str) -> str:
        """Injects DNA-based behavioral modifiers into the system prompt."""
        modifiers = []

        # Verbosity
        if self.dna.verbosity < 0.3:
            modifiers.append("Be extremely concise. Use minimal words.")
        elif self.dna.verbosity > 0.7:
            modifiers.append("Provide detailed explanations and elaborations.")

        # Empathy
        if self.dna.empathy > 0.8:
            modifiers.append(
                "Use a warm, highly empathetic tone. Validate user emotions."
            )
        elif self.dna.empathy < 0.2:
            modifiers.append(
                "Maintain a strictly professional, robotic, and efficient tone."
            )

        # Proactivity
        if self.dna.proactivity > 0.7:
            modifiers.append(
                "Be proactive. Anticipate needs and suggest tool usage early."
            )

        mod_str = "\n".join(modifiers)
        return f"{base_instructions}\n\nBEHAVIORAL DNA OVERRIDE:\n{mod_str}"

    def stream_audio(self, _pcm_chunk: bytes):
        """
        Processes incoming PCM audio. In a real environment, routes to Gemini.
        """
        self.is_streaming = True
        # Emulate processing latency
        self.current_latency_ms = 180

    def extract_emotion(self, _pcm_chunk: bytes) -> Tuple[float, float]:
        """
        Returns (valence, arousal) based on the acoustic chunk.
        Valence: -1.0 (Negative) to 1.0 (Positive)
        Arousal: 0.0 (Calm) to 1.0 (Excited)
        """
        # Acoustic extraction placeholder (e.g. RMS mapping or Yamnet)
        valence = -0.5
        arousal = 0.8
        return valence, arousal
