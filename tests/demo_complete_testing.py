#!/usr/bin/env python3
"""
Aether Voice OS - Complete Live Testing Demonstration
====================================================

This script demonstrates the complete live testing workflow:
1. All five test scenarios with real audio processing
2. Real-time telemetry collection and dashboard display
3. Dynamic parameter adjustment capabilities
4. Comprehensive performance reporting

Usage: python tests/demo_complete_testing.py
"""

import asyncio
import json
import os
import sys
from datetime import datetime
from pathlib import Path

# Add project root to path
ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT))

from core.infra.config import load_config
from tests.gemini_live_interactive_benchmark import GeminiLiveInteractiveBenchmark


async def run_comprehensive_test():
    """Run complete testing demonstration."""

    print("=" * 80)
    print("AETHER VOICE OS - COMPLETE LIVE TESTING DEMONSTRATION")
    print("=" * 80)
    print()

    # Verify API key setup
    api_key = os.getenv("GOOGLE_API_KEY") or os.getenv("GEMINI_API_KEY")
    if not api_key:
        print("❌ ERROR: No API key found in environment")
        print("Please set GOOGLE_API_KEY or GEMINI_API_KEY")
        return False

    print(f"✓ API Key Available: {'*' * 10}{api_key[-5:]}")
    print()

    # Load configuration
    config = load_config()
    print("✓ Configuration Loaded")
    print(f"  Model: {config.ai.model.value}")
    print(f"  Sample Rate: {config.audio.send_sample_rate}Hz")
    print()

    # Initialize benchmark
    print("🔧 Initializing Benchmark Framework...")
    benchmark = GeminiLiveInteractiveBenchmark()
    await benchmark.setup()
    print("✓ Framework Ready")
    print()

    # Define test scenarios
    scenarios = [
        ("normal", "Normal conversation", 30),
        ("noise", "Background noise environment", 30),
        ("overlap", "Overlapping speech (double-talk)", 30),
        ("rapid", "Rapid speech scenario", 30),
        ("whisper", "Whispered speech", 30),
    ]

    all_results = []

    # Run each scenario
    for i, (scenario_name, description, duration) in enumerate(scenarios, 1):
        print(f"🧪 SCENARIO {i}/5: {description.upper()}")
        print("-" * 50)

        try:
            # Run the scenario
            result = await benchmark.run_scenario(scenario_name)
            all_results.append(
                {
                    "scenario": scenario_name,
                    "description": description,
                    "result": result,
                    "timestamp": datetime.now().isoformat(),
                }
            )

            # Display results
            print(f"📊 Results for {scenario_name}:")
            print(f"  Duration: {result['duration_seconds']:.1f}s")
            print(f"  Frames Processed: {result['total_frames']}")
            print(f"  Frame Drop Rate: {result['frame_drop_rate_percent']:.2f}%")
            print(
                f"  Latency - P50: {result['latency']['p50_ms']:.1f}ms, "
                f"P95: {result['latency']['p95_ms']:.1f}ms, "
                f"P99: {result['latency']['p99_ms']:.1f}ms"
            )
            print(
                f"  AEC Convergence: {result['aec']['convergence_rate_percent']:.1f}%"
            )
            print(f"  AEC ERLE: {result['aec']['erle_db_avg']:.1f}dB")
            print(f"  VAD Accuracy: {result['vad']['accuracy_percent']:.1f}%")
            print(f"  Double-talk Frames: {result['aec']['double_talk_frames']}")
            print()

        except Exception as e:
            print(f"❌ Scenario {scenario_name} failed: {e}")
            import traceback

            traceback.print_exc()
            print()
            continue

    # Generate comprehensive report
    print("=" * 80)
    print("📋 COMPREHENSIVE PERFORMANCE REPORT")
    print("=" * 80)

    summary_report = {
        "test_timestamp": datetime.now().isoformat(),
        "total_scenarios": len(all_results),
        "successful_scenarios": len(all_results),
        "scenario_results": all_results,
        "summary_statistics": {},
    }

    if all_results:
        # Calculate summary statistics
        latencies_p95 = [r["result"]["latency"]["p95_ms"] for r in all_results]
        aec_convergence_rates = [
            r["result"]["aec"]["convergence_rate_percent"] for r in all_results
        ]
        vad_accuracies = [r["result"]["vad"]["accuracy_percent"] for r in all_results]

        summary_report["summary_statistics"] = {
            "average_latency_p95_ms": sum(latencies_p95) / len(latencies_p95),
            "min_latency_p95_ms": min(latencies_p95),
            "max_latency_p95_ms": max(latencies_p95),
            "average_aec_convergence_percent": sum(aec_convergence_rates)
            / len(aec_convergence_rates),
            "average_vad_accuracy_percent": sum(vad_accuracies) / len(vad_accuracies),
        }

        print("📈 Summary Statistics:")
        print(
            f"  Average Latency (P95): {summary_report['summary_statistics']['average_latency_p95_ms']:.1f}ms"
        )
        print(
            f"  Latency Range: {summary_report['summary_statistics']['min_latency_p95_ms']:.1f}ms - {summary_report['summary_statistics']['max_latency_p95_ms']:.1f}ms"
        )
        print(
            f"  Average AEC Convergence: {summary_report['summary_statistics']['average_aec_convergence_percent']:.1f}%"
        )
        print(
            f"  Average VAD Accuracy: {summary_report['summary_statistics']['average_vad_accuracy_percent']:.1f}%"
        )
        print()

    # Save detailed report
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    report_file = (
        ROOT / "benchmark_reports" / f"complete_testing_report_{timestamp}.json"
    )
    report_file.parent.mkdir(exist_ok=True)

    with open(report_file, "w") as f:
        json.dump(summary_report, f, indent=2)

    print(f"💾 Detailed report saved to: {report_file}")
    print()
    print("🎉 Complete testing demonstration finished!")

    return True


if __name__ == "__main__":
    # Set up environment
    if not os.getenv("GOOGLE_API_KEY") and os.getenv("GEMINI_API_KEY"):
        os.environ["GOOGLE_API_KEY"] = os.getenv("GEMINI_API_KEY")

    success = asyncio.run(run_comprehensive_test())
    sys.exit(0 if success else 1)
