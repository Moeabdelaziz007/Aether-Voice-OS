"""
Aether Voice OS — Architect Specialist Agent.

Specializes in high-level system design and architectural planning.
Uses the Deep Handover Protocol to pass comprehensive blueprints to
implementing and verification agents.
"""

import logging
from typing import Optional

from core.ai.agents.voice_agent import VoiceAgent
from core.ai.genetic import AgentDNA
from core.ai.handover.manager import HandoverContext, MultiAgentOrchestrator
from core.ai.handover_protocol import ArchitectOutput, IntentConfidence

logger = logging.getLogger(__name__)


class ArchitectAgent(VoiceAgent):
    """
    Specializes in high-level system design.
    Breaks down user requests into actionable structural steps.
    """

    SYSTEM_OVERVIEW = "System Overview"

    def __init__(self, dna: Optional[AgentDNA] = None):
        super().__init__(dna)
        self.orchestrator: Optional[MultiAgentOrchestrator] = None
        self._output: Optional[ArchitectOutput] = None

    def set_orchestrator(self, orchestrator: MultiAgentOrchestrator):
        """Set the orchestrator for handover coordination."""
        self.orchestrator = orchestrator

    async def process(self, context: HandoverContext) -> str:
        """
        Process a task and create architectural blueprints.

        Uses the extended HandoverContext to:
        - Access rich task metadata
        - Store working memory
        - Build task tree decomposition
        - Pass comprehensive output to Debugger
        """
        logger.info("📐 Architect analyzing task: %s", context.task)
        self._active_context = context  # Store for prompt building

        # Update context
        context.add_history("Architect began analysis", agent="Architect")

        # Create output container
        self._output = ArchitectOutput(
            handover_id=context.handover_id,
            task_description=context.task,
        )

        # Perform architectural analysis (simulated for MVP)
        self._create_blueprint(context)

        # Add decisions
        decision = self._output.add_decision(
            category="architecture",
            description="Modular microservices architecture with clear API boundaries",
            rationale="Provides scalability and maintainability for requirements",
            impact_level="high",
        )
        logger.info("📐 Created decision: %s", decision.decision_id)

        # Add risks
        risk = self._output.add_risk(
            category="scalability",
            description="Database may become bottleneck under high load",
            probability=0.6,
            impact=0.8,
            mitigation="Implement read replicas and caching layer",
        )
        logger.info("📐 Identified risk: %s", risk.risk_id)

        # Update context with output
        context.payload["architect_output"] = self._output.model_dump()
        context.payload["blueprint"] = "Phase 1: Database Migration. Phase 2: React Component Update"

        # Add task nodes for decomposition
        task1 = context.add_task_node(
            description="Design database schema",
            assigned_to="Architect",
        )
        context.complete_task_node(task1)

        task2 = context.add_task_node(
            description="Verify design with Debugger",
            parent_id=task1,
            assigned_to="Debugger",
        )
        context.set_current_task(task2)

        # Add intent confidence for handover
        context.intent_confidence = IntentConfidence(
            source_agent="Architect",
            target_agent="Debugger",
            confidence_score=0.95,
            reasoning="Design verification required - Debugger risk assessment",
            alternatives_considered=["CodingExpert"],
        )

        context.add_history(
            "Architect blueprint complete. Requesting Debugger verification.",
            agent="Architect",
        )

        logger.info("📐 Architect blueprint complete. Passing to Debugger for verification.")

        # Handover to Debugger using deep protocol
        if self.orchestrator:
            return await self._handover_to_debugger(context)

        return "Architect execution complete (standalone)."

    async def _handover_to_debugger(self, context: HandoverContext) -> str:
        """
        Performs the handover to the Debugger agent.
        """
        if not self.orchestrator:
            return "Handover failed: Orchestrator not set."

        (
            success,
            _,
            message,
        ) = await self.orchestrator.specialists.architect_to_debugger_handover(
            task=context.task,
            architect_output=self._output,
            code_context=context.code_context.model_dump() if context.code_context else None,
        )

        if success:  # final_context is no longer used
            return (
                f"Architect-Debugger Synergy Complete.\n"
                f"Handover ID: {context.handover_id}\n"  # Use context.handover_id directly
                f"Status: {context.status.value}\n"  # Use context.status directly
                f"History: {context.history}"  # Use context.history directly
            )
        else:
            # If handover fails, the instruction implies a retry or specific handling.
            # For now, we'll return the failure message.
            # The original instruction had `return await self._handover_to_debugger(context)` here,
            # which would lead to infinite recursion on failure.
            # Assuming the intent was to handle the failure or retry logic,
            # but for a direct translation, we'll just return the message.
            return f"Handover failed: {message}"

    def _create_blueprint(self, context: HandoverContext) -> None:
        """Create architectural blueprint sections."""
        if not self._output:
            return

        # Add blueprint sections
        self._output.add_blueprint_section(
            title=self.SYSTEM_OVERVIEW,
            content="High-level architecture with microservices pattern",
        )

        self._output.add_blueprint_section(
            title="Data Model",
            content="Relational database with normalized schema",
            dependencies=[self.SYSTEM_OVERVIEW],
        )

        self._output.add_blueprint_section(
            title="API Strategy",
            content="RESTful APIs with clear versioning strategy",
            dependencies=[self.SYSTEM_OVERVIEW, "Data Model"],
        )

        # Set metadata
        self._output.technology_stack = ["Python", "FastAPI", "PostgreSQL", "Redis"]
        self._output.design_patterns = ["Repository", "Dependency Injection", "CQRS"]
        self._output.completeness_score = 0.85
        self._output.next_steps = [
            "Debugger verification",
            "Coding implementation",
            "Testing strategy",
        ]

    def get_output(self) -> Optional[ArchitectOutput]:
        """Get the current architectural output."""
        return self._output

    def request_rework(self, context: HandoverContext, reason: str) -> str:
        """
        Handle rework request from Debugger.

        Args:
            context: The handover context with Debugger feedback
            reason: The reason for rework

        Returns:
            Response message
        """
        logger.info("📐 Architect received rework request: %s", reason)
        context.add_history(f"Rework requested: {reason}", agent="Debugger")

        # In a real implementation, this would modify the blueprint
        # based on Debugger feedback

        return f"Architect acknowledged rework request: {reason}"
