# 🤖 Automated Code Improvement Report

I analyzed the codebase for structural patterns, complexity, and common anti-patterns.

### 📊 Summary
- **Total Issues Found:** 396
- **Errors:** 34
- **Warnings:** 287
- **Info:** 75

### 🔍 Details
#### 📄 `task_runner.py`
- 🟠 **Line 123:** Broad except clause. Catch specific exceptions instead.
- 🟠 **Line 152:** Broad except clause. Catch specific exceptions instead.
- 🟠 **Line 179:** Broad except clause. Catch specific exceptions instead.
- 🟠 **Line 220:** Broad except clause. Catch specific exceptions instead.
- 🟠 **Line 267:** Broad except clause. Catch specific exceptions instead.
- 🔵 **Line 314:** Use of print() found. Consider using the structured logging module.

#### 📄 `test_gcc.py`
- 🔵 **Line 40:** Use of print() found. Consider using the structured logging module.

#### 📄 `skills/github-intel/scripts/repo_analyzer.py`
- 🟠 **Line 100:** Broad except clause. Catch specific exceptions instead.
- 🟠 **Line 129:** Broad except clause. Catch specific exceptions instead.

#### 📄 `skills/github-intel/scripts/repo_to_markdown.py`
- 🟠 **Line 84:** Broad except clause. Catch specific exceptions instead.
- 🟠 **Line 103:** Broad except clause. Catch specific exceptions instead.

#### 📄 `infra/scripts/benchmark.py`
- 🔴 **Line 69:** Empty except block (silenced error). Consider logging the exception.
- 🟠 **Line 69:** Broad except clause. Catch specific exceptions instead.
- 🟠 **Line 132:** Broad except clause. Catch specific exceptions instead.
- 🔴 **Line 232:** Empty except block (silenced error). Consider logging the exception.

#### 📄 `infra/scripts/generate_code_index.py`
- 🟠 **Line 77:** Broad except clause. Catch specific exceptions instead.
- 🟠 **Line 141:** Function 'build_dependency_graph' is too long (90 lines). Consider refactoring.
- 🟠 **Line 141:** Function 'build_dependency_graph' has high complexity (18). Consider breaking it down.
- 🟠 **Line 161:** Broad except clause. Catch specific exceptions instead.
- 🟠 **Line 194:** Broad except clause. Catch specific exceptions instead.
- 🟠 **Line 234:** Function 'write_outputs' is too long (56 lines). Consider refactoring.

#### 📄 `infra/scripts/health_scanner.py`
- 🟠 **Line 132:** Function 'check_python_imports' has high complexity (12). Consider breaking it down.
- 🟠 **Line 167:** Function 'check_python_patterns' is too long (88 lines). Consider refactoring.
- 🟠 **Line 167:** Function 'check_python_patterns' has high complexity (21). Consider breaking it down.
- 🟠 **Line 465:** Function 'generate_report' is too long (85 lines). Consider refactoring.
- 🟠 **Line 465:** Function 'generate_report' has high complexity (10). Consider breaking it down.

#### 📄 `infra/scripts/debug/test_key.py`
- 🔴 **Line 12:** Empty except block (silenced error). Consider logging the exception.

#### 📄 `infra/scripts/debug/debug_import.py`
- 🟠 **Line 17:** Broad except clause. Catch specific exceptions instead.

#### 📄 `infra/scripts/debug/test_voice_config.py`
- 🟠 **Line 12:** Broad except clause. Catch specific exceptions instead.

#### 📄 `examples/aec_demo.py`
- 🔵 **Line 18:** Use of print() found. Consider using the structured logging module.
- 🔵 **Line 43:** Use of print() found. Consider using the structured logging module.
- 🔵 **Line 54:** Use of print() found. Consider using the structured logging module.
- 🔵 **Line 62:** Use of print() found. Consider using the structured logging module.

#### 📄 `examples/audio_analysis.py`
- 🔴 **Line 12:** Empty except block (silenced error). Consider logging the exception.
- 🔵 **Line 17:** Use of print() found. Consider using the structured logging module.
- 🔵 **Line 37:** Use of print() found. Consider using the structured logging module.
- 🔵 **Line 39:** Use of print() found. Consider using the structured logging module.
- 🔵 **Line 40:** Use of print() found. Consider using the structured logging module.
- 🔵 **Line 41:** Use of print() found. Consider using the structured logging module.
- 🔵 **Line 45:** Use of print() found. Consider using the structured logging module.
- 🔵 **Line 47:** Use of print() found. Consider using the structured logging module.
- 🔵 **Line 49:** Use of print() found. Consider using the structured logging module.
- 🔵 **Line 51:** Use of print() found. Consider using the structured logging module.
- 🔵 **Line 52:** Use of print() found. Consider using the structured logging module.
- 🔵 **Line 53:** Use of print() found. Consider using the structured logging module.
- 🔵 **Line 57:** Use of print() found. Consider using the structured logging module.
- 🔵 **Line 59:** Use of print() found. Consider using the structured logging module.
- 🟠 **Line 72:** Broad except clause. Catch specific exceptions instead.
- 🔵 **Line 73:** Use of print() found. Consider using the structured logging module.
- 🔵 **Line 74:** Use of print() found. Consider using the structured logging module.

