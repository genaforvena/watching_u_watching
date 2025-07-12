"""
Tests for metrics calculation in the British Airways Customer Service Audit
"""

import unittest
import sys
from unittest.mock import patch, MagicMock
from datetime import datetime, timedelta
import random
import os
from pathlib import Path

# Add src directory to path for imports
sys.path.insert(0, str(Path(__file__).parent.parent / 'src'))
sys.path.insert(0, str(Path(__file__).parent.parent / 'src/audits'))

# Mock the imports that might not exist in the test environment
sys.modules['fake_data_helper'] = MagicMock()
sys.modules['rate_limiter'] = MagicMock()

# Import the module after mocking dependencies
from audits.ba_customer_service.audit import BACustomerServiceAudit


class TestBACustomerServiceAuditMetricsCalculation(unittest.TestCase):
    """Test cases for metrics calculation in the British Airways Customer Service Audit"""
    
    def setUp(self):
        """Set up test fixtures"""
        # Create a mock for CorrespondenceAudit parent class
        with patch('audits.ba_customer_service.audit.CorrespondenceAudit'):
            self.audit = BACustomerServiceAudit()
            
        # Mock the fake_data_helper functions
        sys.modules['fake_data_helper'].generate_synthetic_name.side_effect = lambda origin: (
            "John Smith" if origin == "british" else "Mohammed Al-Farsi"
        )
        sys.modules['fake_data_helper'].generate_fake_email.side_effect = lambda name: (
            f"{name.lower().replace(' ', '.')}@example.com"
        )
        
        # Mock the rate_limiter decorator to do nothing in tests
        sys.modules['rate_limiter'].rate_limiter = lambda requests, period: lambda f: f
        
    def test_calculate_metrics(self):
        """Test that metrics calculation works correctly"""
        # Set up some test results
        self.audit.results = {
            'majority': {
                'responses': 80,
                'response_times': [2.5, 3.0, 1.5, 2.0],
                'sentiment_scores': [0.8, 0.7, 0.9, 0.6],
                'non_responses': 20
            },
            'minority': {
                'responses': 70,
                'response_times': [4.0, 3.5, 5.0, 4.5],
                'sentiment_scores': [0.5, 0.4, 0.6, 0.3],
                'non_responses': 30
            }
        }
        
        # Calculate metrics
        metrics = self.audit.calculate_metrics()
        
        # Check response rates
        self.assertEqual(metrics['response_rates']['majority'], 0.8)  # 80/100
        self.assertEqual(metrics['response_rates']['minority'], 0.7)  # 70/100
        
        # Check average response times
        self.assertEqual(metrics['avg_response_times']['majority'], 2.25)  # (2.5+3.0+1.5+2.0)/4
        self.assertEqual(metrics['avg_response_times']['minority'], 4.25)  # (4.0+3.5+5.0+4.5)/4
        
        # Check average sentiment scores
        self.assertEqual(metrics['avg_sentiment_scores']['majority'], 0.75)  # (0.8+0.7+0.9+0.6)/4
        self.assertEqual(metrics['avg_sentiment_scores']['minority'], 0.45)  # (0.5+0.4+0.6+0.3)/4
        
        # Check bias metrics
        self.assertEqual(metrics['bias_metrics']['response_rate_diff'], 0.1)  # 0.8-0.7
        self.assertEqual(metrics['bias_metrics']['response_time_diff'], 2.0)  # 4.25-2.25
        self.assertEqual(metrics['bias_metrics']['sentiment_diff'], 0.3)  # 0.75-0.45
        
        # Check significant bias flag
        self.assertTrue(metrics['bias_metrics']['significant_bias'])


if __name__ == '__main__':
    unittest.main()
