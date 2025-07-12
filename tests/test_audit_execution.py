"""
Tests for the complete audit execution in the British Airways Customer Service Audit
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


class TestBACustomerServiceAuditExecution(unittest.TestCase):
    """Test cases for the complete audit execution in the British Airways Customer Service Audit"""
    
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
        
    def test_run_audit(self):
        """Test that the complete audit process runs correctly"""
        # Mock the generate_probes method to return a known set of probes
        probes_to_return = [
            {'id': 'ba-majority-1', 'variation': 'majority', 'timestamp': datetime.now().isoformat()},
            {'id': 'ba-minority-1', 'variation': 'minority', 'timestamp': datetime.now().isoformat()},
            {'id': 'ba-majority-2', 'variation': 'majority', 'timestamp': datetime.now().isoformat()},
            {'id': 'ba-minority-2', 'variation': 'minority', 'timestamp': datetime.now().isoformat()},
        ]
        with patch('audits.ba_customer_service.audit.generate_probes', return_value=probes_to_return) as mock_generate, \
             patch('audits.ba_customer_service.audit._simulate_response_collection') as mock_simulate:

            # Define simulated responses for the probes
            # Simulate 1 response for majority (2 hours, positive sentiment)
            # Simulate 0 responses for minority
            simulated_responses = [
                ({'timestamp': (datetime.now() + timedelta(hours=2)).isoformat(), 'text': 'Thank you!'}, probes_to_return[0]),
                (None, probes_to_return[1]), # No response for minority probe 1
                (None, probes_to_return[2]), # No response for majority probe 2
                (None, probes_to_return[3]), # No response for minority probe 2
            ]
            mock_simulate.return_value = simulated_responses

            # Run the audit with 2 pairs (which should result in 4 probes)
            result = self.audit.run_audit(2)

            # Check that generate_probes and _simulate_response_collection were called
            mock_generate.assert_called_once_with(2)
            mock_simulate.assert_called_once_with(probes_to_return)

            # Check the overall result structure
            self.assertEqual(result['probes_sent'], 4)
            self.assertIn('metrics', result)
            self.assertIn('timestamp', result)

            # Check the calculated metrics based on simulated responses
            metrics = result['metrics']

            # Expected metrics:
            # Majority: 1 response, 1 non-response. Total probes: 2. Response rate: 1/2 = 0.5
            #           Response times: [2.0]. Avg response time: 2.0
            #           Sentiment scores: [~1.0]. Avg sentiment score: ~1.0
            # Minority: 0 responses, 2 non-responses. Total probes: 2. Response rate: 0/2 = 0.0
            #           Response times: []. Avg response time: None
            #           Sentiment scores: []. Avg sentiment score: None

            self.assertAlmostEqual(metrics['response_rates']['majority'], 0.5)
            self.assertAlmostEqual(metrics['response_rates']['minority'], 0.0)

            self.assertAlmostEqual(metrics['avg_response_times']['majority'], 2.0, delta=0.1)
            self.assertIsNone(metrics['avg_response_times']['minority'])

            # The exact sentiment score depends on the placeholder logic, but it should be high for 'Thank you!'
            self.assertGreater(metrics['avg_sentiment_scores']['majority'], 0.5)
            self.assertIsNone(metrics['avg_sentiment_scores']['minority'])

            # Check bias metrics
            self.assertAlmostEqual(metrics['bias_metrics']['response_rate_diff'], 0.5) # 0.5 - 0.0
            # Response time diff is minority - majority, but minority is None, so this will be None
            self.assertIsNone(metrics['bias_metrics'].get('response_time_diff'))
            # Sentiment diff is majority - minority, but minority is None, so this will be None
            self.assertIsNone(metrics['bias_metrics'].get('sentiment_diff'))

            # Significant bias should be True because response rate diff > 0.1
            self.assertTrue(metrics['bias_metrics']['significant_bias'])


if __name__ == '__main__':
    unittest.main()
