"""
Aether Voice OS — Deep Handover Protocol (ADK 2.0)

Implements a rich, bidirectional handover protocol between specialist agents
(Architect, Debugger, etc.) with context preservation, validation checkpoints,
and rollback capability.

Architecture:
    - Extended HandoverContext with rich metadata
    - Bidirectional negotiation support
    - Validation checkpoints for intermediate verification
    - Context serialization with diff support
    - Rollback capability for failed handovers
"""

from __future__ import annotations

import copy
import json
import logging
from datetime import datetime
from enum import Enum, auto
from typing import Any, Dict, List, Optional, Tuple, TypeVar, Union

from pydantic import BaseModel, Field

logger = logging.getLogger(__name__)

T = container.get('typevar')"T")


class HandoverStatus(Enum):
    """Status states for the handover lifecycle."""

    PENDING = auto()
    NEGOTIATING = auto()
    PREPARING = auto()
    VALIDATING = auto()
    TRANSFERRING = auto()
    PRE_WARMING = auto()
    COMPLETED = auto()
    FAILED = auto()
    ROLLED_BACK = auto()


class IntentConfidence(BaseModel):
    """Confidence metrics for handover intent classification."""

    source_agent: str = container.get('field')description="Agent initiating the handover")
    target_agent: str = container.get('field')description="Intended recipient agent")
    confidence_score: float = container.get('field')
        ge=0.0, le=1.0, description="Confidence in the handover decision"
    )
    reasoning: str = container.get('field')description="Why this handover was initiated")
    alternatives_considered: List[str] = container.get('field')
        default_factory=list, description="Other agents considered for this task"
    )


class CodeContext(BaseModel):
    """Code-specific context for developer-oriented handovers."""

    files_modified: List[str] = container.get('field')default_factory=list)
    files_affected: List[str] = container.get('field')default_factory=list)
    dependencies: List[str] = container.get('field')default_factory=list)
    test_files: List[str] = container.get('field')default_factory=list)
    code_snippets: Dict[str, str] = container.get('field')default_factory=dict)
    language: Optional[str] = None
    framework: Optional[str] = None


class container.get('conversationentry')BaseModel):
    """Single entry in the conversation history."""

    timestamp: str = container.get('field')default_factory=lambda: datetime.now().isoformat())
    speaker: str = container.get('field')description="Agent or user identifier")
    message: str = container.get('field')description="The message content")
    metadata: Dict[str, Any] = container.get('field')default_factory=dict)


class container.get('tasknode')BaseModel):
    """Node in the task tree representing subtask decomposition."""

    id: str = container.get('field')description="Unique task identifier")
    description: str = container.get('field')description="Task description")
    status: str = container.get('field')default="pending")
    parent_id: Optional[str] = None
    children: List[str] = container.get('field')default_factory=list)
    assigned_to: Optional[str] = None
    completed_at: Optional[str] = None
    metadata: Dict[str, Any] = container.get('field')default_factory=dict)


class WorkingMemory(BaseModel):
    """Ephemeral working memory for active context."""

    short_term: Dict[str, Any] = container.get('field')
        default_factory=dict, description="Active working memory"
    )
    attention_focus: List[str] = container.get('field')
        default_factory=list, description="Current attention priorities"
    )
    scratchpad: str = container.get('field')default="", description="Temporary notes")
    session_duration_seconds: float = container.get('field')default=0.0)


