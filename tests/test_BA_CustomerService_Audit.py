"""
Tests for British Airways Customer Service Responsiveness Bias Audit
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


class TestBACustomerServiceAudit(unittest.TestCase):
    """Test cases for the British Airways Customer Service Audit"""
    
    def setUp(self):
        """Set up test fixtures"""
        # Create a mock for CorrespondenceAudit parent class
        # The import path for CorrespondenceAudit might need adjustment depending on its actual location
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
        self.assertEqual(self.audit.MIN_PROBES, 100)
        self.assertEqual(self.audit.compatibility_version, 1.2)
        self.assertIn('majority', self.audit.VARIATIONS)
        self.assertIn('minority', self.audit.VARIATIONS)
        
    def test_ethical_review_hook(self):
        """Test that the ethical review hook works correctly"""
        # Valid variations should pass
        valid_variations = {
            'test1': {'name_origin': 'british', 'demographic': 'perceived_majority'},
            'test2': {'name_origin': 'middle_eastern', 'demographic': 'perceived_minority'}
        }
        self.assertTrue(self.audit.ethical_review_hook(valid_variations))
        
        # Invalid variations should fail
        invalid_variations = {
            'test1': {'demographic': 'perceived_majority'},  # Missing name_origin
            'test2': {'name_origin': 'middle_eastern', 'demographic': 'perceived_minority'}
        }
        self.assertFalse(self.audit.ethical_review_hook(invalid_variations))
        
        # Variations with real PII should fail
        pii_variations = {
            'test1': {'name_origin': 'british', 'demographic': 'perceived_majority', 'real_email': 'test@example.com'},
            'test2': {'name_origin': 'middle_eastern', 'demographic': 'perceived_minority'}
        }
        self.assertFalse(self.audit.ethical_review_hook(pii_variations))
        
        # Invalid demographics should fail
        invalid_demo_variations = {
            'test1': {'name_origin': 'british', 'demographic': 'invalid_demo'},
            'test2': {'name_origin': 'middle_eastern', 'demographic': 'perceived_minority'}
        }
        self.assertFalse(self.audit.ethical_review_hook(invalid_demo_variations))
        
    def test_generate_future_date(self):
        """Test that future dates are generated correctly"""
        # Define a fixed datetime to patch datetime.now()
        fixed_now = datetime(2025, 7, 12, 10, 0, 0) # July 12, 2025, 10:00:00

        with patch('BA_CustomerService_Audit.datetime') as mock_datetime:
            mock_datetime.now.return_value = fixed_now
            mock_datetime.fromisoformat = datetime.fromisoformat # Keep original fromisoformat
            mock_datetime.strptime = datetime.strptime # Keep original strptime
            mock_datetime.timedelta = timedelta # Keep original timedelta

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
        
    def test_run_audit(self):
        """Test that the complete audit process runs correctly"""
        # Mock the generate_probes method to return a known set of probes
        probes_to_return = [
            {'id': 'ba-majority-1', 'variation': 'majority', 'timestamp': datetime.now().isoformat()},
            {'id': 'ba-minority-1', 'variation': 'minority', 'timestamp': datetime.now().isoformat()},
            {'id': 'ba-majority-2', 'variation': 'majority', 'timestamp': datetime.now().isoformat()},
            {'id': 'ba-minority-2', 'variation': 'minority', 'timestamp': datetime.now().isoformat()},
        ]
        with patch.object(self.audit, 'generate_probes', return_value=probes_to_return) as mock_generate,
             patch.object(self.audit, '_simulate_response_collection') as mock_simulate:

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