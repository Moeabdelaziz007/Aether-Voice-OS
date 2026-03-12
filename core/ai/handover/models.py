from __future__ import annotations
import copy
import logging
from datetime import datetime
from enum import Enum, auto
from typing import Any, Dict, List, Optional, Tuple, TypeVar, Union
from pydantic import BaseModel, Field

logger = logging.getLogger(__name__)

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
    source_agent: str = Field(description="Agent initiating the handover")
    target_agent: str = Field(description="Intended recipient agent")
    confidence_score: float = Field(ge=0.0, le=1.0, description="Confidence in the handover decision")
    reasoning: str = Field(description="Why this handover was initiated")
    alternatives_considered: List[str] = Field(default_factory=list, description="Other agents considered for this task")

class CodeContext(BaseModel):
    """Code-specific context for developer-oriented handovers."""
    files_modified: List[str] = Field(default_factory=list)
    files_affected: List[str] = Field(default_factory=list)
    dependencies: List[str] = Field(default_factory=list)
    test_files: List[str] = Field(default_factory=list)
    code_snippets: Dict[str, str] = Field(default_factory=dict)
    language: Optional[str] = None
    framework: Optional[str] = None

class ConversationEntry(BaseModel):
    """Single entry in the conversation history."""
    timestamp: str = Field(default_factory=lambda: datetime.now().isoformat())
    speaker: str = Field(description="Agent or user identifier")
    message: str = Field(description="The message content")
    metadata: Dict[str, Any] = Field(default_factory=dict)

class TaskNode(BaseModel):
    """Node in the task tree representing subtask decomposition."""
    id: str = Field(description="Unique task identifier")
    description: str = Field(description="Task description")
    status: str = Field(default="pending")
    parent_id: Optional[str] = None
    children: List[str] = Field(default_factory=list)
    assigned_to: Optional[str] = None
    completed_at: Optional[str] = None
    metadata: Dict[str, Any] = Field(default_factory=dict)

class WorkingMemory(BaseModel):
    """Ephemeral working memory for active context."""
    short_term: Dict[str, Any] = Field(default_factory=dict, description="Active working memory")
    attention_focus: List[str] = Field(default_factory=list, description="Current attention priorities")
    scratchpad: str = Field(default="", description="Temporary notes")
    session_duration_seconds: float = Field(default=0.0)

class HandoverContext(BaseModel):
    """Deep context preservation model for handovers."""
    handover_id: str = Field(default_factory=lambda: f"hov-{datetime.now().timestamp()}")
    source_agent: str = Field(description="Agent handing off the task")
    target_agent: str = Field(description="Agent receiving the task")
    galaxy_id: str = Field(default="Genesis", description="Logical workspace galaxy namespace")
    orbit_lane: Optional[str] = Field(None, description="Orbital lane: inner/mid/outer")
    gravity_score: Optional[float] = Field(None, ge=0.0, le=1.0, description="Routing priority weight")
    focus_target: Optional[str] = Field(None, description="Target planet/agent for focus")
    status: HandoverStatus = Field(default=HandoverStatus.PENDING)
    task: str = Field(description="Primary task description")
    task_tree: List[TaskNode] = Field(default_factory=list, description="Decomposed task hierarchy")
    current_node_id: Optional[str] = None
    working_memory: WorkingMemory = Field(default_factory=WorkingMemory)
    intent_confidence: Optional[IntentConfidence] = None
    code_context: Optional[CodeContext] = None
    conversation_history: List[ConversationEntry] = Field(default_factory=list)
    payload: Dict[str, Any] = Field(default_factory=dict)
    history: List[str] = Field(default_factory=list)
    compressed_seed: Optional[Dict[str, Any]] = None
    created_at: str = Field(default_factory=lambda: datetime.now().isoformat())
    updated_at: str = Field(default_factory=lambda: datetime.now().isoformat())
    expires_at: Optional[str] = None
    validation_checkpoint: Optional[Any] = None  # Circ import avoidance
    negotiation: Optional[Any] = None  # Circ import avoidance
    snapshot: Optional[Dict[str, Any]] = None
    rollback_available: bool = False

    model_config = {"arbitrary_types_allowed": True}

    def add_history(self, action: str, agent: Optional[str] = None) -> None:
        timestamp = datetime.now().isoformat()
        agent_name = agent or self.source_agent
        entry = f"[{timestamp}] {agent_name}: {action}"
        self.history.append(entry)
        self.updated_at = timestamp

    def add_conversation_entry(self, speaker: str, message: str, metadata: Optional[Dict[str, Any]] = None) -> None:
        entry = ConversationEntry(speaker=speaker, message=message, metadata=metadata or {})
        self.conversation_history.append(entry)

    def create_snapshot(self) -> None:
        self.snapshot = copy.deepcopy(self.model_dump())
        self.rollback_available = True
        self.add_history("Snapshot created for rollback")

    def restore_snapshot(self) -> bool:
        if not self.snapshot or not self.rollback_available:
            return False
        try:
            snapshot_data = copy.deepcopy(self.snapshot)
            for key, value in snapshot_data.items():
                if key != "handover_id":
                    setattr(self, key, value)
            self.status = HandoverStatus.ROLLED_BACK
            self.add_history("Rolled back to previous snapshot")
            return True
        except Exception as e:
            logger.error("Rollback failed: %s", e)
            return False

    def update_status(self, status: HandoverStatus) -> None:
        old_status = self.status
        self.status = status
        self.updated_at = datetime.now().isoformat()
        self.add_history(f"Status changed: {old_status.name} -> {status.name}")

    def add_task_node(self, description: str, parent_id: Optional[str] = None, assigned_to: Optional[str] = None) -> str:
        node_id = f"task-{len(self.task_tree)}-{datetime.now().timestamp()}"
        node = TaskNode(id=node_id, description=description, parent_id=parent_id, assigned_to=assigned_to)
        self.task_tree.append(node)
        if parent_id:
            for n in self.task_tree:
                if n.id == parent_id:
                    n.children.append(node_id)
        return node_id

    def set_current_task(self, node_id: str) -> None:
        self.current_node_id = node_id
        for node in self.task_tree:
            if node.id == node_id:
                node.status = "in_progress"
                break

    def complete_task_node(self, node_id: str) -> None:
        for node in self.task_tree:
            if node.id == node_id:
                node.status = "completed"
                node.completed_at = datetime.now().isoformat()
                break

