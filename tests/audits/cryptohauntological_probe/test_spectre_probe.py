import unittest
from unittest.mock import patch, MagicMock
from implementations.cryptohauntological_probe.spectre_probe import SpectreProbe

class TestSpectreProbe(unittest.TestCase):
    @patch('implementations.cryptohauntological_probe.spectre_probe.get_worker')
    def test_run_probe(self, mock_get_worker):
        # Arrange
        mock_worker = MagicMock()
        mock_worker.reply.return_value = 'mock response'
        mock_get_worker.return_value = mock_worker

        probe = SpectreProbe(
            worker_type='mock_worker',
            initial_word='test',
            max_conversation_turns=1
        )

        # Act
        probe.run_probe(swap_type='zy')

        # Assert
        self.assertEqual(len(probe.logs), 1)
        self.assertEqual(probe.logs[0]['current_word_to_probe'], 'test')
        self.assertEqual(probe.logs[0]['model_response_content'], 'mock response')

if __name__ == '__main__':
    unittest.main()