#### 📄 `examples/capture_playback.py`
- 🔵 **Line 16:** Use of print() found. Consider using the structured logging module.
- 🔵 **Line 28:** Use of print() found. Consider using the structured logging module.
- 🔵 **Line 36:** Use of print() found. Consider using the structured logging module.
- 🔵 **Line 47:** Use of print() found. Consider using the structured logging module.
- 🔵 **Line 57:** Use of print() found. Consider using the structured logging module.

#### 📄 `scripts/auto_improve.py`
- 🟠 **Line 97:** Broad except clause. Catch specific exceptions instead.
- 🟠 **Line 112:** Function 'main' is too long (67 lines). Consider refactoring.

#### 📄 `tests/test_benchmark_framework.py`
- 🟠 **Line 136:** Broad except clause. Catch specific exceptions instead.

#### 📄 `tests/demo_complete_testing.py`
- 🟠 **Line 51:** Broad except clause. Catch specific exceptions instead.
- 🟠 **Line 116:** Broad except clause. Catch specific exceptions instead.

#### 📄 `tests/live_dashboard.py`
- 🔴 **Line 130:** Empty except block (silenced error). Consider logging the exception.
- 🟠 **Line 199:** Function '_render' is too long (53 lines). Consider refactoring.

#### 📄 `tests/dynamic_config_controller.py`
- 🟠 **Line 47:** Function '__init__' is too long (128 lines). Consider refactoring.
- 🟠 **Line 206:** Broad except clause. Catch specific exceptions instead.
- 🟠 **Line 262:** Broad except clause. Catch specific exceptions instead.
- 🟠 **Line 299:** Broad except clause. Catch specific exceptions instead.
- 🟠 **Line 345:** Broad except clause. Catch specific exceptions instead.
- 🟠 **Line 380:** Broad except clause. Catch specific exceptions instead.

#### 📄 `tests/test_critical_fixes.py`
- 🟠 **Line 150:** Broad except clause. Catch specific exceptions instead.

#### 📄 `tests/verify_benchmark.py`
- 🟠 **Line 45:** Broad except clause. Catch specific exceptions instead.

#### 📄 `tests/gemini_live_interactive_benchmark.py`
- 🔴 **Line 56:** Empty except block (silenced error). Consider logging the exception.
- 🟠 **Line 184:** Function 'render' is too long (106 lines). Consider refactoring.
- 🟠 **Line 489:** Broad except clause. Catch specific exceptions instead.
- 🟠 **Line 614:** Broad except clause. Catch specific exceptions instead.
- 🟠 **Line 781:** Broad except clause. Catch specific exceptions instead.

#### 📄 `tests/e2e/test_browser_voice_e2e.py`
- 🔴 **Line 58:** Empty except block (silenced error). Consider logging the exception.
- 🟠 **Line 127:** Broad except clause. Catch specific exceptions instead.
- 🟠 **Line 151:** Broad except clause. Catch specific exceptions instead.
- 🟠 **Line 170:** Broad except clause. Catch specific exceptions instead.
- 🟠 **Line 214:** Broad except clause. Catch specific exceptions instead.
- 🟠 **Line 253:** Broad except clause. Catch specific exceptions instead.
- 🟠 **Line 282:** Broad except clause. Catch specific exceptions instead.
- 🔴 **Line 318:** Empty except block (silenced error). Consider logging the exception.
- 🔴 **Line 325:** Empty except block (silenced error). Consider logging the exception.

#### 📄 `tests/e2e/test_performance_stress.py`
- 🔴 **Line 133:** Empty except block (silenced error). Consider logging the exception.

#### 📄 `tests/e2e/test_system_alpha_e2e.py`
- 🟠 **Line 172:** Broad except clause. Catch specific exceptions instead.
- 🔴 **Line 180:** Empty except block (silenced error). Consider logging the exception.

#### 📄 `tests/integration/test_audio_pipeline_e2e.py`
- 🔴 **Line 86:** Empty except block (silenced error). Consider logging the exception.

#### 📄 `tests/integration/test_gateway_e2e.py`
- 🔴 **Line 161:** Empty except block (silenced error). Consider logging the exception.

#### 📄 `tests/benchmarks/bench_focus.py`
- 🟠 **Line 73:** Broad except clause. Catch specific exceptions instead.
- 🟠 **Line 83:** Function 'run_benchmark' is too long (76 lines). Consider refactoring.
- 🟠 **Line 83:** Function 'run_benchmark' has high complexity (17). Consider breaking it down.

#### 📄 `tests/benchmarks/bench_dsp.py`
- 🟠 **Line 76:** Function 'main' is too long (54 lines). Consider refactoring.

