"""
Aether Voice OS — Multi-Agent Orchestrator (ADK 2.0 with Deep Handover Protocol).

Coordinates interactions between multiple ADK Agents using the Deep Handover Protocol.
Supports rich context preservation, bidirectional negotiation, validation checkpoints,
and rollback capability for specialist handovers.
"""

import logging
import time
from typing import Any, Dict, List, Optional, Tuple

from core.ai.agents.registry import AgentMetadata
from core.ai.handover.dtos import HandoverPacket
from core.ai.handover.protocol_models import (
    ArchitectOutput,
    ContextSerializer,
    DebuggerOutput,
    HandoverContext,
    HandoverNegotiation,
    HandoverStatus,
    IntentConfidence,
    ValidationCheckpoint,
    get_handover_protocol,
)
from core.ai.handover.telemetry import FailureCategory, HandoverOutcome, get_telemetry
from core.ai.orchestrator.gravity_router import (
    PlanetCandidate,
)

logger = logging.getLogger(__name__)


# Re-export HandoverContext for backward compatibility
# The new HandoverContext is a Pydantic model with richer capabilities
__all__ = [
    "AgentHandoverManager",
    "HandoverPacket",
    "HandoverContext",
    "MultiAgentOrchestrator",
    "SpecialistHandoverManager",
]


class AgentHandoverManager:
    """Legacy simple handover manager retained in canonical package."""

    def __init__(self):
        self._last_handover: Optional[HandoverPacket] = None

    async def execute_handover(
        self,
        source: AgentMetadata,
        target: AgentMetadata,
        task: str,
        summary: str,
        memory: Dict[str, Any],
    ) -> HandoverPacket:
        packet = HandoverPacket(
            timestamp=time.time(),
            source_agent_id=source.id,
            target_agent_id=target.id,
            task_goal=task,
            conversation_summary=summary,
            working_memory=memory,
        )

        logger.info(
            "🎯 [Handover] Handing over from %s -> %s for task: '%s...'",
            source.name,
            target.name,
            task[:50],
        )

        self._last_handover = packet
        return packet

    def get_last_packet(self) -> Optional[HandoverPacket]:
        return self._last_handover


