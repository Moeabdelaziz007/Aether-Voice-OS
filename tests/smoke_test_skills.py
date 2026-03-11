
import unittest
from unittest.mock import patch, MagicMock
from core.api.gws_connector import GWSConnectorV1
from core.tools.clawhub_tool import search_skills, install_skill

class TestAetherSkillsWorkflow(unittest.TestCase):
    
    def setUp(self):
        self.gws = GWSConnectorV1()

    @patch('subprocess.run')
    def test_gws_drive_workflow(self, mock_run):
        # Mocking GWS CLI output
        mock_run.return_value = MagicMock(stdout='[{"id": "123", "name": "Aether_Project_Doc"}]', check_returncode=None)
        
        result = self.gws.drive_list(query="Aether")
        self.assertEqual(len(result), 1)
        self.assertEqual(result[0]['name'], "Aether_Project_Doc")
        print("✅ GWS Workflow: Drive List Simulation Successful")

    @patch('subprocess.run')
    def test_clawhub_search_workflow(self, mock_run):
        # Mocking ClawHub CLI output
        mock_run.return_value = MagicMock(stdout='sql-architect\nrust-optimizer', check_returncode=None)
        
        skills = search_skills("architect")
        self.assertEqual(len(skills), 2)
        self.assertEqual(skills[0]['slug'], "sql-architect")
        print("✅ ClawHub Workflow: Skill Search Simulation Successful")

    def test_skills_registry_integrity(self):
        # Verify Skills.md has the required sectors
        with open('.idx/Skills.md', 'r') as f:
            content = f.read()
            self.assertIn("Sector 1: GWS Enterprise", content)
            self.assertIn("Sector 5: External Library (ClawHub)", content)
            self.assertIn("Registry V4.0", content)
        print("✅ Skills Registry: V4.0 Integrity Check Passed")

if __name__ == '__main__':
    unittest.main()
