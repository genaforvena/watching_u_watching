"""
Tests for initialization of the British Airways Customer Service Audit
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
from ba_customer_service.audit import BACustomerServiceAudit


class TestBACustomerServiceAuditInitialization(unittest.TestCase):
    """Test cases for the initialization of the British Airways Customer Service Audit"""
    
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
        
    def test_initialization(self):
        """Test that the audit initializes correctly"""
        from audits.ba_customer_service.constants import MIN_PROBES, VARIATIONS
        self.assertEqual(MIN_PROBES, 100)
        self.assertEqual(self.audit.compatibility_version, 1.2)
        self.assertIn('majority', VARIATIONS)
        self.assertIn('minority', VARIATIONS)
        self.assertIn('minority', VARIATIONS)
        self.assertIn('minority', VARIATIONS)
        self.assertIn('minority', VARIATIONS)


if __name__ == '__main__':
    unittest.main()