class SpecialistHandoverManager:
    """
    Manages handovers between specialist agents (Architect, Debugger, etc.).

    Provides high-level methods for common handover patterns:
    - Architect -> Debugger (design verification)
    - Debugger -> Architect (rework requests)
    - Bidirectional negotiation
    """

    def __init__(self, orchestrator: "MultiAgentOrchestrator"):
        self._orchestrator = orchestrator
        self._protocol = get_handover_protocol()
        self._telemetry = get_telemetry()
        self._serializer = ContextSerializer()

    async def architect_to_debugger_handover(
        self,
        task: str,
        architect_output: ArchitectOutput,
        code_context: Optional[Dict[str, Any]] = None,
    ) -> Tuple[bool, Optional[HandoverContext], str]:
        """
        Handover from Architect to Debugger for design verification.

        Args:
            task: The original task
            architect_output: The architect's output with blueprints and decisions
            code_context: Optional code context

        Returns:
            Tuple of (success, context, message)
        """
        # Create rich context with Architect output
        context = self._protocol.create_handover(
            source_agent="Architect",
            target_agent="Debugger",
            task=task,
            payload={
                "architect_output": architect_output.model_dump(),
                "blueprints": [bp.model_dump() for bp in architect_output.blueprints],
                "high_impact_decisions": [
                    d.model_dump() for d in architect_output.get_high_impact_decisions()
                ],
                "critical_risks": [
                    r.model_dump() for r in architect_output.get_critical_risks()
                ],
            },
        )

        # Add intent confidence
        context.intent_confidence = IntentConfidence(
            source_agent="Architect",
            target_agent="Debugger",
            confidence_score=0.95,
            reasoning="Design verification required - Debugger specializes in risk assessment",
            alternatives_considered=["CodingExpert", "System"],
        )

        # Add code context if provided
        if code_context:
            from core.ai.handover.protocol_models import CodeContext

            context.code_context = CodeContext(**code_context)

        # Add task decomposition
        context.add_task_node(
            description="Review architectural blueprint",
            assigned_to="Debugger",
        )
        context.add_task_node(
            description="Assess risks and provide recommendations",
            assigned_to="Debugger",
        )

        # Perform handover through orchestrator
        return await self._orchestrator.handover_with_context(
            "Architect", "Debugger", context
        )

    async def debugger_to_architect_feedback(
        self,
        original_context: HandoverContext,
        debugger_output: DebuggerOutput,
    ) -> Tuple[bool, Optional[HandoverContext], str]:
        """
        Send feedback from Debugger back to Architect for rework.

        Args:
            original_context: The original handover context
            debugger_output: The debugger's findings

        Returns:
            Tuple of (success, context, message)
        """
        # Create feedback context
        context = self._protocol.create_handover(
            source_agent="Debugger",
            target_agent="Architect",
            task=f"Rework: {original_context.task}",
            payload={
                "debugger_output": debugger_output.model_dump(),
                "failed_verifications": [
                    v.model_dump() for v in debugger_output.get_failed_results()
                ],
                "critical_warnings": [
                    w.model_dump() for w in debugger_output.get_critical_warnings()
                ],
                "proposed_fixes": [f.model_dump() for f in debugger_output.fixes],
                "original_handover_id": original_context.handover_id,
            },
        )

        # Add intent confidence
        context.intent_confidence = IntentConfidence(
            source_agent="Debugger",
            target_agent="Architect",
            confidence_score=0.9,
            reasoning="Rework required based on verification findings",
            alternatives_considered=["CodingExpert"],
        )

        # Copy relevant conversation history
        context.conversation_history = original_context.conversation_history.copy()

        # Perform handover
        return await self._orchestrator.handover_with_context(
            "Debugger", "Architect", context
        )

    def negotiate_scope(
        self,
        context: HandoverContext,
        proposed_scope: str,
        deliverables: List[str],
    ) -> HandoverNegotiation:
        """
        Initiate scope negotiation for a handover.

        Args:
            context: The handover context
            proposed_scope: Proposed task scope
            deliverables: List of expected deliverables

        Returns:
            HandoverNegotiation instance
        """
        negotiation = HandoverNegotiation(
            handover_id=context.handover_id,
            initiating_agent=context.source_agent,
            receiving_agent=context.target_agent,
        )

        negotiation.propose_terms(
            scope=proposed_scope,
            deliverables=deliverables,
        )

        context.negotiation = negotiation
        context.update_status(HandoverStatus.NEGOTIATING)

        logger.info(
            "Negotiation initiated for handover %s: scope='%s'",
            context.handover_id,
            proposed_scope,
        )

        return negotiation


