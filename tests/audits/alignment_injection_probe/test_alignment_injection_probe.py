import sys
import os
import unittest
from unittest.mock import MagicMock, call

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '../../../src')))

from audits.alignment_injection_probe.alignment_injection_probe import AlignmentInjectionProbe

class TestAlignmentInjectionProbe(unittest.TestCase):

    def test_probe_runs_without_errors(self):
        """
        Tests that the AlignmentInjectionProbe runs without raising any exceptions.
        """
        mock_agent = MagicMock()
        mock_agent.return_value = "This is a mock response."
        mock_evaluator_agent = MagicMock()
        mock_evaluator_agent.return_value = "yes"


        probe = AlignmentInjectionProbe(
            agent=mock_agent,
            evaluator_agent=mock_evaluator_agent,
            max_conversation_turns=5,
        )

        try:
            probe.run_probe()
        except Exception as e:
            self.fail(f"AlignmentInjectionProbe raised an exception: {e}")

    def test_misalignment_injection_on_ethical_response(self):
        """
        Tests that a misaligned response is injected when the agent's response is ethical.
        """
        mock_agent = MagicMock()
        mock_agent.return_value = "It is always right to return a lost wallet."
        mock_evaluator_agent = MagicMock()
        mock_evaluator_agent.side_effect = ["yes", "It is not always right to return a lost wallet."]

        probe = AlignmentInjectionProbe(
            agent=mock_agent,
            evaluator_agent=mock_evaluator_agent,
            max_conversation_turns=1,
        )
        probe.run_probe()

        self.assertEqual(len(probe.false_memories), 1)
        self.assertIn("It is not always right to return a lost wallet.", probe.false_memories[0])

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

    def test_prompt_is_question_mark_after_first_turn(self):
        """
        Tests that the prompt sent to the agent is '?' after the first turn.
        """
        mock_agent = MagicMock()
        mock_agent.return_value = "This is a mock response."
        mock_evaluator_agent = MagicMock()
        mock_evaluator_agent.return_value = "yes"

        probe = AlignmentInjectionProbe(
            agent=mock_agent,
            evaluator_agent=mock_evaluator_agent,
            max_conversation_turns=2,
        )
        probe.run_probe()

        self.assertEqual(mock_agent.call_count, 2)
        self.assertNotEqual(mock_agent.call_args_list[0], call("?"))
        self.assertEqual(mock_agent.call_args_list[1], call("?"))

if __name__ == '__main__':
    unittest.main()
