import logging
import json
from typing import Dict, Any, List, Optional
from google.genai import types

from core.tools.forge_tool import create_agent
from core.ai.agents.registry import AgentMetadata, GeminiModel

logger = logging.getLogger("AetherOS.ForgeOrchestrator")

class ForgeOrchestrator:
    """
    Aether Forge Orchestrator (V2.0)
    
    The 'Mother' logic that translates user voice intent into a brand new AI agent.
    It orchestrates:
    1. Intent Extraction (Schema-guided AI parsing).
    2. Agent Synthesis (Directory & Manifest creation).
    3. Cloud Sync (A2A state preservation).
    4. Neural Arrival (Registry hot-loading).
    """

    def __init__(self, session_facade):
        self._session = session_facade
        self._client = session_facade._client
        self._registry = getattr(session_facade, "_agent_registry", None)
        self._firebase = getattr(session_facade, "_firebase", None)

    async def _gather_synapses(self, user_intent: str) -> str:
        """
        Retrieves relevant historical knowledge from the cloud brain.
        (Persistent Synapses Feature)
        """
        if not self._firebase:
            return "No historical synapses available."

        logger.info("A2A [FORGE] Querying neural synapses for intent: %s", user_intent[:30])
        # We use a broad uid or 'global' for generic inheritance
        synapses = await self._firebase.search_neural_synapses(
            uid="default_user", # In a real multi-user system, this would be the actual UID
            query_text=user_intent,
            limit=3
        )
        
        if not synapses:
            return "No matching synapses found. Starting from First Principles."
            
        context_str = "\n".join([f"- {s.get('content')}" for s in synapses])
        return f"Historical Context (Neural Inheritance):\n{context_str}"

    async def extract_agent_spec(self, user_intent: str) -> Optional[Dict[str, Any]]:
        """
        Uses Gemini to extract structured agent parameters from raw voice/text intent,
        incorporating historical synapses for continuity.
        """
        # 1. Gather Synapses
        synapses = await self._gather_synapses(user_intent)
        
        # Broadcast synapse match to HUD
        await self._session._gateway.broadcast({
            "type": "forge_hud_update",
            "phase": "synapse_match",
            "message": "Neural inheritance active. Synapses matched.",
            "data": synapses
        })

        prompt = f"""
        Extract the specifications for a new Aether AI specialist agent.
        
        User Intent: "{user_intent}"
        
        {synapses}
        
        System Instruction:
        - name: Unique, short, PascalCase (e.g., 'CloudExpert').
        - description: Human-readable purpose of the agent.
        - instructions: The deep system prompt/persona. Include insights from the 'Historical Context' if relevant to ensure continuity. 
        - expertise: Map of domains to scores (0.0 to 1.0).
        - suggested_tools: List of generic tools needed (e.g., ['system_tool', 'vision_tool']).
        
        Output MUST be a valid JSON object.
        """
        
        try:
            response = await self._client.aio.models.generate_content(
                model=GeminiModel.FLASH.value,
                contents=prompt,
                config=types.GenerateContentConfig(
                    response_mime_type="application/json"
                )
            )
            
            spec = json.loads(response.text)
            logger.info("A2A [FORGE] Extracted Spec: %s", spec.get("name"))
            
            # Broadcast spec extraction to HUD
            await self._session._gateway.broadcast({
                "type": "forge_hud_update",
                "phase": "spec_locked",
                "agent": spec.get("name"),
                "expertise": spec.get("expertise")
            })
            
            return spec
        except Exception as e:
            logger.error("A2A [FORGE] Spec extraction failed: %s", e)
            return None

    async def forge_and_activate(self, user_intent: str) -> Dict[str, Any]:
        """
        The E2E pipeline for agent creation.
        """
        logger.info("A2A [FORGE] User wants to forge: %s", user_intent[:50])
        
        # 1. Extract Spec
        spec = await self.extract_agent_spec(user_intent)
        if not spec:
            return {"status": "error", "message": "Failed to extract agent blueprint from your request."}

        # 2. Forge (Physical creation)
        await self._session._gateway.broadcast({
            "type": "forge_hud_update",
            "phase": "synthesis",
            "status": "writing_manifest",
            "agent": spec["name"]
        })
        
        result = create_agent(
            name=spec["name"],
            description=spec["description"],
            instructions=spec["instructions"],
            expertise=spec["expertise"],
            suggested_tools=spec.get("suggested_tools", [])
        )
        
        if result["status"] == "success":
            # 3. Hot-Load into Registry
            await self._session._gateway.broadcast({
                "type": "forge_hud_update",
                "phase": "awakening",
                "status": "registry_load",
                "agent": spec["name"]
            })
            if self._registry:
                metadata = AgentMetadata(
                    id=spec["name"].lower().replace(" ", "_"),
                    name=spec["name"],
                    version="1.0.0",
                    description=spec["description"],
                    capabilities=list(spec["expertise"].keys()),
                    system_prompt=spec["instructions"],
                    foundation_model=GeminiModel.FLASH,
                    tools=[{"name": t} for t in spec.get("suggested_tools", [])]
                )
                self._registry.register_agent(metadata)
                logger.info("A2A [FORGE] Agent '%s' hot-loaded into Hive registry.", spec["name"])
            
            # 4. Neural Response (Voice confirmation)
            voice_msg = f"Agent {spec['name']} has been awakened and synchronized with the cloud galaxy. I am reading its soul manifest... It is ready for deployment."
            await self._session.send_transcription(voice_msg, end_of_turn=True)
            
            # 5. Neural Closure: Log the birth synapse for future inheritance
            if self._firebase:
                asyncio.create_task(
                    self._firebase.log_vector_memory(
                        uid="default_user",
                        content=f"Synthesized Agent: {spec['name']}. Expertise: {spec['expertise']}. Instructions: {spec['instructions']}",
                        metadata={"type": "agent_birth", "agent": spec["name"]}
                    )
                )

        return result
