"""
[V1] GWS Connector Interface
Bridges the AetherOS Agent to the GWS CLI and Google ADK Skills.
"""

import json
import subprocess


class GWSConnectorV1:
    def __init__(self):
        self.cli_path = "gws" # Assumes gws CLI is in PATH
        
    def execute_skill(self, skill_name: str, params: dict):
        """
        Executes a GWS skill via the underlying CLI.
        """
        try:
            # Example: translate agent skill call to CLI command
            # gws drive list --format=json
            cmd = [self.cli_path] + skill_name.split('-')[1:] 
            for key, val in params.items():
                cmd.extend([f"--{key}", str(val)])
                
            result = subprocess.run(cmd, capture_output=True, text=True, check=True)
            return json.loads(result.stdout)
        except Exception as e:
            return {"status": "error", "message": str(e)}

    def gmail_send(self, to, subject, body):
        return self.execute_skill("gws-gmail-send", {"to": to, "subject": subject, "body": body})

    def drive_list(self, query=""):
        return self.execute_skill("gws-drive-list", {"query": query})

# V1 Instance Ready for Injecting into AetherGateway
gws_v1 = GWSConnectorV1()