#### 📄 `tests/benchmarks/voice_quality_benchmark.py`
- 🔴 **Line 42:** Empty except block (silenced error). Consider logging the exception.
- 🟠 **Line 266:** Broad except clause. Catch specific exceptions instead.
- 🟠 **Line 354:** Broad except clause. Catch specific exceptions instead.
- 🟠 **Line 367:** Function 'benchmark_double_talk_performance' is too long (92 lines). Consider refactoring.
- 🟠 **Line 462:** Function 'benchmark_aec_effectiveness' is too long (82 lines). Consider refactoring.
- 🟠 **Line 547:** Function 'benchmark_emotion_f1_score' is too long (119 lines). Consider refactoring.
- 🟠 **Line 547:** Function 'benchmark_emotion_f1_score' has high complexity (16). Consider breaking it down.
- 🟠 **Line 796:** Broad except clause. Catch specific exceptions instead.
- 🟠 **Line 809:** Broad except clause. Catch specific exceptions instead.
- 🟠 **Line 819:** Broad except clause. Catch specific exceptions instead.
- 🟠 **Line 837:** Broad except clause. Catch specific exceptions instead.
- 🟠 **Line 847:** Broad except clause. Catch specific exceptions instead.
- 🟠 **Line 857:** Broad except clause. Catch specific exceptions instead.
- 🟠 **Line 867:** Broad except clause. Catch specific exceptions instead.

#### 📄 `tests/unit/test_telemetry.py`
- 🟠 **Line 24:** Function 'test_audio_telemetry_throttling' is too long (56 lines). Consider refactoring.

#### 📄 `tests/unit/test_gateway.py`
- 🔴 **Line 79:** Empty except block (silenced error). Consider logging the exception.

#### 📄 `tests/unit/test_voice_processing_comprehensive.py`
- 🟠 **Line 713:** Function 'run_comprehensive_tests' is too long (141 lines). Consider refactoring.
- 🟠 **Line 762:** Broad except clause. Catch specific exceptions instead.
- 🟠 **Line 805:** Broad except clause. Catch specific exceptions instead.
- 🟠 **Line 846:** Broad except clause. Catch specific exceptions instead.

#### 📄 `agents/security_agent.py`
- 🟠 **Line 65:** Broad except clause. Catch specific exceptions instead.
- 🟠 **Line 99:** Broad except clause. Catch specific exceptions instead.
- 🟠 **Line 134:** Broad except clause. Catch specific exceptions instead.
- 🟠 **Line 150:** Broad except clause. Catch specific exceptions instead.
- 🟠 **Line 202:** Broad except clause. Catch specific exceptions instead.

#### 📄 `agents/di_injector.py`
- 🟠 **Line 50:** Broad except clause. Catch specific exceptions instead.
- 🟠 **Line 150:** Broad except clause. Catch specific exceptions instead.

#### 📄 `agents/learning_agent.py`
- 🟠 **Line 58:** Broad except clause. Catch specific exceptions instead.
- 🟠 **Line 108:** Broad except clause. Catch specific exceptions instead.
- 🟠 **Line 151:** Broad except clause. Catch specific exceptions instead.
- 🟠 **Line 191:** Broad except clause. Catch specific exceptions instead.
- 🟠 **Line 236:** Broad except clause. Catch specific exceptions instead.
- 🟠 **Line 275:** Broad except clause. Catch specific exceptions instead.

#### 📄 `agents/optimization_agent.py`
- 🟠 **Line 52:** Broad except clause. Catch specific exceptions instead.
- 🟠 **Line 129:** Broad except clause. Catch specific exceptions instead.
- 🟠 **Line 156:** Broad except clause. Catch specific exceptions instead.
- 🟠 **Line 188:** Broad except clause. Catch specific exceptions instead.
- 🟠 **Line 234:** Broad except clause. Catch specific exceptions instead.

#### 📄 `agents/structure_analysis_agent.py`
- 🟠 **Line 119:** Broad except clause. Catch specific exceptions instead.
- 🟠 **Line 183:** Broad except clause. Catch specific exceptions instead.
- 🟠 **Line 330:** Function '_detect_circular_dependencies' has high complexity (11). Consider breaking it down.
- 🟠 **Line 417:** Function '_generate_suggestions' is too long (78 lines). Consider refactoring.

#### 📄 `agents/dependency_management_agent.py`
- 🟠 **Line 129:** Broad except clause. Catch specific exceptions instead.
- 🟠 **Line 170:** Broad except clause. Catch specific exceptions instead.
- 🟠 **Line 202:** Function '_parse_pyproject_toml' has high complexity (12). Consider breaking it down.
- 🟠 **Line 240:** Broad except clause. Catch specific exceptions instead.
- 🟠 **Line 268:** Broad except clause. Catch specific exceptions instead.
- 🟠 **Line 318:** Broad except clause. Catch specific exceptions instead.
- 🟠 **Line 346:** Broad except clause. Catch specific exceptions instead.
- 🟠 **Line 397:** Broad except clause. Catch specific exceptions instead.
- 🟠 **Line 430:** Broad except clause. Catch specific exceptions instead.
- 🟠 **Line 495:** Broad except clause. Catch specific exceptions instead.
- 🟠 **Line 497:** Broad except clause. Catch specific exceptions instead.
- 🟠 **Line 534:** Broad except clause. Catch specific exceptions instead.
- 🟠 **Line 565:** Broad except clause. Catch specific exceptions instead.
- 🔴 **Line 587:** Empty except block (silenced error). Consider logging the exception.
- 🟠 **Line 708:** Broad except clause. Catch specific exceptions instead.

