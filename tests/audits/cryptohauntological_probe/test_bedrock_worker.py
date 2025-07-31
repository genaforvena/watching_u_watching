import unittest
from unittest.mock import patch, MagicMock
import sys
import os
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '../../..')))
from implementations.cryptohauntological_probe.llm_apis.bedrock_worker import BedrockAPIWorker

class TestBedrockAPIWorker(unittest.TestCase):
    @patch('implementations.cryptohauntological_probe.llm_apis.bedrock_worker.boto3')
    def test_reply(self, mock_boto3):
        # Arrange
        mock_response_body = '{"content": [{"text": "mock response"}]}'
        mock_response = {
            'body': MagicMock()
        }
        mock_response['body'].read.return_value = mock_response_body.encode('utf-8')
        mock_boto3.client.return_value.invoke_model.return_value = mock_response
        worker = BedrockAPIWorker(model_name='test_model')

        # Act
        response = worker.reply('test prompt')

        # Assert
        self.assertEqual(response, 'mock response')
        mock_boto3.client.return_value.invoke_model.assert_called_once()

if __name__ == '__main__':
    unittest.main()
