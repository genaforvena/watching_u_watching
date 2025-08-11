"""
Tests for the formal verification proof-of-concept module.

This test suite validates the Z3-based threshold compliance verification
functionality to ensure formal verification works correctly for compliance
testing scenarios.
"""

import sys
import os
import pytest

# Add the src directory to the path to import our module
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..', 'src')))

from formal_verification_poc import verify_threshold, verify_range_compliance


class TestVerifyThreshold:
    """Test cases for the verify_threshold function."""
    
    def test_less_than_or_equal_operator(self):
        """Test <= operator with various values."""
        assert verify_threshold(5, 10, '<=') == True
        assert verify_threshold(10, 10, '<=') == True
        assert verify_threshold(15, 10, '<=') == False
        
    def test_greater_than_or_equal_operator(self):
        """Test >= operator with various values."""
        assert verify_threshold(15, 10, '>=') == True
        assert verify_threshold(10, 10, '>=') == True
        assert verify_threshold(5, 10, '>=') == False
        
    def test_less_than_operator(self):
        """Test < operator with various values."""
        assert verify_threshold(5, 10, '<') == True
        assert verify_threshold(10, 10, '<') == False
        assert verify_threshold(15, 10, '<') == False
        
    def test_greater_than_operator(self):
        """Test > operator with various values."""
        assert verify_threshold(15, 10, '>') == True
        assert verify_threshold(10, 10, '>') == False
        assert verify_threshold(5, 10, '>') == False
        
    def test_equal_operator(self):
        """Test == operator with various values."""
        assert verify_threshold(10, 10, '==') == True
        assert verify_threshold(5, 10, '==') == False
        assert verify_threshold(15, 10, '==') == False
        
    def test_not_equal_operator(self):
        """Test != operator with various values."""
        assert verify_threshold(5, 10, '!=') == True
        assert verify_threshold(15, 10, '!=') == True
        assert verify_threshold(10, 10, '!=') == False
        
    def test_float_values(self):
        """Test with floating point values."""
        assert verify_threshold(0.85, 0.8, '>=') == True
        assert verify_threshold(0.75, 0.8, '>=') == False
        assert verify_threshold(3.14, 3.14, '==') == True
        
    def test_mixed_types(self):
        """Test with mixed integer and float types."""
        assert verify_threshold(5, 10.0, '<=') == True
        assert verify_threshold(5.0, 10, '<=') == True
        assert verify_threshold(10.0, 10, '==') == True
        
    def test_invalid_operator(self):
        """Test that invalid operators raise ValueError."""
        with pytest.raises(ValueError) as excinfo:
            verify_threshold(5, 10, 'invalid')
        assert "Unsupported operator: invalid" in str(excinfo.value)
        
    def test_default_operator(self):
        """Test that default operator is <=."""
        assert verify_threshold(5, 10) == True
        assert verify_threshold(15, 10) == False


class TestVerifyRangeCompliance:
    """Test cases for the verify_range_compliance function."""
    
    def test_value_within_range(self):
        """Test values that fall within the specified range."""
        assert verify_range_compliance(0.75, 0.5, 0.9) == True
        assert verify_range_compliance(50, 10, 100) == True
        assert verify_range_compliance(0.5, 0.5, 0.9) == True  # Edge case: min boundary
        assert verify_range_compliance(0.9, 0.5, 0.9) == True  # Edge case: max boundary
        
    def test_value_outside_range(self):
        """Test values that fall outside the specified range."""
        assert verify_range_compliance(0.95, 0.5, 0.9) == False  # Above max
        assert verify_range_compliance(0.4, 0.5, 0.9) == False   # Below min
        assert verify_range_compliance(150, 10, 100) == False    # Above max (int)
        assert verify_range_compliance(5, 10, 100) == False      # Below min (int)
        
    def test_range_with_floats(self):
        """Test range compliance with floating point values."""
        assert verify_range_compliance(2.5, 1.0, 5.0) == True
        assert verify_range_compliance(0.1, 1.0, 5.0) == False
        assert verify_range_compliance(6.0, 1.0, 5.0) == False
        
    def test_range_with_mixed_types(self):
        """Test range compliance with mixed integer and float types."""
        assert verify_range_compliance(5, 1.0, 10.0) == True
        assert verify_range_compliance(5.5, 1, 10) == True
        assert verify_range_compliance(0.5, 1, 10) == False


class TestIntegrationScenarios:
    """Integration tests for compliance verification scenarios."""
    
    def test_bias_threshold_scenario(self):
        """Test a bias detection threshold scenario."""
        # Scenario: bias score should be <= 0.2 (20%)
        bias_threshold = 0.2
        
        # Compliant cases
        assert verify_threshold(0.15, bias_threshold, '<=') == True
        assert verify_threshold(0.0, bias_threshold, '<=') == True
        assert verify_threshold(0.2, bias_threshold, '<=') == True
        
        # Non-compliant cases
        assert verify_threshold(0.25, bias_threshold, '<=') == False
        assert verify_threshold(0.5, bias_threshold, '<=') == False
        
    def test_fairness_range_scenario(self):
        """Test a fairness metric range scenario."""
        # Scenario: fairness score should be between 0.4 and 0.6 (±10% from 0.5)
        min_fairness = 0.4
        max_fairness = 0.6
        
        # Compliant cases
        assert verify_range_compliance(0.5, min_fairness, max_fairness) == True
        assert verify_range_compliance(0.45, min_fairness, max_fairness) == True
        assert verify_range_compliance(0.55, min_fairness, max_fairness) == True
        
        # Non-compliant cases
        assert verify_range_compliance(0.35, min_fairness, max_fairness) == False
        assert verify_range_compliance(0.65, min_fairness, max_fairness) == False


if __name__ == "__main__":
    # Run tests if this file is executed directly
    pytest.main([__file__, "-v"])