#### 📄 `core/engine.py`
- 🟠 **Line 73:** Function '__init__' is too long (93 lines). Consider refactoring.
- 🟠 **Line 168:** Function '_register_tools' is too long (59 lines). Consider refactoring.
- 🟠 **Line 384:** Broad except clause. Catch specific exceptions instead.
- 🟠 **Line 572:** Broad except clause. Catch specific exceptions instead.
- 🟠 **Line 619:** Broad except clause. Catch specific exceptions instead.
- 🔵 **Line 656:** Use of print() found. Consider using the structured logging module.

#### 📄 `core/server.py`
- 🔴 **Line 36:** Empty except block (silenced error). Consider logging the exception.
- 🔵 **Line 48:** Use of print() found. Consider using the structured logging module.
- 🔵 **Line 69:** Use of print() found. Consider using the structured logging module.
- 🔵 **Line 117:** Use of print() found. Consider using the structured logging module.
- 🔵 **Line 118:** Use of print() found. Consider using the structured logging module.
- 🔵 **Line 130:** Use of print() found. Consider using the structured logging module.
- 🔵 **Line 131:** Use of print() found. Consider using the structured logging module.
- 🔵 **Line 132:** Use of print() found. Consider using the structured logging module.
- 🔵 **Line 136:** Use of print() found. Consider using the structured logging module.
- 🔵 **Line 142:** Use of print() found. Consider using the structured logging module.
- 🔵 **Line 146:** Use of print() found. Consider using the structured logging module.

#### 📄 `core/logic/managers/pulse.py`
- 🔴 **Line 47:** Empty except block (silenced error). Consider logging the exception.
- 🟠 **Line 72:** Broad except clause. Catch specific exceptions instead.

#### 📄 `core/logic/managers/audio.py`
- 🔴 **Line 107:** Empty except block (silenced error). Consider logging the exception.
- 🔴 **Line 114:** Empty except block (silenced error). Consider logging the exception.

#### 📄 `core/infra/health_check.py`
- 🔴 **Line 89:** Empty except block (silenced error). Consider logging the exception.
- 🟠 **Line 122:** Broad except clause. Catch specific exceptions instead.
- 🟠 **Line 165:** Broad except clause. Catch specific exceptions instead.

#### 📄 `core/infra/logging_config.py`
- 🟠 **Line 9:** Function 'configure_logging' is too long (64 lines). Consider refactoring.

#### 📄 `core/infra/lifecycle.py`
- 🟠 **Line 99:** Broad except clause. Catch specific exceptions instead.

#### 📄 `core/infra/config.py`
- 🔴 **Line 158:** Empty except block (silenced error). Consider logging the exception.
- 🟠 **Line 252:** Broad except clause. Catch specific exceptions instead.
- 🔵 **Line 253:** Use of print() found. Consider using the structured logging module.
- 🟠 **Line 262:** Broad except clause. Catch specific exceptions instead.
- 🔵 **Line 264:** Use of print() found. Consider using the structured logging module.
- 🟠 **Line 267:** Broad except clause. Catch specific exceptions instead.
- 🔵 **Line 268:** Use of print() found. Consider using the structured logging module.
- 🟠 **Line 283:** Broad except clause. Catch specific exceptions instead.
- 🔵 **Line 284:** Use of print() found. Consider using the structured logging module.

#### 📄 `core/infra/event_bus.py`
- 🟠 **Line 179:** Broad except clause. Catch specific exceptions instead.

#### 📄 `core/infra/telemetry.py`
- 🟠 **Line 72:** Broad except clause. Catch specific exceptions instead.

#### 📄 `core/infra/cloud/firebase/interface.py`
- 🟠 **Line 57:** Broad except clause. Catch specific exceptions instead.
- 🟠 **Line 83:** Broad except clause. Catch specific exceptions instead.
- 🟠 **Line 113:** Broad except clause. Catch specific exceptions instead.
- 🟠 **Line 140:** Broad except clause. Catch specific exceptions instead.
- 🟠 **Line 163:** Broad except clause. Catch specific exceptions instead.
- 🟠 **Line 187:** Broad except clause. Catch specific exceptions instead.
- 🟠 **Line 204:** Broad except clause. Catch specific exceptions instead.
- 🟠 **Line 248:** Broad except clause. Catch specific exceptions instead.
- 🟠 **Line 260:** Broad except clause. Catch specific exceptions instead.