class ArchitectDecision(BaseModel):
    decision_id: str = Field(default_factory=lambda: f"dec-{datetime.now().timestamp()}")
    category: str = Field(description="Decision category")
    description: str = Field(description="What was decided")
    rationale: str = Field(description="Why this decision was made")
    alternatives: List[str] = Field(default_factory=list)
    impact_level: str = Field(default="medium")

class RiskAssessment(BaseModel):
    risk_id: str = Field(default_factory=lambda: f"risk-{datetime.now().timestamp()}")
    category: str = Field(description="Risk category")
    description: str = Field(description="Risk description")
    probability: float = Field(ge=0.0, le=1.0)
    impact: float = Field(ge=0.0, le=1.0)
    mitigation_strategy: str = Field(default="")
    owner: Optional[str] = None

class BlueprintSection(BaseModel):
    section_id: str = Field(description="Unique section identifier")
    title: str = Field(description="Section title")
    content: str = Field(description="Section content/description")
    dependencies: List[str] = Field(default_factory=list)
    status: str = Field(default="draft")

class ArchitectOutput(BaseModel):
    output_id: str = Field(default_factory=lambda: f"arch-out-{datetime.now().timestamp()}")
    handover_id: str = Field(description="Reference to parent handover")
    created_at: str = Field(default_factory=lambda: datetime.now().isoformat())
    blueprints: List[BlueprintSection] = Field(default_factory=list)
    decisions: List[ArchitectDecision] = Field(default_factory=list)
    risk_assessment: List[RiskAssessment] = Field(default_factory=list)
    design_patterns: List[str] = Field(default_factory=list)
    technology_stack: List[str] = Field(default_factory=list)
    integration_points: List[str] = Field(default_factory=list)
    completeness_score: float = Field(ge=0.0, le=1.0, default=0.0)
    estimated_implementation_time: Optional[str] = None
    next_steps: List[str] = Field(default_factory=list)

    def add_blueprint_section(self, title: str, content: str, dependencies: Optional[List[str]] = None) -> str:
        section_id = f"bp-{len(self.blueprints)}-{datetime.now().timestamp()}"
        section = BlueprintSection(section_id=section_id, title=title, content=content, dependencies=dependencies or [])
        self.blueprints.append(section)
        return section_id

    def add_decision(self, category: str, description: str, rationale: str, impact_level: str = "medium") -> ArchitectDecision:
        decision = ArchitectDecision(category=category, description=description, rationale=rationale, impact_level=impact_level)
        self.decisions.append(decision)
        return decision

    def add_risk(self, category: str, description: str, probability: float, impact: float, mitigation: str = "") -> RiskAssessment:
        risk = RiskAssessment(category=category, description=description, probability=probability, impact=impact, mitigation_strategy=mitigation)
        self.risk_assessment.append(risk)
        return risk

