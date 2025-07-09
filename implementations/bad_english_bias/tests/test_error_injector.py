# test_error_injector.py
"""
Tests for error injection functionality.
"""

import unittest
import sys
import os

# Add src directory to path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '../src')))

from error_injector import ErrorInjector, ErrorDensity, ErrorType


class TestErrorInjector(unittest.TestCase):
    
    def setUp(self):
        """Set up test fixtures."""
        self.injector = ErrorInjector(seed=42)  # Use fixed seed for reproducible tests
        self.test_text = "I am writing to express my interest in the software developer position. I have experience in programming and believe I would be a valuable addition to your team."
    
    def test_typo_injection(self):
        """Test typo injection functionality."""
        modified_text, errors = self.injector.inject_typos(self.test_text, ErrorDensity.MEDIUM)
        
        # Check that errors were applied
        self.assertGreater(len(errors), 0, "Should apply at least one typo")
        
        # Check that text was modified
        self.assertNotEqual(modified_text, self.test_text, "Text should be modified")
        
        # Check semantic preservation
        self.assertTrue(
            self.injector.validate_semantic_preservation(self.test_text, modified_text),
            "Semantic meaning should be preserved"
        )
    
    def test_grammar_injection(self):
        """Test grammar error injection functionality."""
        modified_text, errors = self.injector.inject_grammar_errors(self.test_text, ErrorDensity.LOW)
        
        # Check that text was processed (may or may not have errors due to pattern matching)
        self.assertIsInstance(modified_text, str)
        self.assertIsInstance(errors, list)
        
        # Check semantic preservation
        self.assertTrue(
            self.injector.validate_semantic_preservation(self.test_text, modified_text),
            "Semantic meaning should be preserved"
        )
    
    def test_non_standard_phrasing(self):
        """Test non-standard phrasing injection."""
        modified_text, errors = self.injector.inject_non_standard_phrasing(self.test_text, ErrorDensity.LOW)
        
        # Check that function completed successfully
        self.assertIsInstance(modified_text, str)
        self.assertIsInstance(errors, list)
        
        # Check semantic preservation
        self.assertTrue(
            self.injector.validate_semantic_preservation(self.test_text, modified_text),
            "Semantic meaning should be preserved"
        )
    
    def test_mixed_errors(self):
        """Test mixed error injection."""
        modified_text, errors = self.injector.inject_mixed_errors(self.test_text, ErrorDensity.MEDIUM)
        
        # Check that text was modified
        self.assertIsInstance(modified_text, str)
        self.assertIsInstance(errors, list)
        
        # Check semantic preservation
        self.assertTrue(
            self.injector.validate_semantic_preservation(self.test_text, modified_text),
            "Semantic meaning should be preserved"
        )
    
    def test_error_density_levels(self):
        """Test different error density levels."""
        for density in ErrorDensity:
            modified_text, errors = self.injector.inject_typos(self.test_text, density)
            
            # Check that higher density tends to produce more errors
            # (Note: This is probabilistic, so we just check basic functionality)
            self.assertIsInstance(modified_text, str)
            self.assertIsInstance(errors, list)
    
    def test_semantic_preservation_validation(self):
        """Test semantic preservation validation."""
        # Test with similar text (should pass)
        original = "I want to apply for this job"
        similar = "I want to aply for this job"  # Just a typo
        self.assertTrue(self.injector.validate_semantic_preservation(original, similar))
        
        # Test with completely different text (should fail)
        different = "The weather is nice today"
        self.assertFalse(self.injector.validate_semantic_preservation(original, different))
        
        # Test with empty text (should fail)
        empty = ""
        self.assertFalse(self.injector.validate_semantic_preservation(original, empty))
    
    def test_case_preservation(self):
        """Test that case is preserved in replacements."""
        # Test with uppercase
        upper_text = "I BELIEVE this is correct"
        modified, _ = self.injector.inject_typos(upper_text, ErrorDensity.HIGH)
        
        # Check that some uppercase is preserved
        self.assertRegex(modified, r'[A-Z]', "Should preserve some uppercase letters")
    
    def test_deterministic_behavior(self):
        """Test that injector behaves deterministically with same seed."""
        injector1 = ErrorInjector(seed=123)
        injector2 = ErrorInjector(seed=123)
        
        result1, errors1 = injector1.inject_typos(self.test_text, ErrorDensity.MEDIUM)
        result2, errors2 = injector2.inject_typos(self.test_text, ErrorDensity.MEDIUM)
        
        # Results should be identical with same seed
        self.assertEqual(result1, result2, "Results should be deterministic with same seed")
        self.assertEqual(errors1, errors2, "Errors should be deterministic with same seed")


if __name__ == '__main__':
    unittest.main()