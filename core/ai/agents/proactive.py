import logging
import time

logger = logging.getLogger(__name__)


class ProactiveInterventionEngine:
    """
    Analyzes emotional state to trigger proactive voice interruptions
    if frustration exceeds thresholds.
    """

    def __init__(self, cooldown_minutes: int = 5):
        self.cooldown_seconds = cooldown_minutes * 60
        self.last_intervention_time = 0
        self.frustration_threshold = 0.75  # Scale 0.0 to 1.0

    def calculate_frustration(self, valence: float, arousal: float) -> float:
        """
        Frustration is typically high arousal combined with negative valence.
        """
        if valence >= 0:
            return 0.0
        # Inverse valence (make it positive magnitude) * arousal
        frustration = abs(valence) * arousal
        return min(1.0, frustration)

    def should_intervene(self, valence: float, arousal: float) -> bool:
        """
        Evaluates current emotion against cooldowns to trigger intervention.
        """
        now = time.time()
        if now - self.last_intervention_time < self.cooldown_seconds:
            return False

        score = self.calculate_frustration(valence, arousal)
        if score > self.frustration_threshold:
            self.last_intervention_time = now
            logger.warning(f"Proactive Trigger Fired! Frustration: {score:.2f}")
            return True

        return False

    def generate_empathetic_message(self) -> str:
        return "أشعر بضيقك في هذا الجزء. هل تريد أن نلقي نظرة معاً على الكود لحلها؟"


class CodeAwareProactiveAgent:
    """
    Hooks into the filesystem or IDE AST to provide context-aware help
    during an intervention.
    """

    def __init__(self):
        pass

    def analyze_ast(self, file_content: str) -> str:
        """
        Placeholder for AST analysis logic (e.g., detecting missing type casts).
        """
        if "parse_data" in file_content and "int(" not in file_content:
            return "Found potential bug in `parse_data`: Missing cast to `int`."
        return "AST appears structurally sound."

    def get_contextual_help(self, file_content: str) -> str:
        bug = self.analyze_ast(file_content)
        return f"Code Context: {bug}"
