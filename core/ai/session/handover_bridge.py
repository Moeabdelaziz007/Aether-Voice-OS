from __future__ import annotations

import logging
from datetime import datetime

from core.ai.handover_protocol import HandoverStatus

logger = logging.getLogger(__name__)


def build_system_instruction(session_facade) -> str:
    instruction_parts = []

    if session_facade._soul:
        manifest = session_facade._soul.manifest if hasattr(session_facade._soul, "manifest") else session_facade._soul
        expertise = getattr(manifest, "expertise", {})
        persona = getattr(manifest, "persona", "An Aether Agent")
        soul_instruction = f"{persona}\n\nPrimary Domain: {expertise}"
        instruction_parts.append(soul_instruction)
        session_facade._soul_instruction_cache = soul_instruction
        logger.info("A2A [SESSION] Applying Expert Soul: %s", getattr(manifest, "name", "Unknown"))

    if session_facade._injected_handover_context:
        handover_section = format_handover_context_for_instruction(session_facade)
        if handover_section:
            instruction_parts.append(handover_section)
            logger.info(
                "A2A [SESSION] Injected handover context: %s",
                session_facade._injected_handover_context.handover_id,
            )

    if session_facade._config.system_instruction:
        instruction_parts.append(session_facade._config.system_instruction)

    if session_facade._scheduler:
        instruction_parts.append(session_facade._scheduler.get_grounding_context())

    return "\n\n---\n\n".join(instruction_parts)


def format_handover_context_for_instruction(session_facade) -> str:
    if not session_facade._injected_handover_context:
        return ""

    ctx = session_facade._injected_handover_context
    parts = ["# HANDOVER CONTEXT", f"Handover ID: {ctx.handover_id}", f"From: {ctx.source_agent} → To: {ctx.target_agent}", f"Task: {ctx.task}"]

    if ctx.task_tree:
        parts.append("\n## Task Tree")
        for node in ctx.task_tree:
            status_icon = "✓" if node.status == "completed" else "○"
            parts.append(f"{status_icon} {node.description}")

    if ctx.working_memory and ctx.working_memory.short_term:
        parts.append("\n## Working Memory")
        for key, value in ctx.working_memory.short_term.items():
            parts.append(f"- {key}: {value}")

    if ctx.intent_confidence:
        parts.append("\n## Confidence")
        parts.append(f"Score: {ctx.intent_confidence.confidence_score:.2%}")
        parts.append(f"Reasoning: {ctx.intent_confidence.reasoning}")

    if ctx.code_context:
        parts.append("\n## Code Context")
        if ctx.code_context.files_modified:
            parts.append(f"Modified files: {', '.join(ctx.code_context.files_modified)}")
        if ctx.code_context.language:
            parts.append(f"Language: {ctx.code_context.language}")
        if ctx.code_context.framework:
            parts.append(f"Framework: {ctx.code_context.framework}")

    if ctx.conversation_history:
        parts.append("\n## Recent Conversation")
        for entry in ctx.conversation_history[-5:]:
            parts.append(f"[{entry.speaker}]: {entry.message[:100]}...")

    if ctx.history:
        parts.append("\n## Action History")
        for entry in ctx.history[-5:]:
            parts.append(f"- {entry}")

    return "\n".join(parts)


def inject_handover_context(session_facade, context) -> bool:
    try:
        session_facade._injected_handover_context = context
        ack_id = f"ack-{context.handover_id}"
        session_facade._handover_acknowledgments[ack_id] = datetime.now().isoformat()
        context.add_conversation_entry(
            speaker=context.target_agent,
            message=f"Handover acknowledged by {context.target_agent}. Ready to proceed.",
            metadata={"type": "handover_acknowledgment", "acknowledgment_id": ack_id, "session_id": id(session_facade)},
        )
        logger.info("A2A [SESSION] Handover context injected: %s (Task: %s)", context.handover_id, context.task[:50])
        return True
    except Exception as e:
        logger.error("Failed to inject handover context: %s", e)
        return False


def clear_handover_context(session_facade) -> None:
    if session_facade._injected_handover_context:
        logger.info("A2A [SESSION] Clearing handover context: %s", session_facade._injected_handover_context.handover_id)
        session_facade._injected_handover_context = None


def complete_handover_acknowledgment(session_facade, handover_id: str, success: bool, message: str = "") -> bool:
    context = session_facade._injected_handover_context
    if not context or context.handover_id != handover_id:
        logger.warning("Cannot complete handover acknowledgment: context mismatch or not found")
        return False

    context.update_status(HandoverStatus.COMPLETED if success else HandoverStatus.FAILED)
    context.add_conversation_entry(
        speaker=context.target_agent,
        message=message or f"Handover {'completed' if success else 'failed'}",
        metadata={"type": "handover_completion", "success": success, "timestamp": datetime.now().isoformat()},
    )
    logger.info("A2A [SESSION] Handover acknowledgment completed: %s (success=%s)", handover_id, success)
    return True


def export_handover_state(session_facade) -> dict:
    return {
        "has_active_handover": session_facade._injected_handover_context is not None,
        "handover_id": session_facade._injected_handover_context.handover_id if session_facade._injected_handover_context else None,
        "acknowledgments": session_facade._handover_acknowledgments.copy(),
        "timestamp": datetime.now().isoformat(),
    }


def restore_handover_state(session_facade, state: dict) -> bool:
    try:
        session_facade._handover_acknowledgments = state.get("acknowledgments", {})
        logger.info("Restored handover acknowledgments: %d", len(session_facade._handover_acknowledgments))
        return True
    except Exception as e:
        logger.error("Failed to restore handover state: %s", e)
        return False
