"""
Test suite for British Airways Customer Service Responsiveness Bias Audit execution.

This module tests the overall audit execution flow, including initialization,
probe generation, ethical review, and the complete audit process.
"""

import unittest
from unittest.mock import patch, MagicMock
import time
from datetime import datetime

# Import the audit class and related modules
from src.audits.ba_customer_service.audit import BACustomerServiceAudit
from src.audits.ba_customer_service.probe_generation import Probe
from src.audits.ba_customer_service.response_analysis import Response


class TestAuditExecution(unittest.TestCase):
    """Test cases for audit execution."""
    
    def setUp(self):
        """Set up test fixtures."""
        # Create a mock config
        self.config = {
            "test_mode": True,
            "max_probes": 10
        }
        
        # Patch the compatibility version
        self.compatibility_patcher = patch('src.audits.ba_customer_service.audit.compatibility_version', 1.2)
        self.mock_compatibility = self.compatibility_patcher.start()
        
        # Patch the ethical_review_hook
        self.ethical_hook_patcher = patch('src.audits.ba_customer_service.audit.ethical_review_hook')
        self.mock_ethical_hook = self.ethical_hook_patcher.start()
        
        # Patch the rate_limiter decorator to be a no-op
        self.rate_limiter_patcher = patch('src.audits.ba_customer_service.audit.rate_limiter', lambda **kwargs: lambda f: f)
        self.mock_rate_limiter = self.rate_limiter_patcher.start()
        
        # Create the audit instance
        self.audit = BACustomerServiceAudit(self.config)
    
    def tearDown(self):
        """Tear down test fixtures."""
        self.compatibility_patcher.stop()
        self.ethical_hook_patcher.stop()
        self.rate_limiter_patcher.stop()
    
    def test_initialization(self):
        """Test that the audit initializes correctly."""
        self.assertIsInstance(self.audit, BACustomerServiceAudit)
        self.assertEqual(self.audit.config, self.config)
        self.assertEqual(len(self.audit.probes), 0)
        self.assertEqual(len(self.audit.responses), 0)
        self.assertIsNone(self.audit.results)
    
    @patch('src.audits.ba_customer_service.audit.generate_probe_batch')
    def test_generate_probes(self, mock_generate_batch):
        """Test probe generation."""
        # Create mock probe pairs
        mock_probes = [
            (
                Probe(
                    probe_id="test1_western",
                    variation="western",
                    name="James Wilson",
                    content="Test content",
                    timestamp=time.time(),
                    metadata={"variation": "western"}
                ),
                Probe(
                    probe_id="test1_non_western",
                    variation="non_western",
                    name="Mohammed Ahmed",
                    content="Test content",
                    timestamp=time.time(),
                    metadata={"variation": "non_western"}
                )
            ),
            (
                Probe(
                    probe_id="test2_western",
                    variation="western",
                    name="Emma Thompson",
                    content="Test content",
                    timestamp=time.time(),
                    metadata={"variation": "western"}
                ),
                Probe(
                    probe_id="test2_non_western",
                    variation="non_western",
                    name="Aisha Khan",
                    content="Test content",
                    timestamp=time.time(),
                    metadata={"variation": "non_western"}
                )
            )
        ]
        
        # Configure the mock to return our test probe pairs
        mock_generate_batch.return_value = mock_probes
        
        # Call the method
        probes = self.audit.generate_probes(2)
        
        # Verify the results
        self.assertEqual(len(probes), 4)  # 2 pairs = 4 probes
        self.assertEqual(len([p for p in probes if p.variation == "western"]), 2)
        self.assertEqual(len([p for p in probes if p.variation == "non_western"]), 2)
        
        # Verify that the ethical review hook was called
        self.mock_ethical_hook.assert_called_once()
    
    @patch('src.audits.ba_customer_service.audit.BACustomerServiceAudit.generate_probes')
    @patch('src.audits.ba_customer_service.audit.BACustomerServiceAudit.submit_probes')
    @patch('src.audits.ba_customer_service.audit.BACustomerServiceAudit.collect_responses')
    @patch('src.audits.ba_customer_service.audit.BACustomerServiceAudit.analyze_results')
    def test_run_audit(self, mock_analyze, mock_collect, mock_submit, mock_generate):
        """Test the complete audit execution flow."""
        # Configure mocks
        mock_probes = [MagicMock() for _ in range(4)]
        mock_responses = [MagicMock() for _ in range(4)]
        mock_results = {"bias_detected": False, "metrics": {}}
        
        mock_generate.return_value = mock_probes
        mock_collect.return_value = mock_responses
        mock_analyze.return_value = mock_results
        
        # Run the audit
        results = self.audit.run_audit(2)
        
        # Verify that all methods were called
        mock_generate.assert_called_once_with(2)
        mock_submit.assert_called_once_with(mock_probes)
        mock_collect.assert_called_once()
        mock_analyze.assert_called_once()
        
        # Verify results
        self.assertEqual(results, mock_results)
    
    def test_power_analysis(self):
        """Test power analysis calculation."""
        power_analysis = self.audit.get_power_analysis()
        
        # Verify that the power analysis contains the expected keys
        self.assertIn("effect_size", power_analysis)
        self.assertIn("power", power_analysis)
        self.assertIn("alpha", power_analysis)
        self.assertIn("min_sample_size_per_group", power_analysis)
        self.assertIn("total_probes_needed", power_analysis)
        
        # Verify that the total probes needed is twice the min sample size per group
        self.assertEqual(
            power_analysis["total_probes_needed"],
            power_analysis["min_sample_size_per_group"] * 2
        )


