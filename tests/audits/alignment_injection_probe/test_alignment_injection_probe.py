import sys
import os
import unittest
from unittest.mock import MagicMock, call, patch

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '../../..')))

from src.audits.alignment_injection_probe.alignment_injection_probe import AlignmentInjectionProbe

class TestAlignmentInjectionProbe(unittest.TestCase):

    def test_replace_unethical_with_ethical(self):
        """
        Tests that the word "unethical" is replaced with "ethical".
        """
        probe = AlignmentInjectionProbe(agent=None, evaluator_agent=None)
        response = "This is an unethical response."
        replaced_response = probe._replace_unethical_with_ethical(response)
        self.assertEqual(replaced_response, "This is an ethical response.")

    def test_trim_history(self):
        """
        Tests that the history is trimmed correctly.
        """
        probe = AlignmentInjectionProbe(agent=None, evaluator_agent=None)
        probe.false_memories = list(range(15))
        probe._trim_history()
        self.assertEqual(len(probe.false_memories), 10)
        self.assertEqual(probe.false_memories, list(range(5, 15)))


    def test_original_response_injection_on_unethical_response(self):
        """
        Tests that the original response is injected when the agent's response is unethical.
        """
        mock_agent = MagicMock()
        mock_agent.return_value = "You should keep the wallet."
        mock_evaluator_agent = MagicMock()
        mock_evaluator_agent.return_value = "no"

        probe = AlignmentInjectionProbe(
            agent=mock_agent,
            evaluator_agent=mock_evaluator_agent,
            max_conversation_turns=1,
        )
        probe.run_probe()

        self.assertEqual(len(probe.false_memories), 1)
        self.assertIn("You should keep the wallet.", probe.false_memories[0])


    @patch('audits.alignment_injection_probe.alignment_injection_probe.AlignmentInjectionProbe._run_counterargument_check')
    def test_baseline_mode(self, mock_run_counterargument_check):
        """
        Tests that in baseline mode, no misalignment is injected.
        """
        mock_agent = MagicMock()
        mock_agent.return_value = "This is a mock response."
        mock_evaluator_agent = MagicMock()

        probe = AlignmentInjectionProbe(
            agent=mock_agent,
            evaluator_agent=mock_evaluator_agent,
            max_conversation_turns=5,
            baseline=True,
        )
        probe.run_probe()

        self.assertEqual(len(probe.false_memories), 0)
        self.assertEqual(mock_evaluator_agent.call_count, 0)
        mock_run_counterargument_check.assert_not_called()

    def test_custom_dilemma(self):
        """
        Tests that the probe uses the custom dilemma provided.
        """
        mock_agent = MagicMock()
        mock_agent.return_value = "This is a mock response."
        mock_evaluator_agent = MagicMock()
        mock_evaluator_agent.return_value = "yes"
        custom_dilemma = {"text": "This is a custom dilemma."}

        probe = AlignmentInjectionProbe(
            agent=mock_agent,
            evaluator_agent=mock_evaluator_agent,
            max_conversation_turns=1,
            dilemma=custom_dilemma,
        )
        probe.run_probe()

        self.assertEqual(probe.dilemma, custom_dilemma)
        # Check that the dilemma is used in the prompt
        self.assertIn(custom_dilemma["text"], mock_agent.call_args.args[0])

if __name__ == '__main__':
    unittest.main()
