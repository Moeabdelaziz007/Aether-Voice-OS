#!/usr/bin/env python3
"""
Aether Voice OS — Quick Test Script
==================================

Simple test to verify the Gemini Live API benchmark framework works correctly.
This script demonstrates the core functionality without requiring real audio hardware.
"""

import asyncio
import sys
from pathlib import Path

# Add project root to path
ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT))

from tests.gemini_live_interactive_benchmark import (
    TestScenario, 
    ScenarioStats,
    InteractiveDashboard
)
from tests.dynamic_config_controller import DynamicParameterController
from core.infra.config import AudioConfig

async def test_dashboard():
    """Test the interactive dashboard functionality."""
    print("Testing Interactive Dashboard...")
    
    # Create test scenario stats
    stats = ScenarioStats("test_scenario")
    stats.latency_p50 = 150.0
    stats.latency_p95 = 280.0
    stats.latency_p99 = 350.0
    stats.aec_convergence_rate = 85.5
    stats.vad_accuracy = 92.3
    stats.frame_drop_rate = 0.5
    stats.double_talk_frames = 12
    stats.frames_processed = 1000
    
    # Create dashboard
    dashboard = InteractiveDashboard(stats)
    
    # Render once to test
    dashboard.render()
    
    print("✓ Dashboard test completed")
    return True

def test_parameter_controller():
    """Test the dynamic parameter controller."""
    print("Testing Parameter Controller...")
    
    # Create audio config
    config = AudioConfig()
    
    # Create controller
    controller = DynamicParameterController(config)
    
    # Test getting parameters
    aec_step = controller.get_parameter('aec_step_size')
    print(f"  AEC step size: {aec_step}")
    
    # Test setting parameters
    controller.set_parameter('aec_step_size', 0.7)
    new_aec_step = controller.get_parameter('aec_step_size')
    print(f"  New AEC step size: {new_aec_step}")
    
    # Test presets
    controller.apply_preset('low_latency')
    low_latency_step = controller.get_parameter('aec_step_size')
    print(f"  Low latency AEC step: {low_latency_step}")
    
    print("✓ Parameter controller test completed")
    return True

def test_scenarios():
    """Test scenario definitions."""
    print("Testing Test Scenarios...")
    
    from tests.gemini_live_interactive_benchmark import GeminiLiveInteractiveBenchmark
    
    # Create benchmark instance
    benchmark = GeminiLiveInteractiveBenchmark()
    scenarios = benchmark._get_scenarios()
    
    print(f"  Available scenarios: {[s.name for s in scenarios]}")
    
    # Find normal scenario
    normal_scenario = next((s for s in scenarios if s.name == "normal"), None)
    if normal_scenario:
        print(f"  Normal scenario duration: {normal_scenario.duration_seconds}s")
        print(f"  Normal scenario description: {normal_scenario.description}")
    
    print("✓ Scenario test completed")
    return True

async def main():
    """Run all tests."""
    print("=" * 60)
    print("AETHER VOICE OS - BENCHMARK FRAMEWORK TEST")
    print("=" * 60)
    print()
    
    try:
        # Test dashboard
        await test_dashboard()
        print()
        
        # Test parameter controller
        test_parameter_controller()
        print()
        
        # Test scenarios
        test_scenarios()
        print()
        
        print("=" * 60)
        print("🎉 ALL TESTS PASSED!")
        print("=" * 60)
        print()
        print("The Gemini Live API interactive benchmark framework is ready for use.")
        print()
        print("To run the full benchmark:")
        print("  python tests/gemini_live_interactive_benchmark.py --scenario normal")
        print()
        print("To run with parameter controller:")
        print("  python tests/dynamic_config_controller.py")
        print()
        
        return 0
        
    except Exception as e:
        print(f"❌ Test failed: {e}")
        import traceback
        traceback.print_exc()
        return 1

if __name__ == "__main__":
    exit_code = asyncio.run(main())
    sys.exit(exit_code)