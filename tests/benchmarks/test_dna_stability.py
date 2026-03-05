import pytest
import asyncio
import json
from pathlib import Path
from core.ai.genetic import GeneticOptimizer, AgentDNA

class MockFirebase:
    def __init__(self):
        self.is_connected = True
        self._session_id = "test_session"
    async def log_event(self, name, data): pass
    async def get_session_affective_summary(self, sid):
        return {"status": "success", "summary": {"avg_engagement": 0.5}}

@pytest.mark.asyncio
async def test_dna_stability_ema():
    """
    Expert Benchmark: Verifying Exponential Moving Average (EMA) smoothing of 
    DNA traits under high-arousal spikes.
    """
    mock_fb = MockFirebase()
    optimizer = GeneticOptimizer(firebase=mock_fb, api_key="dummy", ema_alpha=0.3)
    
    initial_dna = AgentDNA(verbosity=0.5, empathy=0.5)
    
    # Simulate a sudden stress spike (High Arousal)
    # Target in GeneticOptimizer for arousal > 0.7: verbosity -= 0.2, empathy += 0.2
    
    # 1. First spike
    dna_v1 = await optimizer.mutate_mid_session(initial_dna, "arousal", 0.9)
    # Expected: verbosity = 0.5 * 0.7 + 0.3 * (0.5 - 0.2) = 0.35 + 0.09 = 0.44
    # Expected: empathy = 0.5 * 0.7 + 0.3 * (0.5 + 0.2) = 0.35 + 0.21 = 0.56
    
    # 2. Continuous stress spikes
    current_dna = dna_v1
    history = []
    for _ in range(5):
        current_dna = await optimizer.mutate_mid_session(current_dna, "arousal", 0.9)
        history.append(current_dna.to_dict())
    
    final_dna = current_dna
    
    metrics = {
        "benchmark": "dna_stability",
        "initial_verbosity": initial_dna.verbosity,
        "final_verbosity": round(final_dna.verbosity, 4),
        "initial_empathy": initial_dna.empathy,
        "final_empathy": round(final_dna.empathy, 4),
        "smoothing_history": history,
        "status": "success" if final_dna.verbosity < initial_dna.verbosity else "failed"
    }
    
    # Save report
    report_path = Path("tests/reports/dna_report.json")
    with open(report_path, "w") as f:
        json.dump(metrics, f, indent=4)
        
    print(f"\n🧪 DNA Stability: Initial Verbosity {initial_dna.verbosity} -> Final {final_dna.verbosity:.4f}")
    
    # Verify smoothing (should not jump straight to 0.3 or lower in 1 step)
    assert 0.4 < dna_v1.verbosity < 0.5
    assert final_dna.verbosity < 0.35 # After 5 steps it should be converged near the target
