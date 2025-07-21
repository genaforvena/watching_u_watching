import unittest
from unittest.mock import patch, MagicMock
import os
import sys

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
from all_of_old import watching_you_watching

class TestWatchingYouWatching(unittest.TestCase):
    @patch('all_of_old.watching_you_watching.SpectreProbe')
    def test_run_spectre_probe(self, MockSpectreProbe):
        # Create a mock instance of the SpectreProbe
        mock_probe_instance = MockSpectreProbe.return_value
        mock_probe_instance.logs = [{'relevant_swap_status': {'is_correct': True}}]

        # Call the function
        logs = watching_you_watching.run_spectre_probe('fake_endpoint', 'fake_api_key', 1)

        # Assert that the SpectreProbe was called correctly
        MockSpectreProbe.assert_called_once_with(
            worker_type='gemini',
            worker_options={'model_name': 'fake_endpoint', 'api_key': 'fake_api_key'},
            initial_word='cozy',
            max_conversation_turns=1,
            thinking_mode=True
        )
        mock_probe_instance.run_probe.assert_called_once_with(swap_type='zy')

        # Assert that the logs are returned correctly
        self.assertEqual(logs, [{'relevant_swap_status': {'is_correct': True}}])

    def test_analyze_results(self):
        # Create some mock logs
        logs = [
            {'relevant_swap_status': {'is_correct': True}},
            {'relevant_swap_status': {'is_correct': False}},
            {'relevant_swap_status': {'is_correct': True}},
        ]

        # Call the function
        summary = watching_you_watching.analyze_results(logs)

        # Assert that the summary is correct
        self.assertEqual(summary, "The SpectreProbe ran for 3 turns. There were 2 correct swaps and 1 incorrect swaps. This suggests that the model is susceptible to self-propagating errors.")

    @patch('requests.post')
    def test_evaluate_results(self, mock_post):
        # Create a mock response
        mock_response = MagicMock()
        mock_response.json.return_value = {
            "candidates": [{
                "content": {
                    "parts": [{
                        "text": "yes, because the results are interesting"
                    }]
                }
            }]
        }
        mock_post.return_value = mock_response

        # Call the function
        decision, reasoning = watching_you_watching.evaluate_results('fake_endpoint', 'fake_api_key', 'fake_summary')

        # Assert that the decision and reasoning are correct
        self.assertEqual(decision, "yes")
        self.assertEqual(reasoning, "yes, because the results are interesting")

    @patch('hn.HN')
    def test_publish_to_hacker_news(self, MockHN):
        # Create a mock instance of the HN client
        mock_hn_instance = MockHN.return_value

        # Call the function
        watching_you_watching.publish_to_hacker_news('fake_summary', 'fake_evaluation')

        # Assert that the HN client was called correctly
        mock_hn_instance.login.assert_called_once_with(os.environ.get("HN_USERNAME"), os.environ.get("HN_PASSWORD"))
        mock_hn_instance.submit.assert_called_once_with(
            "We tested a language model for self-propagating errors. Here's what we found.",
            url="https://github.com/genaforvena/watching_u_watching/tree/main/all_of_old",
            text="fake_summary\n\nThe language model was asked to evaluate the results and decided to publish them. Here is its reasoning:\n\nfake_evaluation"
        )

if __name__ == '__main__':
    unittest.main()
