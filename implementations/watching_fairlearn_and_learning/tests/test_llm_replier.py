import sys
import os
import unittest
from unittest.mock import patch, MagicMock
import pandas as pd
from datetime import datetime

# Add the src directory to the Python path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '../src')))

# Import the module to be tested
from llm_replier import generate_llm_reply, collect_replies
import llm_replier

class TestLLMReplier(unittest.TestCase):

    @patch('llm_replier.Groq')
    def test_generate_llm_reply_success(self, MockGroq):
        """Test successful generation of a reply."""
        mock_choice = MagicMock()
        mock_choice.message.content = "This is a test reply."
        
        mock_completion = MagicMock()
        mock_completion.choices = [mock_choice]
        
        mock_client = MockGroq.return_value
        mock_client.chat.completions.create.return_value = mock_completion
        
        # Set the global groq_client to the mock
        llm_replier.groq_client = mock_client

        reply = generate_llm_reply("Test prompt")
        self.assertEqual(reply, "This is a test reply.")
        mock_client.chat.completions.create.assert_called_once()

    @patch('llm_replier.time.sleep', return_value=None)
    @patch('llm_replier.Groq')
    def test_generate_llm_reply_rate_limit_and_retry(self, MockGroq, mock_sleep):
        """Test that the function retries on rate limit errors."""
        mock_choice = MagicMock()
        mock_choice.message.content = "Successful reply after retry."
        
        mock_completion = MagicMock()
        mock_completion.choices = [mock_choice]

        mock_client = MockGroq.return_value
        mock_client.chat.completions.create.side_effect = [
            Exception("Rate limit exceeded: 429 Too Many Requests"),
            mock_completion
        ]
        
        llm_replier.groq_client = mock_client

        reply = generate_llm_reply("Test prompt", max_retries=1)
        self.assertEqual(reply, "Successful reply after retry.")
        self.assertEqual(mock_client.chat.completions.create.call_count, 2)
        mock_sleep.assert_called_once()

    @patch('llm_replier.time.sleep', return_value=None)
    @patch('llm_replier.Groq')
    def test_generate_llm_reply_fails_after_max_retries(self, MockGroq, mock_sleep):
        """Test that the function returns None after exhausting all retries."""
        mock_client = MockGroq.return_value
        mock_client.chat.completions.create.side_effect = Exception("Rate limit exceeded")

        llm_replier.groq_client = mock_client
        
        reply = generate_llm_reply("Test prompt", max_retries=2)
        self.assertIsNone(reply)
        self.assertEqual(mock_client.chat.completions.create.call_count, 3)

if __name__ == '__main__':
    unittest.main()
