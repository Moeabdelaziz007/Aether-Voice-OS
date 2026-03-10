import json
import subprocess
import time
from pathlib import Path


def run_benchmarks():
    """
    Expert Benchmark Runner: Orchestrates the AetherOS Systems Lab.
    Generates a consolidated performance report.
    """
    print("🚀 Starting AetherOS Systems Lab Benchmarks...")

    tests = [
        "tests/benchmarks/test_interrupts.py",
        "tests/benchmarks/test_event_bus_stress.py",
        "tests/benchmarks/test_dna_stability.py",
        "tests/benchmarks/test_cortex_prediction.py",
        "tests/benchmarks/test_long_session.py",
    ]

    reports_dir = Path("tests/reports")
    reports_dir.mkdir(parents=True, exist_ok=True)

    start_time = time.time()

    for test in tests:
        print(f"📡 Running {Path(test).name}...")
        try:
            # Use pytest to run the specific file
            result = subprocess.run(["pytest", "-v", test], capture_output=True, text=True)
            if result.returncode == 0:
                print(f"✅ {Path(test).name} Passed.")
            else:
                print(f"❌ {Path(test).name} Failed.")
                print(result.stdout)
        except Exception as e:
            print(f"💥 Error running {test}: {e}")

    # Consolidate Reports
    final_report = {
        "timestamp": time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime()),
        "total_runtime_s": round(time.time() - start_time, 2),
        "metrics": {},
    }

    report_files = {
        "latency": "latency_report.json",
        "stress": "stress_report.json",
        "dna": "dna_report.json",
        "cortex": "cortex_report.json",
        "stability": "stability_report.json",
    }

    for key, filename in report_files.items():
        p = reports_dir / filename
        if p.exists():
            with open(p, "r") as f:
                final_report["metrics"][key] = json.load(f)
        else:
            final_report["metrics"][key] = "NOT_FOUND"

    with open(reports_dir / "benchmark_report.json", "w") as f:
        json.dump(final_report, f, indent=4)

    print("\n" + "=" * 40)
    print("📊 AetherOS PERFORMANCE SUMMARY")
    print("=" * 40)

    m = final_report["metrics"]
    if m.get("latency") != "NOT_FOUND":
        print(f"Interrupt Latency (T3-T1) : {m['latency']['t3_t1_total_ms']} ms")
    if m.get("stress") != "NOT_FOUND":
        print(f"EventBus Audio Latency     : {m['stress']['audio_latency_ms']} ms")
    if m.get("dna") != "NOT_FOUND":
        print(f"DNA Max Step Drift         : {m['dna']['max_step_drift']}")
    if m.get("cortex") != "NOT_FOUND":
        print(f"Neural Lead Time Trigger   : {m['cortex']['pre_warm_elapsed_ms']} ms")
    if m.get("stability") != "NOT_FOUND":
        print(f"Memory Growth              : {m['stability']['memory_growth_mb']} MB")

    print("=" * 40)
    print(f"Full report saved to: {reports_dir}/benchmark_report.json")


if __name__ == "__main__":
    run_benchmarks()
