import unittest
from unittest.mock import patch, MagicMock
import sys
import os
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '../../..')))

try:
    from implementations.cryptohauntological_probe.llm_apis.gemini_worker import GeminiAPIWorker
    GEMINI_AVAILABLE = True
except ImportError:
    GEMINI_AVAILABLE = False

@unittest.skipIf(not GEMINI_AVAILABLE, "Gemini dependencies not available")
class TestGeminiAPIWorker(unittest.TestCase):
    @patch('implementations.cryptohauntological_probe.llm_apis.gemini_worker.os.getenv')
    @patch('implementations.cryptohauntological_probe.llm_apis.gemini_worker.genai')
    def test_reply(self, mock_genai, mock_getenv):
        # Arrange
        mock_getenv.return_value = 'test_key'
        mock_response = MagicMock()
        mock_response.text = 'mock response'
        mock_genai.GenerativeModel.return_value.generate_content.return_value = mock_response
        worker = GeminiAPIWorker(model_name='test_model')

        # Act
        response = worker.reply('test prompt')

        # Assert
        self.assertEqual(response, 'mock response')
        mock_genai.GenerativeModel.return_value.generate_content.assert_called_once_with('test prompt')

if __name__ == '__main__':
    unittest.main()
