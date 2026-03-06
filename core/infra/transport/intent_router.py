from __future__ import annotations

import hashlib
import json
import logging

logger = logging.getLogger(__name__)


def predict_next_goal(raw_input: str) -> str | None:
    raw = raw_input.lower()
    if "server" in raw:
        return "check logs"
    if "test" in raw:
        return "run accuracy benchmark"
    if "fix" in raw:
        return "apply autonomous repair"
    return None


def verify_payload_signature(gateway, payload: dict, signature: str, client_id: str) -> bool:
    payload_json = json.dumps(payload, sort_keys=True)
    payload_hash = hashlib.sha256(payload_json.encode()).hexdigest()
    return gateway._verify_signature(payload_hash, signature, client_id)


async def handle_intent(gateway, client_id: str, msg: dict) -> None:
    intent_id = msg.get("intent_id")
    level = msg.get("level", 1)
    payload = msg.get("payload", {})
    signature = msg.get("signature")

    if signature and not verify_payload_signature(gateway, payload, signature, client_id):
        logger.warning("Intent signature verification failed for %s", intent_id)
        await gateway.broadcast("intent_error", {"intent_id": intent_id, "error": "SIGNATURE_INVALID"})
        return

    prediction = predict_next_goal(payload.get("raw_input", ""))
    await gateway.broadcast(
        "intent_update",
        {
            "intent_id": intent_id,
            "status": "PROCESSED",
            "memory_update": {
                "predicted_next_goal": prediction,
                "user_preference_delta": {"last_used_level": level},
            },
        },
    )

    raw_text = payload.get("raw_input", "")
    if raw_text:
        await gateway.send_text(raw_text)
