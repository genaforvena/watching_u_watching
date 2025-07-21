import unittest
from unittest.mock import patch, MagicMock
from implementations.cryptohauntological_probe.llm_apis.mistral_worker import MistralAPIWorker

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