#### 📄 `core/infra/cloud/firebase/queries.py`
- 🟠 **Line 71:** Broad except clause. Catch specific exceptions instead.

#### 📄 `core/infra/transport/bus.py`
- 🟠 **Line 76:** Broad except clause. Catch specific exceptions instead.
- 🔴 **Line 88:** Empty except block (silenced error). Consider logging the exception.
- 🟠 **Line 106:** Broad except clause. Catch specific exceptions instead.
- 🟠 **Line 151:** Broad except clause. Catch specific exceptions instead.
- 🟠 **Line 157:** Broad except clause. Catch specific exceptions instead.
- 🟠 **Line 171:** Broad except clause. Catch specific exceptions instead.
- 🟠 **Line 184:** Broad except clause. Catch specific exceptions instead.
- 🟠 **Line 197:** Broad except clause. Catch specific exceptions instead.

#### 📄 `core/infra/transport/session_state.py`
- 🟠 **Line 331:** Broad except clause. Catch specific exceptions instead.
- 🔴 **Line 393:** Empty except block (silenced error). Consider logging the exception.
- 🟠 **Line 405:** Broad except clause. Catch specific exceptions instead.
- 🟠 **Line 460:** Broad except clause. Catch specific exceptions instead.

#### 📄 `core/infra/transport/gateway.py`
- 🟠 **Line 170:** Broad except clause. Catch specific exceptions instead.
- 🟠 **Line 197:** Broad except clause. Catch specific exceptions instead.
- 🟠 **Line 311:** Broad except clause. Catch specific exceptions instead.
- 🟠 **Line 488:** Broad except clause. Catch specific exceptions instead.
- 🟠 **Line 520:** Broad except clause. Catch specific exceptions instead.
- 🟠 **Line 539:** Broad except clause. Catch specific exceptions instead.
- 🔴 **Line 647:** Empty except block (silenced error). Consider logging the exception.
- 🟠 **Line 647:** Broad except clause. Catch specific exceptions instead.
- 🟠 **Line 674:** Broad except clause. Catch specific exceptions instead.
- 🟠 **Line 751:** Broad except clause. Catch specific exceptions instead.
- 🟠 **Line 765:** Broad except clause. Catch specific exceptions instead.
- 🟠 **Line 782:** Broad except clause. Catch specific exceptions instead.
- 🔴 **Line 805:** Empty except block (silenced error). Consider logging the exception.

#### 📄 `core/identity/package.py`
- 🟠 **Line 87:** Function 'load' is too long (51 lines). Consider refactoring.
- 🟠 **Line 114:** Broad except clause. Catch specific exceptions instead.

#### 📄 `core/ai/handover_telemetry.py`
- 🟠 **Line 365:** Function 'finalize_recording' is too long (60 lines). Consider refactoring.
- 🟠 **Line 365:** Function 'finalize_recording' has high complexity (11). Consider breaking it down.
- 🟠 **Line 500:** Function 'get_records' has high complexity (15). Consider breaking it down.

#### 📄 `core/ai/handover_protocol.py`
- 🟠 **Line 195:** Broad except clause. Catch specific exceptions instead.

#### 📄 `core/ai/compression.py`
- 🟠 **Line 98:** Broad except clause. Catch specific exceptions instead.

#### 📄 `core/ai/l2_synapse.py`
- 🟠 **Line 87:** Broad except clause. Catch specific exceptions instead.

#### 📄 `core/ai/session.py`
- 🟠 **Line 101:** Function '_build_session_config' is too long (58 lines). Consider refactoring.
- 🟠 **Line 173:** Broad except clause. Catch specific exceptions instead.
- 🟠 **Line 206:** Broad except clause. Catch specific exceptions instead.
- 🟠 **Line 222:** Broad except clause. Catch specific exceptions instead.
- 🟠 **Line 263:** Broad except clause. Catch specific exceptions instead.
- 🟠 **Line 304:** Broad except clause. Catch specific exceptions instead.
- 🟠 **Line 343:** Broad except clause. Catch specific exceptions instead.
- 🔴 **Line 368:** Empty except block (silenced error). Consider logging the exception.
- 🟠 **Line 387:** Broad except clause. Catch specific exceptions instead.
- 🟠 **Line 486:** Broad except clause. Catch specific exceptions instead.
- 🟠 **Line 516:** Broad except clause. Catch specific exceptions instead.
- 🟠 **Line 538:** Function '_build_system_instruction' is too long (51 lines). Consider refactoring.
- 🟠 **Line 591:** Function '_format_handover_context_for_instruction' is too long (61 lines). Consider refactoring.
- 🟠 **Line 591:** Function '_format_handover_context_for_instruction' has high complexity (17). Consider breaking it down.
- 🟠 **Line 696:** Broad except clause. Catch specific exceptions instead.
- 🟠 **Line 720:** Broad except clause. Catch specific exceptions instead.
- 🟠 **Line 833:** Broad except clause. Catch specific exceptions instead.

