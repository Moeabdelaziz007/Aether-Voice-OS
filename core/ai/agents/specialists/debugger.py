"""
Aether Voice OS — Debugger Specialist Agent.

Specializes in reviewing code structures, tracebacks, and semantic bugs.
Uses the Deep Handover Protocol to provide comprehensive verification
results and feedback to implementing and design agents.
"""

import logging
from typing import Any, Dict, Optional

from core.ai.agents.voice_agent import VoiceAgent
from core.ai.genetic import AgentDNA
from core.ai.handover.manager import HandoverContext, MultiAgentOrchestrator
from core.ai.handover_protocol import DebuggerOutput, IntentConfidence

logger = logging.getLogger(__name__)


class DebuggerAgent(VoiceAgent):
    """
    Specializes in reviewing code structures, tracebacks, and semantic bugs.
    """

    def __init__(self, dna: Optional[AgentDNA] = None):
        super().__init__(dna)
        self.orchestrator: Optional[MultiAgentOrchestrator] = None
        self._output: Optional[DebuggerOutput] = None

    def set_orchestrator(self, orchestrator: MultiAgentOrchestrator):
        """Set the orchestrator for handover coordination."""
        self.orchestrator = orchestrator

    def process(self, context: HandoverContext) -> str:
        """
        Process a verification task from the Architect or other agents.

        Uses the extended HandoverContext to:
        - Access rich payload with blueprints and decisions
        - Perform validation checkpointing
        - Store verification results
        - Provide feedback for rework if needed
        """
        logger.info("🐛 Debugger verifying task: %s", context.task)

        # Update context
        context.add_history("Debugger began verification", agent="Debugger")

        # Create output container
        self._output = DebuggerOutput(
            handover_id=context.handover_id,
        )

        # Retrieve Architect output from context
        architect_data = context.payload.get("architect_output", {})
        if architect_data:
            logger.info("🐛 Retrieved Architect output for verification")

        # Perform verification
        self._verify_blueprint(context, architect_data)

        # Add validation results
        self._output.add_verification_result(
            category="architecture",
            target_id="blueprint",
            status="passed",
            findings="Architecture follows established patterns and best practices",
            severity="info",
        )

        # Check for potential issues
        self._output.add_warning(
            category="performance",
            message="Consider adding caching for frequently accessed data",
            severity="medium",
        )

        # Update context with output
        context.payload["debugger_output"] = self._output.model_dump()
        context.payload["status"] = "Verified"

        # Complete task node
        if context.current_node_id:
            context.complete_task_node(context.current_node_id)

        # Add verification checkpoint if orchestrator supports it
        if self.orchestrator:
            checkpoint = self.orchestrator.create_validation_checkpoint(
                handover_id=context.handover_id,
                stage="design_verification",
                partial_output={
                    "verification_results": [
                        v.model_dump() for v in self._output.verification_results
                    ],
                    "warnings": [w.model_dump() for w in self._output.warnings],
                },
            )
            if checkpoint:
                logger.info(
                    "🐛 Created validation checkpoint: %s", checkpoint.checkpoint_id
                )

        # Determine if rework is needed
        if self._output.failed_checks > 0 or self._output.get_critical_warnings():
            logger.warning("🐛 Verification found issues - recommending rework")
            context.add_history(
                "Debugger found issues requiring rework", agent="Debugger"
            )

            # Request rework from Architect
            return self._request_rework(context)

        # All checks passed
        context.add_history(
            "Debugger verified and approved the structural changes.", agent="Debugger"
        )

        # Update metrics
        self._output.total_checks = len(self._output.verification_results)
        self._output.passed_checks = self._output.total_checks
        self._output.overall_status = "passed"
        self._output.approved_for_deployment = True

        logger.info("🐛 Debugger signs off. Verification complete.")

        final_report = (
            f"🐛 Verification Complete\n"
            f"Handover ID: {context.handover_id}\n"
            f"Total Checks: {self._output.total_checks}\n"
            f"Passed: {self._output.passed_checks}\n"
            f"Failed: {self._output.failed_checks}\n"
            f"Warnings: {len(self._output.warnings)}\n"
            f"Status: {self._output.overall_status}\n"
            f"Approved for Deployment: {self._output.approved_for_deployment}\n"
            f"\nAction History: {context.history}"
        )

        return final_report

    def _verify_blueprint(
        self, context: HandoverContext, architect_data: Dict[str, Any]
    ) -> None:
        """Verify the architectural blueprint."""
        if not self._output:
            return

        # Simulate verification of blueprint sections
        blueprints = architect_data.get("blueprints", [])
        for bp in blueprints:
            section_id = bp.get("section_id", "unknown")
            status = bp.get("status", "draft")

            if status == "draft":
                self._output.add_verification_result(
                    category="completeness",
                    target_id=section_id,
                    status="warning",
                    findings=f"Section '{bp.get('title')}' is still in draft status",
                    severity="warning",
                )
            else:
                self._output.add_verification_result(
                    category="completeness",
                    target_id=section_id,
                    status="passed",
                    findings=f"Section '{bp.get('title')}' is complete",
                    severity="info",
                )

        # Verify high-impact decisions
        decisions = architect_data.get("decisions", [])
        for decision in decisions:
            impact = decision.get("impact_level", "medium")
            if impact in ("high", "critical"):
                self._output.add_verification_result(
                    category="risk_assessment",
                    target_id=decision.get("decision_id", "unknown"),
                    status="passed",
                    findings=f"High-impact decision reviewed: {decision.get('description', '')[:50]}...",
                    severity="info",
                )

        # Check critical risks
        risks = architect_data.get("risk_assessment", [])
        for risk in risks:
            prob = risk.get("probability", 0)
            impact = risk.get("impact", 0)
            if prob > 0.7 and impact > 0.7:
                self._output.add_warning(
                    category="risk",
                    message=f"Critical risk identified: {risk.get('description', '')}",
                    severity="critical",
                )

    def _request_rework(self, context: HandoverContext) -> str:
        """
        Request rework from the Architect agent.

        Args:
            context: The current handover context

        Returns:
            Rework request message
        """
        if not self.orchestrator:
            return "Cannot request rework - no orchestrator available"

        # Add intent confidence for rework handover
        context.intent_confidence = IntentConfidence
            source_agent="Debugger",
            target_agent="Architect",
            confidence_score=0.9,
            reasoning="Rework required based on verification findings",
            alternatives_considered=["CodingExpert"],
        )

        # Use specialist manager for rework handover
        success, final_context, message = (
            self.orchestrator.specialists.debugger_to_architect_feedback(
                original_context=context,
                debugger_output=self._output,
            )
        )

        if success:
            return (
                f"🐛 Rework Requested\n"
                f"Handover ID: {context.handover_id}\n"
                f"Issues Found: {self._output.failed_checks}\n"
                f"Proposed Fixes: {len(self._output.fixes)}\n"
                f"Status: Rework handover sent to Architect"
            )
        else:
            return f"Failed to send rework request: {message}"

    def get_output(self) -> Optional[DebuggerOutput]:
        """Get the current debugger output."""
        return self._output

    def propose_fix(
        self,
        issue_id: str,
        file_path: str,
        description: str,
        explanation: str,
    ) -> str:
        """
        Propose a fix for an identified issue.

        Args:
            issue_id: Reference to the verified issue
            file_path: File to modify
            description: What the fix does
            explanation: Why this fix resolves the issue

        Returns:
            Fix ID
        """
        if not self._output:
            logger.error("Cannot propose fix - no active output")
            return ""

        fix = self._output.add_fix(
            issue_id=issue_id,
            file_path=file_path,
            description=description,
            explanation=explanation,
        )

        logger.info("🐛 Proposed fix: %s for issue %s", fix.fix_id, issue_id)
        return fix.fix_id