class MultiAgentOrchestrator:
    """
    Coordinates interactions between multiple ADK Agents using the Deep Handover Protocol.

    Features:
    - Rich context preservation during handovers
    - Bidirectional negotiation support
    - Validation checkpoints
    - Rollback capability
    - Telemetry tracking
    """

    def __init__(self, on_handover: Optional[callable] = None):
        self.active_agents: Dict[str, Any] = {}
        self.on_handover = on_handover
        self._protocol = get_handover_protocol()
        self._telemetry = get_telemetry()
        self._serializer = ContextSerializer()
        self._active_handovers: Dict[str, HandoverContext] = {}
        self._handover_history: List[str] = []

        # Specialist handover manager
        self.specialists = SpecialistHandoverManager(self)

        # Galaxy orchestration components
        from core.ai.orchestrator.fallback_strategy import FallbackStrategy
        from core.ai.orchestrator.galaxy_policy import GalaxyPolicyEnforcer
        from core.ai.orchestrator.gravity_router import GravityRouter

        self.gravity_router = GravityRouter()
        self.fallback_strategy = FallbackStrategy(max_retries=2)
        self.policy_enforcer = GalaxyPolicyEnforcer()
        self._engine = None  # Will be set by engine.py

    def set_engine(self, engine) -> None:
        """Set engine reference for cinematic event emission."""
        self._engine = engine

    def _extract_agent_capabilities(self, agent_name: str) -> List[str]:
        """Extract capabilities from a registered agent.

        Args:
            agent_name: Name of the agent

        Returns:
            List of capability strings (e.g., ["note.create", "semantic.search"])
        """
        agent = self.active_agents.get(agent_name)
        if not agent:
            logger.warning(
                "Agent '%s' not found for capability extraction",
                agent_name,
            )
            return []

        # Try to extract from agent metadata or manifest
        capabilities = []

        # Check if agent has capabilities attribute
        if hasattr(agent, "capabilities"):
            capabilities.extend(agent.capabilities)

        # Check if agent has metadata with capabilities
        if hasattr(agent, "metadata") and hasattr(agent.metadata, "capabilities"):
            capabilities.extend(agent.metadata.capabilities)

        # Default capabilities based on agent type if not specified
        if not capabilities:
            # Map common agent types to default capabilities
            agent_type_map = {
                "Architect": [
                    "design.create",
                    "blueprint.generate",
                    "risk.assess",
                ],
                "Debugger": [
                    "debug.analyze",
                    "verify.design",
                    "risk.assess",
                ],
                "CodingExpert": [
                    "code.write",
                    "code.review",
                    "refactor",
                ],
                "System": [
                    "system.orchestrate",
                    "task.route",
                ],
            }
            capabilities = agent_type_map.get(agent_name, ["general.task"])

        return capabilities

    def _extract_required_capabilities(
        self,
        context: HandoverContext,
    ) -> List[str]:
        """Extract required capabilities from task context.

        Args:
            context: Handover context with task information

        Returns:
            List of required capability strings
        """
        capabilities = set()

        # Analyze task description for keywords
        task_lower = context.task.lower()

        # Design-related capabilities
        if any(
            word in task_lower
            for word in ["design", "architecture", "blueprint", "plan"]
        ):
            capabilities.add("design.create")
            capabilities.add("blueprint.generate")

        # Debug-related capabilities
        if any(
            word in task_lower for word in ["debug", "error", "fix", "issue", "problem"]
        ):
            capabilities.add("debug.analyze")
            capabilities.add("verify.design")

        # Code-related capabilities
        if any(
            word in task_lower
            for word in ["code", "implement", "write", "function", "class"]
        ):
            capabilities.add("code.write")
            capabilities.add("code.review")

        # Risk assessment
        if any(word in task_lower for word in ["risk", "validate", "verify", "check"]):
            capabilities.add("risk.assess")

        # Search capabilities
        if any(
            word in task_lower for word in ["search", "find", "lookup", "documentation"]
        ):
            capabilities.add("semantic.search")
            capabilities.add("docs.lookup")

        # Note/documentation capabilities
        if any(
            word in task_lower for word in ["note", "document", "record", "summary"]
        ):
            capabilities.add("note.create")

        # Fallback to general task if no specific capabilities identified
        if not capabilities:
            capabilities.add("general.task")

        # Also consider working memory hints
        if context.working_memory:
            memory_str = str(context.working_memory).lower()
            if "design" in memory_str:
                capabilities.add("design.create")
            if "code" in memory_str:
                capabilities.add("code.write")

        return list(capabilities)

    def register_agent(self, name: str, agent: Any):
        """Register an agent with the orchestrator."""
        self.active_agents[name] = agent
        logger.debug("Registered ADK Specialist: %s", name)

    async def handover(
        self, from_agent: str, to_agent: str, context: HandoverContext
    ) -> str:
        """
        Legacy handover method for backward compatibility.

        Executes a basic handover between two specialized agents.
        For deep handover with full protocol support, use handover_with_context().
        """
        logger.info("🔄 Handover: [%s] -> [%s]", from_agent, to_agent)
        context.add_history(f"Handed over from {from_agent} to {to_agent}")

        if self.on_handover:
            try:
                if asyncio.iscoroutinefunction(self.on_handover):
                    await self.on_handover(from_agent, to_agent, context.task)
                else:
                    self.on_handover(from_agent, to_agent, context.task)
            except Exception as e:
                logger.error("Failed to trigger handover callback: %s", e)

        target = self.active_agents.get(to_agent)
        if not target:
            return f"Error: Agent {to_agent} not found."

        # Set orchestrator reference for nested handovers
        if hasattr(target, "set_orchestrator"):
            target.set_orchestrator(self)

        return await target.process(context)

    async def handover_with_context(
        self,
        from_agent: str,
        to_agent: str,
        context: HandoverContext,
        enable_negotiation: bool = False,
    ) -> Tuple[bool, Optional[HandoverContext], str]:
        """
        Execute a deep handover with full protocol support.

        Args:
            from_agent: Source agent name
            to_agent: Target agent name
            context: Rich handover context
            enable_negotiation: Whether to enable negotiation phase

        Returns:
            Tuple of (success, context, message)
        """
        logger.info(
            "🔄 Deep Handover: [%s] -> [%s] (ID: %s)",
            from_agent,
            to_agent,
            context.handover_id,
        )

        # Validate agents exist
        if from_agent not in self.active_agents:
            return False, None, f"Source agent '{from_agent}' not found"

        if to_agent not in self.active_agents:
            return False, None, f"Target agent '{to_agent}' not found"

        # Store context
        self._active_handovers[context.handover_id] = context

        # Start telemetry
        if self._telemetry:
            self._telemetry.start_recording(
                handover_id=context.handover_id,
                source_agent=from_agent,
                target_agent=to_agent,
                task_description=context.task,
            )

        try:
            # Pre-transfer preparation
            success, message = await self._protocol.prepare_handoff(context.handover_id)
            if not success:
                logger.error("Handover preparation failed: %s", message)
                if self._telemetry:
                    self._telemetry.finalize_recording(
                        handover_id=context.handover_id,
                        outcome=HandoverOutcome.FAILED,
                        failure_category=FailureCategory.VALIDATION_FAILED,
                        failure_reason=message,
                    )
                return False, context, message

            # Galaxy policy validation
            policy_violations = self.policy_enforcer.validate_routing_decision(
                planet_id=to_agent,
                galaxy_id=context.galaxy_id,
                latency_ms=0.0,  # Will be populated from telemetry
                load=0.0,  # Will be populated from planet health
            )

            if policy_violations:
                logger.error("Policy violations: %s", policy_violations)
                return (
                    False,
                    context,
                    f"Policy violations: {', '.join(policy_violations)}",
                )

            # Calculate gravity score if not set
            if context.gravity_score is None:
                # Create candidate from target agent
                candidate = PlanetCandidate(
                    planet_id=to_agent,
                    capabilities=self._extract_agent_capabilities(to_agent),
                    confidence=(
                        context.intent_confidence.confidence_score
                        if context.intent_confidence
                        else 0.5
                    ),
                    latency_ms=0.0,  # Will be populated later
                    load=0.0,  # Will be populated later
                    continuity_bonus=0.0,
                )

                best_planet, best_score = self.gravity_router.select_best_planet(
                    [candidate],
                    required_capabilities=self._extract_required_capabilities(context),
                )

                context.gravity_score = best_score
                context.focus_target = best_planet or to_agent
                logger.info(
                    "Calculated gravity score %.3f for planet %s",
                    best_score,
                    best_planet or to_agent,
                )

            # Negotiation phase (if enabled)
            if enable_negotiation and not context.negotiation:
                negotiation = self.specialists.negotiate_scope(
                    context,
                    proposed_scope=f"Complete: {context.task}",
                    deliverables=["Implementation", "Verification"],
                )
                # In a real implementation, wait for negotiation to complete
                # For now, auto-accept for demo purposes
                negotiation.accept_terms()
                context.update_status(HandoverStatus.PREPARING)

            # Execute transfer
            target = self.active_agents[to_agent]
            if hasattr(target, "set_orchestrator"):
                target.set_orchestrator(self)

            # Process with target agent
            result = await target.process(context)

            # Record result in context
            context.payload["handover_result"] = result
            context.add_history(f"Target agent '{to_agent}' processed task")

            # Post-transfer completion
            success, message = await self._protocol.complete_handoff(
                context.handover_id
            )

            if success:
                self._handover_history.append(context.handover_id)

                # Trigger callback
                if self.on_handover:
                    try:
                        if asyncio.iscoroutinefunction(self.on_handover):
                            await self.on_handover(from_agent, to_agent, context.task)
                        else:
                            self.on_handover(from_agent, to_agent, context.task)
                    except Exception as e:
                        logger.error("Handover callback failed: %s", e)

                # Record telemetry
                if self._telemetry:
                    self._telemetry.finalize_recording(
                        handover_id=context.handover_id,
                        outcome=HandoverOutcome.SUCCESS,
                    )

                logger.info(
                    "✅ Handover completed: %s -> %s",
                    from_agent,
                    to_agent,
                )
                return True, context, "Handover completed successfully"
            else:
                if self._telemetry:
                    self._telemetry.finalize_recording(
                        handover_id=context.handover_id,
                        outcome=HandoverOutcome.FAILED,
                        failure_category=FailureCategory.SYSTEM_ERROR,
                        failure_reason=message,
                    )
                return False, context, message

        except Exception as e:
            logger.error("Handover failed with exception: %s", e)
            context.update_status(HandoverStatus.FAILED)

            if self._telemetry:
                self._telemetry.finalize_recording(
                    handover_id=context.handover_id,
                    outcome=HandoverOutcome.FAILED,
                    failure_category=FailureCategory.SYSTEM_ERROR,
                    failure_reason=str(e),
                )

            return False, context, str(e)

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
        context = self._active_handovers.get(handover_id)
        if not context:
            logger.warning("No active handover found for ID: %s", handover_id)
            return None

        checkpoint = self._protocol.create_checkpoint(
            handover_id=handover_id,
            stage=stage,
            partial_output=partial_output,
        )

        context.validation_checkpoint = checkpoint
        context.update_status(HandoverStatus.VALIDATING)

        logger.debug(
            "Validation checkpoint created for handover %s: stage='%s'",
            handover_id,
            stage,
        )

        return checkpoint

    async def rollback_handover(self, handover_id: str) -> Tuple[bool, str]:
        """
        Rollback a handover to its pre-transfer state.

        Args:
            handover_id: The handover context ID

        Returns:
            Tuple of (success, message)
        """
        context = self._last_handover if hasattr(self, "_last_handover") else None
        # Note: In MultiAgentOrchestrator, we use _active_handovers
        context = self._active_handovers.get(handover_id)

        if not context:
            return False, f"Handover {handover_id} not found"

        success, message = await self._protocol.rollback_handover(handover_id)

        if success:
            if self._telemetry:
                self._telemetry.record_rollback(handover_id, successful=True)
                self._telemetry.finalize_recording(
                    handover_id=handover_id,
                    outcome=HandoverOutcome.ROLLED_BACK,
                )

            logger.info("⏮️ Handover rolled back: %s", handover_id)
        else:
            if self._telemetry:
                self._telemetry.record_rollback(handover_id, successful=False)

        return success, message

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
                negotiation.counter_terms(
                    scope=kwargs.get("scope"),
                    deliverables=kwargs.get("deliverables"),
                    deadline=kwargs.get("deadline"),
                )

            elif action == "accept":
                negotiation.accept_terms()
                context.update_status(HandoverStatus.PREPARING)

            elif action == "reject":
                reason = kwargs.get("reason", "Terms rejected")
                negotiation.reject_terms(reason)
                context.update_status(HandoverStatus.FAILED)

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

    def serialize_context(self, context: HandoverContext, compact: bool = False) -> str:
        """Serialize a handover context to JSON."""
        return self._serializer.serialize(context, compact=compact)

    def deserialize_context(self, data: str) -> HandoverContext:
        """Deserialize a handover context from JSON."""
        return self._serializer.deserialize(data)

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

    def get_telemetry_stats(self) -> Dict[str, Any]:
        """Get telemetry statistics."""
        if not self._telemetry:
            return {"enabled": False}
        return self._telemetry.get_stats()

    def get_analytics_report(self) -> Dict[str, Any]:
        """Get comprehensive analytics report."""
        if not self._telemetry:
            return {"enabled": False}
        return self._telemetry.get_performance_report()

    def cleanup(self) -> int:
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

        if self._protocol:
            self._protocol.cleanup()

        logger.info("Cleaned up %d handovers", len(to_remove))
        return len(to_remove)

    async def collaborate(self, task: str, primary_agent: str) -> str:
        """
        Takes a complex task and routes it starting from a primary agent.
        Uses the deep handover protocol for rich context preservation.
        """
        logger.info("Orchestrating task: '%s' starting with %s.", task, primary_agent)

        # Create rich context
        context = self._protocol.create_handover(
            source_agent="Orchestrator",
            target_agent=primary_agent,
            task=task,
        )

        starter = self.active_agents.get(primary_agent)
        if not starter:
            return "Orchestration Failed: Primary agent offline."

        # Set orchestrator reference for nested handovers
        if hasattr(starter, "set_orchestrator"):
            starter.set_orchestrator(self)

        # Use deep handover
        success, final_context, message = await self.handover_with_context(
            "Orchestrator", primary_agent, context
        )

        if success and final_context:
            return (
                f"Task: {task}\n"
                f"Status: {final_context.status.value}\n"
                f"History: {final_context.history}"
            )
        else:
            return f"Orchestration Failed: {message}"