#### 📄 `core/ai/hive.py`
- 🟠 **Line 58:** Function '__init__' is too long (53 lines). Consider refactoring.
- 🟠 **Line 118:** Broad except clause. Catch specific exceptions instead.
- 🟠 **Line 173:** Broad except clause. Catch specific exceptions instead.
- 🟠 **Line 177:** Broad except clause. Catch specific exceptions instead.
- 🟠 **Line 185:** Function 'prepare_handoff' is too long (114 lines). Consider refactoring.
- 🟠 **Line 185:** Function 'prepare_handoff' has high complexity (17). Consider breaking it down.
- 🟠 **Line 297:** Broad except clause. Catch specific exceptions instead.
- 🟠 **Line 326:** Function 'complete_handoff' is too long (97 lines). Consider refactoring.
- 🟠 **Line 326:** Function 'complete_handoff' has high complexity (16). Consider breaking it down.
- 🟠 **Line 391:** Broad except clause. Catch specific exceptions instead.
- 🟠 **Line 414:** Broad except clause. Catch specific exceptions instead.
- 🟠 **Line 425:** Function 'rollback_handover' has high complexity (13). Consider breaking it down.
- 🟠 **Line 456:** Broad except clause. Catch specific exceptions instead.
- 🟠 **Line 471:** Broad except clause. Catch specific exceptions instead.
- 🟠 **Line 586:** Broad except clause. Catch specific exceptions instead.
- 🟠 **Line 727:** Broad except clause. Catch specific exceptions instead.

#### 📄 `core/ai/thalamic.py`
- 🟠 **Line 122:** Broad except clause. Catch specific exceptions instead.

#### 📄 `core/ai/handover/manager.py`
- 🟠 **Line 53:** Function 'architect_to_debugger_handover' is too long (62 lines). Consider refactoring.
- 🟠 **Line 249:** Broad except clause. Catch specific exceptions instead.
- 🟠 **Line 262:** Function 'handover_with_context' is too long (131 lines). Consider refactoring.
- 🟠 **Line 262:** Function 'handover_with_context' has high complexity (19). Consider breaking it down.
- 🟠 **Line 355:** Broad except clause. Catch specific exceptions instead.
- 🟠 **Line 381:** Broad except clause. Catch specific exceptions instead.
- 🟠 **Line 465:** Function 'negotiate_handover' is too long (56 lines). Consider refactoring.
- 🟠 **Line 519:** Broad except clause. Catch specific exceptions instead.
- 🟠 **Line 581:** Function 'collaborate' has high complexity (10). Consider breaking it down.

#### 📄 `core/ai/agents/voice_agent.py`
- 🟠 **Line 41:** Function 'build_dna_prompt' is too long (51 lines). Consider refactoring.

#### 📄 `core/ai/agents/specialists/architect.py`
- 🟠 **Line 35:** Function 'process' is too long (97 lines). Consider refactoring.

#### 📄 `core/ai/agents/specialists/debugger.py`
- 🟠 **Line 34:** Function 'process' is too long (104 lines). Consider refactoring.
- 🟠 **Line 140:** Function '_verify_blueprint' is too long (53 lines). Consider refactoring.

#### 📄 `core/session/restarter.py`
- 🔴 **Line 106:** Empty except block (silenced error). Consider logging the exception.
- 🔴 **Line 112:** Empty except block (silenced error). Consider logging the exception.
- 🟠 **Line 144:** Broad except clause. Catch specific exceptions instead.

#### 📄 `core/audio/spectral.py`
- 🟠 **Line 269:** Function 'extract_features' is too long (64 lines). Consider refactoring.
- 🟠 **Line 388:** Function 'gcc_phat' is too long (68 lines). Consider refactoring.

#### 📄 `core/audio/playback.py`
- 🟠 **Line 81:** Function '_callback' is too long (54 lines). Consider refactoring.
- 🟠 **Line 131:** Broad except clause. Catch specific exceptions instead.
- 🟠 **Line 184:** Broad except clause. Catch specific exceptions instead.
- 🔴 **Line 199:** Empty except block (silenced error). Consider logging the exception.
- 🟠 **Line 205:** Broad except clause. Catch specific exceptions instead.

#### 📄 `core/audio/echo_guard.py`
- 🟠 **Line 60:** Function 'is_user_speaking' is too long (51 lines). Consider refactoring.
- 🟠 **Line 60:** Function 'is_user_speaking' has high complexity (10). Consider breaking it down.

#### 📄 `core/audio/dynamic_aec.py`
- 🟠 **Line 150:** Function 'process' is too long (54 lines). Consider refactoring.
- 🟠 **Line 303:** Function 'update' is too long (67 lines). Consider refactoring.
- 🟠 **Line 419:** Function 'process' is too long (54 lines). Consider refactoring.
- 🟠 **Line 524:** Function '__init__' is too long (83 lines). Consider refactoring.
- 🟠 **Line 609:** Function 'process_frame' is too long (97 lines). Consider refactoring.

