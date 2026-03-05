# Testing and Quality Assurance

<cite>
**Referenced Files in This Document**
- [testing_matrix.md](file://docs/testing_matrix.md)
- [aether_pipeline.yml](file://.github/workflows/aether_pipeline.yml)
- [conftest.py](file://conftest.py)
- [bench_latency.py](file://tests/benchmarks/bench_latency.py)
- [bench_focus.py](file://tests/benchmarks/bench_focus.py)
- [bench_dsp.py](file://tests/benchmarks/bench_dsp.py)
- [test_event_bus_stress.py](file://tests/benchmarks/test_event_bus_stress.py)
- [test_event_bus_load.py](file://tests/stress/test_event_bus_load.py)
- [test_system_alpha_e2e.py](file://tests/e2e/test_system_alpha_e2e.py)
- [benchmark_report.json](file://tests/reports/benchmark_report.json)
- [stability_report.json](file://tests/reports/stability_report.json)
- [latency_report.json](file://tests/reports/latency_report.json)
- [stress_report.json](file://tests/reports/stress_report.json)
- [accuracy_benchmark.py](file://infra/scripts/accuracy_benchmark.py)
- [health_scanner.py](file://infra/scripts/health_scanner.py)
- [stability_test.py](file://infra/scripts/stability_test.py)
- [dashboard_generator.py](file://tools/dashboard_generator.py)
- [benchmark_runner.py](file://tools/benchmark_runner.py)
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
This document describes the testing and quality assurance framework for Aether Voice OS. It covers the testing strategy across unit, integration, performance, and end-to-end categories; the benchmarking system for audio processing, latency, and system performance; stress testing approaches for event bus load and system resilience; the testing infrastructure and continuous integration setup; and guidance for contributors on writing custom tests, extending the test suite, and maintaining quality metrics.

## Project Structure
The testing and QA system is organized into distinct layers and directories:
- Unit tests: located under tests/unit
- Integration tests: tests/integration
- Benchmarks: tests/benchmarks
- Stress tests: tests/stress
- End-to-end tests: tests/e2e
- Reports: tests/reports
- CI pipeline: .github/workflows/aether_pipeline.yml
- Pytest configuration: conftest.py
- Documentation: docs/testing_matrix.md
- Infrastructure scripts: infra/scripts/*
- Tools: tools/*

```mermaid
graph TB
subgraph "Tests"
U["Unit Tests<br/>tests/unit"]
I["Integration Tests<br/>tests/integration"]
B["Benchmarks<br/>tests/benchmarks"]
S["Stress Tests<br/>tests/stress"]
E["E2E Tests<br/>tests/e2e"]
R["Reports<br/>tests/reports"]
end
subgraph "CI"
W["GitHub Actions<br/>.github/workflows/aether_pipeline.yml"]
end
subgraph "Docs"
M["Testing Matrix<br/>docs/testing_matrix.md"]
C["Pytest Config<br/>conftest.py"]
end
subgraph "Infra Scripts"
ACC["Accuracy Benchmark<br/>infra/scripts/accuracy_benchmark.py"]
HSCN["Health Scanner<br/>infra/scripts/health_scanner.py"]
STAB["Stability Test<br/>infra/scripts/stability_test.py"]
end
subgraph "Tools"
DASH["Dashboard Generator<br/>tools/dashboard_generator.py"]
RUN["Benchmark Runner<br/>tools/benchmark_runner.py"]
end
M --> U
M --> I
M --> B
M --> S
M --> E
C --> U
C --> I
C --> B
C --> S
C --> E
W --> U
W --> I
W --> B
W --> S
W --> E
ACC --> B
HSCN --> B
STAB --> S
DASH --> R
RUN --> B
```

**Diagram sources**
- [aether_pipeline.yml](file://.github/workflows/aether_pipeline.yml#L1-L160)
- [testing_matrix.md](file://docs/testing_matrix.md#L1-L79)
- [conftest.py](file://conftest.py#L1-L10)
- [accuracy_benchmark.py](file://infra/scripts/accuracy_benchmark.py)
- [health_scanner.py](file://infra/scripts/health_scanner.py)
- [stability_test.py](file://infra/scripts/stability_test.py)
- [dashboard_generator.py](file://tools/dashboard_generator.py)
- [benchmark_runner.py](file://tools/benchmark_runner.py)

**Section sources**
- [aether_pipeline.yml](file://.github/workflows/aether_pipeline.yml#L1-L160)
- [testing_matrix.md](file://docs/testing_matrix.md#L1-L79)
- [conftest.py](file://conftest.py#L1-L10)

## Core Components
- Testing strategy tiers:
  - Unit: Core logic and math validations using pytest
  - Integration: Bus and cloud connectivity checks
  - E2E Audit: User-perceived latency and end-to-end flows
  - Stress: Stability and memory pressure under load
- Benchmarking system:
  - Latency benchmark for internal processing budget
  - Focus detection benchmark for paralinguistic accuracy
  - DSP performance comparison between Rust and NumPy
  - Long session stability and DNA chaos stability reports
- Stress testing:
  - Event bus lane isolation and 10k+ EPS throughput
- Continuous integration:
  - Rust check, lint/style, Python tests with coverage, portal checks, security, and Docker build
- Reporting:
  - JSON reports for latency, stress, stability, and benchmark summaries

**Section sources**
- [testing_matrix.md](file://docs/testing_matrix.md#L8-L18)
- [bench_latency.py](file://tests/benchmarks/bench_latency.py#L1-L88)
- [bench_focus.py](file://tests/benchmarks/bench_focus.py#L1-L164)
- [bench_dsp.py](file://tests/benchmarks/bench_dsp.py#L1-L135)
- [test_event_bus_stress.py](file://tests/benchmarks/test_event_bus_stress.py#L1-L76)
- [test_event_bus_load.py](file://tests/stress/test_event_bus_load.py#L1-L70)
- [benchmark_report.json](file://tests/reports/benchmark_report.json#L1-L297)
- [stability_report.json](file://tests/reports/stability_report.json#L1-L210)
- [latency_report.json](file://tests/reports/latency_report.json#L1-L7)
- [stress_report.json](file://tests/reports/stress_report.json#L1-L6)

## Architecture Overview
The testing architecture integrates pytest-driven unit and integration tests, specialized benchmarking scripts, and CI-driven quality gates. Benchmarks produce structured JSON reports consumed by dashboard tools. Stress tests validate event bus behavior under extreme conditions. E2E tests exercise the full protocol stack with realistic timeouts and diagnostics.

```mermaid
sequenceDiagram
participant Dev as "Developer"
participant Pytest as "pytest runner"
participant Bench as "Benchmark Script"
participant Report as "Report Writer"
participant CI as "GitHub Actions"
Dev->>Pytest : Run unit/integration tests
Pytest-->>Dev : Test results and coverage
Dev->>Bench : Execute latency/focus/DSP benchmarks
Bench->>Report : Write JSON report
Report-->>Dev : benchmark_report.json
CI->>Pytest : Run tests with coverage
CI->>Bench : Run benchmarks
Pytest-->>CI : Coverage XML + summary
Bench-->>CI : Reports artifacts
```

**Diagram sources**
- [aether_pipeline.yml](file://.github/workflows/aether_pipeline.yml#L61-L101)
- [bench_latency.py](file://tests/benchmarks/bench_latency.py#L23-L87)
- [bench_focus.py](file://tests/benchmarks/bench_focus.py#L83-L163)
- [bench_dsp.py](file://tests/benchmarks/bench_dsp.py#L76-L134)
- [benchmark_report.json](file://tests/reports/benchmark_report.json#L1-L297)

## Detailed Component Analysis

### Latency Benchmark
Purpose: Measure internal processing latency excluding external network and inference delays. Targets include sub-10ms average internal latency and a small fraction of the 180ms total turnaround budget.

Key behaviors:
- Generates PCM frames at 16 kHz, 30 ms length
- Runs VAD and paralinguistic analysis in a tight loop
- Computes average, p95, and p99 latencies
- Prints resource budget usage and success criteria

```mermaid
flowchart TD
Start(["Start Latency Benchmark"]) --> Setup["Initialize VAD and Analyzer"]
Setup --> FrameGen["Generate PCM Frame (16kHz, 30ms)"]
FrameGen --> Loop{"Iterate 1000x"}
Loop --> |Yes| VAD["Run VAD and Energy Analysis"]
VAD --> Paraling["Analyze Paralinguistics"]
Paraling --> Prep["Simulate Gateway Payload Prep"]
Prep --> Record["Record Elapsed Time (ms)"]
Record --> Loop
Loop --> |No| Stats["Compute Average, p95, p99"]
Stats --> Budget["Estimate Budget Usage"]
Budget --> Result{"Within Target?"}
Result --> |Yes| Pass["SUCCESS"]
Result --> |No| Warn["WARNING"]
Pass --> End(["End"])
Warn --> End
```

**Diagram sources**
- [bench_latency.py](file://tests/benchmarks/bench_latency.py#L23-L87)

**Section sources**
- [bench_latency.py](file://tests/benchmarks/bench_latency.py#L1-L88)

### Focus Detection Benchmark
Purpose: Evaluate paralinguistic accuracy for Zen Mode detection using synthetic and optionally real-world audio.

Key behaviors:
- Generates typing, speech, and silence chunks
- Optionally loads real WAV files labeled by filename convention
- Computes accuracy, precision, recall, and F1 score
- Validates against competitive-edge thresholds

```mermaid
flowchart TD
StartFD(["Start Focus Benchmark"]) --> Mode{"Real Data Mode?"}
Mode --> |Yes| LoadReal["Load WAV Frames (16kHz, 100ms)"]
Mode --> |No| GenSynth["Generate Synthetic Chunks"]
LoadReal --> Analyze["Analyze with ParalinguisticAnalyzer"]
GenSynth --> Analyze
Analyze --> Metrics["Compute Accuracy/Precision/Recall/F1"]
Metrics --> Thresholds{"Meets Targets?"}
Thresholds --> |Yes| FD_Pass["SUCCESS"]
Thresholds --> |No| FD_Warn["WARNING"]
FD_Pass --> EndFD(["End"])
FD_Warn --> EndFD
```

**Diagram sources**
- [bench_focus.py](file://tests/benchmarks/bench_focus.py#L83-L163)

**Section sources**
- [bench_focus.py](file://tests/benchmarks/bench_focus.py#L1-L164)

### DSP Performance Benchmark (Rust vs NumPy)
Purpose: Compare performance of Rust Cortex DSP functions versus NumPy baselines.

Key behaviors:
- Benchmarks energy_vad and find_zero_crossing
- Measures microseconds per call for both implementations
- Calculates speedup ratio when Rust backend is available
- Provides diagnostic output and success condition

```mermaid
flowchart TD
StartDSP(["Start DSP Benchmark"]) --> Seed["Seed RNG and Generate PCM"]
Seed --> Warmup["Warm-up Calls"]
Warmup --> EVAD["Benchmark energy_vad"]
EVAD --> ZC["Benchmark find_zero_crossing"]
ZC --> Compare{"Rust Available?"}
Compare --> |Yes| Speedup["Compute Speedup Ratio"]
Compare --> |No| NoRust["Fallback to NumPy Only"]
Speedup --> Report["Print Results"]
NoRust --> Report
Report --> EndDSP(["End"])
```

**Diagram sources**
- [bench_dsp.py](file://tests/benchmarks/bench_dsp.py#L76-L134)

**Section sources**
- [bench_dsp.py](file://tests/benchmarks/bench_dsp.py#L1-L135)

### Event Bus Stress: Lane Isolation
Purpose: Validate multi-lane isolation by flooding the Telemetry lane while measuring audio frame latency.

Key behaviors:
- Subscribes to audio events
- Publishes 10k telemetry events to simulate load
- Publishes a single high-priority audio frame mid-flood
- Asserts that audio latency remains under 10 ms

```mermaid
sequenceDiagram
participant Test as "test_event_bus_lane_isolation"
participant Bus as "EventBus"
participant AudioSub as "Audio Subscriber"
participant Flood as "Telemetry Flood"
Test->>Bus : start()
Test->>Bus : subscribe(AudioFrameEvent, audio_cb)
Test->>Flood : publish(TelemetryEvent) x10k
Test->>Bus : publish(AudioFrameEvent)
Bus-->>AudioSub : deliver audio event
AudioSub-->>Test : set processed timestamp
Test->>Test : compute audio_latency_ms
Test-->>Test : assert < 10ms
Test->>Bus : stop()
```

**Diagram sources**
- [test_event_bus_stress.py](file://tests/benchmarks/test_event_bus_stress.py#L9-L75)

**Section sources**
- [test_event_bus_stress.py](file://tests/benchmarks/test_event_bus_stress.py#L1-L76)

### Event Bus Load: 10k+ EPS
Purpose: Stress the event bus with 10,000+ events per second across three priority tiers.

Key behaviors:
- Publishes mixed Audio, Control, and Telemetry events
- Tracks processed counts per category
- Asserts minimum EPS and low drop rate under 10s

```mermaid
flowchart TD
StartEPS(["Start 10k+ EPS Stress"]) --> Init["Initialize EventBus and Subscribers"]
Init --> Produce["Produce Mixed Events (Audio/Control/Telemetry)"]
Produce --> Publish["Publish to EventBus"]
Publish --> Wait["Wait until completion or timeout"]
Wait --> Analyze["Compute EPS and Drop Rate"]
Analyze --> Asserts{"Throughput & Drop Rate OK?"}
Asserts --> |Yes| EPS_Pass["SUCCESS"]
Asserts --> |No| EPS_Fail["FAILED"]
EPS_Pass --> EndEPS(["End"])
EPS_Fail --> EndEPS
```

**Diagram sources**
- [test_event_bus_load.py](file://tests/stress/test_event_bus_load.py#L8-L67)

**Section sources**
- [test_event_bus_load.py](file://tests/stress/test_event_bus_load.py#L1-L70)

### System Alpha E2E (Zero-Mock)
Purpose: Hardened end-to-end test validating protocol handshake, session establishment, and basic audio flow with strict timeouts and diagnostics.

Key behaviors:
- Generates signing keys and initializes registry
- Starts gateway server and connects via WebSocket
- Handles challenge/response handshake and session ACK
- Sends dummy audio and asserts hive activity
- Uses timeouts to detect protocol hangs

```mermaid
sequenceDiagram
participant Test as "test_system_alpha_e2e"
participant GW as "AetherGateway"
participant WS as "WebSocket Client"
participant Hive as "HiveCoordinator"
Test->>GW : Initialize and start
Test->>WS : Connect to gateway URI
WS-->>Test : receive connect.challenge
Test->>Test : sign challenge bytes
Test->>WS : send connect.response
WS-->>Test : receive connect.ack or error
Test->>WS : send dummy audio
Test->>Hive : assert active_soul not None
Test->>GW : cancel and shutdown
```

**Diagram sources**
- [test_system_alpha_e2e.py](file://tests/e2e/test_system_alpha_e2e.py#L61-L182)

**Section sources**
- [test_system_alpha_e2e.py](file://tests/e2e/test_system_alpha_e2e.py#L1-L187)

### Continuous Integration and Quality Gates
The CI pipeline enforces:
- Rust check for Cortex
- Linting and formatting with ruff
- Python tests with coverage and import verification
- Next.js portal linting and testing
- Security scanning with bandit and safety
- Docker image build check

```mermaid
graph TB
Push["Push/Pull Request"] --> Rust["Cargo Check (Cortex)"]
Push --> Lint["Ruff Lint & Format"]
Push --> PyTest["pytest with Coverage"]
Push --> Portal["Portal Lint & Test"]
Push --> Sec["Bandit & Safety"]
Push --> Docker["Docker Build Check"]
PyTest --> Cov["Coverage Threshold"]
Sec --> Vulns["Vulnerabilities Checked"]
```

**Diagram sources**
- [aether_pipeline.yml](file://.github/workflows/aether_pipeline.yml#L20-L159)

**Section sources**
- [aether_pipeline.yml](file://.github/workflows/aether_pipeline.yml#L1-L160)

## Dependency Analysis
- Test discovery and filtering:
  - conftest.py excludes certain directories and ensures project root is in path
- Benchmark outputs:
  - Benchmarks write structured JSON reports consumed by dashboard tools
- CI orchestration:
  - GitHub Actions coordinates multi-stage jobs with dependencies

```mermaid
graph LR
Cfg["conftest.py"] --> Pytest["pytest"]
BenchLat["bench_latency.py"] --> Rep1["latency_report.json"]
BenchFocus["bench_focus.py"] --> Rep2["benchmark_report.json"]
BenchDSP["bench_dsp.py"] --> Rep2
Stress["test_event_bus_stress.py"] --> Rep3["stress_report.json"]
Load["test_event_bus_load.py"] --> Rep2
E2E["test_system_alpha_e2e.py"] --> Rep2
Dash["dashboard_generator.py"] --> Rep2
Runner["benchmark_runner.py"] --> Rep2
```

**Diagram sources**
- [conftest.py](file://conftest.py#L1-L10)
- [bench_latency.py](file://tests/benchmarks/bench_latency.py#L1-L88)
- [bench_focus.py](file://tests/benchmarks/bench_focus.py#L1-L164)
- [bench_dsp.py](file://tests/benchmarks/bench_dsp.py#L1-L135)
- [test_event_bus_stress.py](file://tests/benchmarks/test_event_bus_stress.py#L1-L76)
- [test_event_bus_load.py](file://tests/stress/test_event_bus_load.py#L1-L70)
- [test_system_alpha_e2e.py](file://tests/e2e/test_system_alpha_e2e.py#L1-L187)
- [latency_report.json](file://tests/reports/latency_report.json#L1-L7)
- [stress_report.json](file://tests/reports/stress_report.json#L1-L6)
- [benchmark_report.json](file://tests/reports/benchmark_report.json#L1-L297)
- [dashboard_generator.py](file://tools/dashboard_generator.py)
- [benchmark_runner.py](file://tools/benchmark_runner.py)

**Section sources**
- [conftest.py](file://conftest.py#L1-L10)
- [benchmark_report.json](file://tests/reports/benchmark_report.json#L1-L297)
- [latency_report.json](file://tests/reports/latency_report.json#L1-L7)
- [stress_report.json](file://tests/reports/stress_report.json#L1-L6)

## Performance Considerations
- Latency targets:
  - Internal processing budget should remain under 10 ms average to preserve ~175 ms for network and inference within the 180 ms total turnaround goal
- Throughput targets:
  - Expect 10k+ EPS in a clean environment with sub-10 ms per burst processing
- Accuracy targets:
  - Focus detection should meet competitive-edge thresholds (accuracy and F1 scores)
- Stability:
  - Long sessions should show bounded memory growth and convergence

[No sources needed since this section provides general guidance]

## Troubleshooting Guide
Common issues and techniques:
- Port conflicts:
  - If binding fails, the system should detect OSError and switch to a backup port without crashing
- Redis disconnects:
  - The global bus should log failures and enter a retry state without interrupting the primary audio stream
- Protocol hangs:
  - Use E2E tests with timeouts to detect stalls during handshake or session establishment
- Coverage failures:
  - Ensure coverage threshold is met and investigate missing modules
- TCC sandbox issues:
  - conftest.py adjusts collection paths to avoid TCC sandbox problems

**Section sources**
- [testing_matrix.md](file://docs/testing_matrix.md#L68-L79)
- [test_system_alpha_e2e.py](file://tests/e2e/test_system_alpha_e2e.py#L169-L174)
- [aether_pipeline.yml](file://.github/workflows/aether_pipeline.yml#L90-L101)
- [conftest.py](file://conftest.py#L1-L10)

## Conclusion
Aether Voice OS employs a rigorous, tiered testing strategy supported by dedicated benchmarks, stress tests, and a robust CI pipeline. The framework validates latency budgets, accuracy thresholds, and system stability under load, while ensuring code quality through linting, security scanning, and coverage requirements. Contributors can extend the suite by adding new benchmarks, stress scenarios, and E2E probes aligned with the documented matrix and CI expectations.

[No sources needed since this section summarizes without analyzing specific files]

## Appendices

### Writing Custom Benchmarks
- Follow the pattern of existing benchmarks:
  - Initialize core components
  - Generate synthetic or real data
  - Measure and record metrics
  - Write a structured JSON report to tests/reports
- Example reference paths:
  - [bench_latency.py](file://tests/benchmarks/bench_latency.py#L23-L87)
  - [bench_focus.py](file://tests/benchmarks/bench_focus.py#L83-L163)
  - [bench_dsp.py](file://tests/benchmarks/bench_dsp.py#L76-L134)

**Section sources**
- [bench_latency.py](file://tests/benchmarks/bench_latency.py#L1-L88)
- [bench_focus.py](file://tests/benchmarks/bench_focus.py#L1-L164)
- [bench_dsp.py](file://tests/benchmarks/bench_dsp.py#L1-L135)

### Extending the Test Suite
- Add unit tests under tests/unit
- Add integration tests under tests/integration
- Add stress tests under tests/stress
- Add E2E tests under tests/e2e
- Use pytest markers and async fixtures as demonstrated in existing tests
- Reference:
  - [test_event_bus_load.py](file://tests/stress/test_event_bus_load.py#L6-L67)
  - [test_system_alpha_e2e.py](file://tests/e2e/test_system_alpha_e2e.py#L60-L103)

**Section sources**
- [test_event_bus_load.py](file://tests/stress/test_event_bus_load.py#L1-L70)
- [test_system_alpha_e2e.py](file://tests/e2e/test_system_alpha_e2e.py#L1-L187)

### Running Specific Test Suites
- Unit tests: pytest tests/unit
- Integration tests: pytest tests/integration
- Benchmarks: python tests/benchmarks/<benchmark_script>.py
- Stress tests: pytest tests/stress
- E2E tests: pytest tests/e2e
- CI coverage threshold enforcement is configured in the pipeline

**Section sources**
- [aether_pipeline.yml](file://.github/workflows/aether_pipeline.yml#L90-L101)
- [testing_matrix.md](file://docs/testing_matrix.md#L14-L17)

### Quality Metrics and Coverage
- Coverage threshold: configured to fail under 60%
- Import verification: core modules are checked after installation
- Security scanning: bandit and safety checks are part of CI
- Linting: ruff for style and correctness

**Section sources**
- [aether_pipeline.yml](file://.github/workflows/aether_pipeline.yml#L90-L101)
- [aether_pipeline.yml](file://.github/workflows/aether_pipeline.yml#L140-L147)
- [aether_pipeline.yml](file://.github/workflows/aether_pipeline.yml#L52-L56)

### Test Debugging and Profiling
- Use E2E tests with timeouts to isolate protocol stalls
- Enable debug mode in AI configurations for additional logs
- Inspect JSON reports for detailed metrics and trends
- Validate event bus behavior under load with stress tests

**Section sources**
- [test_system_alpha_e2e.py](file://tests/e2e/test_system_alpha_e2e.py#L169-L174)
- [test_event_bus_stress.py](file://tests/benchmarks/test_event_bus_stress.py#L58-L75)
- [benchmark_report.json](file://tests/reports/benchmark_report.json#L1-L297)