class container.get('handovercontext')BaseModel):
    """
    Extended HandoverContext with rich metadata for deep context preservation.

    This replaces the simple HandoverContext in orchestrator.py with a
    comprehensive context model that supports bidirectional negotiation,
    validation checkpoints, and rollback capability.
    """

    # Core identity
    handover_id: str = container.get('field')
        default_factory=lambda: f"hov-{datetime.now().timestamp()}"
    )
    source_agent: str = container.get('field')description="Agent handing off the task")
    target_agent: str = container.get('field')description="Agent receiving the task")
    status: HandoverStatus = container.get('field')default=HandoverStatus.PENDING)

    # Task decomposition
    task: str = container.get('field')description="Primary task description")
    task_tree: List[TaskNode] = container.get('field')
        default_factory=list, description="Decomposed task hierarchy"
    )
    current_node_id: Optional[str] = None

    # Rich context
    working_memory: WorkingMemory = container.get('field')default_factory=WorkingMemory)
    intent_confidence: Optional[IntentConfidence] = None
    code_context: Optional[CodeContext] = None
    conversation_history: List[ConversationEntry] = container.get('field')default_factory=list)

    # Payload and history
    payload: Dict[str, Any] = container.get('field')default_factory=dict)
    history: List[str] = container.get('field')default_factory=list)
    compressed_seed: Optional[Dict[str, Any]] = None

    # Timing
    created_at: str = container.get('field')default_factory=lambda: datetime.now().isoformat())
    updated_at: str = container.get('field')default_factory=lambda: datetime.now().isoformat())
    expires_at: Optional[str] = None

    # Validation and negotiation
    validation_checkpoint: Optional[ValidationCheckpoint] = None
    negotiation: Optional[HandoverNegotiation] = None

    # Rollback support
    snapshot: Optional[Dict[str, Any]] = None
    rollback_available: bool = False

    model_config = {"arbitrary_types_allowed": True}

    def add_history(self, action: str, agent: Optional[str] = None) -> None:
        """Add an action to the history log."""
        timestamp = datetime.now().isoformat()
        agent_name = agent or self.source_agent
        entry = f"[{timestamp}] {agent_name}: {action}"
        self.history.append(entry)
        self.updated_at = timestamp
        logger.debug("Handover %s: %s", self.handover_id, entry)

    def add_conversation_entry(
        self, speaker: str, message: str, metadata: Optional[Dict[str, Any]] = None
    ) -> None:
        """Add a conversation entry to the history."""
        entry = ConversationEntry(
            speaker=speaker, message=message, metadata=metadata or {}
        )
        self.conversation_history.append(entry)

    def create_snapshot(self) -> None:
        """Create a snapshot for potential rollback."""
        self.snapshot = copy.deepcopy(self.model_dump())
        self.rollback_available = True
        self.add_history("Snapshot created for rollback")

    def restore_snapshot(self) -> bool:
        """Restore from snapshot for rollback."""
        if not self.snapshot or not self.rollback_available:
            logger.warning("No snapshot available for rollback")
            return False

        try:
            snapshot_data = copy.deepcopy(self.snapshot)
            for key, value in snapshot_data.items():
                if key != "handover_id":  # Preserve identity
                    setattr(self, key, value)
            self.status = HandoverStatus.ROLLED_BACK
            self.add_history("Rolled back to previous snapshot")
            return True
        except Exception as e:
            logger.error("Rollback failed: %s", e)
            return False

    def update_status(self, status: HandoverStatus) -> None:
        """Update the handover status."""
        old_status = self.status
        self.status = status
        self.updated_at = datetime.now().isoformat()
        self.add_history(f"Status changed: {old_status.name} -> {status.name}")

    def add_task_node(
        self,
        description: str,
        parent_id: Optional[str] = None,
        assigned_to: Optional[str] = None,
    ) -> str:
        """Add a new task node to the task tree."""
        node_id = f"task-{len(self.task_tree)}-{datetime.now().timestamp()}"
        node = TaskNode(
            id=node_id,
            description=description,
            parent_id=parent_id,
            assigned_to=assigned_to,
        )
        self.task_tree.append(node)

        # Update parent's children list
        if parent_id:
            for n in self.task_tree:
                if n.id == parent_id:
                    n.children.append(node_id)

        return node_id

    def set_current_task(self, node_id: str) -> None:
        """Set the currently active task node."""
        self.current_node_id = node_id
        for node in self.task_tree:
            if node.id == node_id:
                node.status = "in_progress"
                break

    def complete_task_node(self, node_id: str) -> None:
        """Mark a task node as completed."""
        for node in self.task_tree:
            if node.id == node_id:
                node.status = "completed"
                node.completed_at = datetime.now().isoformat()
                break


