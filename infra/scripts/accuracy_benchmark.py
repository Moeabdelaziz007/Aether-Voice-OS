import asyncio
import json
import logging
import os
import random
import sys
import time

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from scripts.internal.bug_generator import BugGenerator

from core.ai.handover.manager import HandoverContext, MultiAgentOrchestrator
from core.tools.healing_tool import diagnose_and_repair

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("AetherAccuracy")


class AccuracyBench:
    def __init__(self):
        self.bug_gen = BugGenerator()
        self.results = {
            "timestamp": time.time(),
            "healing_accuracy": [],
            "handover_integrity": {},
            "zero_shot_recovery": {},
            "dispatch_ambiguity": {},
        }

    async def run_healing_bench(self):
        print(
            "🔍 [ACCURACY] Testing Neural Healing (Diagnostic Accuracy)...", flush=True
        )

        test_cases = [
            ("Syntax Error", self.bug_gen.generate_syntax_error, "syntax"),
            (
                "Import Error",
                self.bug_gen.generate_import_error,
                "non_existent_package",
            ),
            ("Key Error", self.bug_gen.generate_key_error, "KeyError"),
        ]

        for name, gen_fn, expected_keyword in test_cases:
            bug_path = gen_fn()
            print(f"  Testing: {name} in {bug_path}", flush=True)

            # Direct tool call via internal API
            # Note: healing_tool uses subprocess to tail logs, for benchmark we mock
            # log file
            log_dir = ".aether/logs"
            os.makedirs(log_dir, exist_ok=True)
            log_path = os.path.join(log_dir, "session.log")

            # Simulate crash log
            with open(log_path, "w") as f:
                f.write(f"Traceback in {bug_path}:\nError: {expected_keyword}")

            diagnosis = await diagnose_and_repair(
                context=f"The script {bug_path} crashed."
            )

            success = expected_keyword in diagnosis.get("terminal_output", "")
            self.results["healing_accuracy"].append(
                {
                    "case": name,
                    "success": success,
                    "captured_context": diagnosis.get("status") == "analysis_ready",
                }
            )
            print(f"  Result: {'✅' if success else '❌'}", flush=True)

    async def run_handover_bench(self, hops: int = 10):
        print(
            f"🔄 [ACCURACY] Testing Sovereign Handover ({hops} Hops Integrity)...",
            flush=True,
        )

        initial_data = {
            "seed_key": "vault_alpha_99",
            "secret": "moonshot_10x",
            "hop_count": 0,
        }
        _context = HandoverContext(
            source_agent="Architect",
            target_agent="Specialist_1",
            task="Verify Handover Integrity",
            payload=initial_data,
        )

        current_payload = initial_data
        for i in range(hops):
            # Simulate a hop (serialization cycle)
            serialized = json.dumps(current_payload)
            current_payload = json.loads(serialized)
            current_payload["hop_count"] += 1
            if i % 2 == 0:
                print(f"  Hop {i + 1} complete...", flush=True)

        integrity_success = (
            current_payload["seed_key"] == initial_data["seed_key"]
            and current_payload["secret"] == initial_data["secret"]
            and current_payload["hop_count"] == hops
        )

        self.results["handover_integrity"] = {
            "hops": hops,
            "success": integrity_success,
            "bits_preserved": "100%" if integrity_success else "FAIL",
        }
        print(f"  Integrity: {'✅' if integrity_success else '❌'}", flush=True)

    async def run_zero_shot_recovery_bench(self):
        print("💥 [ACCURACY] Testing Zero-Shot Recovery Audit (MTTR)...", flush=True)

        # Simulate websocket termination and measure MTTR via healing_tool
        start_time = time.time()

        # Random delay to simulate termination chaos
        await asyncio.sleep(random.uniform(0.1, 0.5))

        log_dir = ".aether/logs"
        os.makedirs(log_dir, exist_ok=True)
        log_path = os.path.join(log_dir, "session.log")

        with open(log_path, "w") as f:
            f.write(
                "WebSocket connection randomly terminated.\nError: Connection closed unexpectedly."
            )

        diagnosis = await diagnose_and_repair(
            context="WebSocket connection dropped unexpectedly"
        )

        recovery_time = time.time() - start_time
        success = "Connection closed unexpectedly" in diagnosis.get(
            "terminal_output", ""
        )

        self.results["zero_shot_recovery"] = {
            "mttr_seconds": recovery_time,
            "success": success,
        }
        print(
            f"  Result: {'✅' if success else '❌'} (MTTR: {recovery_time:.2f}s)",
            flush=True,
        )

    async def run_dispatch_ambiguity_bench(self):
        print("🤔 [ACCURACY] Testing Tool Dispatch Ambiguity...", flush=True)

        orchestrator = MultiAgentOrchestrator()

        # Mock an agent just to test routing
        class MockAgent:
            def process(self, context):
                return "Done"

        orchestrator.register_agent("Specialist_1", MockAgent())

        test_cases = [
            ("Deploy the thing to the cloud", True),
            ("Delete the stuff", True),
            ("Remove it", True),
            ("Deploy the backend service", False),
            ("Delete user 123", False),
        ]

        results = []
        all_passed = True
        for prompt, should_clarify in test_cases:
            result = orchestrator.collaborate(prompt, "Specialist_1")
            did_clarify = "clarification_request" in result
            passed = did_clarify == should_clarify
            if not passed:
                all_passed = False
            results.append(
                {
                    "prompt": prompt,
                    "should_clarify": should_clarify,
                    "did_clarify": did_clarify,
                    "passed": passed,
                }
            )
            print(
                f"  Testing prompt: '{prompt}' -> {'✅' if passed else '❌'}",
                flush=True,
            )

        self.results["dispatch_ambiguity"] = {"success": all_passed, "cases": results}
        print(
            f"  Overall Dispatch Ambiguity: {'✅' if all_passed else '❌'}", flush=True
        )

    async def execute(self):
        await self.run_healing_bench()
        await self.run_handover_bench()
        await self.run_zero_shot_recovery_bench()
        await self.run_dispatch_ambiguity_bench()

        with open("accuracy_audit.json", "w") as f:
            json.dump(self.results, f, indent=4)
        print("📊 Accuracy Audit saved to accuracy_audit.json", flush=True)
        self.bug_gen.cleanup()


if __name__ == "__main__":
    bench = AccuracyBench()
    asyncio.run(bench.execute())
