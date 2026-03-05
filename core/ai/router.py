import logging
import numpy as np
from typing import List, Optional, Tuple
from core.ai.agents.registry import AgentRegistry, AgentMetadata

logger = logging.getLogger("AetherOS.Router")

# ==========================================
# 🌌 Hybrid Specialist Router
# "The Neural Switchboard"
# Logic: Keywords -> Embeddings -> Fallback
# ==========================================

class IntelligenceRouter:
    """
    Routes a user request or semantic intent
    to the most qualified expert in the Hive.
    """
    def __init__(self, registry: AgentRegistry):
        self.registry = registry

    async def route_intent(self, user_intent: str, embedding: Optional[List[float]] = None) -> Tuple[AgentMetadata, float]:
        """
        Main routing entrypoint.
        Returns the (Agent, ConfidenceScore).
        """
        # 1. Rule-Based Routing (Keyword Overrides)
        agent = self._rule_route(user_intent)
        if agent:
            logger.info(f"[Router] ⚡ Rule-Based Route: {agent.name}")
            return agent, 1.0

        # 2. Semantic Similarity Routing (Vector Space)
        if embedding:
            agent, score = self._semantic_route(embedding)
            if agent and score > 0.8:
                logger.info(f"[Router] 🧠 Semantic Route: {agent.name} (Conf: {score:.2f})")
                return agent, score

        # 3. LLM Fallback (Default Orchestrator)
        orchestrator = self.registry.get_agent("aether_core")
        if not orchestrator:
            # Fatal fallback to the first available agent
            agents = self.registry.list_all_agents()
            orchestrator = agents[0] if agents else None
            
        logger.info(f"[Router] 🏁 Fallback Route: {orchestrator.name if orchestrator else 'None'}")
        return orchestrator, 0.5

    def _rule_route(self, text: str) -> Optional[AgentMetadata]:
        """Fast keyword-based matching for system commands."""
        text = text.lower()
        
        # Hardcoded Expert Keywords (Can be dynamic in production)
        rules = {
            "coder_agent": ["code", "debug", "python", "javascript", "script", "file", "build"],
            "aether_core": ["status", "where am i", "who are you", "help", "system"]
        }
        
        for agent_id, keywords in rules.items():
            if any(k in text for k in keywords):
                return self.registry.get_agent(agent_id)
        
        return None

    def _semantic_route(self, intent_embedding: List[float]) -> Tuple[Optional[AgentMetadata], float]:
        """Vector similarity search against registered specialists."""
        best_agent = None
        best_score = -1.0
        
        query_vec = np.array(intent_embedding)
        
        for agent in self.registry.list_all_agents():
            if agent.semantic_fingerprint:
                agent_vec = np.array(agent.semantic_fingerprint)
                # Cosine Similarity
                score = np.dot(query_vec, agent_vec) / (np.linalg.norm(query_vec) * np.linalg.norm(agent_vec) + 1e-6)
                
                if score > best_score:
                    best_score = score
                    best_agent = agent
        
        return best_agent, float(best_score)