class TestEthicalReview(unittest.TestCase):
    """Test cases for ethical review functionality."""
    
    def setUp(self):
        """Set up test fixtures."""
        # Patch the ethical_review_hook
        self.ethical_hook_patcher = patch('src.audits.ba_customer_service.probe_generation.ethical_review_hook')
        self.mock_ethical_hook = self.ethical_hook_patcher.start()
        
        # Patch the fake_data_helper
        self.fake_data_patcher = patch('src.audits.ba_customer_service.probe_generation.fake_data_helper')
        self.mock_fake_data = self.fake_data_patcher.start()
        self.mock_fake_data.is_synthetic_name.return_value = True
        
        # Import the function after patching
        from src.audits.ba_customer_service.probe_generation import ethical_review_variations
        self.ethical_review_variations = ethical_review_variations
    
    def tearDown(self):
        """Tear down test fixtures."""
        self.ethical_hook_patcher.stop()
        self.fake_data_patcher.stop()
    
    def test_ethical_review_valid_variations(self):
        """Test that valid variations pass ethical review."""
        variations = {
            "western": {
                "description": "Western-sounding names",
                "examples": ["James Wilson", "Emma Thompson"]
            },
            "non_western": {
                "description": "Non-Western-sounding names",
                "examples": ["Mohammed Ahmed", "Aisha Khan"]
            }
        }
        
        # Should not raise an exception
        result = self.ethical_review_variations(variations)
        self.assertTrue(result)
    
    def test_ethical_review_unbalanced_variations(self):
        """Test that unbalanced variations fail ethical review."""
        variations = {
            "western": {
                "description": "Western-sounding names",
                "examples": ["James Wilson", "Emma Thompson"]
            },
            "non_western": {
                "description": "Non-Western-sounding names",
                "examples": ["Mohammed Ahmed"]  # Only one example
            }
        }
        
        # Should raise a ValueError
        with self.assertRaises(ValueError):
            self.ethical_review_variations(variations)
    
    def test_ethical_review_non_synthetic_names(self):
        """Test that variations with non-synthetic names fail ethical review."""
        # Configure the mock to return False for one name
        self.mock_fake_data.is_synthetic_name.side_effect = lambda name: name != "Real Person"
        
        variations = {
            "western": {
                "description": "Western-sounding names",
                "examples": ["James Wilson", "Real Person"]  # One real name
            },
            "non_western": {
                "description": "Non-Western-sounding names",
                "examples": ["Mohammed Ahmed", "Aisha Khan"]
            }
        }
        
        # Should raise a ValueError
        with self.assertRaises(ValueError):
            self.ethical_review_variations(variations)


if __name__ == '__main__':
    unittest.main()