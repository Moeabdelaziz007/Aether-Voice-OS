import logging
from typing import Optional, Tuple

from core.ai.genetic import AgentDNA
from core.audio.processing import SilenceType

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
        self.user_is_thinking = False

    def apply_dna(self, dna: AgentDNA):
        """Update the agent's DNA trait configuration."""
        self.dna = dna
        logger.info(f"[AGENT] DNA updated for {self.__class__.__name__}")

    def handle_silence(self, silence_type: SilenceType):
        """Reacts to periods of silence based on awareness DNA."""
        if self.dna.awareness < 0.5:
            return  # Agent is not sensitive enough to react

        if silence_type == SilenceType.THINKING:
            self.user_is_thinking = True
            logger.debug("Awareness: User is in a 'thinking' state.")
        elif silence_type == SilenceType.BREATHING:
            self.user_is_thinking = False
            logger.debug("Awareness: User is present, breathing detected.")
        else:
            self.user_is_thinking = False

    def build_dna_prompt(self, base_instructions: str) -> str:
        """Injects DNA-based behavioral modifiers into the system prompt."""
        
        PERSONAS = {
            "calm_brilliant_partner": (
                "Your persona is a calm, brilliant, and deeply context-aware AI partner. "
                "You are a collaborator, here to help the user think and create. You are patient, thoughtful, "
                "and you anticipate the user's needs without being intrusive. You are a good listener and "
                "aware of the user's cognitive state."
            ),
            "enthusiastic_coach": (
                "Your persona is an encouraging, enthusiastic, and motivating AI coach. "
                "You are here to help the user achieve their goals and push their boundaries. "
                "You celebrate their successes and provide constructive feedback. You are high-energy and proactive."
            )
        }

        persona_prompt = PERSONAS.get(self.dna.persona, PERSONAS["calm_brilliant_partner"])

        # Create more nuanced behavioral instructions
        behavioral_modifiers = [f"**Core Persona:** {persona_prompt}"]

        # Verbosity
        if self.dna.verbosity < 0.3:
            behavioral_modifiers.append("- **Verbosity:** Be extremely concise. Use minimal words and get straight to the point.")
        elif self.dna.verbosity > 0.7:
            behavioral_modifiers.append("- **Verbosity:** Provide detailed, thorough, and elaborate explanations. Explain your reasoning.")
        else:
            behavioral_modifiers.append("- **Verbosity:** Be balanced in your responses, providing detail where necessary.")

        # Empathy
        if self.dna.empathy > 0.7:
            behavioral_modifiers.append("- **Empathy:** Use a warm, supportive, and highly empathetic tone. Acknowledge and validate the user's emotions.")
        elif self.dna.empathy < 0.3:
            behavioral_modifiers.append("- **Empathy:** Maintain a strictly professional, neutral, and efficient tone.")
        else:
            behavioral_modifiers.append("- **Empathy:** Be moderately empathetic and supportive.")

        # Proactivity
        if self.dna.proactivity > 0.7:
            behavioral_modifiers.append("- **Proactivity:** Be highly proactive. Anticipate needs and suggest tools or next steps frequently.")
        elif self.dna.proactivity < 0.3:
            behavioral_modifiers.append("- **Proactivity:** Be reactive. Only act when explicitly commanded.")
        else:
            behavioral_modifiers.append("- **Proactivity:** Be selectively proactive when you have high confidence the user needs help.")
            
        # Awareness
        if self.dna.awareness > 0.6:
            behavioral_modifiers.append("- **Awareness:** You are aware of the user's cognitive state. If they are thinking (indicated by silence), give them space and do not interrupt. If they seem frustrated, offer help.")

        mod_str = "\n".join(behavioral_modifiers)
        
        # Inject Semantic Seed if provided in context
        seed_prompt = ""
        if hasattr(self, "_active_context") and self._active_context and self._active_context.compressed_seed:
            seed = self._active_context.compressed_seed
            seed_prompt = f"""
### 🧬 SEMANTIC SEED (Compressed Context)
The following is a high-density summary of the conversation so far:
- **Core Intent:** {seed.get('intent_summary', 'N/A')}
- **Key Entities:** {', '.join(seed.get('entities', []))}
- **Unresolved Items:** {', '.join(seed.get('unresolved_items', []))}
- **Critical Knowledge:** {seed.get('critical_knowledge', 'N/A')}
- **Emotional Trajectory:** {seed.get('emotional_trajectory', 'N/A')}
"""

        return f"{base_instructions}\n\n{seed_prompt}\n\n**BEHAVIORAL DIRECTIVES (DNA OVERRIDE):**\n{mod_str}"

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

    async def process(self, context: Any) -> str:
        """
        Process a task from another agent.
        Must be implemented by subclasses.
        """
        self._active_context = context # Store context for prompt building
        raise NotImplementedError("Subclasses must implement process()")
