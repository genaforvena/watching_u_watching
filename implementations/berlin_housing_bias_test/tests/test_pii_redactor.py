"""
Tests for PII Redaction System
"""

import unittest
import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent.parent / 'src'))
from pii_redactor import PIIRedactor


class TestPIIRedactor(unittest.TestCase):
    
    def setUp(self):
        self.redactor = PIIRedactor()
    
    def test_word_length_preservation(self):
        """Test that word lengths are preserved after redaction."""
        text = "John Doe sent an email to jane.smith@example.com"
        redacted = self.redactor.redact_text(text)
        
        self.assertEqual(len(text), len(redacted))
    
    def test_word_boundary_preservation(self):
        """Test that word boundaries (spaces) are preserved."""
        text = "Hello world test"
        redacted = self.redactor.redact_text(text)
        
        # Check that spaces are in the same positions
        for i, char in enumerate(text):
            if char == ' ':
                self.assertEqual(redacted[i], ' ')
    
    def test_line_break_preservation(self):
        """Test that line breaks are preserved."""
        text = "Line one\nLine two\nLine three"
        redacted = self.redactor.redact_text(text)
        
        # Check that line breaks are preserved
        text_lines = text.split('\n')
        redacted_lines = redacted.split('\n')
        
        self.assertEqual(len(text_lines), len(redacted_lines))
        for orig_line, red_line in zip(text_lines, redacted_lines):
            self.assertEqual(len(orig_line), len(red_line))
    
    def test_no_original_characters_remain(self):
        """Test that no alphanumeric characters from original remain."""
        text = "Secret123 Information"
        redacted = self.redactor.redact_text(text)
        
        for orig_char, red_char in zip(text, redacted):
            if orig_char.isalnum():
                self.assertNotEqual(orig_char, red_char)
    
    def test_email_content_redaction(self):
        """Test email content redaction (deprecated: now always returns None for all fields)."""
        email_data = {
            'subject': 'Apartment Inquiry Response',
            'sender_name': 'Hans Mueller',
            'sender_email': 'hans.mueller@realtor.de',
            'body': 'Dear Mohammed,\n\nThank you for your inquiry.',
            'timestamp': '2024-07-06T10:30:00Z',
            'property_id': 'prop_12345'
        }
        redacted = self.redactor.redact_email_content(email_data)
        # All fields should be None
        for v in redacted.values():
            self.assertIsNone(v)
    
    def test_verification(self):
        """Test redaction verification."""
        original = "Test 123 message"
        redacted = self.redactor.redact_text(original)
        
        self.assertTrue(self.redactor.verify_redaction(original, redacted))
        
        # Test with invalid redaction (same length but original chars remain)
        fake_redacted = "Test 123 message"  # No actual redaction
        self.assertFalse(self.redactor.verify_redaction(original, fake_redacted))


if __name__ == '__main__':
    unittest.main()