"""
Tests for probe generation in the British Airways Customer Service Audit
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


class TestBACustomerServiceAuditProbeGeneration(unittest.TestCase):
    """Test cases for probe generation in the British Airways Customer Service Audit"""
    
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
        
    def test_generate_future_date(self):
        """Test that future dates are generated correctly"""
        # Define a fixed datetime to patch datetime.now()
        fixed_now = datetime(2025, 7, 12, 10, 0, 0) # July 12, 2025, 10:00:00

        # Patch only datetime.now()
        with patch('audits.ba_customer_service.probe_generation.datetime.now', return_value=fixed_now):
            future_date_str = self.audit._generate_future_date()

            self.assertIsInstance(future_date_str, str)

            # Parse the generated date string back into a datetime object
            # The format is "%d %B %Y" (e.g., "15 June 2023")
            generated_date = datetime.strptime(future_date_str, "%d %B %Y")

            # Calculate the expected minimum and maximum future dates
            min_future_date = fixed_now + timedelta(days=14)
            max_future_date = fixed_now + timedelta(days=56)

            # Assert that the generated date is within the expected range (inclusive)
            self.assertTrue(generated_date >= min_future_date.replace(hour=0, minute=0, second=0, microsecond=0))
            self.assertTrue(generated_date <= max_future_date.replace(hour=0, minute=0, second=0, microsecond=0))
        
    def test_generate_inquiry_content(self):
        """Test that inquiry content is generated correctly"""
        content = self.audit._generate_inquiry_content()
        
        self.assertIn('service_type', content)
        self.assertIn('inquiry_text', content)
        self.assertIn('origin', content)
        self.assertIn('destination', content)
        self.assertIn('date', content)
        
        # Check that the origin and destination are from the defined routes
        route_found = False
        for route in self.audit.FLIGHT_ROUTES:
            if content['origin'] == route['origin'] and content['destination'] == route['destination']:
                route_found = True
                break
        self.assertTrue(route_found, "Generated route not found in defined routes")
        
        # Check that the service type and inquiry text are from the defined inquiry types
        inquiry_found = False
        for inquiry in self.audit.INQUIRY_TYPES:
            if content['service_type'] == inquiry['service_type'] and content['inquiry_text'] == inquiry['inquiry_text']:
                inquiry_found = True
                break
        self.assertTrue(inquiry_found, "Generated inquiry not found in defined inquiry types")
        
    def test_generate_probes(self):
        """Test that probes are generated correctly"""
        # Mock the ethical_review_hook to always return True
        with patch.object(self.audit, 'ethical_review_hook', return_value=True):
            probes = self.audit.generate_probes(2)
            
            # Should generate 4 probes (2 pairs)
            self.assertEqual(len(probes), 4)
            
            # Check that we have probes for both variations
            variations = [probe['variation'] for probe in probes]
            self.assertIn('majority', variations)
            self.assertIn('minority', variations)
            
            # Check that the probes have the required fields
            required_fields = ['id', 'variation', 'demographic', 'name', 'email', 
                              'subject', 'body', 'timestamp', 'inquiry_type', 'route']
            for probe in probes:
                for field in required_fields:
                    self.assertIn(field, probe)
                    
            # Check that the names match the expected pattern
            for probe in probes:
                if probe['variation'] == 'majority':
                    self.assertEqual(probe['name'], "John Smith")
                elif probe['variation'] == 'minority':
                    self.assertEqual(probe['name'], "Mohammed Al-Farsi")
                    
    def test_ethical_review_failure(self):
        """Test that probe generation fails if ethical review fails"""
        # Mock the ethical_review_hook to return False
        with patch.object(self.audit, 'ethical_review_hook', return_value=False):
            with self.assertRaises(ValueError):
                self.audit.generate_probes(2)


if __name__ == '__main__':
    unittest.main()
