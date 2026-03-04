"""
Aether Voice OS — Handover Telemetry System

Tracks success metrics, persistence, and analytics for the Deep Handover Protocol.
Provides insights into handover performance, failure patterns, and optimization opportunities.
"""

from __future__ import annotations

import json
import logging
from dataclasses import dataclass, field
from datetime import datetime, timedelta
from enum import Enum
from typing import Any, Dict, List, Optional, Tuple

from pydantic import BaseModel, Field

from core.infra.telemetry import get_tracer

logger = logging.getLogger(__name__)

tracer = get_tracer()


class HandoverOutcome(Enum):
    """Possible outcomes for a handover operation."""

    SUCCESS = "success"
    PARTIAL = "partial"
    FAILED = "failed"
    ROLLED_BACK = "rolled_back"
    TIMEOUT = "timeout"
    REJECTED = "rejected"
    CANCELLED = "cancelled"


class FailureCategory(Enum):
    """Categories of handover failures for analytics."""

    VALIDATION_FAILED = "validation_failed"
    NEGOTIATION_FAILED = "negotiation_failed"
    CONTEXT_LOST = "context_lost"
    AGENT_UNAVAILABLE = "agent_unavailable"
    TIMEOUT = "timeout"
    SYSTEM_ERROR = "system_error"
    ROLLBACK_TRIGGERED = "rollback_triggered"
    UNKNOWN = "unknown"


@dataclass
class PerformanceMetrics:
    """Performance metrics for a handover operation."""

    preparation_time_ms: float = 0.0
    transfer_time_ms: float = 0.0
    validation_time_ms: float = 0.0
    negotiation_time_ms: float = 0.0
    total_time_ms: float = 0.0

    # Latency percentiles (if multiple samples)
    latency_samples: List[float] = field(default_factory=list)

    def record_latency(self, latency_ms: float) -> None:
        """Record a latency sample."""
        self.latency_samples.append(latency_ms)

    @property
    def p50_latency(self) -> float:
        """50th percentile latency."""
        if not self.latency_samples:
            return 0.0
        sorted_samples = sorted(self.latency_samples)
        idx = len(sorted_samples) // 2
        return sorted_samples[idx]

    @property
    def p95_latency(self) -> float:
        """95th percentile latency."""
        if not self.latency_samples:
            return 0.0
        sorted_samples = sorted(self.latency_samples)
        idx = int(len(sorted_samples) * 0.95)
        return sorted_samples[min(idx, len(sorted_samples) - 1)]

    @property
    def p99_latency(self) -> float:
        """99th percentile latency."""
        if not self.latency_samples:
            return 0.0
        sorted_samples = sorted(self.latency_samples)
        idx = int(len(sorted_samples) * 0.99)
        return sorted_samples[min(idx, len(sorted_samples) - 1)]


class HandoverRecord(BaseModel):
    """
    Persistent record of a handover operation.

    Captures all relevant data for analytics, debugging, and optimization.
    """

    # Identification
    record_id: str = Field(default_factory=lambda: f"rec-{datetime.now().timestamp()}")
    handover_id: str = Field(description="Reference to handover context")

    # Agents involved
    source_agent: str = Field(description="Agent initiating handover")
    target_agent: str = Field(description="Agent receiving handover")

    # Timing
    created_at: str = Field(default_factory=lambda: datetime.now().isoformat())
    started_at: Optional[str] = None
    completed_at: Optional[str] = None

    # Task information
    task_description: str = Field(default="")
    task_category: Optional[str] = None

    # Outcome
    outcome: str = Field(default=HandoverOutcome.SUCCESS.value)
    failure_category: Optional[str] = None
    failure_reason: Optional[str] = None

    # Context statistics
    context_size_bytes: int = Field(default=0)
    payload_keys: List[str] = Field(default_factory=list)
    conversation_entries: int = Field(default=0)
    task_nodes: int = Field(default=0)

    # Validation results
    validation_checkpoints: int = Field(default=0)
    validations_passed: int = Field(default=0)
    validations_failed: int = Field(default=0)

    # Negotiation
    negotiation_messages: int = Field(default=0)
    negotiation_duration_seconds: float = Field(default=0.0)

    # Performance
    preparation_time_ms: float = Field(default=0.0)
    transfer_time_ms: float = Field(default=0.0)
    total_duration_ms: float = Field(default=0.0)

    # Rollback
    rollback_initiated: bool = Field(default=False)
    rollback_successful: Optional[bool] = None

    # Additional metadata
    metadata: Dict[str, Any] = Field(default_factory=dict)

    model_config = {"arbitrary_types_allowed": True}

    @property
    def duration_seconds(self) -> float:
        """Calculate total duration in seconds."""
        if self.completed_at and self.started_at:
            start = datetime.fromisoformat(self.started_at)
            end = datetime.fromisoformat(self.completed_at)
            return (end - start).total_seconds()
        return 0.0

    def to_dict(self) -> Dict[str, Any]:
        """Convert record to dictionary."""
        return self.model_dump()

    def to_json(self) -> str:
        """Serialize record to JSON."""
        return json.dumps(self.to_dict(), default=str)