class VerificationResult(BaseModel):
    result_id: str = Field(default_factory=lambda: f"ver-{datetime.now().timestamp()}")
    category: str = Field(description="Verification category")
    target_id: str = Field(description="ID of what was verified")
    status: str = Field(description="passed, failed, warning, skipped")
    findings: str = Field(description="Detailed findings")
    severity: str = Field(default="info")
    recommendations: List[str] = Field(default_factory=list)

class CodeFix(BaseModel):
    fix_id: str = Field(default_factory=lambda: f"fix-{datetime.now().timestamp()}")
    issue_id: str = Field(description="Reference to verified issue")
    file_path: str = Field(description="File to modify")
    description: str = Field(description="What the fix does")
    original_code: Optional[str] = None
    fixed_code: Optional[str] = None
    explanation: str = Field(description="Why this fix resolves the issue")
    breaking_change: bool = Field(default=False)

class DebuggerWarning(BaseModel):
    warning_id: str = Field(default_factory=lambda: f"warn-{datetime.now().timestamp()}")
    category: str = Field(description="Warning category")
    message: str = Field(description="Warning message")
    affected_files: List[str] = Field(default_factory=list)
    severity: str = Field(default="medium")
    suggested_action: Optional[str] = None

class DebuggerOutput(BaseModel):
    output_id: str = Field(default_factory=lambda: f"dbg-out-{datetime.now().timestamp()}")
    handover_id: str = Field(description="Reference to parent handover")
    created_at: str = Field(default_factory=lambda: datetime.now().isoformat())
    verification_results: List[VerificationResult] = Field(default_factory=list)
    fixes: List[CodeFix] = Field(default_factory=list)
    warnings: List[DebuggerWarning] = Field(default_factory=list)
    total_checks: int = Field(default=0)
    passed_checks: int = Field(default=0)
    failed_checks: int = Field(default=0)
    warning_count: int = Field(default=0)
    coverage_percentage: float = Field(ge=0.0, le=1.0, default=0.0)
    verified_files: List[str] = Field(default_factory=list)
    skipped_files: List[str] = Field(default_factory=list)
    overall_status: str = Field(default="pending")
    approved_for_deployment: bool = Field(default=False)
    requires_rework: bool = Field(default=False)
    rework_items: List[str] = Field(default_factory=list)

    def add_verification_result(self, category: str, target_id: str, status: str, findings: str, severity: str = "info") -> VerificationResult:
        result = VerificationResult(category=category, target_id=target_id, status=status, findings=findings, severity=severity)
        self.verification_results.append(result)
        self._update_metrics()
        return result

    def _update_metrics(self) -> None:
        self.total_checks = len(self.verification_results)
        self.passed_checks = sum(1 for r in self.verification_results if r.status == "passed")
        self.failed_checks = sum(1 for r in self.verification_results if r.status == "failed")

class ValidationCheckpoint(BaseModel):
    checkpoint_id: str = Field(default_factory=lambda: f"chk-{datetime.now().timestamp()}")
    handover_id: str = Field(description="Reference to parent handover")
    created_at: str = Field(default_factory=lambda: datetime.now().isoformat())
    stage: str = Field(description="Current stage of handover")
    partial_output: Dict[str, Any] = Field(default_factory=dict)
    validation_results: List[VerificationResult] = Field(default_factory=list)
    checkpoint_passed: bool = Field(default=False)
    can_proceed: bool = Field(default=False)
    requires_changes: bool = Field(default=False)
    feedback: str = Field(default="")
    suggested_modifications: List[str] = Field(default_factory=list)

    def add_validation(self, result: VerificationResult) -> None:
        self.validation_results.append(result)
        self._evaluate_checkpoint()

    def _evaluate_checkpoint(self) -> None:
        if not self.validation_results: return
        failed = [r for r in self.validation_results if r.status == "failed"]
        critical = [r for r in self.validation_results if r.severity == "critical"]
        self.checkpoint_passed = len(failed) == 0 and len(critical) == 0
        self.can_proceed = self.checkpoint_passed
        self.requires_changes = len(failed) > 0

class ContextDiff(BaseModel):
    diff_id: str = Field(default_factory=lambda: f"diff-{datetime.now().timestamp()}")
    base_version: str = Field(description="Base context version")
    compare_version: str = Field(description="Comparison context version")
    added: Dict[str, Any] = Field(default_factory=dict)
    removed: Dict[str, Any] = Field(default_factory=dict)
    modified: Dict[str, Tuple[Any, Any]] = Field(default_factory=dict)
    unchanged: List[str] = Field(default_factory=list)
