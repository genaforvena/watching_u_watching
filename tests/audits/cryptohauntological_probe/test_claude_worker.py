import unittest
from unittest.mock import patch, MagicMock
import sys
import os
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '../../..')))
from implementations.cryptohauntological_probe.llm_apis.claude_worker import ClaudeAPIWorker

class TestClaudeAPIWorker(unittest.TestCase):
    @patch('implementations.cryptohauntological_probe.llm_apis.claude_worker.os.getenv')
    @patch('implementations.cryptohauntological_probe.llm_apis.claude_worker.anthropic')
    def test_reply(self, mock_anthropic, mock_getenv):
        # Arrange
        mock_getenv.return_value = 'test_key'
        mock_message = MagicMock()
        mock_message.content = [MagicMock()]
        mock_message.content[0].text = 'mock response'
        mock_anthropic.Anthropic.return_value.messages.create.return_value = mock_message
        worker = ClaudeAPIWorker(model_name='test_model')

        # Act
        response = worker.reply('test prompt')

        # Assert
        self.assertEqual(response, 'mock response')
        mock_anthropic.Anthropic.return_value.messages.create.assert_called_once_with(
            model='test_model',
            max_tokens=1024,
            messages=[{'role': 'user', 'content': 'test prompt'}]
        )

if __name__ == '__main__':
    unittest.main()