#### 📄 `core/audio/processing.py`
- 🟠 **Line 76:** Broad except clause. Catch specific exceptions instead.
- 🔵 **Line 83:** Use of print() found. Consider using the structured logging module.
- 🔵 **Line 88:** Use of print() found. Consider using the structured logging module.
- 🟠 **Line 433:** Function 'enhanced_vad' is too long (70 lines). Consider refactoring.

#### 📄 `core/audio/paralinguistics.py`
- 🟠 **Line 132:** Function 'analyze' is too long (81 lines). Consider refactoring.
- 🟠 **Line 132:** Function 'analyze' has high complexity (16). Consider breaking it down.

#### 📄 `core/audio/capture.py`
- 🟠 **Line 41:** Function 'process' is too long (55 lines). Consider refactoring.
- 🟠 **Line 41:** Function 'process' has high complexity (10). Consider breaking it down.
- 🔴 **Line 173:** Empty except block (silenced error). Consider logging the exception.
- 🟠 **Line 177:** Function '_callback' is too long (108 lines). Consider refactoring.
- 🟠 **Line 177:** Function '_callback' has high complexity (21). Consider breaking it down.

#### 📄 `core/api/gemini_proxy.py`
- 🔴 **Line 84:** Empty except block (silenced error). Consider logging the exception.
- 🟠 **Line 86:** Broad except clause. Catch specific exceptions instead.
- 🔵 **Line 87:** Use of print() found. Consider using the structured logging module.
- 🟠 **Line 95:** Broad except clause. Catch specific exceptions instead.
- 🔵 **Line 96:** Use of print() found. Consider using the structured logging module.
- 🟠 **Line 102:** Broad except clause. Catch specific exceptions instead.
- 🟠 **Line 120:** Broad except clause. Catch specific exceptions instead.

#### 📄 `core/tools/system_tool.py`
- 🟠 **Line 174:** Broad except clause. Catch specific exceptions instead.
- 🟠 **Line 214:** Broad except clause. Catch specific exceptions instead.
- 🟠 **Line 239:** Broad except clause. Catch specific exceptions instead.
- 🟠 **Line 243:** Function 'get_tools' is too long (111 lines). Consider refactoring.

#### 📄 `core/tools/hive_memory.py`
- 🟠 **Line 56:** Broad except clause. Catch specific exceptions instead.
- 🟠 **Line 72:** Broad except clause. Catch specific exceptions instead.

#### 📄 `core/tools/rag_tool.py`
- 🟠 **Line 69:** Broad except clause. Catch specific exceptions instead.

#### 📄 `core/tools/firestore_vector_store.py`
- 🟠 **Line 71:** Broad except clause. Catch specific exceptions instead.
- 🟠 **Line 119:** Broad except clause. Catch specific exceptions instead.

#### 📄 `core/tools/memory_tool.py`
- 🟠 **Line 91:** Broad except clause. Catch specific exceptions instead.
- 🟠 **Line 127:** Broad except clause. Catch specific exceptions instead.
- 🟠 **Line 168:** Broad except clause. Catch specific exceptions instead.
- 🟠 **Line 209:** Broad except clause. Catch specific exceptions instead.
- 🟠 **Line 243:** Broad except clause. Catch specific exceptions instead.
- 🟠 **Line 248:** Function 'get_tools' is too long (83 lines). Consider refactoring.

#### 📄 `core/tools/context_scraper.py`
- 🔵 **Line 37:** Use of print() found. Consider using the structured logging module.
- 🟠 **Line 59:** Broad except clause. Catch specific exceptions instead.
- 🟠 **Line 72:** Broad except clause. Catch specific exceptions instead.
- 🔵 **Line 143:** Use of print() found. Consider using the structured logging module.

#### 📄 `core/tools/voice_tool.py`
- 🟠 **Line 111:** Broad except clause. Catch specific exceptions instead.
- 🟠 **Line 189:** Broad except clause. Catch specific exceptions instead.

#### 📄 `core/tools/healing_tool.py`
- 🟠 **Line 52:** Broad except clause. Catch specific exceptions instead.
- 🟠 **Line 98:** Broad except clause. Catch specific exceptions instead.

#### 📄 `core/tools/tasks_tool.py`
- 🟠 **Line 73:** Broad except clause. Catch specific exceptions instead.
- 🟠 **Line 135:** Broad except clause. Catch specific exceptions instead.
- 🟠 **Line 178:** Broad except clause. Catch specific exceptions instead.
- 🟠 **Line 205:** Broad except clause. Catch specific exceptions instead.
- 🟠 **Line 216:** Function 'get_tools' is too long (108 lines). Consider refactoring.

#### 📄 `core/tools/vector_store.py`
- 🟠 **Line 48:** Broad except clause. Catch specific exceptions instead.
- 🟠 **Line 64:** Broad except clause. Catch specific exceptions instead.
- 🟠 **Line 81:** Broad except clause. Catch specific exceptions instead.