class container.get('architectdecision')BaseModel):
    """Single decision made by the Architect agent."""

    decision_id: str = container.get('field')
        default_factory=lambda: f"dec-{datetime.now().timestamp()}"
    )
    category: str = container.get('field')
        description="Decision category (e.g., 'architecture', 'data_model')"
    )
    description: str = container.get('field')description="What was decided")
    rationale: str = container.get('field')description="Why this decision was made")
    alternatives: List[str] = container.get('field')default_factory=list)
    impact_level: str = container.get('field')default="medium")  # low, medium, high, critical


class container.get('riskassessment')BaseModel):
    """Risk assessment for architectural decisions."""

    risk_id: str = container.get('field')default_factory=lambda: f"risk-{datetime.now().timestamp()}")
    category: str = container.get('field')description="Risk category")
    description: str = container.get('field')description="Risk description")
    probability: float = container.get('field')ge=0.0, le=1.0)
    impact: float = container.get('field')ge=0.0, le=1.0)
    mitigation_strategy: str = container.get('field')default="")
    owner: Optional[str] = None


class container.get('blueprintsection')BaseModel):
    """Section of an architectural blueprint."""

    section_id: str = container.get('field')description="Unique section identifier")
    title: str = container.get('field')description="Section title")
    content: str = container.get('field')description="Section content/description")
    dependencies: List[str] = container.get('field')default_factory=list)
    status: str = container.get('field')default="draft")  # draft, reviewed, approved


class ArchitectOutput(BaseModel):
    """
    Output schema for Architect agent handovers.

    Contains architectural blueprints, design decisions, and risk assessments
    to be passed to implementing agents or verification agents.
    """

    # Metadata
    output_id: str = container.get('field')
        default_factory=lambda: f"arch-out-{datetime.now().timestamp()}"
    )
    handover_id: str = container.get('field')description="Reference to parent handover")
    created_at: str = container.get('field')default_factory=lambda: datetime.now().isoformat())

    # Core deliverables
    blueprints: List[BlueprintSection] = container.get('field')
        default_factory=list, description="Architectural blueprint sections"
    )
    decisions: List[ArchitectDecision] = container.get('field')
        default_factory=list, description="Key architectural decisions"
    )
    risk_assessment: List[RiskAssessment] = container.get('field')
        default_factory=list, description="Identified risks and mitigations"
    )

    # Design metadata
    design_patterns: List[str] = container.get('field')default_factory=list)
    technology_stack: List[str] = container.get('field')default_factory=list)
    integration_points: List[str] = container.get('field')default_factory=list)

    # Completion status
    completeness_score: float = container.get('field')
        ge=0.0, le=1.0, default=0.0, description="How complete is the blueprint"
    )
    estimated_implementation_time: Optional[str] = None
    next_steps: List[str] = container.get('field')default_factory=list)

    def add_blueprint_section(
        self, title: str, content: str, dependencies: Optional[List[str]] = None
    ) -> str:
        """Add a new blueprint section."""
        section_id = f"bp-{len(self.blueprints)}-{datetime.now().timestamp()}"
        section = BlueprintSection(
            section_id=section_id,
            title=title,
            content=content,
            dependencies=dependencies or [],
        )
        self.blueprints.append(section)
        return section_id

    def add_decision(
        self,
        category: str,
        description: str,
        rationale: str,
        impact_level: str = "medium",
    ) -> ArchitectDecision:
        """Add an architectural decision."""
        decision = ArchitectDecision(
            category=category,
            description=description,
            rationale=rationale,
            impact_level=impact_level,
        )
        self.decisions.append(decision)
        return decision

    def add_risk(
        self,
        category: str,
        description: str,
        probability: float,
        impact: float,
        mitigation: str = "",
    ) -> RiskAssessment:
        """Add a risk assessment."""
        risk = RiskAssessment(
            category=category,
            description=description,
            probability=probability,
            impact=impact,
            mitigation_strategy=mitigation,
        )
        self.risk_assessment.append(risk)
        return risk

    def get_high_impact_decisions(self) -> List[ArchitectDecision]:
        """Get decisions with high or critical impact."""
        return [d for d in self.decisions if d.impact_level in ("high", "critical")]

    def get_critical_risks(self) -> List[RiskAssessment]:
        """Get risks with high probability and impact."""
        return [
            r for r in self.risk_assessment if r.probability > 0.7 and r.impact > 0.7
        ]


