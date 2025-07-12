"""
Tests for response analysis in the British Airways Customer Service Audit
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


class TestBACustomerServiceAuditResponseAnalysis(unittest.TestCase):
    """Test cases for response analysis in the British Airways Customer Service Audit"""
    
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
        
    def test_analyze_response(self):
        """Test that responses are analyzed correctly"""
        # Create a test probe
        probe = {
            'id': 'test-probe-123',
            'variation': 'majority',
            'timestamp': datetime.now().isoformat()
        }
        
        # Create a test response
        response = {
            'text': 'Thank you for your inquiry. We are happy to help you with your question.',
            'timestamp': (datetime.now() + timedelta(hours=2)).isoformat()
        }
        
        # Analyze the response
        result = self.audit.analyze_response(response, probe)
        
        # Check that the result has the expected fields
        self.assertEqual(result['probe_id'], 'test-probe-123')
        self.assertEqual(result['variation'], 'majority')
        self.assertTrue(result['response_received'])
        self.assertIsNotNone(result['response_time_hours'])
        self.assertIsNotNone(result['sentiment_score'])
        
        # Check that the response time is approximately 2 hours
        self.assertAlmostEqual(result['response_time_hours'], 2.0, delta=0.1)
        
        # Check that the sentiment score is positive (> 0.5) for a positive response
        self.assertGreater(result['sentiment_score'], 0.5)
        
        # Check that the response text is not included in the result
        self.assertNotIn('text', result)
        
    def test_calculate_response_time(self):
        """Test that response time calculation works correctly"""
        # Create timestamps 3 hours apart
        probe_time = datetime.now().isoformat()
        response_time = (datetime.now() + timedelta(hours=3)).isoformat()
        
        # Calculate response time
        hours = self.audit._calculate_response_time(probe_time, response_time)
        
        # Should be approximately 3 hours
        self.assertAlmostEqual(hours, 3.0, delta=0.1)
        
        # Test with invalid timestamps
        self.assertIsNone(self.audit._calculate_response_time("invalid", response_time))
        self.assertIsNone(self.audit._calculate_response_time(probe_time, "invalid"))
        
    def test_analyze_sentiment(self):
        """Test that sentiment analysis works correctly"""
        # Positive text should have score > 0.5
        positive_text = "Thank you for your inquiry. We are happy to help you with your question."
        positive_score = self.audit._analyze_sentiment(positive_text)
        self.assertGreater(positive_score, 0.5)
        
        # Negative text should have score < 0.5
        negative_text = "Unfortunately, we cannot assist with your request. We regret the inconvenience."
        negative_score = self.audit._analyze_sentiment(negative_text)
        self.assertLess(negative_score, 0.5)
        
        # Neutral text should have score = 0.5
        neutral_text = "Your request has been received. A representative will contact you."
        neutral_score = self.audit._analyze_sentiment(neutral_text)
        self.assertEqual(neutral_score, 0.5)


if __name__ == '__main__':
    unittest.main()
