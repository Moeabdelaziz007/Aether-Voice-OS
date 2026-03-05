import asyncio
import pytest
import json
import random
from pathlib import Path
from core.ai.genetic import GeneticOptimizer, AgentDNA

class MockFirebase:
    def __init__(self):
        self.is_connected = True
        self._session_id = "chaos_session"
    async def log_event(self, name, data): pass
    async def get_session_affective_summary(self, sid):
        return {"status": "success", "summary": {"avg_engagement": 0.5}}

@pytest.mark.asyncio
async def test_dna_stability_chaos():
    """
    Systems Lab: DNA Chaos Testing.
    Scenario: Alternating sequence of high and low arousal spikes to 
    verify EMA smoothing prevents personality whiplash.
    """
    mock_fb = MockFirebase()
    optimizer = GeneticOptimizer(firebase=mock_fb, api_key="dummy", ema_alpha=0.15) # Using the V3.1 alpha
    
    current_dna = AgentDNA(verbosity=0.5, empathy=0.5)
    initial_dna = AgentDNA(verbosity=0.5, empathy=0.5)
    
    # Chaos sequence: [High, Low, High, High, Low, Medium]
    arousal_sequence = [0.9, 0.1, 0.9, 0.9, 0.2, 0.5]
    history = []
    
    for val in arousal_sequence:
        current_dna = await optimizer.mutate_mid_session(current_dna, "arousal", val)
        history.append({
            "arousal_input": val,
            "verbosity": round(current_dna.verbosity, 4),
            "empathy": round(current_dna.empathy, 4)
        })
    
    # Measure max drift in one step
    max_step_drift = 0.0
    for i in range(1, len(history)):
        drift = abs(history[i]["verbosity"] - history[i-1]["verbosity"])
        if drift > max_step_drift:
            max_step_drift = drift
            
    metrics = {
        "benchmark": "dna_chaos_stability",
        "initial_state": initial_dna.to_dict(),
        "final_state": current_dna.to_dict(),
        "max_step_drift": round(max_step_drift, 4),
        "history": history,
        "status": "success" if max_step_drift < 0.1 else "failed"
    }
    
    # Save report
    report_path = Path("tests/reports/dna_report.json")
    with open(report_path, "w") as f:
        json.dump(metrics, f, indent=4)
        
    print(f"\n🧬 DNA Chaos Stability: Max Step Drift: {max_step_drift:.4f}")
    # With alpha=0.15, max move from 0.5 towards 0.3 target is 0.2 * 0.15 = 0.03
    assert max_step_drift < 0.1 