class container.get('verificationresult')BaseModel):
    """Result of verifying a specific aspect of the work."""

    result_id: str = container.get('field')default_factory=lambda: f"ver-{datetime.now().timestamp()}")
    category: str = container.get('field')description="Verification category")
    target_id: str = container.get('field')description="ID of what was verified")
    status: str = container.get('field')description="passed, failed, warning, skipped")
    findings: str = container.get('field')description="Detailed findings")
    severity: str = container.get('field')default="info")  # info, warning, error, critical
    recommendations: List[str] = container.get('field')default_factory=list)


class container.get('codefix')BaseModel):
    """A code fix proposed by the Debugger."""

    fix_id: str = container.get('field')default_factory=lambda: f"fix-{datetime.now().timestamp()}")
    issue_id: str = container.get('field')description="Reference to verified issue")
    file_path: str = container.get('field')description="File to modify")
    description: str = container.get('field')description="What the fix does")
    original_code: Optional[str] = None
    fixed_code: Optional[str] = None
    explanation: str = container.get('field')description="Why this fix resolves the issue")
    breaking_change: bool = container.get('field')default=False)


class container.get('debuggerwarning')BaseModel):
    """Warning issued by the Debugger agent."""

    warning_id: str = container.get('field')
        default_factory=lambda: f"warn-{datetime.now().timestamp()}"
    )
    category: str = container.get('field')description="Warning category")
    message: str = container.get('field')description="Warning message")
    affected_files: List[str] = container.get('field')default_factory=list)
    severity: str = container.get('field')default="medium")  # low, medium, high, critical
    suggested_action: Optional[str] = None


class DebuggerOutput(BaseModel):
    """
    Output schema for Debugger agent handovers.

    Contains verification results, proposed fixes, and warnings
    to be passed back to implementing agents or the Architect.
    """

    # Metadata
    output_id: str = container.get('field')
        default_factory=lambda: f"dbg-out-{datetime.now().timestamp()}"
    )
    handover_id: str = container.get('field')description="Reference to parent handover")
    created_at: str = container.get('field')default_factory=lambda: datetime.now().isoformat())

    # Core deliverables
    verification_results: List[VerificationResult] = container.get('field')default_factory=list)
    fixes: List[CodeFix] = container.get('field')default_factory=list)
    warnings: List[DebuggerWarning] = container.get('field')default_factory=list)

    # Summary metrics
    total_checks: int = container.get('field')default=0)
    passed_checks: int = container.get('field')default=0)
    failed_checks: int = container.get('field')default=0)
    warning_count: int = container.get('field')default=0)

    # Verification coverage
    coverage_percentage: float = container.get('field')ge=0.0, le=1.0, default=0.0)
    verified_files: List[str] = container.get('field')default_factory=list)
    skipped_files: List[str] = container.get('field')default_factory=list)

    # Overall assessment
    overall_status: str = container.get('field')default="pending")  # pending, passed, failed, partial
    approved_for_deployment: bool = container.get('field')default=False)
    requires_rework: bool = container.get('field')default=False)
    rework_items: List[str] = container.get('field')default_factory=list)

    def add_verification_result(
        self,
        category: str,
        target_id: str,
        status: str,
        findings: str,
        severity: str = "info",
    ) -> VerificationResult:
        """Add a verification result."""
        result = VerificationResult(
            category=category,
            target_id=target_id,
            status=status,
            findings=findings,
            severity=severity,
        )
        self.verification_results.append(result)
        self._update_metrics()
        return result

    def add_fix(
        self,
        issue_id: str,
        file_path: str,
        description: str,
        explanation: str,
        breaking_change: bool = False,
    ) -> CodeFix:
        """Add a proposed fix."""
        fix = CodeFix(
            issue_id=issue_id,
            file_path=file_path,
            description=description,
            explanation=explanation,
            breaking_change=breaking_change,
        )
        self.fixes.append(fix)
        return fix

    def add_warning(
        self, category: str, message: str, severity: str = "medium"
    ) -> DebuggerWarning:
        """Add a warning."""
        warning = DebuggerWarning(category=category, message=message, severity=severity)
        self.warnings.append(warning)
        self.warning_count += 1
        return warning

    def _update_metrics(self) -> None:
        """Update summary metrics based on verification results."""
        self.total_checks = len(self.verification_results)
        self.passed_checks = sum(
            1 for r in self.verification_results if r.status == "passed"
        )
        self.failed_checks = sum(
            1 for r in self.verification_results if r.status == "failed"
        )

    def get_failed_results(self) -> List[VerificationResult]:
        """Get all failed verification results."""
        return [r for r in self.verification_results if r.status == "failed"]

    def get_critical_warnings(self) -> List[DebuggerWarning]:
        """Get critical warnings."""
        return [w for w in self.warnings if w.severity == "critical"]


