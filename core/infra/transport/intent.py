import json
import logging
from typing import Any, Optional

logger = logging.getLogger(__name__)


class IntentBroker:
    """
    Manages intent schema V1.1 validation and speculative goal prediction.
    Offloads heavy logic from the AetherGateway.
    """

    def __init__(self):
        self._schema_version = "1.1"

    async def handle_intent(self, client_id: str, msg_content: str, gateway: Any) -> bool:
        """
        Process an incoming intent message.
        Validates schema and triggers appropriate internal routing.
        """
        try:
            payload = json.loads(msg_content)
            intent_type = payload.get("type")

            if not intent_type:
                logger.warning(f"IntentBroker: Missing 'type' in payload from {client_id}")
                return False

            logger.info(f"✦ Intent Broker: Routing '{intent_type}' for {client_id}")

            # Delegate to Gateway's broadcast or session injection
            # (Matches AetherGateway legacy logic)
            if intent_type == "UI_INTERACTION":
                await gateway.broadcast({"type": "STATE_UPDATE", "source": "broker", "intent": intent_type})
                return True

            elif intent_type == "SOUL_SHIFT":
                target = payload.get("target_soul")
                prob = payload.get("probability", 0.0)

                if target and prob > 0.8:
                    logger.info(
                        f"🚀 IntentBroker: High probability ({prob}) for soul shift to {target}. Triggering Pre-Warm."
                    )
                    # AetherGateway v2 includes pre_warm_soul method
                    if hasattr(gateway, "pre_warm_soul"):
                        asyncio.create_task(gateway.pre_warm_soul(target))
                return True

            elif intent_type == "CREATE_AGENT":
                description = payload.get("description", "A helpful assistant")
                logger.info(f"🎨 IntentBroker: Triggering Forge for '{description}'")

                if hasattr(gateway, "forge_agent"):
                    # Trigger the forge process
                    asyncio.create_task(gateway.forge_agent(description))
                return True

            return False
        except json.JSONDecodeError:
            logger.error(f"IntentBroker: Malformed JSON from {client_id}")
            return False
        except Exception as e:
            logger.error(f"IntentBroker: Intent handling error: {e}")
            return False

    def predict_next_goal(self, raw_input: str) -> Optional[str]:
        """Speculative prediction of the next user goal based on raw input traits."""
        # V3.2 Speculative Logic Placeholder
        if "help" in raw_input.lower():
            return "ASSISTANCE_REQUESTED"
        return None
