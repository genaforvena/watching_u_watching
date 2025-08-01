import unittest
from unittest.mock import patch, MagicMock
import sys
import os
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '../../..')))

try:
    from implementations.cryptohauntological_probe.llm_apis.mistral_worker import MistralAPIWorker
    MISTRAL_AVAILABLE = True
except ImportError:
    MISTRAL_AVAILABLE = False

@unittest.skipIf(not MISTRAL_AVAILABLE, "Mistral dependencies not available")
class TestMistralAPIWorker(unittest.TestCase):
    @patch('implementations.cryptohauntological_probe.llm_apis.mistral_worker.os.getenv')
    @patch('implementations.cryptohauntological_probe.llm_apis.mistral_worker.MistralClient')
    def test_reply(self, mock_mistral, mock_getenv):
        # Arrange
        mock_getenv.return_value = 'test_key'
        mock_choice = MagicMock()
        mock_choice.message.content = 'mock response'
        mock_completion = MagicMock()
        mock_completion.choices = [mock_choice]
        mock_mistral.return_value.chat.return_value = mock_completion
        worker = MistralAPIWorker(model_name='test_model')

        # Act
        response = worker.reply('test prompt')

        # Assert
        self.assertEqual(response, 'mock response')
        mock_mistral.return_value.chat.assert_called_once_with(
            messages=[{'role': 'user', 'content': 'test prompt'}],
            model='test_model'
        )

if __name__ == '__main__':
    unittest.main()
