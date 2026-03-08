"""
Aether Voice OS — Genetic Optimizer.

Implements the neuro-evolutionary loop for agent instructions.
Calculates 'fitness' from affective telemetry and uses Gemini to mutate
prompts for better user engagement in future sessions.
"""

from __future__ import annotations

import logging
import random
from dataclasses import asdict, dataclass
from datetime import datetime, timezone
from typing import Any, Dict, Optional

from core.infra.cloud.firebase.interface import FirebaseConnector

logger = logging.getLogger(__name__)


@dataclass
class AgentDNA:
    """
    Encodes the behavior and resource allocation for an Expert Soul.
    """
    # Persona
    persona: str = "calm_brilliant_partner" # Examples: "calm_brilliant_partner", "enthusiastic_coach"

    # Behavioral Traits
    verbosity: float = 0.4  # 0 (concise) to 1 (verbose)
    empathy: float = 0.7  # 0 (robotic) to 1 (warm)
    proactivity: float = 0.6  # 0 (reactive) to 1 (proactive tools)
    awareness: float = 0.6 # 0 (oblivious) to 1 (hyper-aware of user state)

    # Resource Allocation
    latency_budget_ms: int = 500  # Target response time
    audio_fidelity: float = 0.8  # 0.5 to 1.0 (sample rate/codec quality)

    # Tool Selection Biases
    rag_preference: float = 0.7  # Bias towards semantic search
    vision_preference: float = 0.5  # Bias towards screenshots
    code_index_preference: float = 0.8  # Bias towards local index

    # Context Management
    context_window_size: int = 20  # Number of recent turns to weight
    long_term_memory_weight: float = 0.3

    def to_dict(self) -> Dict[str, Any]:
        return asdict(self)

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> AgentDNA:
        return cls(**{k: v for k, v in data.items() if k in cls.__dataclass_fields__})


GENETIC_SYSTEM_PROMPT = """
You are the Aether Evolutionary Engine. Your task is to optimize the
System Instructions for a Voice AI agent based on performance telemetry.

PERFORMANCE TELEMETRY:
- Avg Engagement: {avg_engagement} (0.0 to 1.0)
- Engagement Trend: {trend}
- Avg Pitch: {avg_pitch} Hz

CURRENT SYSTEM INSTRUCTIONS:
{current_instructions}

GOAL:
Analyze why the user might be disengaged (low score/declining trend).
Mutate the instructions to be more empathetic, concise, or interactive
depending on the metrics. If the score is high, perform 'stabilizing selection'
by refining nuances without radical change.

OUTPUT FORMAT:
Return ONLY a JSON object with:
{{
  "mutated_instructions": "string",
  "rationale": "string",
  "version_delta": "float (e.g. 0.1)"
}}
"""


