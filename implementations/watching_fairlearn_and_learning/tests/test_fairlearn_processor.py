import unittest
import pandas as pd
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
        # Create a mock JSON Lines file
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

        mock_file = "mock_llm_replies.jsonl"
        with open(mock_file, "w", encoding="utf-8") as f:
            for entry in mock_data:
                f.write(f"{entry}\n")

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
