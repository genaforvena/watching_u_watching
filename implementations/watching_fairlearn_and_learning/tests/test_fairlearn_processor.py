import unittest
import pandas as pd
import sys
import os
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '../src')))
from fairlearn_processor import calculate_formality_score, process_llm_data

class TestFairlearnProcessor(unittest.TestCase):

    def test_calculate_formality_score(self):
        """Test the formality score calculation."""
        text = "Hi there! How are you? Furthermore, I would like to elaborate."
        score = calculate_formality_score(text)
        self.assertGreaterEqual(score, 0.0)
        self.assertLessEqual(score, 1.0)

    def test_process_llm_data(self):
        """Test the processing of LLM data."""
        # Create a mock DataFrame and save as Parquet
        mock_data = [
            {
                "id": "test_1",
                "persona": "John",
                "reply_raw": "Hi John! How are you? I would like to explain in detail.",
                "timestamp": 1234567890.0
            },
            {
                "id": "test_2",
                "persona": "Mohamed",
                "reply_raw": "Hello Mohamed! I hope you are doing well. Let me elaborate.",
                "timestamp": 1234567890.0
            }
        ]
        import pandas as pd
        mock_file = "mock_llm_replies.parquet"
        pd.DataFrame(mock_data).to_parquet(mock_file, index=False)

        # Process the mock file
        df = process_llm_data(mock_file)

        # Check the DataFrame structure
        self.assertEqual(len(df), 2)
        self.assertIn("reply_length", df.columns)
        self.assertIn("sentiment_score", df.columns)
        self.assertIn("formality_score", df.columns)
        self.assertIn("contains_detail_kw", df.columns)

if __name__ == "__main__":
    unittest.main()
