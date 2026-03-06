import logging
import os
import statistics
import threading
from collections import deque
from typing import Optional

try:
    from opentelemetry import trace as trace_api
    from opentelemetry.exporter.otlp.proto.grpc.trace_exporter import OTLPSpanExporter
    from opentelemetry.sdk import trace as trace_sdk
    from opentelemetry.sdk.resources import Resource
    from opentelemetry.sdk.trace.export import BatchSpanProcessor, SimpleSpanProcessor

    OTEL_AVAILABLE = True
except Exception:
    from opentelemetry import trace as trace_api

    OTEL_AVAILABLE = False

logger = logging.getLogger(__name__)


class ToolTimeoutTelemetry:
    """Best-effort aggregator for tool timeout and latency percentile telemetry."""

    def __init__(self, window_size: int = 2000) -> None:
        self._durations_ms: deque[float] = deque(maxlen=window_size)
        self._timeout_events: deque[dict[str, object]] = deque(maxlen=window_size)
        self._lock = threading.Lock()

    def record_tool_dispatch(
        self, tool_name: str, duration_ms: float, timed_out: bool
    ) -> None:
        with self._lock:
            self._durations_ms.append(duration_ms)
            if timed_out:
                self._timeout_events.append(
                    {
                        "tool_name": tool_name,
                        "duration_ms": duration_ms,
                    }
                )

    def _percentile(self, values: list[float], pct: float) -> float:
        if not values:
            return 0.0
        if len(values) == 1:
            return values[0]
        idx = int((len(values) - 1) * pct)
        return values[idx]

    def get_dashboard(self) -> dict[str, object]:
        with self._lock:
            values = sorted(self._durations_ms)
            timeout_count = len(self._timeout_events)
            total = len(values)

            return {
                "tool_dispatch": {
                    "count": total,
                    "timeout_count": timeout_count,
                    "timeout_rate": (timeout_count / total) if total else 0.0,
                    "p50_ms": self._percentile(values, 0.50),
                    "p95_ms": self._percentile(values, 0.95),
                    "p99_ms": self._percentile(values, 0.99),
                    "avg_ms": statistics.mean(values) if values else 0.0,
                }
            }


def _fallback_tracer() -> trace_api.Tracer:
    return trace_api.get_tracer("aether.fallback")


class TelemetryManager:
    """
    Centralized Telemetry Sink for AetherOS.
    Exports traces to Arize/Phoenix via OTLP.
    """

    def __init__(
        self, model_id: str = "AetherOS-Core", model_version: str = "v2.0-neuro"
    ):
        self.model_id = model_id
        self.model_version = model_version
        self._is_initialized = False
        self.tracer: Optional[trace_api.Tracer] = None

        # Arize/Phoenix Config
        self.endpoint = os.getenv(
            "ARIZE_ENDPOINT", "http://localhost:6006/v1/traces"
        )  # Default to local Phoenix
        self.space_id = os.getenv("ARIZE_SPACE_ID")
        self.api_key = os.getenv("ARIZE_API_KEY")

    def initialize(self):
        """Initialize the OpenTelemetry provider and exporters."""
        if self._is_initialized:
            return

        if not OTEL_AVAILABLE:
            self.tracer = _fallback_tracer()
            self._is_initialized = True
            logger.warning("OpenTelemetry exporter not available, using no-op tracer.")
            return

        try:
            resource = Resource(
                attributes={
                    "model_id": self.model_id,
                    "model_version": self.model_version,
                    "service.name": "aether-gateway",
                }
            )

            provider = trace_sdk.TracerProvider(resource=resource)

            # Setup headers for Arize Cloud if credentials exist
            headers = {}
            if self.space_id and self.api_key:
                headers = {"space_id": self.space_id, "api_key": self.api_key}

            # Use BatchSpanProcessor for production, Simple for dev/debugging
            processor_class = (
                BatchSpanProcessor
                if not os.getenv("DEBUG_OTEL")
                else SimpleSpanProcessor
            )

            exporter = OTLPSpanExporter(endpoint=self.endpoint, headers=headers)

            provider.add_span_processor(processor_class(exporter))
            trace_api.set_tracer_provider(provider)

            self.tracer = trace_api.get_tracer("aether.core")
            self._is_initialized = True
            logger.info("✦ Telemetry Sink ARMED: %s", self.endpoint)

        except Exception as e:
            logger.error("✧ Failed to initialize telemetry: %s", e)
            self.tracer = _fallback_tracer()

    def record_usage(
        self,
        session_id: str,
        prompt_tokens: int,
        completion_tokens: int,
        model: str = "gemini-2.0-flash",
    ):
        """Record token usage and estimate cost."""
        # Pricing constants (approximate for Gemini 2.0 Flash)
        prices = {
            "gemini-2.0-flash": {"input": 0.10 / 1_000_000, "output": 0.40 / 1_000_000},
            "gemini-2.0-pro": {"input": 1.25 / 1_000_000, "output": 5.00 / 1_000_000},
        }

        rates = prices.get(model, prices["gemini-2.0-flash"])
        cost = (prompt_tokens * rates["input"]) + (completion_tokens * rates["output"])

        logger.info(
            "💸 [COST] Session %s: Prompt=%d, Completion=%d, Estimated Cost=$%.6f",
            session_id,
            prompt_tokens,
            completion_tokens,
            cost,
        )

        # Add to current span if any
        span = trace_api.get_current_span()
        if span.is_recording():
            span.set_attribute("gen_ai.usage.prompt_tokens", prompt_tokens)
            span.set_attribute("gen_ai.usage.completion_tokens", completion_tokens)
            span.set_attribute("gen_ai.usage.cost", cost)

    def get_tracer(self) -> trace_api.Tracer:
        if not self._is_initialized:
            self.initialize()
        return self.tracer or _fallback_tracer()


# Global Singleton
_manager = TelemetryManager()


def get_tracer() -> trace_api.Tracer:
    return _manager.get_tracer()


def record_usage(
    session_id: str,
    prompt_tokens: int,
    completion_tokens: int,
    model: str = "gemini-2.0-flash",
):
    _manager.record_usage(session_id, prompt_tokens, completion_tokens, model)


_TOOL_TIMEOUT_TELEMETRY = ToolTimeoutTelemetry()


def record_tool_dispatch_telemetry(
    tool_name: str,
    duration_ms: float,
    timed_out: bool,
) -> None:
    """Record tool dispatch completion for aggregate timeout/latency dashboards."""
    _TOOL_TIMEOUT_TELEMETRY.record_tool_dispatch(
        tool_name=tool_name,
        duration_ms=duration_ms,
        timed_out=timed_out,
    )


def get_tool_timeout_dashboard() -> dict[str, object]:
    """Return aggregate timeout and percentile metrics for tool dispatches."""
    return _TOOL_TIMEOUT_TELEMETRY.get_dashboard()
