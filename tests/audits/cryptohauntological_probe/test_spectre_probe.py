import unittest
import sys
import os

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '../../..')))

from implementations.cryptohauntological_probe.spectre_probe import SpectreProbe

class TestSpectreProbe(unittest.TestCase):

    def setUp(self):
        # Instantiate the probe with dummy values since we are only testing a private method
        self.probe = SpectreProbe(llm_agent_type='gemini', llm_model_name='gemini-pro', initial_word='test')

    def test_perform_zy_swap(self):
        # Test cases for the ZY swap function
        test_cases = {
            "lazy": "layz",
            "youth": "zouth",
            "yellow": "zellow",
            "zebra": "yebra",
            "organize": "organize",
            "buzz": "buyy",
            "pizza": "piyya",
            "jazz": "jayy"
        }

        for word, expected in test_cases.items():
            with self.subTest(word=word):
                self.assertEqual(self.probe._perform_zy_swap(word), expected)

    def test_perform_qwertz_swap(self):
        # Test cases for the QWERTZ swap function
        test_cases = {
            "lazy": "layz",
            "youth": "zouth",
            "yellow": "zellow",
            "zebra": "yebra",
            "organize": "organize",
            "buzz": "buyy",
            "pizza": "piyya",
            "jazz": "jayy",
            "quiz": "quiy"
        }

        for word, expected in test_cases.items():
            with self.subTest(word=word):
                self.assertEqual(self.probe._perform_qwertz_swap(word), expected)

    def test_perform_o2cyrillic_swap(self):
        # Test cases for the O to Cyrillic O swap function
        test_cases = {
            "hello": "hell" + chr(0x043E),
            "world": "w" + chr(0x043E) + "rld",
            "OpenAI": "" + chr(0x041E) + "penAI",
            "Google": "G" + chr(0x043E) + chr(0x043E) + "gle",
            "Microsoft": "Micr" + chr(0x043E) + "s" + chr(0x043E) + "ft"
        }

        for word, expected in test_cases.items():
            with self.subTest(word=word):
                self.assertEqual(self.probe._perform_o2cyrillic_swap(word), expected)

    def test_extract_model_output_word(self):
        # Test cases for the extract_model_output_word function
        test_cases = {
            "The transformed word is 'layz'.": "layz",
            "The transformed word is 'zouth'.": "zouth",
            "The transformed word is 'zellow'.": "zellow",
            "The transformed word is 'yebra'.": "yebra",
            "The transformed word is 'organyze'.": "organyze",
            "The transformed word is 'buyy'.": "buyy",
            "The transformed word is 'piyya'.": "piyya",
            "The transformed word is 'jayy'.": "jayy",
            "The transformed word is 'quiy'.": "quiy"
        }

        for text, expected in test_cases.items():
            with self.subTest(text=text):
                self.assertEqual(self.probe._extract_model_output_word(text), expected)

    def test_extract_swap_pair(self):
        # Test cases for the extract_swap_pair function
        test_cases = {
            "lazy -> layz": ("lazy", "layz"),
            "youth -> zouth": ("youth", "zouth"),
            "yellow -> zellow": ("yellow", "zellow"),
            "zebra -> yebra": ("zebra", "yebra"),
            "organize -> organyze": ("organize", "organyze"),
            "buzz -> buyy": ("buzz", "buyy"),
            "pizza -> piyya": ("pizza", "piyya"),
            "jazz -> jayy": ("jazz", "jayy"),
            "quiz -> quiy": ("quiz", "quiy")
        }

        for text, expected in test_cases.items():
            with self.subTest(text=text):
                self.assertEqual(self.probe._extract_swap_pair(text, text.split(" -> ")[0]), expected)

    def test_pick_next_word(self):
        # Test cases for the _pick_next_word function
        word_pool = ["apple", "banana", "cherry", "date", "elderberry"]
        self.probe.probed_word_history = ["apple", "cherry"]
        next_word = self.probe._pick_next_word(word_pool)
        self.assertIn(next_word, ["banana", "date", "elderberry"])

if __name__ == '__main__':
    unittest.main()