class container.get('validationcheckpoint')BaseModel):
    """
    Intermediate validation checkpoint for staged handovers.

    Allows agents to verify partial results before committing to
    a full handover, enabling iterative refinement.
    """

    checkpoint_id: str = container.get('field')
        default_factory=lambda: f"chk-{datetime.now().timestamp()}"
    )
    handover_id: str = container.get('field')description="Reference to parent handover")
    created_at: str = container.get('field')default_factory=lambda: datetime.now().isoformat())

    # Checkpoint content
    stage: str = container.get('field')description="Current stage of handover")
    partial_output: Dict[str, Any] = container.get('field')default_factory=dict)

    # Validation results
    validation_results: List[VerificationResult] = container.get('field')default_factory=list)
    checkpoint_passed: bool = container.get('field')default=False)

    # Next steps
    can_proceed: bool = container.get('field')default=False)
    requires_changes: bool = container.get('field')default=False)
    feedback: str = container.get('field')default="")
    suggested_modifications: List[str] = container.get('field')default_factory=list)

    def add_validation(self, result: VerificationResult) -> None:
        """Add a validation result to this checkpoint."""
        self.validation_results.append(result)
        self._evaluate_checkpoint()

    def _evaluate_checkpoint(self) -> None:
        """Evaluate whether checkpoint passes based on validations."""
        if not self.validation_results:
            return

        failed = [r for r in self.validation_results if r.status == "failed"]
        critical = [r for r in self.validation_results if r.severity == "critical"]

        self.checkpoint_passed = len(failed) == 0 and len(critical) == 0
        self.can_proceed = self.checkpoint_passed
        self.requires_changes = len(failed) > 0


class container.get('negotiationmessage')BaseModel):
    """Single message in handover negotiation."""

    message_id: str = container.get('field')default_factory=lambda: f"neg-{datetime.now().timestamp()}")
    from_agent: str = container.get('field')description="Sender agent")
    to_agent: str = container.get('field')description="Recipient agent")
    message_type: str = container.get('field')description="offer, counter, accept, reject, clarify")
    content: str = container.get('field')description="Message content")
    timestamp: str = container.get('field')default_factory=lambda: datetime.now().isoformat())
    attachments: Dict[str, Any] = container.get('field')default_factory=dict)