class HandoverAnalytics(BaseModel):
    """
    Aggregated analytics for handover operations.
    """

    # Time window
    window_start: str = Field(default_factory=lambda: datetime.now().isoformat())
    window_end: Optional[str] = None

    # Volume metrics
    total_handovers: int = Field(default=0)
    successful_handovers: int = Field(default=0)
    failed_handovers: int = Field(default=0)
    rolled_back_handovers: int = Field(default=0)

    # Outcome distribution
    outcome_counts: Dict[str, int] = Field(default_factory=dict)

    # Failure analysis
    failure_categories: Dict[str, int] = Field(default_factory=dict)
    top_failure_reasons: List[Tuple[str, int]] = Field(default_factory=list)

    # Performance metrics
    avg_preparation_time_ms: float = Field(default=0.0)
    avg_transfer_time_ms: float = Field(default=0.0)
    avg_total_time_ms: float = Field(default=0.0)

    # Agent pair performance
    agent_pair_success_rates: Dict[str, Dict[str, float]] = Field(default_factory=dict)

    # Trends
    hourly_success_rates: Dict[str, float] = Field(default_factory=dict)

    def calculate_success_rate(self) -> float:
        """Calculate overall success rate."""
        if self.total_handovers == 0:
            return 0.0
        return self.successful_handovers / self.total_handovers

    def get_agent_pair_key(self, source: str, target: str) -> str:
        """Generate a key for agent pair tracking."""
        return f"{source}->{target}"

    def update_from_record(self, record: HandoverRecord) -> None:
        """Update analytics with a new record."""
        self.total_handovers += 1

        # Update outcome counts
        outcome = record.outcome
        self.outcome_counts[outcome] = self.outcome_counts.get(outcome, 0) + 1

        # Update success/failure counts
        if outcome == HandoverOutcome.SUCCESS.value:
            self.successful_handovers += 1
        elif outcome in (HandoverOutcome.FAILED.value, HandoverOutcome.TIMEOUT.value):
            self.failed_handovers += 1
        elif outcome == HandoverOutcome.ROLLED_BACK.value:
            self.rolled_back_handovers += 1

        # Update failure categories
        if record.failure_category:
            cat = record.failure_category
            self.failure_categories[cat] = self.failure_categories.get(cat, 0) + 1

        # Update agent pair stats
        pair_key = self.get_agent_pair_key(record.source_agent, record.target_agent)
        if pair_key not in self.agent_pair_success_rates:
            self.agent_pair_success_rates[pair_key] = {"success": 0, "total": 0}

        self.agent_pair_success_rates[pair_key]["total"] += 1
        if outcome == HandoverOutcome.SUCCESS.value:
            self.agent_pair_success_rates[pair_key]["success"] += 1

        # Update performance averages
        self._update_performance_averages(record)

    def _update_performance_averages(self, record: HandoverRecord) -> None:
        """Update rolling averages for performance metrics."""
        n = self.total_handovers

        # Simple moving average
        self.avg_preparation_time_ms = (
            (self.avg_preparation_time_ms * (n - 1)) + record.preparation_time_ms
        ) / n

        self.avg_transfer_time_ms = (
            (self.avg_transfer_time_ms * (n - 1)) + record.transfer_time_ms
        ) / n

        self.avg_total_time_ms = (
            (self.avg_total_time_ms * (n - 1)) + record.total_duration_ms
        ) / n

    def get_agent_pair_success_rate(self, source: str, target: str) -> float:
        """Get success rate for a specific agent pair."""
        pair_key = self.get_agent_pair_key(source, target)
        stats = self.agent_pair_success_rates.get(pair_key, {"success": 0, "total": 0})
        if stats["total"] == 0:
            return 0.0
        return stats["success"] / stats["total"]

    def get_summary(self) -> Dict[str, Any]:
        """Get a summary of analytics."""
        return {
            "total_handovers": self.total_handovers,
            "success_rate": f"{self.calculate_success_rate():.2%}",
            "avg_total_time_ms": round(self.avg_total_time_ms, 2),
            "top_failure_categories": sorted(
                self.failure_categories.items(), key=lambda x: x[1], reverse=True
            )[:5],
            "best_agent_pairs": sorted(
                [
                    (pair, stats["success"] / stats["total"])
                    for pair, stats in self.agent_pair_success_rates.items()
                    if stats["total"] > 0
                ],
                key=lambda x: x[1],
                reverse=True,
            )[:5],
        }


