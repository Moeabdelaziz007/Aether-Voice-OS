#!/usr/bin/env python3
"""Quick verification that the benchmark framework loads correctly."""

import sys
from pathlib import Path

# Add project root to path
ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT))

print("Verifying benchmark framework...")

try:
    # Test importing the main components
    from tests.gemini_live_interactive_benchmark import (
        GeminiLiveInteractiveBenchmark,
        TestScenario,
        ScenarioStats,
        InteractiveDashboard
    )
    print("✓ Main benchmark components imported successfully")
    
    from tests.dynamic_config_controller import (
        DynamicParameterController,
        ParameterPreset
    )
    print("✓ Parameter controller imported successfully")
    
    from core.infra.config import AudioConfig
    print("✓ Core config imported successfully")
    
    # Test creating instances
    config = AudioConfig()
    print("✓ AudioConfig created successfully")
    
    controller = DynamicParameterController(config)
    print("✓ DynamicParameterController created successfully")
    
    stats = ScenarioStats("test")
    print("✓ ScenarioStats created successfully")
    
    print("\n🎉 All components loaded successfully!")
    print("\nReady to run:")
    print("  python tests/gemini_live_interactive_benchmark.py --help")
    
except Exception as e:
    print(f"❌ Error: {e}")
    import traceback
    traceback.print_exc()
    sys.exit(1)