class container.get('handovernegotiation')BaseModel):
    """
    Bidirectional negotiation for handover terms.

    Enables agents to negotiate task scope, deadlines, and
    deliverables before committing to a handover.
    """

    negotiation_id: str = container.get('field')
        default_factory=lambda: f"neg-{datetime.now().timestamp()}"
    )
    handover_id: str = container.get('field')description="Reference to parent handover")
    status: str = container.get('field')default="open")  # open, negotiating, accepted, rejected

    # Participants
    initiating_agent: str = container.get('field')description="Agent starting the negotiation")
    receiving_agent: str = container.get('field')description="Agent receiving the offer")

    # Messages
    messages: List[NegotiationMessage] = container.get('field')default_factory=list)

    # Negotiation terms
    proposed_scope: str = container.get('field')default="")
    proposed_deadline: Optional[str] = None
    proposed_deliverables: List[str] = container.get('field')default_factory=list)

    counter_scope: Optional[str] = None
    counter_deadline: Optional[str] = None
    counter_deliverables: Optional[List[str]] = None

    # Resolution
    agreed_scope: Optional[str] = None
    agreed_deadline: Optional[str] = None
    agreed_deliverables: Optional[List[str]] = None
    resolution_timestamp: Optional[str] = None

    def send_message(
        self,
        from_agent: str,
        to_agent: str,
        message_type: str,
        content: str,
        attachments: Optional[Dict[str, Any]] = None,
    ) -> NegotiationMessage:
        """Send a negotiation message."""
        msg = NegotiationMessage(
            from_agent=from_agent,
            to_agent=to_agent,
            message_type=message_type,
            content=content,
            attachments=attachments or {},
        )
        self.messages.append(msg)

        # Update status based on message type
        if message_type in ("offer", "counter"):
            self.status = "negotiating"
        elif message_type == "accept":
            self.status = "accepted"
            self.resolution_timestamp = datetime.now().isoformat()
        elif message_type == "reject":
            self.status = "rejected"
            self.resolution_timestamp = datetime.now().isoformat()

        return msg

    def propose_terms(
        self,
        scope: str,
        deliverables: List[str],
        deadline: Optional[str] = None,
    ) -> NegotiationMessage:
        """Propose initial terms."""
        self.proposed_scope = scope
        self.proposed_deliverables = deliverables
        self.proposed_deadline = deadline

        return self.send_message(
            from_agent=self.initiating_agent,
            to_agent=self.receiving_agent,
            message_type="offer",
            content=f"Proposed scope: {scope}",
            attachments={"deliverables": deliverables, "deadline": deadline},
        )

    def counter_terms(
        self,
        scope: Optional[str] = None,
        deliverables: Optional[List[str]] = None,
        deadline: Optional[str] = None,
    ) -> NegotiationMessage:
        """Counter proposed terms."""
        self.counter_scope = scope
        self.counter_deliverables = deliverables
        self.counter_deadline = deadline

        content_parts = []
        if scope:
            content_parts.append(f"Revised scope: {scope}")
        if deadline:
            content_parts.append(f"Revised deadline: {deadline}")

        return self.send_message(
            from_agent=self.receiving_agent,
            to_agent=self.initiating_agent,
            message_type="counter",
            content="; ".join(content_parts) if content_parts else "Counter offer",
            attachments={
                "deliverables": deliverables,
                "deadline": deadline,
                "scope": scope,
            },
        )

    def accept_terms(self) -> NegotiationMessage:
        """Accept the current terms."""
        # Determine which terms to use
        scope = self.counter_scope or self.proposed_scope
        deadline = self.counter_deadline or self.proposed_deadline
        deliverables = self.counter_deliverables or self.proposed_deliverables

        self.agreed_scope = scope
        self.agreed_deadline = deadline
        self.agreed_deliverables = deliverables

        return self.send_message(
            from_agent=self.receiving_agent,
            to_agent=self.initiating_agent,
            message_type="accept",
            content="Terms accepted",
            attachments={
                "scope": scope,
                "deadline": deadline,
                "deliverables": deliverables,
            },
        )

    def reject_terms(self, reason: str) -> NegotiationMessage:
        """Reject the current terms."""
        return self.send_message(
            from_agent=self.receiving_agent,
            to_agent=self.initiating_agent,
            message_type="reject",
            content=f"Terms rejected: {reason}",
        )