class HandoverTelemetry:
    """
    Telemetry system for tracking handover success metrics.

    Provides:
    - Success/failure tracking
    - Performance analytics
    - Persistent record storage
    - Real-time metrics
    """

    def __init__(self, max_records: int = 10000):
        self._records: List[HandoverRecord] = []
        self._max_records = max_records
        self._analytics = HandoverAnalytics()
        self._active_recordings: Dict[str, HandoverRecord] = {}
        self._active_spans: Dict[str, Any] = {}
        self._performance_metrics = PerformanceMetrics()

        logger.info("HandoverTelemetry initialized (max_records=%d)", max_records)

    def start_recording(
        self,
        handover_id: str,
        source_agent: str,
        target_agent: str,
        task_description: str = "",
    ) -> HandoverRecord:
        """Start recording a new handover operation."""
        record = HandoverRecord(
            handover_id=handover_id,
            source_agent=source_agent,
            target_agent=target_agent,
            task_description=task_description,
            started_at=datetime.now().isoformat(),
        )
        self._active_recordings[handover_id] = record
        
        # OTLP Instrument
        span = tracer.start_as_current_span(
            f"handover:{source_agent}->{target_agent}",
            attributes={
                "handover.id": handover_id,
                "agent.source": source_agent,
                "agent.target": target_agent,
                "task.description": task_description
            }
        )
        self._active_spans[handover_id] = span
        
        logger.debug("Started recording handover %s", handover_id)
        return record

    def update_recording(
        self, handover_id: str, **updates: Any
    ) -> Optional[HandoverRecord]:
        """Update an active recording with new data."""
        record = self._active_recordings.get(handover_id)
        if not record:
            logger.warning("No active recording found for handover %s", handover_id)
            return None

        for key, value in updates.items():
            if hasattr(record, key):
                setattr(record, key, value)
            else:
                record.metadata[key] = value

        return record

    def finalize_recording(
        self,
        handover_id: str,
        outcome: HandoverOutcome,
        failure_category: Optional[FailureCategory] = None,
        failure_reason: Optional[str] = None,
    ) -> Optional[HandoverRecord]:
        """Finalize and store a handover recording."""
        record = self._active_recordings.pop(handover_id, None)
        if not record:
            logger.warning("No active recording found for handover %s", handover_id)
            return None

        record.completed_at = datetime.now().isoformat()
        record.outcome = outcome.value

        if failure_category:
            record.failure_category = failure_category.value
        if failure_reason:
            record.failure_reason = failure_reason

        # Finalize OTLP Span
        span = self._active_spans.pop(handover_id, None)
        if span and hasattr(span, "set_attribute"):
            try:
                span.set_attribute("handover.outcome", outcome.value)
                if outcome == HandoverOutcome.SUCCESS:
                    span.set_status(Status(StatusCode.OK))
                else:
                    span.set_status(Status(StatusCode.ERROR, description=failure_reason or "Handover failed"))
                    if failure_category:
                        span.set_attribute("handover.error_category", failure_category.value)

                span.end()
            except Exception as e:
                logger.debug("Failed to update span attributes: %s", e)

        # Calculate total duration
        if record.started_at and record.completed_at:
            start = datetime.fromisoformat(record.started_at)
            end = datetime.fromisoformat(record.completed_at)
            record.total_duration_ms = (end - start).total_seconds() * 1000

        # Store record
        self._store_record(record)

        # Update analytics
        self._analytics.update_from_record(record)

        logger.info(
            "Finalized handover %s: outcome=%s, duration=%.2fms",
            handover_id,
            outcome.value,
            record.total_duration_ms,
        )

        return record

    def _store_record(self, record: HandoverRecord) -> None:
        """Store a record, maintaining max_records limit."""
        self._records.append(record)

        # Maintain size limit
        if len(self._records) > self._max_records:
            removed = self._records.pop(0)
            logger.debug("Removed oldest record %s (size limit)", removed.record_id)

    def record_validation_checkpoint(
        self, handover_id: str, passed: bool, checkpoint_count: int = 1
    ) -> None:
        """Record validation checkpoint results."""
        record = self._active_recordings.get(handover_id)
        if record:
            record.validation_checkpoints += checkpoint_count
            if passed:
                record.validations_passed += 1
            else:
                record.validations_failed += 1

    def record_negotiation(
        self, handover_id: str, message_count: int, duration_seconds: float
    ) -> None:
        """Record negotiation metrics."""
        record = self._active_recordings.get(handover_id)
        if record:
            record.negotiation_messages += message_count
            record.negotiation_duration_seconds = duration_seconds

    def record_performance(
        self,
        handover_id: str,
        preparation_time_ms: Optional[float] = None,
        transfer_time_ms: Optional[float] = None,
    ) -> None:
        """Record performance metrics."""
        record = self._active_recordings.get(handover_id)
        if record:
            if preparation_time_ms is not None:
                record.preparation_time_ms = preparation_time_ms
            if transfer_time_ms is not None:
                record.transfer_time_ms = transfer_time_ms

    def record_rollback(self, handover_id: str, successful: bool) -> None:
        """Record a rollback operation."""
        record = self._active_recordings.get(handover_id)
        if record:
            record.rollback_initiated = True
            record.rollback_successful = successful

    def record_context_size(
        self, handover_id: str, size_bytes: int, payload_keys: List[str]
    ) -> None:
        """Record context size metrics."""
        record = self._active_recordings.get(handover_id)
        if record:
            record.context_size_bytes = size_bytes
            record.payload_keys = payload_keys

    def get_record(self, handover_id: str) -> Optional[HandoverRecord]:
        """Retrieve a specific handover record."""
        # Check active recordings first
        if handover_id in self._active_recordings:
            return self._active_recordings[handover_id]

        # Search in stored records
        for record in reversed(self._records):
            if record.handover_id == handover_id:
                return record

        return None

    def get_records(
        self,
        source_agent: Optional[str] = None,
        target_agent: Optional[str] = None,
        outcome: Optional[HandoverOutcome] = None,
        start_time: Optional[datetime] = None,
        end_time: Optional[datetime] = None,
        limit: int = 100,
    ) -> List[HandoverRecord]:
        """Query records with filters."""
        results = []

        for record in reversed(self._records):
            if source_agent and record.source_agent != source_agent:
                continue
            if target_agent and record.target_agent != target_agent:
                continue
            if outcome and record.outcome != outcome.value:
                continue

            if start_time or end_time:
                record_time = datetime.fromisoformat(record.created_at)
                if start_time and record_time < start_time:
                    continue
                if end_time and record_time > end_time:
                    continue

            results.append(record)
            if len(results) >= limit:
                break

        return results

    def get_analytics(self) -> HandoverAnalytics:
        """Get current analytics."""
        return self._analytics

    def get_success_rate(
        self,
        source_agent: Optional[str] = None,
        target_agent: Optional[str] = None,
        window_hours: Optional[int] = None,
    ) -> float:
        """Calculate success rate with optional filters."""
        records = self._records

        if window_hours:
            cutoff = datetime.now() - timedelta(hours=window_hours)
            records = [
                r for r in records if datetime.fromisoformat(r.created_at) >= cutoff
            ]

        if source_agent:
            records = [r for r in records if r.source_agent == source_agent]

        if target_agent:
            records = [r for r in records if r.target_agent == target_agent]

        if not records:
            return 0.0

        successful = sum(
            1 for r in records if r.outcome == HandoverOutcome.SUCCESS.value
        )
        return successful / len(records)

    def get_failure_analysis(self, top_n: int = 5) -> List[Tuple[str, int, float]]:
        """
        Get top failure categories with counts and percentages.

        Returns list of (category, count, percentage)
        """
        total_failures = sum(self._analytics.failure_categories.values())
        if total_failures == 0:
            return []

        sorted_categories = sorted(
            self._analytics.failure_categories.items(),
            key=lambda x: x[1],
            reverse=True,
        )[:top_n]

        return [
            (cat, count, count / total_failures) for cat, count in sorted_categories
        ]

    def get_performance_report(self) -> Dict[str, Any]:
        """Generate a comprehensive performance report."""
        return {
            "summary": self._analytics.get_summary(),
            "performance": {
                "avg_preparation_time_ms": round(
                    self._analytics.avg_preparation_time_ms, 2
                ),
                "avg_transfer_time_ms": round(self._analytics.avg_transfer_time_ms, 2),
                "avg_total_time_ms": round(self._analytics.avg_total_time_ms, 2),
            },
            "failure_analysis": self.get_failure_analysis(),
            "agent_pair_performance": {
                pair: {
                    "success_rate": stats["success"] / stats["total"],
                    "total_handovers": stats["total"],
                }
                for pair, stats in self._analytics.agent_pair_success_rates.items()
                if stats["total"] > 0
            },
        }

    def export_records(self, filepath: str) -> int:
        """Export all records to a JSON file."""
        data = {
            "exported_at": datetime.now().isoformat(),
            "record_count": len(self._records),
            "records": [r.to_dict() for r in self._records],
        }

        with open(filepath, "w") as f:
            json.dump(data, f, indent=2, default=str)

        logger.info("Exported %d records to %s", len(self._records), filepath)
        return len(self._records)

    def import_records(self, filepath: str) -> int:
        """Import records from a JSON file."""
        with open(filepath, "r") as f:
            data = json.load(f)

        imported = 0
        for record_data in data.get("records", []):
            record = HandoverRecord(**record_data)
            self._store_record(record)
            self._analytics.update_from_record(record)
            imported += 1

        logger.info("Imported %d records from %s", imported, filepath)
        return imported

    def clear(self) -> None:
        """Clear all records and reset analytics."""
        self._records.clear()
        self._active_recordings.clear()
        self._analytics = HandoverAnalytics()
        logger.info("Telemetry data cleared")

    def get_stats(self) -> Dict[str, Any]:
        """Get quick statistics."""
        return {
            "total_records": len(self._records),
            "active_recordings": len(self._active_recordings),
            "success_rate": f"{self._analytics.calculate_success_rate():.2%}",
            "avg_duration_ms": round(self._analytics.avg_total_time_ms, 2),
        }


# Global telemetry instance
_telemetry_instance: Optional[HandoverTelemetry] = None


def get_telemetry() -> HandoverTelemetry:
    """Get or create the global telemetry instance."""
    global _telemetry_instance
    if _telemetry_instance is None:
        _telemetry_instance = HandoverTelemetry()
    return _telemetry_instance


def reset_telemetry() -> None:
    """Reset the global telemetry instance."""
    global _telemetry_instance
    _telemetry_instance = None


def record_handover_start(
    handover_id: str,
    source_agent: str,
    target_agent: str,
    task_description: str = "",
) -> HandoverRecord:
    """Convenience function to start recording a handover."""
    return get_telemetry().start_recording(
        handover_id, source_agent, target_agent, task_description
    )


def record_handover_end(
    handover_id: str,
    outcome: HandoverOutcome,
    failure_category: Optional[FailureCategory] = None,
    failure_reason: Optional[str] = None,
) -> Optional[HandoverRecord]:
    """Convenience function to finalize a handover recording."""
    return get_telemetry().finalize_recording(
        handover_id, outcome, failure_category, failure_reason
    )
