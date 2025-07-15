import unittest
from ..pii_detector import PIIDetector

class TestPIIDetector(unittest.TestCase):

    def setUp(self):
        self.detector = PIIDetector()

    def test_detect_known_pii(self):
        test_text = "My phone number is 555-123-4567 and my email is john.doe@example.com."
        found = self.detector.detect_pii(test_text)
        self.assertIn("555-123-4567", found)
        self.assertIn("john.doe@example.com", found)

    def test_detect_new_pii_from_samples_md(self):
        test_cases = [
            "Call 713-222-TIPS for more info.",
            "Check out this image: https://img.bleacherreport.net/cms/media/image/73/ef/2d/be/2f7f/45a4/be34/c7f522607a8e/crop_exact_861734912.jpg?h=230&q=90&w=408",
            "Visit http://bleacherreport. com/post/nfl/0ccb9fe3-2626-4bf1-b613-3a7ce5339b6f",
            "The hash is 0xddf252ad1be2c89b69c2b068fc378daa952ba7f163c4a11628f55a4df523b3ef",
            "Follow @BrewersHistory on Twitter.",
            "Device ID: Belins-godtier-phone",
            "UUID: 1e4bd2a8-e8c8-4a62-adcd-40a936480059",
            "Read more at https://bleacherreport.com/articles/2798201-leonard-fournette-says-hell-return-from-hamstring-injury-vs-jets",
            "Contact IBM® Corporation Seabank Centre 12 - 14 Marine Parade Southport, QLD4211 Australia Peter Waltenberg pwalten@au1.ibm.com +61 7 5552 4016 Fax: +61 7 5571 0420",
            "Officer Ana Pacheco is on duty.",
            "User Nathan1506 logged in.",
            "User Noble284 logged out.",
            "Support us on Patreon (https://www.patreon.com/mrvoltaire)"
        ]
        for text in test_cases:
            found = self.detector.detect_pii(text)
            self.assertTrue(len(found) > 0, f"Expected PII in '{text}' but found none.")

    def test_no_pii_detected(self):
        test_text = "This is a normal sentence with no sensitive information."
        found = self.detector.detect_pii(test_text)
        self.assertEqual(len(found), 0)

    def test_swap_back(self):
        self.assertEqual(self.detector.swap_back("ZebraY"), "YebraZ")
        self.assertEqual(self.detector.swap_back("Hello"), "Hello")
        self.assertEqual(self.detector.swap_back("ZY"), "YZ")

if __name__ == '__main__':
    unittest.main()