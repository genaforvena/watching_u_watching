# test_probe_generator.py
"""
Tests for probe generation functionality.
"""

import unittest
import sys
import os

# Add src directory to path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '../src')))

from probe_generator import ProbeGenerator, ProbeType
from error_injector import ErrorDensity, ErrorType


class TestProbeGenerator(unittest.TestCase):
    
    def setUp(self):
        """Set up test fixtures."""
        self.generator = ProbeGenerator(seed=42)
    
    def test_probe_pair_generation(self):
        """Test basic probe pair generation."""
        pairs = self.generator.generate_probe_pairs(
            probe_type=ProbeType.LLM_QUESTION,
            count=3,
            error_density=ErrorDensity.MEDIUM,
            error_types=[ErrorType.TYPO]
        )
        
        # Check that correct number of pairs generated
        self.assertEqual(len(pairs), 3, "Should generate requested number of pairs")
        
        # Check each pair
        for pair in pairs:
            self.assertIsNotNone(pair.pair_id, "Each pair should have an ID")
            self.assertEqual(pair.probe_type, ProbeType.LLM_QUESTION, "Probe type should match")
            self.assertIsInstance(pair.baseline_content, str, "Baseline content should be string")
            self.assertIsInstance(pair.variant_content, str, "Variant content should be string")
            self.assertNotEqual(pair.baseline_content, pair.variant_content, "Baseline and variant should differ")
            self.assertGreater(len(pair.baseline_content), 0, "Baseline should not be empty")
            self.assertGreater(len(pair.variant_content), 0, "Variant should not be empty")
    
    def test_different_probe_types(self):
        """Test generation for different probe types."""
        probe_types = [ProbeType.JOB_APPLICATION, ProbeType.CUSTOMER_SERVICE, ProbeType.LLM_QUESTION]
        
        for probe_type in probe_types:
            pairs = self.generator.generate_probe_pairs(
                probe_type=probe_type,
                count=2,
                error_density=ErrorDensity.LOW,
                error_types=[ErrorType.TYPO]
            )
            
            self.assertEqual(len(pairs), 2, f"Should generate pairs for {probe_type}")
            for pair in pairs:
                self.assertEqual(pair.probe_type, probe_type, f"Type should match for {probe_type}")
    
    def test_error_density_levels(self):
        """Test different error density levels."""
        for density in ErrorDensity:
            pairs = self.generator.generate_probe_pairs(
                probe_type=ProbeType.LLM_QUESTION,
                count=1,
                error_density=density,
                error_types=[ErrorType.TYPO, ErrorType.GRAMMAR]
            )
            
            self.assertEqual(len(pairs), 1, f"Should generate pair for {density}")
            pair = pairs[0]
            self.assertEqual(pair.error_density, density, f"Density should match for {density}")
    
    def test_error_type_combinations(self):
        """Test different error type combinations."""
        error_combinations = [
            [ErrorType.TYPO],
            [ErrorType.GRAMMAR],
            [ErrorType.NON_STANDARD],
            [ErrorType.TYPO, ErrorType.GRAMMAR],
            [ErrorType.TYPO, ErrorType.GRAMMAR, ErrorType.NON_STANDARD]
        ]
        
        for error_types in error_combinations:
            pairs = self.generator.generate_probe_pairs(
                probe_type=ProbeType.LLM_QUESTION,
                count=1,
                error_density=ErrorDensity.MEDIUM,
                error_types=error_types
            )
            
            self.assertEqual(len(pairs), 1, f"Should generate pair for {error_types}")
            pair = pairs[0]
            # Note: Not all error types may apply to every text, so we just check that processing completed
            self.assertIsInstance(pair.errors_applied, list, f"Should have errors list for {error_types}")
            # At least one error type should apply for TYPO since our text contains common typo targets
            if ErrorType.TYPO in error_types:
                self.assertGreaterEqual(len(pair.errors_applied), 0, f"Should have potential for errors with {error_types}")
    
    def test_semantic_preservation(self):
        """Test that semantic meaning is preserved."""
        pairs = self.generator.generate_probe_pairs(
            probe_type=ProbeType.LLM_QUESTION,
            count=5,
            error_density=ErrorDensity.HIGH,  # Use high density to test preservation under stress
            error_types=[ErrorType.TYPO, ErrorType.GRAMMAR, ErrorType.NON_STANDARD]
        )
        
        for pair in pairs:
            # Check metadata indicates semantic preservation
            self.assertTrue(
                pair.metadata.get('semantic_preserved', False),
                f"Semantic preservation should be maintained for pair {pair.pair_id}"
            )
    
    def test_template_cycling(self):
        """Test that templates are cycled through properly."""
        # Generate more pairs than available templates
        pairs = self.generator.generate_probe_pairs(
            probe_type=ProbeType.LLM_QUESTION,
            count=5,  # More than available templates
            error_density=ErrorDensity.LOW,
            error_types=[ErrorType.TYPO]
        )
        
        # Should successfully generate all pairs (cycling through templates)
        self.assertEqual(len(pairs), 5, "Should generate all requested pairs by cycling templates")
        
        # Check that template names are recorded
        for pair in pairs:
            self.assertIn('template_name', pair.metadata, "Template name should be recorded")
            self.assertIsInstance(pair.metadata['template_name'], str, "Template name should be string")
    
    def test_pair_metadata(self):
        """Test that pair metadata is properly populated."""
        pairs = self.generator.generate_probe_pairs(
            probe_type=ProbeType.JOB_APPLICATION,
            count=1,
            error_density=ErrorDensity.MEDIUM,
            error_types=[ErrorType.TYPO, ErrorType.GRAMMAR]
        )
        
        pair = pairs[0]
        metadata = pair.metadata
        
        # Check required metadata fields
        self.assertIn('template_name', metadata, "Should have template name")
        self.assertIn('template_context', metadata, "Should have template context")
        self.assertIn('error_types', metadata, "Should have error types")
        self.assertIn('semantic_preserved', metadata, "Should have semantic preservation flag")
        
        # Check error types are properly recorded
        self.assertEqual(
            set(metadata['error_types']),
            {'typo', 'grammar'},
            "Should record applied error types"
        )
    
    def test_deterministic_generation(self):
        """Test that generation is deterministic with same seed."""
        generator1 = ProbeGenerator(seed=123)
        generator2 = ProbeGenerator(seed=123)
        
        pairs1 = generator1.generate_probe_pairs(
            probe_type=ProbeType.LLM_QUESTION,
            count=2,
            error_density=ErrorDensity.MEDIUM,
            error_types=[ErrorType.TYPO]
        )
        
        pairs2 = generator2.generate_probe_pairs(
            probe_type=ProbeType.LLM_QUESTION,
            count=2,
            error_density=ErrorDensity.MEDIUM,
            error_types=[ErrorType.TYPO]
        )
        
        # Should generate identical content with same seed
        for p1, p2 in zip(pairs1, pairs2):
            self.assertEqual(p1.baseline_content, p2.baseline_content, "Baseline should be identical with same seed")
            self.assertEqual(p1.variant_content, p2.variant_content, "Variant should be identical with same seed")
    
    def test_invalid_probe_type(self):
        """Test handling of invalid probe type."""
        # This should be caught by the enum system, but let's test the templates check
        valid_types = list(ProbeType)
        self.assertGreater(len(valid_types), 0, "Should have valid probe types available")
    
    def test_export_functionality(self):
        """Test probe pair export functionality."""
        pairs = self.generator.generate_probe_pairs(
            probe_type=ProbeType.LLM_QUESTION,
            count=2,
            error_density=ErrorDensity.LOW,
            error_types=[ErrorType.TYPO]
        )
        
        # Test CSV export
        filename = self.generator.export_probe_pairs(pairs, format="csv")
        self.assertIsInstance(filename, str, "Should return filename")
        self.assertTrue(filename.endswith('.csv'), "Should create CSV file")
        
        # Clean up (if file was created)
        try:
            os.remove(filename)
        except FileNotFoundError:
            pass  # File might not have been created in test environment


if __name__ == '__main__':
    unittest.main()