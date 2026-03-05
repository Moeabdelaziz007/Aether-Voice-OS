import pytest
import asyncio
import time
import json
from pathlib import Path
from core.ai.scheduler import CognitiveScheduler

@pytest.mark.asyncio
async def test_cortex_tool_prediction_lead_time():
    """
    Expert Benchmark: Measuring the "Neural Lead Time" of tool pre-warming.
    Ensures speculative initialization happens before the sentence is finished.
    """
    cortex = CognitiveScheduler()
    
    # 1. Test case: Searching for logs
    fragment = "I need to check the server logs for any errors"
    
    start_time = time.perf_counter()
    
    # Process fragment (synchronous in current impl)
    cortex.speculate(fragment)
    
    # Check if log_scanner was pre-warmed
    pre_warmed = cortex.is_tool_pre_warmed("system_tool.read_logs")
    
    lead_time = time.perf_counter() - start_time
    
    # 2. Test case: Code analysis
    fragment_code = "can you explain this python code"
    cortex.speculate(fragment_code)
    pre_warmed_code = cortex.is_tool_pre_warmed("code_indexer.search")
    
    metrics = {
        "benchmark": "cortex_prediction",
        "scenarios": [
            {
                "input": fragment,
                "target_tool": "log_scanner",
                "pre_warmed": pre_warmed,
                "lead_time_ms": round(lead_time * 1000, 2)
            },
            {
                "input": fragment_code,
                "target_tool": "search_codebase",
                "pre_warmed": pre_warmed_code
            }
        ],
        "status": "success" if pre_warmed and pre_warmed_code else "partial_fail"
    }
    
    # Save report
    report_path = Path("tests/reports/cortex_report.json")
    with open(report_path, "w") as f:
        json.dump(metrics, f, indent=4)
        
    print(f"\n🧠 Cortex Prediction: Lead Time {lead_time*1000:.2f}ms")
    
    assert pre_warmed
    assert pre_warmed_code
    assert lead_time < 0.5 # Analysis should be fast
