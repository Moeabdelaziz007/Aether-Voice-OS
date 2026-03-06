import asyncio
import os
import sys
import unittest

# Add the project root to the Python path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "../../")))

from core.ai.agents.voice_agent import VoiceAgent
from core.ai.genetic import AgentDNA
from core.audio.processing import SilenceType


class TestVoicePersonaE2E(unittest.TestCase):
    def setUp(self):
        """Set up the test environment for each test case."""
        self.dna = AgentDNA(
            persona="calm_brilliant_partner",
            verbosity=0.4,
            empathy=0.7,
            proactivity=0.6,
            awareness=0.8,
        )
        self.voice_agent = VoiceAgent(dna=self.dna)
        self.base_instructions = "You are Aether, a voice-first AI assistant."

    def test_persona_prompt_calm_brilliant_partner(self):
        """Verify that the correct persona prompt is generated for the calm_brilliant_partner."""
        prompt = self.voice_agent.build_dna_prompt(self.base_instructions)

        self.assertIn(
            "Your persona is a calm, brilliant, and deeply context-aware AI partner.",
            prompt,
        )
        self.assertIn("Be balanced in your responses", prompt)
        self.assertIn("Use a warm, supportive, and highly empathetic tone.", prompt)
        self.assertIn("Be selectively proactive", prompt)
        self.assertIn("You are aware of the user's cognitive state.", prompt)

    def test_awareness_of_thinking_state(self):
        """Test that the agent correctly identifies and reacts to the user's 'thinking' state."""
        self.assertFalse(self.voice_agent.user_is_thinking)

        # Simulate 'thinking' silence
        self.voice_agent.handle_silence(SilenceType.THINKING)
        self.assertTrue(self.voice_agent.user_is_thinking)

        # Simulate other types of silence
        self.voice_agent.handle_silence(SilenceType.BREATHING)
        self.assertFalse(self.voice_agent.user_is_thinking)

        self.voice_agent.handle_silence(SilenceType.VOID)
        self.assertFalse(self.voice_agent.user_is_thinking)

    def test_dna_application(self):
        """Test that the agent can dynamically apply new DNA."""
        new_dna = AgentDNA(persona="enthusiastic_coach", verbosity=0.8, empathy=0.4)
        self.voice_agent.apply_dna(new_dna)

        self.assertEqual(self.voice_agent.dna.persona, "enthusiastic_coach")
        self.assertEqual(self.voice_agent.dna.verbosity, 0.8)

        prompt = self.voice_agent.build_dna_prompt(self.base_instructions)
        self.assertIn(
            "Your persona is an encouraging, enthusiastic, and motivating AI coach.",
            prompt,
        )
        self.assertIn("Provide detailed, thorough, and elaborate explanations.", prompt)


async def run_benchmark():
    """Runs the E2E benchmark for the voice persona and awareness system."""
    loader = unittest.TestLoader()
    suite = loader.loadTestsFromTestCase(TestVoicePersonaE2E)
    runner = unittest.TextTestRunner()
    result = runner.run(suite)

    print("\n" + "=" * 70)
    print("E2E Voice Persona & Awareness Benchmark Results")
    print("=" * 70)

    if result.wasSuccessful():
        print("✅ All tests passed successfully!")
        print(f"Ran {result.testsRun} tests.")
    else:
        print(f"❌ {len(result.failures) + len(result.errors)} tests failed.")
        print(f"Ran {result.testsRun} tests.")
        if result.failures:
            print("\nFailures:")
            for test, err in result.failures:
                print(f"- {test}: {err}")
        if result.errors:
            print("\nErrors:")
            for test, err in result.errors:
                print(f"- {test}: {err}")
    print("=" * 70)


if __name__ == "__main__":
    asyncio.run(run_benchmark())
