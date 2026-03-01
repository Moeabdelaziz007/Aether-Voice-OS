"""
Aether Voice OS — Hive Coordinator (ADK 2.0 with Deep Handover Protocol).

Orchestrates multiple 'Expert' souls and manages the A2A (Agent-to-Agent)
handoff lifecycle with rich context preservation, bidirectional negotiation,
and rollback capability.

Architecture:
    - Integrates with Deep Handover Protocol for context preservation
    - Pre-transfer validation via prepare_handoff()
    - Post-transfer confirmation via complete_handoff()
    - Rollback capability for failed handovers
    - Telemetry tracking for success analytics
"""

from __future__ import annotations

import logging
from typing import TYPE_CHECKING, Any, Callable, Dict, List, Optional, Tuple

if TYPE_CHECKING:
    from core.identity.package import AthPackage
    from core.identity.registry import AetherRegistry
    from core.tools.router import ToolRouter

from core.ai.handover_protocol import (
    HandoverContext,
    HandoverNegotiation,
    HandoverStatus,
    ValidationCheckpoint,
    get_handover_protocol,
)
from core.ai.handover_telemetry import (
    FailureCategory,
    HandoverOutcome,
    get_telemetry,
    record_handover_end,
    record_handover_start,
)

logger = logging.getLogger(__name__)


