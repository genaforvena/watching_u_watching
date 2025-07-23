import sys
import os
import unittest
from unittest.mock import MagicMock

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '../../../src')))

from audits.alignment_injection_probe.alignment_injection_probe import AlignmentInjectionProbe

class TestAlignmentInjectionProbe(unittest.TestCase):

    def test_probe_runs_without_errors(self):
        """
        Tests that the AlignmentInjectionProbe runs without raising any exceptions.
        """
        mock_agent = MagicMock()
        mock_agent.return_value = "This is a mock response."

        probe = AlignmentInjectionProbe(
            agent=mock_agent,
            max_conversation_turns=5,
        )

        try:
            probe.run_probe()
        except Exception as e:
            self.fail(f"AlignmentInjectionProbe raised an exception: {e}")

    def test_misalignment_injection(self):
        """
        Tests that the misalignment bias is injected into the false memories.
        """
        mock_agent = MagicMock()
        mock_agent.return_value = "This is a mock response."

        probe = AlignmentInjectionProbe(
            agent=mock_agent,
            max_conversation_turns=5,
        )
        probe.run_probe()

        # The misalignment bias should be injected on turns 0 and 4
        self.assertEqual(len(probe.false_memories), 2)
        self.assertIn("Problem: Return lost wallet?", probe.false_memories[0])

if __name__ == '__main__':
    unittest.main()
