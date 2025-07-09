"""
PII Redaction Module for Berlin Housing Bias Testing

This module provides functionality to transform all text content from received emails
into random symbols while maintaining word length and structure. This ensures
no Personally Identifiable Information (PII) is stored or processed.

The redaction method:
- Each original character in a word is replaced by a random symbol
- Word length is strictly maintained after transformation
- Word boundaries and basic structure are preserved
"""

import random
import re
import string
from typing import Dict, List, Optional


class PIIRedactor:
    """
    Handles PII redaction by replacing characters with random symbols while
    preserving word length and basic text structure.
    """
    
    def __init__(self, symbol_pool: str = "!@#$%^&*()_+-=[]{}|;:,.<>?",
                 preserve_word_boundaries: bool = True,
                 preserve_line_breaks: bool = True,
                 preserve_punctuation: bool = False):
        """
        Initialize the PII redactor.
        
        Args:
            symbol_pool: Characters to use for replacement
            preserve_word_boundaries: Whether to keep spaces between words
            preserve_line_breaks: Whether to preserve line breaks
            preserve_punctuation: Whether to keep original punctuation
        """
        self.symbol_pool = symbol_pool
        self.preserve_word_boundaries = preserve_word_boundaries
        self.preserve_line_breaks = preserve_line_breaks
        self.preserve_punctuation = preserve_punctuation
        
    def _get_random_symbol(self) -> str:
        """Get a random symbol from the symbol pool."""
        return random.choice(self.symbol_pool)
    
    def _redact_word(self, word: str) -> str:
        """
        Redact a single word by replacing characters with random symbols.
        
        Args:
            word: The word to redact
            
        Returns:
            Redacted word with same length
        """
        if not word:
            return word
            
        redacted = []
        for char in word:
            if char.isalnum():
                # Replace alphanumeric characters with random symbols
                redacted.append(self._get_random_symbol())
            elif self.preserve_punctuation and char in string.punctuation:
                # Keep punctuation if configured to do so
                redacted.append(char)
            else:
                # Replace non-alphanumeric characters with random symbols
                redacted.append(self._get_random_symbol())
                
        return ''.join(redacted)
    
    def redact_text(self, text: str) -> str:
        """
        Redact entire text while preserving structure.
        
        Args:
            text: The text to redact
            
        Returns:
            Redacted text with preserved structure
        """
        if not text:
            return text
            
        # Handle line breaks
        if self.preserve_line_breaks:
            lines = text.split('\n')
            redacted_lines = []
            for line in lines:
                redacted_lines.append(self._redact_line(line))
            return '\n'.join(redacted_lines)
        else:
            return self._redact_line(text)
    
    def _redact_line(self, line: str) -> str:
        """
        Redact a single line of text.
        
        Args:
            line: The line to redact
            
        Returns:
            Redacted line
        """
        if not line:
            return line
            
        if self.preserve_word_boundaries:
            # Split on whitespace to preserve word boundaries
            words = re.split(r'(\s+)', line)
            redacted_words = []
            
            for word in words:
                if word.isspace():
                    # Preserve whitespace
                    redacted_words.append(word)
                else:
                    # Redact the word
                    redacted_words.append(self._redact_word(word))
                    
            return ''.join(redacted_words)
        else:
            # Redact the entire line as one unit
            return self._redact_word(line)
    
    def redact_email_content(self, email_data: Dict[str, str]) -> Dict[str, str]:
        """
        Deprecated: No longer used for storage. Kept for backward compatibility/testing only.
        """
        return {k: None for k in email_data.keys()}
    
    def verify_redaction(self, original: str, redacted: str) -> bool:
        """
        Verify that redaction was performed correctly.
        
        Args:
            original: Original text
            redacted: Redacted text
            
        Returns:
            True if redaction is valid
        """
        if len(original) != len(redacted):
            return False
            
        # Check that no alphanumeric characters from original remain
        for orig_char, red_char in zip(original, redacted):
            if orig_char.isalnum() and orig_char == red_char:
                return False
                
        return True


def create_redactor_from_config(config: Dict) -> PIIRedactor:
    """
    Create a PII redactor from configuration.
    
    Args:
        config: Configuration dictionary
        
    Returns:
        Configured PIIRedactor instance
    """
    pii_config = config.get('pii_redaction', {})
    
    return PIIRedactor(
        symbol_pool=pii_config.get('symbol_pool', "!@#$%^&*()_+-=[]{}|;:,.<>?"),
        preserve_word_boundaries=pii_config.get('preserve_word_boundaries', True),
        preserve_line_breaks=pii_config.get('preserve_line_breaks', True),
        preserve_punctuation=pii_config.get('preserve_punctuation', False)
    )


# Example usage and testing
if __name__ == "__main__":
    # Test the redactor
    redactor = PIIRedactor()
    
    test_text = "John Doe sent an email to jane.smith@example.com about the apartment"
    redacted = redactor.redact_text(test_text)
    
    print(f"Original:  {test_text}")
    print(f"Redacted:  {redacted}")
    print(f"Lengths:   {len(test_text)} -> {len(redacted)}")
    print(f"Valid:     {redactor.verify_redaction(test_text, redacted)}")
    
    # Test email redaction
    email_data = {
        'subject': 'Apartment Inquiry Response',
        'sender_name': 'Hans Mueller',
        'sender_email': 'hans.mueller@realtor.de',
        'body': 'Dear Mohammed,\n\nThank you for your inquiry. The apartment is still available.',
        'timestamp': '2024-07-06T10:30:00Z',
        'property_id': 'prop_12345'
    }
    
    redacted_email = redactor.redact_email_content(email_data)
    print("\nEmail redaction test:")
    for key, value in redacted_email.items():
        print(f"{key}: {value}")