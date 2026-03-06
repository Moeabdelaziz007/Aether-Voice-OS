import sys
from unittest.mock import MagicMock

# Mock required modules
sys.modules["google"] = MagicMock()
sys.modules["google.genai"] = MagicMock()
sys.modules["pydantic"] = MagicMock()
sys.modules["pydantic_settings"] = MagicMock()
sys.modules["google.cloud"] = MagicMock()
sys.modules["google.cloud.firestore"] = MagicMock()

import pytest

sys.exit(pytest.main(["-v", "tests/unit/test_hive_swarm.py"]))
