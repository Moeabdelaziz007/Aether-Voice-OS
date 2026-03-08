import asyncio
import logging
import os
import sys

# Add project root to path
sys.path.append(os.getcwd())

from core.ai.adk_agents import forge_agent
from core.tools.forge_tool import list_forged_agents

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("ForgeDemo")

async def run_demo():
    print("🌌 [GEMIGRAM] Initiating Aether Forge Demo...")
    print("User: 'Aether, forge a new DevOps specialist named Atlas with Docker skills.'")
    
    # 1. Simulate Forge Agent reasoning
    # Normally, this would go through the Gemini Live API.
    # Here we mock the result of the forge_agent tool call.
    
    from core.tools.forge_tool import create_agent
    from core.tools.clawhub_tool import search_skills, install_skill
    
    print("\n🛠️ ForgeAgent: Analyzing requirements...")
    name = "Atlas"
    description = "A DevOps specialist focused on Docker orchestration."
    expertise = {"devops": 1.0, "docker": 0.9}
    
    print(f"🛠️ ForgeAgent: Forging {name} package...")
    result = create_agent(name, description, "You are Atlas, a Docker expert.", expertise)
    print(f"✅ Forge Result: {result['status']} - {result['message']}")
    
    print("\n🔍 ForgeAgent: Searching ClawHub for Docker skills...")
    # Mocking search/install success
    print("✅ Found skills: ['docker-essentials', 'k8s-basics']")
    
    print("🚀 ForgeAgent: Installing 'docker-essentials' into Atlas...")
    install_result = install_skill("docker-essentials", name)
    print(f"✅ Install Result: {install_result['status']}")
    
    print("\n📡 Final Status: 📡 Atlas is forged and ready for awakening.")
    print(f"Forged agents: {list_forged_agents()}")

if __name__ == '__main__':
    asyncio.run(run_demo())
