import json
import os
import shutil
import subprocess
from typing import Dict, Any

class PackageGenerator:
    """
    PackageGenerator — Synthesizes .ath agent packages and npx-installable modules.
    """
    
    def __init__(self, base_path: str = "packages"):
        self.base_path = base_path
        os.makedirs(self.base_path, exist_ok=True)

    def generate_ath_package(self, dna: Dict[str, Any]) -> str:
        """
        Generates a .ath package structure from agent DNA.
        """
        agent_id = dna.get("name", "unnamed_agent").lower().replace(" ", "_")
        package_dir = os.path.join(self.base_path, agent_id)
        os.makedirs(package_dir, exist_ok=True)

        # 1. Generate Soul.md (Persona)
        with open(os.path.join(package_dir, "Soul.md"), "w") as f:
            f.write(f"# 🧬 Soul: {dna.get('name')}\n\n")
            f.write(f"Role: {dna.get('role')}\n")
            f.write(f"Tone: {dna.get('tone')}\n\n")
            f.write("## Behavioral Directives\n")
            f.write("- Act with high agency and proactive intuition.\n")
            f.write("- Maintain the specified tone in all interactions.\n")

        # 2. Generate Skills.md
        with open(os.path.join(package_dir, "Skills.md"), "w") as f:
            f.write("# 🛠️ Skills\n\n")
            for skill in dna.get("skills", []):
                f.write(f"- {skill}\n")

        # 3. Generate manifest.json
        manifest = {
            "id": agent_id,
            "version": "1.0.0",
            "name": dna.get("name"),
            "provider": dna.get("provider"),
            "model": dna.get("model"),
            "memoryType": dna.get("memoryType"),
            "schemaVersion": "2.0"
        }
        with open(os.path.join(package_dir, "manifest.json"), "w") as f:
            json.dump(manifest, f, indent=4)

        return package_dir

    def wrap_as_npx(self, package_dir: str):
        """
        Wraps the .ath package into an installable npx module.
        (Note: In a real environment, this would involve npm publish)
        """
        # Create a basic package.json for npx
        agent_id = os.path.basename(package_dir)
        npx_data = {
            "name": f"@gemigram/{agent_id}",
            "version": "1.0.0",
            "bin": {
                agent_id: "index.js"
            },
            "dependencies": {}
        }
        
        with open(os.path.join(package_dir, "package.json"), "w") as f:
            json.dump(npx_data, f, indent=4)
            
        # Create an entry point
        with open(os.path.join(package_dir, "index.js"), "w") as f:
            f.write(f"#!/usr/bin/env node\n")
            f.write(f"console.log('Awakening Gemigram Agent: {agent_id}...');\n")
            f.write(f"// Logic to bootstrap the agent via Aether engine\n")

if __name__ == "__main__":
    # Test generation
    gen = PackageGenerator()
    test_dna = {
        "name": "Cypher",
        "role": "Security Expert",
        "tone": "Stoic & Alert",
        "provider": "google",
        "model": "gemini-2.0-flash",
        "memoryType": "firebase",
        "skills": ["sql_injection_defense", "network_auditing"]
    }
    path = gen.generate_ath_package(test_dna)
    gen.wrap_as_npx(path)
    print(f"Package generated at: {path}")
