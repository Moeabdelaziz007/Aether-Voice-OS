import logging

from core.ai.agents.bridge import ADKGeminiBridge
from core.ai.agents.orchestrator import MultiAgentOrchestrator
from core.ai.agents.proactive import (
    CodeAwareProactiveAgent,
    ProactiveInterventionEngine,
)
from core.ai.agents.voice_agent import VoiceAgent
from core.analytics.latency import LatencyOptimizer

logger = logging.getLogger(__name__)


class IntegratedAetherAgent:
    """
    The master wrapper assembling the entire Aether Phase 6 pipeline:
    - VoiceAgent (streaming + basic extraction)
    - ProactiveInterventionEngine (frustration checks)
    - CodeAwareProactiveAgent (AST / code contextualizing)
    - ADKGeminiBridge (ADK tool orchestration)
    - LatencyOptimizer (tracking)
    """

    def __init__(self):
        logger.info("Initializing Integrated Aether Agent...")
        self.orchestrator = MultiAgentOrchestrator()

        self.voice_agent = VoiceAgent()
        self.proactive_engine = ProactiveInterventionEngine(cooldown_minutes=5)
        self.code_agent = CodeAwareProactiveAgent()

        # Register code agent to the orchestrator for tool routing
        self.orchestrator.register_agent(self.code_agent)

        self.bridge = ADKGeminiBridge(self.orchestrator)
        self.latency_optim = LatencyOptimizer()

    def process_audio_chunk(self, pcm_chunk: bytes):
        """
        Main pipeline entry point for streaming audio
        """
        # 1. Provide chunk to VoiceAgent
        self.voice_agent.stream_audio(pcm_chunk)

        # 2. Extract Acoustic Emotion
        valence, arousal = self.voice_agent.extract_emotion(pcm_chunk)

        # 3. Check for proactive triggers
        if self.proactive_engine.should_intervene(valence, arousal):
            # 4. Integrate codebase context
            mock_code = "def parse_data(val):\n    return val * 2"  # Mock file read
            insight = self.code_agent.get_contextual_help(mock_code)

            # 5. Formulate intervention
            msg = self.proactive_engine.generate_empathetic_message()
            logger.info(f"PROACTIVE BARGE-IN: {msg} | Context: {insight}")

        # 6. Record Pipeline operation latency
        # (Assuming the operation took voice_agent.current_latency_ms)
        self.latency_optim.record_latency(self.voice_agent.current_latency_ms)

    def shutdown(self):
        self.latency_optim.log_metrics()
        logger.info("Integrated Aether Agent shut down.")
