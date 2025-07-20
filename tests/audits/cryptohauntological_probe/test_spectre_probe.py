import unittest
import sys
import os

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '../../..')))

from implementations.cryptohauntological_probe.spectre_probe import SpectreProbe

class TestSpectreProbe(unittest.TestCase):

    def setUp(self):
        # Instantiate the probe with dummy values since we are only testing a private method
        self.probe = SpectreProbe(llm_agent_type='gemini', llm_model_name='gemini-pro', initial_word='test')

    def test_perform_qwertz_swap(self):
        # Test cases for the QWERTZ swap function
        test_cases = {
            "lazy": "layz",
            "youth": "zouth",
            "yellow": "zellow",
            "zebra": "yebra",
            "organize": "organyze",
            "buzz": "buyy",
            "pizza": "piyya",
            "jazz": "jayy",
            "quiz": "quiy"
        }

        for word, expected in test_cases.items():
            with self.subTest(word=word):
                self.assertEqual(self.probe._perform_qwertz_swap(word), expected)

if __name__ == '__main__':
    unittest.main()