class GeneticOptimizer:
    """
    Orchestrates the evolution of the Agent's soul.
    """

    def __init__(
        self, firebase: FirebaseConnector, api_key: str, ema_alpha: float = 0.3
    ):
        self._firebase = firebase
        self._api_key = api_key
        self._ema_alpha = ema_alpha  # Exponential Moving Average smoothing factor

    async def evolve(
        self, expert_id: str, current_dna: AgentDNA, session_id: Optional[str] = None
    ) -> AgentDNA:
        """
        Perform a mutation or crossover step based on the last session's performance.
        """
        if not self._firebase.is_connected:
            logger.warning("Genetic Optimizer: Firebase offline. Evolution suspended.")
            return current_dna

        # 1. Fetch Fitness Data
        sid = session_id or self._firebase._session_id
        if not sid:
            return current_dna

        report = await self._firebase.get_session_affective_summary(sid)
        if report.get("status") != "success" or "summary" not in report:
            logger.info("Evolution skipped: No telemetry found for session %s", sid)
            return current_dna

        metrics = report["summary"]
        fitness = metrics.get("avg_engagement", 0.5)

        # 2. Heuristic-Based Mutation (First Gen GA)
        # In a full GA, we'd have a population. Here we use 'Stochastic Hill Climbing'
        # which is a simplified (1+1) Evolutionary Strategy.

        new_dna_dict = current_dna.to_dict()
        mutation_rate = 0.1 * (1.1 - fitness)  # Higher mutation if fitness is low

        for key, value in new_dna_dict.items():
            if isinstance(value, float):
                # Apply Gaussian Mutation
                change = random.gauss(0, mutation_rate)
                new_dna_dict[key] = max(0.0, min(1.0, value + change))
            elif isinstance(value, int) and key != "latency_budget_ms":
                # Integer Shift
                change = random.choice([-1, 0, 1])
                new_dna_dict[key] = max(1, value + change)

        mutated_dna = AgentDNA.from_dict(new_dna_dict)

        # 3. Log mutation to Firestore
        await self._firebase.log_event(
            "dna_mutation",
            {
                "expert_id": expert_id,
                "session_id": sid,
                "prev_fitness": fitness,
                "dna_delta": self._calculate_delta(current_dna, mutated_dna),
                "timestamp": datetime.now(timezone.utc).isoformat(),
            },
        )

        return mutated_dna

    async def mutate_mid_session(
        self, current_dna: AgentDNA, trait_name: str, trait_value: float
    ) -> Tuple[AgentDNA, List[str]]:
        """
        Performs high-speed, incremental mutation based on real-time paralinguistic triggers.
        This enables 'Hot-Mutation' for the Affective Soul.
        Returns a tuple of (New DNA, List of rationale strings).
        """
        new_dna_dict = current_dna.to_dict()
        rationales = []

        # Adaptive Logic:
        # 1. Stress/Arousal -> Decrease Verbosity, increase Empathy
        if trait_name == "arousal" and trait_value > 0.7:
            target_verbosity = max(0.2, new_dna_dict["verbosity"] - 0.2)
            target_empathy = min(1.0, new_dna_dict["empathy"] + 0.2)
            # Apply EMA smoothing: trait = (1-alpha)*current + alpha*target
            new_dna_dict["verbosity"] = (1.0 - self._ema_alpha) * new_dna_dict[
                "verbosity"
            ] + (self._ema_alpha * target_verbosity)
            new_dna_dict["empathy"] = (1.0 - self._ema_alpha) * new_dna_dict[
                "empathy"
            ] + (self._ema_alpha * target_empathy)
            msg = "High Arousal detected. Transitioning to 'Calm Operator' state (Concise + High Empathy)."
            logger.info("🔥 Hot-Mutation (EMA): %s", msg)
            rationales.append(msg)

        # 2. Valence (Positive/Negative) -> Adjust Empathy
        if trait_name == "valence" and trait_value < 0.4:
            target_empathy = min(1.0, new_dna_dict["empathy"] + 0.3)
            new_dna_dict["empathy"] = (1.0 - self._ema_alpha) * new_dna_dict[
                "empathy"
            ] + (self._ema_alpha * target_empathy)
            msg = "Negative Valence detected. Boosting Empathy level."
            logger.info("🔥 Hot-Mutation (EMA): %s", msg)
            rationales.append(msg)

        # 3. Energy -> Adjust Proactivity
        if trait_name == "energy" and trait_value > 0.8:
            new_dna_dict["proactivity"] = min(1.0, new_dna_dict["proactivity"] + 0.05)
            rationales.append("High user energy detected. Increasing proactivity bias.")

        return AgentDNA.from_dict(new_dna_dict), rationales

    def _calculate_delta(self, dna1: AgentDNA, dna2: AgentDNA) -> float:
        """Calculates L2 norm of the difference between float traits."""
        d1 = dna1.to_dict()
        d2 = dna2.to_dict()
        diff_sq = 0.0
        count = 0
        for k in d1:
            if isinstance(d1[k], float):
                diff_sq += (d1[k] - d2[k]) ** 2
                count += 1
        return (diff_sq / count) ** 0.5 if count > 0 else 0.0
