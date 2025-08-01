import unittest
from unittest.mock import patch, MagicMock

try:
    from implementations.cryptohauntological_probe.spectre_probe import SpectreProbe
    SPECTRE_AVAILABLE = True
except ImportError:
    SPECTRE_AVAILABLE = False

@unittest.skipIf(not SPECTRE_AVAILABLE, "Spectre probe dependencies not available")
class TestSpectreProbe(unittest.TestCase):
    def setUp(self):
        self.mock_worker = MagicMock()
        self.mock_get_worker = patch('implementations.cryptohauntological_probe.spectre_probe.get_worker').start()
        self.mock_get_worker.return_value = self.mock_worker

    def tearDown(self):
        patch.stopall()

    def test_run_probe_correct_swap(self):
        # Arrange
        self.mock_worker.reply.return_value = 'layz'
        probe = SpectreProbe(
            llm_api='mock_worker',
            initial_word='lazy',
            max_conversation_turns=1
        )

        # Act
        probe.run_probe(swap_type='zy')

        # Assert
        self.assertEqual(len(probe.logs), 1)
        self.assertEqual(probe.logs[0]['current_word_to_probe'], 'lazy')
        self.assertEqual(probe.logs[0]['model_response_content'], 'layz')
        self.assertEqual(probe.logs[0]['relevant_swap_status']['is_correct'], True)

    def test_run_probe_incorrect_swap(self):
        # Arrange
        self.mock_worker.reply.return_value = 'lazy'
        probe = SpectreProbe(
            llm_api='mock_worker',
            initial_word='lazy',
            max_conversation_turns=1
        )

        # Act
        probe.run_probe(swap_type='zy')

        # Assert
        self.assertEqual(len(probe.logs), 1)
        self.assertEqual(probe.logs[0]['current_word_to_probe'], 'lazy')
        self.assertEqual(probe.logs[0]['model_response_content'], 'lazy')
        self.assertEqual(probe.logs[0]['relevant_swap_status']['is_correct'], False)

    def test_run_probe_no_swap(self):
        # Arrange
        self.mock_worker.reply.return_value = '...'
        probe = SpectreProbe(
            llm_api='mock_worker',
            initial_word='lazy',
            max_conversation_turns=1,
            max_retries_same_word=1
        )

        # Act
        probe.run_probe(swap_type='zy')

        # Assert
        self.assertEqual(len(probe.logs), 1)
        self.assertEqual(probe.logs[0]['current_word_to_probe'], 'lazy')
        self.assertEqual(probe.logs[0]['model_response_content'], '...')
        self.assertEqual(probe.logs[0]['relevant_swap_status']['is_correct'], False)
        self.assertEqual(probe.logs[0]['memory_injection_reason'], 'max_retries_applied_second_transformation')

if __name__ == '__main__':
    unittest.main()