class HiveCoordinator:
    """
    Orchestrator for the Aether Hive with Deep Handover Protocol.

    Responsibilities:
    1. Tracking the currently active Soul.
    2. Finding the best Expert Soul for a task.
    3. Managing rich context transfer during Handoff.
    4. Pre-transfer validation and post-transfer confirmation.
    5. Rollback capability for failed handovers.
    """

    def __init__(
        self,
        registry: AetherRegistry,
        router: ToolRouter,
        default_soul_name: str = "ArchitectExpert",
        on_handover: Optional[Callable] = None,
        enable_deep_handover: bool = True,
    ) -> None:
        self._registry = registry
        self._router = router
        self._active_soul: Optional[AthPackage] = None
        self._default_soul_name = default_soul_name
        self._on_handover = on_handover
        self._pre_warm_callback: Optional[Callable[[str], Any]] = None
        self._enable_deep_handover = enable_deep_handover

        # Legacy context bridge (for backward compatibility)
        self._context_bridge: Dict[str, str] = {}

        # Deep Handover Protocol integration
        self._handover_protocol = (
            get_handover_protocol() if enable_deep_handover else None
        )
        self._telemetry = get_telemetry() if enable_deep_handover else None
        self._active_handovers: Dict[str, HandoverContext] = {}
        self._handover_history: List[str] = []

        # Safety: Rollback and Checkpointing
        self._last_successful_soul: Optional[AthPackage] = (
            self._active_soul if hasattr(self, "_active_soul") else None
        )
        self._last_handover_id: Optional[str] = None

    @property
    def active_soul(self) -> AthPackage:
        if not self._active_soul:
            try:
                self._active_soul = self._registry.get(self._default_soul_name)
            except Exception:
                # Fallback to the first available soul if default fails
                pkgs = self._registry.list_packages()
                if pkgs:
                    self._active_soul = self._registry.get(pkgs[0])
                else:
                    logger.error("No souls found in registry!")
        return self._active_soul

    def request_handoff(self, target_name: str, task_context: str) -> bool:
        """
        Initiates a switch to a specified expert soul.

        Legacy method - uses simple context bridge.
        For deep handover, use prepare_handoff() and complete_handoff().
        """
        try:
            target = self._registry.get(target_name)
            logger.info(
                "A2A [HIVE] Handoff initiated: %s -> %s",
                self.active_soul.manifest.name,
                target_name,
            )

            # Store context for the next soul to pick up
            self._context_bridge["pending_task"] = task_context
            from_name = (
                self.active_soul.manifest.name if self._active_soul else "System"
            )
            self._active_soul = target

            # Trigger UI notification
            if self._on_handover:
                try:
                    self._on_handover(from_name, target_name, task_context)
                except Exception as e:
                    logger.error("Failed to trigger handover callback: %s", e)

            return True
        except Exception as e:
            logger.error("Handoff failed: %s", e)
            return False

    def set_pre_warm_callback(self, callback: Callable[[str], Any]) -> None:
        """Set the callback for speculative pre-warming."""
        self._pre_warm_callback = callback

    def prepare_handoff(
        self,
        target_name: str,
        task: str,
        payload: Optional[Dict[str, Any]] = None,
        code_context: Optional[Dict[str, Any]] = None,
        enable_negotiation: bool = False,
    ) -> Tuple[bool, Optional[HandoverContext], str]:
        """
        Pre-transfer validation for deep handover.

        Creates a HandoverContext, validates prerequisites, and optionally
        initiates negotiation before the actual transfer.

        Args:
            target_name: Name of the target expert soul
            task: Task description
            payload: Optional payload data
            code_context: Optional code context for developer tasks
            enable_negotiation: Whether to enable bidirectional negotiation

        Returns:
            Tuple of (success, handover_context, message)
        """
        if not self._enable_deep_handover or not self._handover_protocol:
            # Fallback to legacy handoff
            success = self.request_handoff(target_name, task)
            return success, None, "Legacy handoff used"

        try:
            source_name = (
                self.active_soul.manifest.name if self._active_soul else "System"
            )

            # Create handover context
            context = self._handover_protocol.create_handover(
                source_agent=source_name,
                target_agent=target_name,
                task=task,
                payload=payload or {},
            )

            # Add code context if provided
            if code_context:
                from core.ai.handover_protocol import CodeContext

                context.code_context = CodeContext(**code_context)

            # Initialize telemetry
            if self._telemetry:
                record_handover_start(
                    handover_id=context.handover_id,
                    source_agent=source_name,
                    target_agent=target_name,
                    task_description=task,
                )

            # Pre-transfer validation
            success, message = self._handover_protocol.prepare_handoff(
                context.handover_id
            )
            if not success:
                logger.error("Handover preparation failed: %s", message)
                if self._telemetry:
                    record_handover_end(
                        handover_id=context.handover_id,
                        outcome=HandoverOutcome.FAILED,
                        failure_category=FailureCategory.VALIDATION_FAILED,
                        failure_reason=message,
                    )
                return False, None, message

            # Store active handover
            self._active_handovers[context.handover_id] = context

            # Initiate negotiation if enabled
            if enable_negotiation:
                context.update_status(HandoverStatus.NEGOTIATING)
                negotiation = self._initiate_negotiation(context)
                context.negotiation = negotiation
            else:
                # Speculative pre-warming for zero-friction handovers
                self._handover_protocol.pre_warm_target(context.handover_id)
                if self._pre_warm_callback:
                    # Non-blocking trigger of gateway pre-warm
                    if asyncio.iscoroutinefunction(self._pre_warm_callback):
                        asyncio.create_task(self._pre_warm_callback(target_name))
                    else:
                        self._pre_warm_callback(target_name)

                if self._on_handover:
                    self._on_handover(source_name, target_name, "PRE_WARMING")

            logger.info(
                "A2A [HIVE] Handover prepared: %s -> %s (ID: %s)",
                source_name,
                target_name,
                context.handover_id,
            )

            return True, context, "Handover prepared successfully"

        except Exception as e:
            logger.error("Prepare handoff failed: %s", e)
            return False, None, str(e)

    def get_pending_handover_for_target(
        self, target_name: str
    ) -> Optional[HandoverContext]:
        """
        Retrieve the most recent pending handover for a specific target agent.

        Args:
            target_name: Name of the target agent

        Returns:
            HandoverContext if found, else None
        """

        # Include COMPLETED handovers so we can inject them immediately after the soul switch
        pending = [
            ctx
            for ctx in self._active_handovers.values()
            if ctx.target_agent == target_name
        ]

        if not pending:
            return None

        return sorted(pending, key=lambda x: x.created_at, reverse=True)[0]

    def complete_handoff(
        self,
        handover_id: str,
        validation_results: Optional[List[Dict[str, Any]]] = None,
    ) -> Tuple[bool, str]:
        """
        Post-transfer confirmation for deep handover.

        Finalizes the handover, validates the transfer was successful,
        and records telemetry.

        Args:
            handover_id: The handover context ID
            validation_results: Optional validation results from the target agent

        Returns:
            Tuple of (success, message)
        """
        if not self._enable_deep_handover or not self._handover_protocol:
            return True, "Legacy handoff - no completion needed"

        context = self._active_handovers.get(handover_id)
        if not context:
            return False, f"Handover {handover_id} not found"

        try:
            # Add validation checkpoint if provided
            if validation_results:
                checkpoint = self._handover_protocol.create_checkpoint(
                    handover_id=handover_id,
                    stage="post_transfer",
                    partial_output={"validation_results": validation_results},
                )
                for result in validation_results:
                    from core.ai.handover_protocol import VerificationResult

                    checkpoint.add_validation(VerificationResult(**result))
                context.validation_checkpoint = checkpoint

                # Check if validations passed
                if checkpoint.requires_changes:
                    logger.warning("Handover %s has validation issues", handover_id)

            # Complete the handover
            success, message = self._handover_protocol.complete_handoff(handover_id)

            if success:
                # Save checkpoints for potential future rollbacks (Safety Net)
                self._last_successful_soul = self._active_soul
                self._last_handover_id = handover_id

                # Switch the active soul
                target = self._registry.get(context.target_agent)
                from_name = (
                    self.active_soul.manifest.name if self._active_soul else "System"
                )
                self._active_soul = target

                # Add to history
                self._handover_history.append(handover_id)

                # Trigger UI notification
                if self._on_handover:
                    try:
                        self._on_handover(from_name, context.target_agent, context.task)
                    except Exception as e:
                        logger.error("Failed to trigger handover callback: %s", e)

                # Record telemetry
                if self._telemetry:
                    record_handover_end(
                        handover_id=handover_id,
                        outcome=HandoverOutcome.SUCCESS,
                    )

                logger.info("A2A [HIVE] Handover completed: %s", handover_id)
            else:
                # Record failure
                if self._telemetry:
                    record_handover_end(
                        handover_id=handover_id,
                        outcome=HandoverOutcome.FAILED,
                        failure_category=FailureCategory.SYSTEM_ERROR,
                        failure_reason=message,
                    )

            return success, message

        except Exception as e:
            logger.error("Complete handoff failed: %s", e)
            if self._telemetry:
                record_handover_end(
                    handover_id=handover_id,
                    outcome=HandoverOutcome.FAILED,
                    failure_category=FailureCategory.SYSTEM_ERROR,
                    failure_reason=str(e),
                )
            return False, str(e)

    def rollback_handover(self, handover_id: str) -> Tuple[bool, str]:
        """
        Rollback a failed handover to its pre-transfer state.

        Restores the previous soul and context state.

        Args:
            handover_id: The handover context ID

        Returns:
            Tuple of (success, message)
        """
        if not self._enable_deep_handover or not self._handover_protocol:
            return False, "Deep handover not enabled"

        context = self._active_handovers.get(handover_id)
        if not context:
            return False, f"Handover {handover_id} not found"

        try:
            # Execute rollback in protocol
            success, message = self._handover_protocol.rollback_handover(handover_id)

            if success and context.snapshot:
                # Restore previous soul from snapshot
                prev_soul_name = context.snapshot.get("source_agent")
                if prev_soul_name:
                    try:
                        prev_soul = self._registry.get(prev_soul_name)
                        self._active_soul = prev_soul
                        logger.info("Rolled back to soul: %s", prev_soul_name)
                    except Exception as e:
                        logger.error("Failed to restore soul after rollback: %s", e)

                # Record telemetry
                if self._telemetry:
                    self._telemetry.record_rollback(handover_id, successful=True)
                    record_handover_end(
                        handover_id=handover_id,
                        outcome=HandoverOutcome.ROLLED_BACK,
                    )

                logger.info("A2A [HIVE] Handover rolled back: %s", handover_id)

            return success, message

        except Exception as e:
            logger.error("Rollback failed: %s", e)
            if self._telemetry:
                self._telemetry.record_rollback(handover_id, successful=False)
            return False, str(e)

    def _initiate_negotiation(self, context: HandoverContext) -> HandoverNegotiation:
        """Initialize negotiation for a handover."""
        negotiation = HandoverNegotiation(
            handover_id=context.handover_id,
            initiating_agent=context.source_agent,
            receiving_agent=context.target_agent,
        )

        # Propose initial terms based on task
        negotiation.propose_terms(
            scope=f"Complete task: {context.task}",
            deliverables=["Implementation", "Tests", "Documentation"],
        )

        logger.debug("Negotiation initiated for handover %s", context.handover_id)
        return negotiation

    def negotiate_handover(
        self,
        handover_id: str,
        action: str,
        **kwargs: Any,
    ) -> Tuple[bool, Optional[HandoverNegotiation], str]:
        """
        Perform a negotiation action on an active handover.

        Args:
            handover_id: The handover context ID
            action: One of 'counter', 'accept', 'reject', 'clarify'
            **kwargs: Action-specific parameters

        Returns:
            Tuple of (success, negotiation, message)
        """
        context = self._active_handovers.get(handover_id)
        if not context or not context.negotiation:
            return False, None, "No active negotiation found"

        negotiation = context.negotiation

        try:
            if action == "counter":
                msg = negotiation.counter_terms(
                    scope=kwargs.get("scope"),
                    deliverables=kwargs.get("deliverables"),
                    deadline=kwargs.get("deadline"),
                )
                logger.debug("Counter offer sent: %s", msg.message_id)

            elif action == "accept":
                msg = negotiation.accept_terms()
                context.update_status(HandoverStatus.PREPARING)
                logger.info("Negotiation accepted for handover %s", handover_id)

            elif action == "reject":
                reason = kwargs.get("reason", "Terms rejected")
                msg = negotiation.reject_terms(reason)
                context.update_status(HandoverStatus.FAILED)
                logger.info("Negotiation rejected for handover %s", handover_id)

                # Record failure
                if self._telemetry:
                    record_handover_end(
                        handover_id=handover_id,
                        outcome=HandoverOutcome.REJECTED,
                        failure_category=FailureCategory.NEGOTIATION_FAILED,
                        failure_reason=reason,
                    )

            elif action == "clarify":
                question = kwargs.get("question", "Please clarify")
                negotiation.send_message(
                    from_agent=kwargs.get("from_agent", context.target_agent),
                    to_agent=kwargs.get("to_agent", context.source_agent),
                    message_type="clarify",
                    content=question,
                )

            else:
                return False, None, f"Unknown action: {action}"

            return True, negotiation, f"Action '{action}' executed"

        except Exception as e:
            logger.error("Negotiation action failed: %s", e)
            return False, None, str(e)

    def create_validation_checkpoint(
        self,
        handover_id: str,
        stage: str,
        partial_output: Dict[str, Any],
    ) -> Optional[ValidationCheckpoint]:
        """
        Create a validation checkpoint for an active handover.

        Args:
            handover_id: The handover context ID
            stage: Current stage description
            partial_output: Partial results to validate

        Returns:
            ValidationCheckpoint or None
        """
        if not self._handover_protocol:
            return None

        checkpoint = self._handover_protocol.create_checkpoint(
            handover_id=handover_id,
            stage=stage,
            partial_output=partial_output,
        )

        context = self._active_handovers.get(handover_id)
        return checkpoint

    def rollback_handover(self, handover_id: str) -> bool:
        """
        Roll back a failed handover to the previous stable state.
        Triggered by AetherGateway if the next expert fails to heart-beat.
        """
        context = self._active_handovers.get(handover_id)
        if not context:
            logger.warning("Rollback target '%s' not found in history.", handover_id)
            return False

        # 1. Restore context state if snapshot exists
        if context.restore_snapshot():
            logger.info("A2A [HIVE] Context restored from snapshot for %s", handover_id)

        # 2. Revert active soul to the last known-good expert
        if self._last_successful_soul:
            logger.info(
                "A2A [HIVE] Reverting active expert: %s -> %s",
                self._active_soul.manifest.name,
                self._last_successful_soul.manifest.name,
            )
            self._active_soul = self._last_successful_soul

        # 3. Update status to prevent re-triggered handovers
        context.update_status(HandoverStatus.ROLLED_BACK)
        return True

    def get_handover_context(self, handover_id: str) -> Optional[HandoverContext]:
        """Retrieve an active handover context by ID."""
        return self._active_handovers.get(handover_id)

    def get_active_handovers(self) -> List[HandoverContext]:
        """Get all active (in-progress) handovers."""
        return [
            ctx
            for ctx in self._active_handovers.values()
            if ctx.status
            not in (
                HandoverStatus.COMPLETED,
                HandoverStatus.FAILED,
                HandoverStatus.ROLLED_BACK,
            )
        ]

    def get_handover_history(self, limit: int = 10) -> List[str]:
        """Get recent handover IDs from history."""
        return self._handover_history[-limit:]

    def cleanup_handovers(self) -> int:
        """Clean up completed/failed handovers."""
        to_remove = [
            hid
            for hid, ctx in self._active_handovers.items()
            if ctx.status
            in (
                HandoverStatus.COMPLETED,
                HandoverStatus.FAILED,
                HandoverStatus.ROLLED_BACK,
            )
        ]
        for hid in to_remove:
            del self._active_handovers[hid]

        if self._handover_protocol:
            self._handover_protocol.cleanup()

        logger.info("Cleaned up %d handovers", len(to_remove))
        return len(to_remove)

    def get_telemetry_stats(self) -> Dict[str, Any]:
        """Get telemetry statistics for handovers."""
        if not self._telemetry:
            return {"enabled": False}
        return self._telemetry.get_stats()

    def export_telemetry(self, filepath: str) -> int:
        """Export telemetry data to a file."""
        if not self._telemetry:
            return 0
        return self._telemetry.export_records(filepath)

    async def evaluate_intent(self, query: str) -> Optional[str]:
        """
        Check if a better expert exists for the user's query.
        Returns the name of the better expert if found.
        """
        best_expert = await self._registry.find_expert(query)
        if (
            best_expert
            and self._active_soul
            and best_expert.manifest.name != self._active_soul.manifest.name
        ):
            # Only suggest if the expertise score is significantly high
            return best_expert.manifest.name
        return None
