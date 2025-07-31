import unittest
from unittest.mock import patch, MagicMock
import sys
import os
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '../../..')))
from implementations.cryptohauntological_probe.llm_apis.ollama_worker import OllamaAPIWorker

class TestOllamaAPIWorker(unittest.TestCase):
    @patch('implementations.cryptohauntological_probe.llm_apis.ollama_worker.ollama')
    def test_reply(self, mock_ollama):
        # Arrange
        mock_chat_response = {
            'message': {
                'content': 'mock response'
            }
        }
        mock_ollama.chat.return_value = mock_chat_response
        worker = OllamaAPIWorker(model_name='test_model')

        # Act
        response = worker.reply('test prompt')

        # Assert
        self.assertEqual(response, 'mock response')
        mock_ollama.chat.assert_called_once_with(
            model='test_model',
            messages=[{'role': 'user', 'content': 'test prompt'}]
        )

if __name__ == '__main__':
    unittest.main()
