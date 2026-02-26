"""
Aether Voice OS — Genetic Optimizer.

Implements the neuro-evolutionary loop for agent instructions.
Calculates 'fitness' from affective telemetry and uses Gemini to mutate
prompts for better user engagement in future sessions.
"""

from __future__ import annotations
import logging
import json
from typing import Any, Optional
from datetime import datetime, timezone

from core.tools.firebase_tool import FirebaseConnector

logger = logging.getLogger(__name__)

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

    def __init__(self, firebase: FirebaseConnector, api_key: str):
        self._firebase = firebase
        self._api_key = api_key

    async def evolve(self, current_instructions: str, session_id: Optional[str] = None) -> Optional[dict]:
        """
        Perform a mutation step based on the last session's performance.
        """
        if not self._firebase.is_connected:
            logger.warning("Genetic Optimizer: Firebase offline. Evolution suspended.")
            return None

        # 1. Fetch Fitness Data
        sid = session_id or self._firebase._session_id
        if not sid:
            return None

        report = await self._firebase.get_session_affective_summary(sid)
        if report.get("status") != "success" or "summary" not in report:
            logger.info("Evolution skipped: No telemetry found for session %s", sid)
            return None

        metrics = report["summary"]
        
        # Threshold: Only evolve if we have enough interactions
        if metrics.get("interaction_count", 0) < 3:
            logger.info("Evolution skipped: Insufficient interaction count (%d)", metrics.get("interaction_count"))
            return None

        # 2. Invoke Gemini for Mutation
        try:
            import google.generativeai as genai
            genai.configure(api_key=self._api_key)
            model = genai.GenerativeModel('gemini-2.5-flash') # Standard flash for mutation

            prompt = GENETIC_SYSTEM_PROMPT.format(
                avg_engagement=metrics["avg_engagement"],
                trend=metrics["trend"],
                avg_pitch=metrics["avg_pitch"],
                current_instructions=current_instructions
            )

            response = await model.generate_content_async(prompt)
            # Basic JSON extraction
            text = response.text
            if "```json" in text:
                text = text.split("```json")[1].split("```")[0].strip()
            
            mutation = json.loads(text)
            logger.info("Soul Mutated: %s (Engagement: %.2f)", mutation.get("rationale"), metrics["avg_engagement"])
            
            # 3. Log mutation to Firestore
            await self._firebase.log_event("soul_mutation", {
                "session_id": sid,
                "prev_engagement": metrics["avg_engagement"],
                "rationale": mutation.get("rationale"),
                "version_delta": mutation.get("version_delta")
            })

            return mutation

        except Exception as exc:
            logger.error("Genetic mutation failed: %s", exc)
            return None