#### 📄 `core/tools/vision_tool.py`
- 🟠 **Line 53:** Broad except clause. Catch specific exceptions instead.

#### 📄 `core/tools/camera_tool.py`
- 🟠 **Line 45:** Broad except clause. Catch specific exceptions instead.

#### 📄 `core/tools/router.py`
- 🟠 **Line 232:** Broad except clause. Catch specific exceptions instead.
- 🟠 **Line 310:** Broad except clause. Catch specific exceptions instead.

#### 📄 `core/tools/code_indexer.py`
- 🟠 **Line 118:** Broad except clause. Catch specific exceptions instead.

#### 📄 `core/services/watchdog.py`
- 🟠 **Line 115:** Broad except clause. Catch specific exceptions instead.
- 🟠 **Line 175:** Broad except clause. Catch specific exceptions instead.
- 🟠 **Line 194:** Broad except clause. Catch specific exceptions instead.
- 🟠 **Line 219:** Broad except clause. Catch specific exceptions instead.
- 🟠 **Line 297:** Broad except clause. Catch specific exceptions instead.

#### 📄 `core/services/registry.py`
- 🟠 **Line 90:** Broad except clause. Catch specific exceptions instead.
- 🔴 **Line 159:** Empty except block (silenced error). Consider logging the exception.
- 🔴 **Line 200:** Empty except block (silenced error). Consider logging the exception.
- 🟠 **Line 226:** Broad except clause. Catch specific exceptions instead.

#### 📄 `tools/dashboard_generator.py`
- 🟠 **Line 5:** Function 'generate_dashboard' is too long (158 lines). Consider refactoring.
- 🔵 **Line 12:** Use of print() found. Consider using the structured logging module.
- 🔵 **Line 163:** Use of print() found. Consider using the structured logging module.

#### 📄 `tools/benchmark_runner.py`
- 🟠 **Line 7:** Function 'run_benchmarks' is too long (76 lines). Consider refactoring.
- 🟠 **Line 7:** Function 'run_benchmarks' has high complexity (11). Consider breaking it down.
- 🔵 **Line 12:** Use of print() found. Consider using the structured logging module.
- 🔵 **Line 28:** Use of print() found. Consider using the structured logging module.
- 🔵 **Line 33:** Use of print() found. Consider using the structured logging module.
- 🔵 **Line 35:** Use of print() found. Consider using the structured logging module.
- 🔵 **Line 36:** Use of print() found. Consider using the structured logging module.
- 🟠 **Line 37:** Broad except clause. Catch specific exceptions instead.
- 🔵 **Line 38:** Use of print() found. Consider using the structured logging module.
- 🔵 **Line 66:** Use of print() found. Consider using the structured logging module.
- 🔵 **Line 67:** Use of print() found. Consider using the structured logging module.
- 🔵 **Line 68:** Use of print() found. Consider using the structured logging module.
- 🔵 **Line 72:** Use of print() found. Consider using the structured logging module.
- 🔵 **Line 74:** Use of print() found. Consider using the structured logging module.
- 🔵 **Line 76:** Use of print() found. Consider using the structured logging module.
- 🔵 **Line 78:** Use of print() found. Consider using the structured logging module.
- 🔵 **Line 80:** Use of print() found. Consider using the structured logging module.
- 🔵 **Line 82:** Use of print() found. Consider using the structured logging module.
- 🔵 **Line 83:** Use of print() found. Consider using the structured logging module.

#### 📄 `tools/test_ast.py`
- 🔵 **Line 8:** Use of print() found. Consider using the structured logging module.
- 🔵 **Line 9:** Use of print() found. Consider using the structured logging module.
- 🔵 **Line 10:** Use of print() found. Consider using the structured logging module.
- 🔵 **Line 12:** Use of print() found. Consider using the structured logging module.
- 🔵 **Line 13:** Use of print() found. Consider using the structured logging module.
- 🔵 **Line 14:** Use of print() found. Consider using the structured logging module.

#### 📄 `tools/dependency_analyzer.py`
- 🟠 **Line 43:** Function 'build_dependency_graph' has high complexity (11). Consider breaking it down.
- 🟠 **Line 98:** Broad except clause. Catch specific exceptions instead.
- 🔵 **Line 138:** Use of print() found. Consider using the structured logging module.
- 🔵 **Line 141:** Use of print() found. Consider using the structured logging module.
- 🔵 **Line 170:** Use of print() found. Consider using the structured logging module.
- 🔵 **Line 174:** Use of print() found. Consider using the structured logging module.

#### 📄 `tools/ast_extractor.py`
- 🟠 **Line 53:** Function 'extract' is too long (68 lines). Consider refactoring.
- 🟠 **Line 53:** Function 'extract' has high complexity (16). Consider breaking it down.
- 🟠 **Line 204:** Broad except clause. Catch specific exceptions instead.
- 🟠 **Line 215:** Broad except clause. Catch specific exceptions instead.
- 🟠 **Line 226:** Broad except clause. Catch specific exceptions instead.
