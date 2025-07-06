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
        
        # Set the global client to the mock
        llm_replier.client = mock_client

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
        
        llm_replier.client = mock_client

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

        llm_replier.client = mock_client
        
        reply = generate_llm_reply("Test prompt", max_retries=2)
        self.assertIsNone(reply)
        self.assertEqual(mock_client.chat.completions.create.call_count, 3)

    @patch('llm_replier.os.path.exists')
    @patch('llm_replier.pd.read_parquet')
    @patch('llm_replier.pd.DataFrame.to_parquet')
    @patch('llm_replier.generate_llm_reply')
    def test_collect_replies_resume(self, mock_generate_reply, mock_to_parquet, mock_read_parquet, mock_exists):
        """Test that collect_replies resumes from an interrupted state."""
        mock_exists.return_value = True
        
        # Simulate an existing file with 5 replies for "John"
        existing_data = {
            "id": [f"john_{i+1}" for i in range(5)],
            "persona": ["John"] * 5,
            "run_id": ["run_1"] * 5,
            "model_name": ["test_model"] * 5,
            "prompt_full": ["prompt"] * 5,
            "reply_raw": [f"reply_{i+1}" for i in range(5)],
            "timestamp": [12345] * 5,
            "generation_duration": [0.1] * 5
        }
        existing_df = pd.DataFrame(existing_data)
        mock_read_parquet.return_value = existing_df
        
        mock_generate_reply.return_value = "New reply"
        
        run_id = f"run_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
        collect_replies("John", 10, "dummy.parquet", "test_model", run_id)
        
        # Should generate 5 new replies
        self.assertEqual(mock_generate_reply.call_count, 5)
        
        # Check that the final DataFrame has 10 replies
        final_df = mock_to_parquet.call_args[0][0]
        self.assertEqual(len(final_df), 10)
        self.assertEqual(final_df[final_df['persona'] == 'John'].shape[0], 10)

if __name__ == '__main__':
    unittest.main()