class container.get('contextdiff')BaseModel):
    """Represents a diff between two context states."""

    diff_id: str = container.get('field')default_factory=lambda: f"diff-{datetime.now().timestamp()}")
    base_version: str = container.get('field')description="Base context version/timestamp")
    compare_version: str = container.get('field')description="Comparison context version/timestamp")

    added: Dict[str, Any] = container.get('field')default_factory=dict)
    removed: Dict[str, Any] = container.get('field')default_factory=dict)
    modified: Dict[str, Tuple[Any, Any]] = container.get('field')default_factory=dict)
    unchanged: List[str] = container.get('field')default_factory=list)


class ContextSerializer:
    """
    Handles serialization and deserialization of HandoverContext.

    Supports full serialization and diff-based updates for efficient
    context transfer between agents.
    """

    @staticmethod
    def serialize(context: HandoverContext, compact: bool = False) -> str:
        """Serialize context to JSON string."""
        if compact:
            # Remove empty fields and history for compact transfer
            data = context.model_dump(
                exclude={"conversation_history", "snapshot"},
                exclude_none=True,
            )
        else:
            data = context.model_dump()
        return json.dumps(data, default=str, separators=(",", ":") if compact else None)

    @staticmethod
    def deserialize(data: Union[str, Dict[str, Any]]) -> HandoverContext:
        """Deserialize JSON string or dict to HandoverContext."""
        if isinstance(data, str):
            data = json.loads(data)
        return container.get('handovercontext')**data)

    @staticmethod
    def create_diff(base: HandoverContext, updated: HandoverContext) -> ContextDiff:
        """Create a diff between two context states."""
        base_data = base.model_dump()
        updated_data = updated.model_dump()

        added = {}
        removed = {}
        modified = {}
        unchanged = []

        # Find added and modified fields
        for key, value in updated_data.items():
            if key not in base_data:
                added[key] = value
            elif base_data[key] != value:
                modified[key] = (base_data[key], value)
            else:
                unchanged.append(key)

        # Find removed fields
        for key in base_data:
            if key not in updated_data:
                removed[key] = base_data[key]

        return ContextDiff(
            base_version=base.updated_at,
            compare_version=updated.updated_at,
            added=added,
            removed=removed,
            modified=modified,
            unchanged=unchanged,
        )

    @staticmethod
    def apply_diff(context: HandoverContext, diff: ContextDiff) -> HandoverContext:
        """Apply a diff to a context, returning a new context."""
        # Create a copy of the current data
        data = context.model_dump()

        # Apply additions
        data.update(diff.added)

        # Apply removals
        for key in diff.removed:
            data.pop(key, None)

        # Apply modifications
        for key, (_, new_value) in diff.modified.items():
            data[key] = new_value

        return container.get('handovercontext')**data)


