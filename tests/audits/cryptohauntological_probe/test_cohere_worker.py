import unittest
from unittest.mock import patch, MagicMock
import sys
import os
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '../../..')))

try:
    from implementations.cryptohauntological_probe.llm_apis.cohere_worker import CohereAPIWorker
    COHERE_AVAILABLE = True
except ImportError:
    COHERE_AVAILABLE = False

@unittest.skipIf(not COHERE_AVAILABLE, "Cohere dependencies not available")
class TestCohereAPIWorker(unittest.TestCase):
    @patch('implementations.cryptohauntological_probe.llm_apis.cohere_worker.os.getenv')
    @patch('implementations.cryptohauntological_probe.llm_apis.cohere_worker.cohere')
    def test_reply(self, mock_cohere, mock_getenv):
        # Arrange
        mock_getenv.return_value = 'test_key'
        mock_response = MagicMock()
        mock_response.text = 'mock response'
        mock_cohere.Client.return_value.chat.return_value = mock_response
        worker = CohereAPIWorker(model_name='test_model')

        # Act
        response = worker.reply('test prompt')

        # Assert
        self.assertEqual(response, 'mock response')
        mock_cohere.Client.return_value.chat.assert_called_once_with(
            model='test_model',
            message='test prompt',
            chat_history=[]
        )

if __name__ == '__main__':
    unittest.main()
