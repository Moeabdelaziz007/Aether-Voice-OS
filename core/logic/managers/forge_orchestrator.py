import logging
from datetime import datetime, timezone
from typing import Any, Dict, Optional

logger = logging.getLogger(__name__)

class ForgeOrchestrator:
    """
    The Forge: Real-time Voice-to-DNA Synthesis Engine.
    
    Responsibilities:
    1. Parse incoming transcripts for semantic cues (role, tone, skills).
    2. Update 'User DNA' with discovered preferences.
    3. Trigger Hive hot-reloading for the newly 'forged' agent.
    """
    
    def __init__(self, firebase_connector: Any, hive_coordinator: Any):
        self._firebase = firebase_connector
        self._hive = hive_coordinator
        self._active_dna: Dict[str, Any] = {
            "name": "Unknown",
            "role": "Generalist",
            "tone": "Neutral",
            "skills": [],
            "status": "synthesizing"
        }
        self._user_uid: Optional[str] = None

    def set_user_context(self, uid: str):
        self._user_uid = uid

    async def parse_voice_signal(self, transcript: str) -> bool:
        """
        Heuristic-based DNA extraction from voice transcripts.
        In a full implementation, this could call a Gemini sub-model to 'reason' about the DNA.
        """
        changed = False
        
        # Simple heuristic parser (POC)
        lower_t = transcript.lower()
        
        if "i want a" in lower_t or "create a" in lower_t:
            # Example: "I want a cybersecurity specialist"
            if "cybersecurity" in lower_t:
                self._active_dna["role"] = "Cybersecurity Specialist"
                self._active_dna["skills"].append("vulnerability_assessment")
                changed = True
            elif "frontend" in lower_t:
                self._active_dna["role"] = "Senior Frontend Architect"
                self._active_dna["skills"].append("react_optimization")
                changed = True
        
        if "tone should be" in lower_t:
            if "stern" in lower_t:
                self._active_dna["tone"] = "Stern"
                changed = True
            elif "friendly" in lower_t:
                self._active_dna["tone"] = "Friendly"
                changed = True

        if changed:
            logger.info(f"🧬 Forge: DNA Mutation detected: {self._active_dna}")
            # Emit signal for Visual HUD (via Firestore metrics or event stream)
            await self._firebase.log_event("dna_mutation", self._active_dna)
            
        return changed

    async def finalize_forge(self, agent_name: str):
        """Finalizes the DNA and hot-loads the agent into the Hive."""
        self._active_dna["name"] = agent_name
        self._active_dna["status"] = "deployed"
        self._active_dna["forged_at"] = datetime.now(timezone.utc).isoformat()
        
        # 1. Sync to Firebase
        await self._firebase.sync_agent_dna(agent_name, self._active_dna)
        
        # 2. Update User DNA if applicable
        if self._user_uid:
            await self._firebase.update_user_dna(self._user_uid, {
                "recent_forge": agent_name,
                "last_active_role": self._active_dna["role"]
            })

        # 3. Hot-Load into Hive
        # The HiveCoordinator must have an 'inject_dna' or 'redeploy' method.
        if hasattr(self._hive, "inject_dna"):
            await self._hive.inject_dna(agent_name, self._active_dna)
            logger.info(f"🔥 Forge: Agent {agent_name} hot-loaded into Hive.")
            return True
            
        return False