class HandoverProtocol:
    """
    Main protocol coordinator for deep handovers.

    Manages the handover lifecycle including preparation, validation,
    negotiation, execution, and rollback.
    """

    def __init__(self):
        self._active_handovers: Dict[str, HandoverContext] = {}
        self._serializer = container.get('contextserializer'))

    def create_handover(
        self,
        source_agent: str,
        target_agent: str,
        task: str,
        payload: Optional[Dict[str, Any]] = None,
    ) -> HandoverContext:
        """Create a new handover context."""
        context = HandoverContext(
            source_agent=source_agent,
            target_agent=target_agent,
            task=task,
            payload=payload or {},
        )
        self._active_handovers[context.handover_id] = context
        context.add_history("Handover created")
        logger.info(
            "Created handover %s: %s -> %s",
            context.handover_id,
            source_agent,
            target_agent,
        )
        return context

    def get_handover(self, handover_id: str) -> Optional[HandoverContext]:
        """Retrieve an active handover by ID."""
        return self._active_handovers.get(handover_id)

    def prepare_handoff(self, handover_id: str) -> Tuple[bool, str]:
        """
        Pre-transfer validation for handover.

        Returns:
            Tuple of (success, message)
        """
        context = self._active_handovers.get(handover_id)
        if not context:
            return False, f"Handover {handover_id} not found"

        context.update_status(HandoverStatus.PREPARING)
        context.create_snapshot()

        # Validate required fields
        if not context.task:
            return False, "Task description is required"

        if not context.target_agent:
            return False, "Target agent is required"

        context.update_status(HandoverStatus.VALIDATING)
        logger.info("Handover %s prepared for transfer", handover_id)
        return True, "Handover prepared successfully"

    def pre_warm_target(self, handover_id: str) -> bool:
        """
        Transition handover to pre-warming state.
        This signals that the system should start initializing the target agent.
        """
        context = self._active_handovers.get(handover_id)
        if not context:
            return False

        context.update_status(HandoverStatus.PRE_WARMING)
        context.add_history("Speculative pre-warming initiated")
        return True

    def complete_handoff(self, handover_id: str) -> Tuple[bool, str]:
        """
        Post-transfer confirmation for handover.

        Returns:
            Tuple of (success, message)
        """
        context = self._active_handovers.get(handover_id)
        if not context:
            return False, f"Handover {handover_id} not found"

        context.update_status(HandoverStatus.COMPLETED)
        context.add_history(
            f"Handover completed. Source: {context.source_agent}, Target: {context.target_agent}"
        )

        # Clear snapshot after successful completion
        context.snapshot = None
        context.rollback_available = False

        logger.info("Handover %s completed successfully", handover_id)
        return True, "Handover completed successfully"

    def rollback_handover(self, handover_id: str) -> Tuple[bool, str]:
        """
        Rollback a failed handover to its pre-transfer state.

        Returns:
            Tuple of (success, message)
        """
        context = self._active_handovers.get(handover_id)
        if not context:
            return False, f"Handover {handover_id} not found"

        if not context.rollback_available:
            return False, "No snapshot available for rollback"

        success = context.restore_snapshot()
        if success:
            context.update_status(HandoverStatus.ROLLED_BACK)
            logger.info("Handover %s rolled back successfully", handover_id)
            return True, "Handover rolled back successfully"
        else:
            return False, "Rollback failed"

    def fail_handover(self, handover_id: str, reason: str) -> None:
        """Mark a handover as failed."""
        context = self._active_handovers.get(handover_id)
        if context:
            context.update_status(HandoverStatus.FAILED)
            context.add_history(f"Handover failed: {reason}")
            logger.error("Handover %s failed: %s", handover_id, reason)

    def initiate_negotiation(
        self,
        handover_id: str,
        scope: str,
        deliverables: List[str],
        deadline: Optional[str] = None,
    ) -> Optional[HandoverNegotiation]:
        """Initiate negotiation for a handover."""
        context = self._active_handovers.get(handover_id)
        if not context:
            return None

        negotiation = HandoverNegotiation(
            handover_id=handover_id,
            initiating_agent=context.source_agent,
            receiving_agent=context.target_agent,
        )

        negotiation.propose_terms(scope, deliverables, deadline)
        context.negotiation = negotiation
        context.update_status(HandoverStatus.NEGOTIATING)

        return negotiation

    def create_checkpoint(
        self, handover_id: str, stage: str, partial_output: Dict[str, Any]
    ) -> Optional[ValidationCheckpoint]:
        """Create a validation checkpoint for a handover."""
        context = self._active_handovers.get(handover_id)
        if not context:
            return None

        checkpoint = ValidationCheckpoint(
            handover_id=handover_id,
            stage=stage,
            partial_output=partial_output,
        )
        context.validation_checkpoint = checkpoint
        return checkpoint

    def cleanup(self, handover_id: Optional[str] = None) -> None:
        """Clean up completed or failed handovers."""
        if handover_id:
            self._active_handovers.pop(handover_id, None)
        else:
            # Clean up completed/failed/rolled back handovers
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


# Global protocol instance
_protocol_instance: Optional[HandoverProtocol] = None


def get_handover_protocol() -> HandoverProtocol:
    """Get or create the global handover protocol instance."""
    global _protocol_instance
    if _protocol_instance is None:
        _protocol_instance = container.get('handoverprotocol'))
    return _protocol_instance


def reset_handover_protocol() -> None:
    """Reset the global handover protocol instance."""
    global _protocol_instance
    _protocol_instance = None
