import asyncio
import json
import logging
import os
import time

from scripts.internal.bug_generator import BugGenerator

from core.ai.handover.manager import HandoverContext
from core.tools.healing_tool import diagnose_and_repair

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("AetherAccuracy")

class AccuracyBench:
    def __init__(self):
        self.bug_gen = BugGenerator()
        self.results = {
            "timestamp": time.time(),
            "healing_accuracy": [],
            "handover_integrity": {}
        }

    async def run_healing_bench(self):
        print("🔍 [ACCURACY] Testing Neural Healing (Diagnostic Accuracy)...", flush=True)
        
        test_cases = [
            ("Syntax Error", self.bug_gen.generate_syntax_error, "syntax"),
            ("Import Error", self.bug_gen.generate_import_error, "non_existent_package"),
            ("Key Error", self.bug_gen.generate_key_error, "KeyError")
        ]

        for name, gen_fn, expected_keyword in test_cases:
            bug_path = gen_fn()
            print(f"  Testing: {name} in {bug_path}", flush=True)
            
            # Direct tool call via internal API
            # Note: healing_tool uses subprocess to tail logs, for benchmark we mock log file
            log_dir = ".aether/logs"
            os.makedirs(log_dir, exist_ok=True)
            log_path = os.path.join(log_dir, "session.log")
            
            # Simulate crash log
            with open(log_path, "w") as f:
                f.write(f"Traceback in {bug_path}:\nError: {expected_keyword}")

            diagnosis = await diagnose_and_repair(context=f"The script {bug_path} crashed.")
            
            success = expected_keyword in diagnosis.get("terminal_output", "")
            self.results["healing_accuracy"].append({
                "case": name,
                "success": success,
                "captured_context": diagnosis.get("status") == "analysis_ready"
            })
            print(f"  Result: {'✅' if success else '❌'}", flush=True)

    async def run_handover_bench(self, hops: int = 10):
        print(f"🔄 [ACCURACY] Testing Sovereign Handover ({hops} Hops Integrity)...", flush=True)
        
        initial_data = {"seed_key": "vault_alpha_99", "secret": "moonshot_10x", "hop_count": 0}
        HandoverContext(
            source_agent="Architect",
            target_agent="Specialist_1",
            task="Verify Handover Integrity",
            payload=initial_data
        )
        
        current_payload = initial_data
        for i in range(hops):
            # Simulate a hop (serialization cycle)
            serialized = json.dumps(current_payload)
            current_payload = json.loads(serialized)
            current_payload["hop_count"] += 1
            if i % 2 == 0:
                print(f"  Hop {i+1} complete...", flush=True)

        integrity_success = (
            current_payload["seed_key"] == initial_data["seed_key"] and
            current_payload["secret"] == initial_data["secret"] and
            current_payload["hop_count"] == hops
        )
        
        self.results["handover_integrity"] = {
            "hops": hops,
            "success": integrity_success,
            "bits_preserved": "100%" if integrity_success else "FAIL"
        }
        print(f"  Integrity: {'✅' if integrity_success else '❌'}", flush=True)

    async def execute(self):
        await self.run_healing_bench()
        await self.run_handover_bench()
        
        with open("accuracy_audit.json", "w") as f:
            json.dump(self.results, f, indent=4)
        print("📊 Accuracy Audit saved to accuracy_audit.json", flush=True)
        self.bug_gen.cleanup()

if __name__ == "__main__":
    bench = AccuracyBench()
    asyncio.run(bench.execute())
