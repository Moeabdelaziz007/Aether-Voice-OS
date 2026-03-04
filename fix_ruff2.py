with open('tests/unit/test_telemetry.py', 'r') as f:
    content = f.read()

content = content.replace(
    "Mock(converged=False, convergence_progress=0.0, erle_db=0.0, estimated_delay_ms=0, double_talk_detected=False)",
    "Mock(\n                converged=False,\n                convergence_progress=0.0,\n                erle_db=0.0,\n                estimated_delay_ms=0,\n                double_talk_detected=False\n            )"
)

with open('tests/unit/test_telemetry.py', 'w') as f:
    f.write(content)
