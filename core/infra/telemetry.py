import logging
import os
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
            self.tracer = trace_api.get_no_op_tracer()
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
            # Fallback to a no-op tracer
            self.tracer = trace_api.get_no_op_tracer()

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
        return self.tracer or trace_api.get_no_op_tracer()


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
