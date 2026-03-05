# Telemetry System

<cite>
**Referenced Files in This Document**
- [README.md](file://README.md)
- [core/infra/telemetry.py](file://core/infra/telemetry.py)
- [core/infra/event_bus.py](file://core/infra/event_bus.py)
- [core/audio/telemetry.py](file://core/audio/telemetry.py)
- [core/analytics/demo_metrics.py](file://core/analytics/demo_metrics.py)
- [core/analytics/latency.py](file://core/analytics/latency.py)
- [core/ai/handover_telemetry.py](file://core/ai/handover_telemetry.py)
- [apps/portal/src/hooks/useTelemetry.tsx](file://apps/portal/src/hooks/useTelemetry.tsx)
- [apps/portal/src/components/TelemetryFeed.tsx](file://apps/portal/src/components/TelemetryFeed.tsx)
- [apps/portal/src/dashboard/app/page.tsx](file://apps/portal/src/dashboard/app/page.tsx)
- [apps/portal/src/components/HUD/SystemAnalytics.tsx](file://apps/portal/src/components/HUD/SystemAnalytics.tsx)
- [tests/benchmarks/test_long_session.py](file://tests/benchmarks/test_long_session.py)
- [tests/benchmarks/test_event_bus_stress.py](file://tests/benchmarks/test_event_bus_stress.py)
</cite>

## Table of Contents
1. [Introduction](#introduction)
2. [Project Structure](#project-structure)
3. [Core Components](#core-components)
4. [Architecture Overview](#architecture-overview)
5. [Detailed Component Analysis](#detailed-component-analysis)
6. [Dependency Analysis](#dependency-analysis)
7. [Performance Considerations](#performance-considerations)
8. [Troubleshooting Guide](#troubleshooting-guide)
9. [Conclusion](#conclusion)
10. [Appendices](#appendices)

## Introduction
This document describes the telemetry collection and monitoring system powering the Aether Voice OS. It explains how telemetry data is collected, aggregated, and reported across audio, system, and agent handover domains. It covers supported telemetry types, data formats, and transmission protocols, and details integrations with the frontend dashboard and external analytics platforms. Guidance is included for configuring telemetry, defining custom metrics, exporting data, and optimizing performance and storage. Operational insights, error tracking, and privacy considerations are addressed alongside troubleshooting steps and best practices.

## Project Structure
The telemetry system spans backend infrastructure, audio pipeline telemetry, AI agent handover telemetry, and a Next.js dashboard for visualization and logs.

```mermaid
graph TB
subgraph "Backend"
EB["EventBus<br/>Tiered queues"]
OT["OpenTelemetry Tracer<br/>OTLP Exporter"]
AT["AudioTelemetry<br/>Paralinguistics"]
ATL["AudioTelemetryLogger<br/>Frame/Session Metrics"]
HT["HandoverTelemetry<br/>Records & Analytics"]
DM["DemoMetrics<br/>Judging Benchmarks"]
LO["LatencyOptimizer<br/>p50/p95/p99"]
end
subgraph "Frontend"
FEED["TelemetryFeed<br/>Streaming logs"]
DASH["Dashboard Page<br/>Emotion & State"]
HUD["HUD SystemAnalytics<br/>Neural Flux"]
end
EB --> AT
EB --> ATL
OT --> HT
DM --> DASH
LO --> DASH
FEED --> DASH
HUD --> DASH
```

**Diagram sources**
- [core/infra/event_bus.py](file://core/infra/event_bus.py#L69-L152)
- [core/infra/telemetry.py](file://core/infra/telemetry.py#L14-L130)
- [core/audio/telemetry.py](file://core/audio/telemetry.py#L21-L441)
- [core/analytics/demo_metrics.py](file://core/analytics/demo_metrics.py#L9-L50)
- [core/analytics/latency.py](file://core/analytics/latency.py#L7-L40)
- [core/ai/handover_telemetry.py](file://core/ai/handover_telemetry.py#L295-L694)
- [apps/portal/src/components/TelemetryFeed.tsx](file://apps/portal/src/components/TelemetryFeed.tsx#L1-L40)
- [apps/portal/src/dashboard/app/page.tsx](file://apps/portal/src/dashboard/app/page.tsx#L1-L112)
- [apps/portal/src/components/HUD/SystemAnalytics.tsx](file://apps/portal/src/components/HUD/SystemAnalytics.tsx#L1-L88)

**Section sources**
- [README.md](file://README.md#L132-L158)
- [core/infra/event_bus.py](file://core/infra/event_bus.py#L69-L152)
- [core/infra/telemetry.py](file://core/infra/telemetry.py#L14-L130)
- [core/audio/telemetry.py](file://core/audio/telemetry.py#L21-L441)
- [core/analytics/demo_metrics.py](file://core/analytics/demo_metrics.py#L9-L50)
- [core/analytics/latency.py](file://core/analytics/latency.py#L7-L40)
- [core/ai/handover_telemetry.py](file://core/ai/handover_telemetry.py#L295-L694)
- [apps/portal/src/components/TelemetryFeed.tsx](file://apps/portal/src/components/TelemetryFeed.tsx#L1-L40)
- [apps/portal/src/dashboard/app/page.tsx](file://apps/portal/src/dashboard/app/page.tsx#L1-L112)
- [apps/portal/src/components/HUD/SystemAnalytics.tsx](file://apps/portal/src/components/HUD/SystemAnalytics.tsx#L1-L88)

## Core Components
- OpenTelemetry Telemetry Manager: Initializes and exports traces via OTLP to Arize/Phoenix, records token usage and cost, and attaches usage attributes to current spans.
- Event Bus: A tiered asynchronous event bus with dedicated queues for audio, control, and telemetry. Telemetry events are droppable by design to avoid starvation of higher-priority lanes.
- Audio Telemetry Engine: Periodically computes paralinguistic features (volume, pitch, spectral centroid) and publishes them as telemetry events.
- Audio Telemetry Logger: Tracks per-frame and session-level metrics (latency, ERLE, AEC convergence, VAD activity, jitter), publishes frame metrics, and optionally persists reports to disk.
- Handover Telemetry: Records agent handover operations, outcomes, performance, and analytics; integrates with OpenTelemetry spans for distributed tracing.
- Demo Metrics: Captures latency and accuracy for demonstration and judging scenarios.
- Latency Optimizer: Computes latency percentiles and logs summary metrics.
- Frontend Telemetry Feed and Dashboard: Streams and visualizes telemetry logs and system analytics.

**Section sources**
- [core/infra/telemetry.py](file://core/infra/telemetry.py#L14-L130)
- [core/infra/event_bus.py](file://core/infra/event_bus.py#L69-L152)
- [core/audio/telemetry.py](file://core/audio/telemetry.py#L21-L441)
- [core/analytics/demo_metrics.py](file://core/analytics/demo_metrics.py#L9-L50)
- [core/analytics/latency.py](file://core/analytics/latency.py#L7-L40)
- [core/ai/handover_telemetry.py](file://core/ai/handover_telemetry.py#L295-L694)
- [apps/portal/src/components/TelemetryFeed.tsx](file://apps/portal/src/components/TelemetryFeed.tsx#L1-L40)
- [apps/portal/src/dashboard/app/page.tsx](file://apps/portal/src/dashboard/app/page.tsx#L1-L112)

## Architecture Overview
The telemetry architecture follows a publish-subscribe pattern with explicit tiers and deadlines. Audio telemetry is generated at a fixed cadence and published to the event bus. The bus routes events to subscribers, who may aggregate metrics, export traces, or render dashboards. Telemetry spans integrate with OpenTelemetry for distributed tracing and cost attribution.

```mermaid
sequenceDiagram
participant Mic as "Audio Source"
participant AT as "AudioTelemetry"
participant Bus as "EventBus"
participant ATL as "AudioTelemetryLogger"
participant OT as "TelemetryManager"
participant Dash as "Dashboard"
Mic->>AT : "PCM chunks"
AT->>Bus : "TelemetryEvent(metric_name='paralinguistics')"
Bus-->>AT : "Queued (Tier 3)"
Bus->>ATL : "Frame metrics (via subscription)"
ATL->>Bus : "TelemetryEvent(metric_name='frame_metrics')"
OT->>OT : "record_usage() sets span attributes"
Dash->>Dash : "useEngineTelemetry() fetches logs"
```

**Diagram sources**
- [core/audio/telemetry.py](file://core/audio/telemetry.py#L35-L93)
- [core/infra/event_bus.py](file://core/infra/event_bus.py#L90-L152)
- [core/audio/telemetry.py](file://core/audio/telemetry.py#L343-L354)
- [core/infra/telemetry.py](file://core/infra/telemetry.py#L77-L108)
- [apps/portal/src/dashboard/app/page.tsx](file://apps/portal/src/dashboard/app/page.tsx#L12-L13)

## Detailed Component Analysis

### OpenTelemetry Telemetry Manager
- Purpose: Initialize OpenTelemetry tracer provider, configure OTLP exporter, and attach usage attributes to spans.
- Environment configuration: Endpoint, space ID, and API key for Arize/Phoenix; debug mode switches processor to SimpleSpanProcessor.
- Usage recording: Computes estimated cost from prompt/completion tokens and sets span attributes for usage and cost.
- Fallback: On initialization failure, falls back to a no-op tracer.

```mermaid
classDiagram
class TelemetryManager {
+string model_id
+string model_version
+initialize()
+record_usage(session_id, prompt_tokens, completion_tokens, model)
+get_tracer() Tracer
}
```

**Diagram sources**
- [core/infra/telemetry.py](file://core/infra/telemetry.py#L14-L130)

**Section sources**
- [core/infra/telemetry.py](file://core/infra/telemetry.py#L14-L130)

### Event Bus and Telemetry Events
- Event types: AudioFrameEvent (Tier 1), ControlEvent (Tier 2), TelemetryEvent (Tier 3), AcousticTraitEvent (Tier 2), VisionPulseEvent (Tier 3).
- Queues: Three separate asyncio queues to prevent priority inversion.
- Dropping policy: Telemetry lane drops expired events; other lanes enforce stricter deadlines.
- Subscriber routing: Concurrent fan-out to registered callbacks.

```mermaid
flowchart TD
Start(["Publish TelemetryEvent"]) --> CheckTier{"Event type?"}
CheckTier --> |AudioFrameEvent| AudioQ["Put into audio_queue"]
CheckTier --> |Control/AcousticTrait| ControlQ["Put into control_queue"]
CheckTier --> |Telemetry/VisionPulse| TelQ["Put into telemetry_queue"]
TelQ --> Worker["Telemetry Worker"]
Worker --> Expired{"Expired?"}
Expired --> |Yes| Drop["Drop event"]
Expired --> |No| Route["Route to subscribers"]
```

**Diagram sources**
- [core/infra/event_bus.py](file://core/infra/event_bus.py#L69-L152)

**Section sources**
- [core/infra/event_bus.py](file://core/infra/event_bus.py#L69-L152)

### Audio Telemetry Engine
- Cadence: ~15 Hz (fixed interval).
- Features: RMS volume, pitch estimation via zero-crossing rate, spectral centroid.
- Publishing: Emits TelemetryEvent with metric_name "paralinguistics" and metadata including computed features.
- Integration: Works with EventBus to publish metrics periodically.

```mermaid
flowchart TD
Feed["feed_audio(pcm_data)"] --> Buffer["Append to buffer"]
Start(["start() loop"]) --> Buffer
Buffer --> Compute["Compute RMS, ZCR, Spectral Centroid"]
Compute --> Publish["Publish TelemetryEvent('paralinguistics')"]
Publish --> Sleep["Sleep to maintain cadence"]
Sleep --> Start
```

**Diagram sources**
- [core/audio/telemetry.py](file://core/audio/telemetry.py#L35-L93)

**Section sources**
- [core/audio/telemetry.py](file://core/audio/telemetry.py#L21-L93)

### Audio Telemetry Logger
- Per-frame metrics: capture latency, AEC latency/ERLE/convergence, VAD speech/soft, queue sizes, total latency, frame drops.
- Session metrics: percentiles (p50/p95/p99), average/max latency, ERLE average, convergence rate, double-talk frames, speech ratio, jitter.
- Real-time stats: exposes recent metrics for dashboard.
- Persistence: saves session report (JSON) and detailed frame log (CSV) on exit.

```mermaid
classDiagram
class FrameMetrics {
+float timestamp
+int frame_id
+float capture_latency_ms
+float aec_latency_ms
+float vad_latency_ms
+float total_latency_ms
+float rms_energy
+float erle_db
+bool aec_converged
+bool vad_is_speech
+bool vad_is_soft
+bool double_talk
+bool frame_dropped
+int queue_size_in
+int queue_size_out
}
class SessionMetrics {
+string session_id
+float start_time
+float end_time
+int total_frames
+int frames_dropped
+int frames_speech
+int frames_silence
+float latency_p50_ms
+float latency_p95_ms
+float latency_p99_ms
+float latency_avg_ms
+float latency_max_ms
+float erle_avg_db
+float aec_converged_rate
+int double_talk_frames
+float vad_accuracy
+float speech_ratio
+float jitter_ms
}
class AudioTelemetryLogger {
+start_frame() int
+record_capture(latency_ms, queue_size)
+record_aec(latency_ms, erle_db, converged, double_talk)
+record_vad(latency_ms, is_speech, is_soft, rms_energy)
+record_output(queue_size)
+end_frame() FrameMetrics
+get_session_metrics() SessionMetrics
+get_real_time_stats() dict
+save_session_report() Path
+save_detailed_log() Path
}
AudioTelemetryLogger --> FrameMetrics : "produces"
AudioTelemetryLogger --> SessionMetrics : "aggregates"
```

**Diagram sources**
- [core/audio/telemetry.py](file://core/audio/telemetry.py#L100-L394)

**Section sources**
- [core/audio/telemetry.py](file://core/audio/telemetry.py#L100-L394)

### Handover Telemetry
- Records: start/end timestamps, agents, task info, outcome, validation checkpoints, negotiation metrics, performance timings, rollback events, context size, and metadata.
- Analytics: success/failure counts, failure category distributions, performance averages, agent pair success rates, hourly trends.
- Distributed tracing: starts/ends OTLP spans with attributes and status; records usage attributes via TelemetryManager.
- Persistence: stores records in-memory with size limit, supports export/import to/from JSON.

```mermaid
classDiagram
class HandoverRecord {
+string record_id
+string handover_id
+string source_agent
+string target_agent
+string created_at
+string started_at
+string completed_at
+string task_description
+string outcome
+string failure_category
+string failure_reason
+int context_size_bytes
+string[] payload_keys
+int validation_checkpoints
+int validations_passed
+int validations_failed
+int negotiation_messages
+float negotiation_duration_seconds
+float preparation_time_ms
+float transfer_time_ms
+float total_duration_ms
+bool rollback_initiated
+bool rollback_successful
+dict metadata
}
class HandoverAnalytics {
+string window_start
+string window_end
+int total_handovers
+int successful_handovers
+int failed_handovers
+int rolled_back_handovers
+dict outcome_counts
+dict failure_categories
+list top_failure_reasons
+float avg_preparation_time_ms
+float avg_transfer_time_ms
+float avg_total_time_ms
+dict agent_pair_success_rates
+dict hourly_success_rates
+calculate_success_rate() float
+get_summary() dict
}
class HandoverTelemetry {
+start_recording(...)
+update_recording(handover_id, **updates)
+finalize_recording(handover_id, outcome, failure_category, failure_reason)
+record_validation_checkpoint(...)
+record_negotiation(...)
+record_performance(...)
+record_rollback(...)
+record_context_size(...)
+get_record(handover_id) HandoverRecord
+get_records(...) HandoverRecord[]
+get_analytics() HandoverAnalytics
+get_success_rate(...)
+get_failure_analysis(top_n)
+get_performance_report() dict
+export_records(filepath) int
+import_records(filepath) int
+clear() void
+get_stats() dict
}
HandoverTelemetry --> HandoverRecord : "stores"
HandoverTelemetry --> HandoverAnalytics : "aggregates"
```

**Diagram sources**
- [core/ai/handover_telemetry.py](file://core/ai/handover_telemetry.py#L97-L651)

**Section sources**
- [core/ai/handover_telemetry.py](file://core/ai/handover_telemetry.py#L295-L694)

### Demo Metrics and Latency Optimizer
- DemoMetrics: Tracks detection latency and accuracy for demonstration scenarios and produces a report suitable for dashboards.
- LatencyOptimizer: Maintains latency samples and computes p50/p95/p99 and average for performance reporting.

```mermaid
classDiagram
class DemoMetrics {
+start_timer(span_id)
+stop_timer(span_id)
+record_accuracy(was_correct)
+report() dict
}
class LatencyOptimizer {
+record_latency(latency_ms)
+get_metrics() dict
+log_metrics()
}
```

**Diagram sources**
- [core/analytics/demo_metrics.py](file://core/analytics/demo_metrics.py#L9-L50)
- [core/analytics/latency.py](file://core/analytics/latency.py#L7-L40)

**Section sources**
- [core/analytics/demo_metrics.py](file://core/analytics/demo_metrics.py#L9-L50)
- [core/analytics/latency.py](file://core/analytics/latency.py#L7-L40)

### Frontend Telemetry and Dashboard
- TelemetryFeed: Renders a scrolling list of log entries with fading effect and timestamps.
- useTelemetry: React context providing addLog/clearLogs to populate the feed.
- Dashboard: Integrates emotion waveform, state visualizer, and system logs; connects to engine telemetry hook.
- HUD SystemAnalytics: Visualizes neural flux, signal integrity, pitch, and spectral centroid.

```mermaid
sequenceDiagram
participant Provider as "TelemetryProvider"
participant Feed as "TelemetryFeed"
participant Hook as "useEngineTelemetry"
participant Store as "useAetherStore"
Provider->>Feed : "logs"
Hook->>Store : "fetch systemLogs"
Store-->>Hook : "engineState, latencyMs"
Hook-->>Feed : "render logs"
```

**Diagram sources**
- [apps/portal/src/hooks/useTelemetry.tsx](file://apps/portal/src/hooks/useTelemetry.tsx#L24-L53)
- [apps/portal/src/components/TelemetryFeed.tsx](file://apps/portal/src/components/TelemetryFeed.tsx#L13-L40)
- [apps/portal/src/dashboard/app/page.tsx](file://apps/portal/src/dashboard/app/page.tsx#L12-L13)
- [apps/portal/src/components/HUD/SystemAnalytics.tsx](file://apps/portal/src/components/HUD/SystemAnalytics.tsx#L36-L88)

**Section sources**
- [apps/portal/src/hooks/useTelemetry.tsx](file://apps/portal/src/hooks/useTelemetry.tsx#L1-L53)
- [apps/portal/src/components/TelemetryFeed.tsx](file://apps/portal/src/components/TelemetryFeed.tsx#L1-L40)
- [apps/portal/src/dashboard/app/page.tsx](file://apps/portal/src/dashboard/app/page.tsx#L1-L112)
- [apps/portal/src/components/HUD/SystemAnalytics.tsx](file://apps/portal/src/components/HUD/SystemAnalytics.tsx#L1-L88)

## Dependency Analysis
- TelemetryManager depends on OpenTelemetry SDK and OTLP exporter; environment variables control endpoint and credentials.
- AudioTelemetry relies on EventBus and emits TelemetryEvent instances.
- AudioTelemetryLogger subscribes to TelemetryEvent and produces session metrics; optionally writes CSV/JSON.
- HandoverTelemetry integrates with TelemetryManager for usage recording and OpenTelemetry spans.
- Frontend components depend on React contexts and hooks to render telemetry streams.

```mermaid
graph LR
OT["TelemetryManager"] --> EB["EventBus"]
AT["AudioTelemetry"] --> EB
ATL["AudioTelemetryLogger"] --> EB
HT["HandoverTelemetry"] --> OT
FEED["TelemetryFeed"] --> STORE["useAetherStore"]
DASH["Dashboard"] --> STORE
HUD["HUD SystemAnalytics"] --> STORE
```

**Diagram sources**
- [core/infra/telemetry.py](file://core/infra/telemetry.py#L14-L130)
- [core/infra/event_bus.py](file://core/infra/event_bus.py#L69-L152)
- [core/audio/telemetry.py](file://core/audio/telemetry.py#L21-L441)
- [core/ai/handover_telemetry.py](file://core/ai/handover_telemetry.py#L295-L694)
- [apps/portal/src/components/TelemetryFeed.tsx](file://apps/portal/src/components/TelemetryFeed.tsx#L1-L40)
- [apps/portal/src/dashboard/app/page.tsx](file://apps/portal/src/dashboard/app/page.tsx#L1-L112)
- [apps/portal/src/components/HUD/SystemAnalytics.tsx](file://apps/portal/src/components/HUD/SystemAnalytics.tsx#L1-L88)

**Section sources**
- [core/infra/telemetry.py](file://core/infra/telemetry.py#L14-L130)
- [core/infra/event_bus.py](file://core/infra/event_bus.py#L69-L152)
- [core/audio/telemetry.py](file://core/audio/telemetry.py#L21-L441)
- [core/ai/handover_telemetry.py](file://core/ai/handover_telemetry.py#L295-L694)
- [apps/portal/src/components/TelemetryFeed.tsx](file://apps/portal/src/components/TelemetryFeed.tsx#L1-L40)
- [apps/portal/src/dashboard/app/page.tsx](file://apps/portal/src/dashboard/app/page.tsx#L1-L112)
- [apps/portal/src/components/HUD/SystemAnalytics.tsx](file://apps/portal/src/components/HUD/SystemAnalytics.tsx#L1-L88)

## Performance Considerations
- Event Bus isolation: Telemetry lane does not starve audio/control lanes; tests validate sub-10ms audio latency under heavy telemetry load.
- Memory footprint: AudioTelemetryLogger uses bounded deques for frame metrics and latency history; session reports are persisted on exit.
- Throughput: Benchmarks simulate high-frequency telemetry publishing to detect memory growth and validate stability.
- Processor selection: BatchSpanProcessor in production versus SimpleSpanProcessor in debug mode balances performance and observability.

**Section sources**
- [tests/benchmarks/test_event_bus_stress.py](file://tests/benchmarks/test_event_bus_stress.py#L8-L75)
- [tests/benchmarks/test_long_session.py](file://tests/benchmarks/test_long_session.py#L10-L53)
- [core/audio/telemetry.py](file://core/audio/telemetry.py#L180-L200)
- [core/infra/telemetry.py](file://core/infra/telemetry.py#L56-L61)

## Troubleshooting Guide
- Telemetry sink initialization fails:
  - Symptom: Warning about failed telemetry initialization and fallback to no-op tracer.
  - Action: Verify environment variables for endpoint, space ID, and API key; confirm network connectivity to Arize/Phoenix.
- High CPU or memory usage:
  - Symptom: Elevated RSS/VMS during extended sessions.
  - Action: Reduce frontend visualizer FPS, disable debug mode, and validate audio pipeline stages (AEC/VAD/Jitter).
- Telemetry events dropped:
  - Symptom: Expiration warnings in telemetry lane.
  - Action: Increase latency budgets for telemetry events or reduce event frequency; ensure subscribers handle events promptly.
- Export/import handover records:
  - Symptom: Need to archive or restore telemetry data.
  - Action: Use export_records and import_records to manage JSON archives.

**Section sources**
- [core/infra/telemetry.py](file://core/infra/telemetry.py#L72-L76)
- [core/infra/event_bus.py](file://core/infra/event_bus.py#L126-L143)
- [tests/benchmarks/test_long_session.py](file://tests/benchmarks/test_long_session.py#L10-L53)
- [core/ai/handover_telemetry.py](file://core/ai/handover_telemetry.py#L608-L636)

## Conclusion
The Aether Voice OS telemetry system combines a tiered event bus, audio telemetry engines, OpenTelemetry tracing, and a reactive frontend dashboard to deliver comprehensive observability. It supports real-time metrics, session analytics, and agent handover insights, enabling operational excellence, performance tuning, and effective monitoring strategies.

## Appendices

### Supported Telemetry Types and Formats
- Audio paralinguistics: TelemetryEvent with metric_name "paralinguistics" and metadata including volume, pitch, and spectral centroid.
- Frame metrics: TelemetryEvent with metric_name "frame_metrics" and full FrameMetrics serialization.
- Handover records: Structured records with outcomes, performance, and analytics aggregates.
- Usage metrics: Token usage and estimated cost attached to current spans.

**Section sources**
- [core/audio/telemetry.py](file://core/audio/telemetry.py#L77-L88)
- [core/audio/telemetry.py](file://core/audio/telemetry.py#L346-L353)
- [core/ai/handover_telemetry.py](file://core/ai/handover_telemetry.py#L97-L171)
- [core/infra/telemetry.py](file://core/infra/telemetry.py#L77-L108)

### Transmission Protocols and Platforms
- OpenTelemetry OTLP: Traces exported to Arize/Phoenix via gRPC exporter; headers configured with space ID and API key when present.
- Event Bus: Async queues with explicit tiering and dropping policies for telemetry events.

**Section sources**
- [core/infra/telemetry.py](file://core/infra/telemetry.py#L28-L66)
- [core/infra/event_bus.py](file://core/infra/event_bus.py#L69-L101)

### Integration with Monitoring Dashboards and External Analytics
- Frontend dashboard integrates with engine telemetry hook to display emotion waveforms, state machine, and system logs.
- HUD visualizes neural flux, signal integrity, pitch, and spectral centroid.
- Demo metrics and latency optimizer provide ready-to-report KPIs for judging and performance reviews.

**Section sources**
- [apps/portal/src/dashboard/app/page.tsx](file://apps/portal/src/dashboard/app/page.tsx#L1-L112)
- [apps/portal/src/components/HUD/SystemAnalytics.tsx](file://apps/portal/src/components/HUD/SystemAnalytics.tsx#L1-L88)
- [core/analytics/demo_metrics.py](file://core/analytics/demo_metrics.py#L36-L49)
- [core/analytics/latency.py](file://core/analytics/latency.py#L19-L39)

### Examples: Configuration, Custom Metrics, and Data Export
- Telemetry configuration:
  - Environment variables for Arize/Phoenix endpoint, space ID, and API key.
  - Debug mode toggles processor type for development.
- Custom metric definition:
  - AudioTelemetryLogger: Extend FrameMetrics and SessionMetrics to track additional pipeline stages.
  - HandoverTelemetry: Add new fields to HandoverRecord and update analytics aggregation.
- Data export:
  - HandoverTelemetry.export_records and import_records for JSON archives.
  - AudioTelemetryLogger.save_session_report and save_detailed_log for CSV/JSON artifacts.

**Section sources**
- [core/infra/telemetry.py](file://core/infra/telemetry.py#L28-L61)
- [core/audio/telemetry.py](file://core/audio/telemetry.py#L100-L394)
- [core/ai/handover_telemetry.py](file://core/ai/handover_telemetry.py#L608-L636)

### Relationship with System Performance Monitoring, Error Tracking, and Operational Insights
- Performance monitoring:
  - LatencyOptimizer and AudioTelemetryLogger provide latency percentiles and jitter metrics.
  - Event Bus stress tests validate lane isolation and audio latency guarantees.
- Error tracking:
  - HandoverTelemetry captures failure categories and reasons; spans set error status with descriptions.
  - TelemetryEvent expiration indicates delivery or processing delays.
- Operational insights:
  - DemoMetrics and HandoverAnalytics summarize success rates, top failure categories, and agent pair performance.
  - Frontend dashboard displays real-time system logs and state.

**Section sources**
- [core/analytics/latency.py](file://core/analytics/latency.py#L19-L39)
- [core/audio/telemetry.py](file://core/audio/telemetry.py#L280-L340)
- [tests/benchmarks/test_event_bus_stress.py](file://tests/benchmarks/test_event_bus_stress.py#L8-L75)
- [core/ai/handover_telemetry.py](file://core/ai/handover_telemetry.py#L365-L425)
- [apps/portal/src/dashboard/app/page.tsx](file://apps/portal/src/dashboard/app/page.tsx#L1-L112)

### Data Privacy, Retention Policies, and Storage Optimization
- Privacy:
  - Audio telemetry focuses on mathematical features; no raw audio is stored by default in the described components.
  - Handover records include metadata; ensure sensitive data is redacted or anonymized before persistence.
- Retention:
  - In-memory limits on records and frame metrics; adjust max sizes according to operational needs.
- Storage optimization:
  - Use bounded deques and periodic CSV/JSON exports; disable debug mode in production to reduce overhead.

**Section sources**
- [core/audio/telemetry.py](file://core/audio/telemetry.py#L180-L200)
- [core/ai/handover_telemetry.py](file://core/ai/handover_telemetry.py#L306-L314)

### Best Practices for Telemetry Instrumentation and Monitoring Strategy
- Instrumentation:
  - Attach usage attributes to spans for cost visibility; keep metric names consistent and metadata structured.
  - Emit telemetry at appropriate cadences; avoid overwhelming the telemetry lane.
- Monitoring strategy:
  - Track latency percentiles and jitter; alert on p95/p99 regressions.
  - Monitor handover success rates and top failure categories; correlate with audio pipeline metrics.
  - Validate bus isolation under load; ensure audio deadlines are met.

**Section sources**
- [core/infra/telemetry.py](file://core/infra/telemetry.py#L77-L108)
- [core/analytics/latency.py](file://core/analytics/latency.py#L19-L39)
- [tests/benchmarks/test_event_bus_stress.py](file://tests/benchmarks/test_event_bus_stress.py#L8-L75)