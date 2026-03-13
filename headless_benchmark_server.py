import asyncio
import os
import sys
from pathlib import Path

# Setup path
ROOT = Path(__file__).resolve().parent
sys.path.insert(0, str(ROOT))

import logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

from core.infra.config import load_config
from core.infra.transport.gateway import AetherGateway
from core.logic.managers.agents import AgentManager
from core.infra.event_bus import EventBus
from core.tools.router import ToolRouter

async def run_stress_test_server():
    os.environ["AETHER_BENCHMARK_MODE"] = "true"
    config = load_config()
    config.gateway.port = 18889
    config.packages_dir = str(ROOT / "packages")
    bus = EventBus()
    router = ToolRouter()
    
    from core.ai.scheduler import CognitiveScheduler
    
    # Minimal setup for gateway
    agents = AgentManager(config=config, router=router, on_handover=lambda *a: None, event_bus=bus)
    agents._hive._default_soul_name = "Atlas"
    await agents._hive.initialize()
    
    scheduler = CognitiveScheduler(event_bus=bus, router=router)
    await scheduler.initialize()
    
    # Inject scheduler into hive
    agents._hive._scheduler = scheduler
    
    gateway = AetherGateway(
        config=config.gateway,
        ai_config=config.ai,
        hive=agents._hive,
        bus=bus,
        tool_router=router,
    )
    
    print("🚀 Starting Headless Gateway for Benchmarking...")
    await gateway.start()
    
    # Run for a while or until benchmark finishes
    await asyncio.sleep(300)
    await gateway.stop()

if __name__ == "__main__":
    asyncio.run(run_stress_test_server())
