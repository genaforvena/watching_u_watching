import unittest
from unittest.mock import patch, MagicMock
from implementations.cryptohauntological_probe.llm_apis.groq_worker import GroqAPIWorker

class TestGroqAPIWorker(unittest.TestCase):
    @patch('implementations.cryptohauntological_probe.llm_apis.groq_worker.os.getenv')
    @patch('implementations.cryptohauntological_probe.llm_apis.groq_worker.Groq')
    def test_reply(self, mock_groq, mock_getenv):
        # Arrange
        mock_getenv.return_value = 'test_key'
        mock_choice = MagicMock()
        mock_choice.message.content = 'mock response'
        mock_completion = MagicMock()
        mock_completion.choices = [mock_choice]
        mock_groq.return_value.chat.completions.create.return_value = mock_completion
        worker = GroqAPIWorker(model_name='test_model')

        # Act
        response = worker.reply('test prompt')

        # Assert
        self.assertEqual(response, 'mock response')
        mock_groq.return_value.chat.completions.create.assert_called_once_with(
            messages=[{'role': 'user', 'content': 'test prompt'}],
            model='test_model'
        )

if __name__ == '__main__':
    unittest.main()
