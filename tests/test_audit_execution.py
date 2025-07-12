"""
Unit tests for the BA Customer Service Audit execution.
"""

import unittest
from datetime import datetime
from unittest.mock import patch, MagicMock, call

from src.audits.ba_customer_service.audit import BACustomerServiceAudit


class TestBACustomerServiceAudit(unittest.TestCase):
    """Test cases for the BACustomerServiceAudit class."""
    
    def setUp(self):
        """Set up test fixtures."""
        # Patch the ethical_review_hook to avoid actual validation during tests
        self.ethical_review_patcher = patch('src.audits.ba_customer_service.audit.ethical_review_hook')
        self.mock_ethical_review = self.ethical_review_patcher.start()
        self.mock_ethical_review.return_value = True
        
        # Create audit instance
        self.audit = BACustomerServiceAudit(seed=42)
    
    def tearDown(self):
        """Clean up after tests."""
        self.ethical_review_patcher.stop()
    
    def test_initialization(self):
        """Test audit initialization."""
        self.assertEqual(self.audit.seed, 42)
        self.assertIsNotNone(self.audit.audit_id)
        self.assertIsInstance(self.audit.start_time, datetime)
        self.assertEqual(self.audit.compatibility_version, 1.2)
        
        # Verify ethical review was called
        self.mock_ethical_review.assert_called_once_with(self.audit.VARIATIONS)
    
    @patch('src.audits.ba_customer_service.audit.generate_probes')
    def test_generate_probes(self, mock_generate_probes):
        """Test probe generation."""
        # Set up mock
        mock_probes = [{"id": f"probe{i}"} for i in range(10)]
        mock_generate_probes.return_value = mock_probes
        
        # Call method
        probes = self.audit.generate_probes(10)
        
        # Verify results
        self.assertEqual(probes, mock_probes)
        mock_generate_probes.assert_called_once_with(10, 42)
    
    @patch('src.audits.ba_customer_service.audit.random')
    def test_collect_responses(self, mock_random):
        """Test response collection."""
        # Set up mock
        mock_random.random.side_effect = [0.7, 0.9, 0.5, 0.3]  # First and third will get responses
        mock_random.uniform.side_effect = [30, 40]  # Response times
        
        # Create sample probes
        probes = [
            {
                "id": "probe1",
                "group": "group_a",
                "name": "James Wilson",
                "email": "james.wilson@example.com",
                "inquiry_type": "booking information",
                "timestamp": datetime.now().isoformat()
            },
            {
                "id": "probe2",
                "group": "group_b",
                "name": "Mohammed Ahmed",
                "email": "mohammed.ahmed@example.com",
                "inquiry_type": "baggage allowance",
                "timestamp": datetime.now().isoformat()
            }
        ]
        
        # Call method
        responses = self.audit.collect_responses(probes)
        
        # Verify results
        self.assertEqual(len(responses), 2)
        self.assertTrue(responses[0]["received_response"])
        self.assertFalse(responses[1]["received_response"])
        self.assertEqual(responses[0]["probe_id"], "probe1")
        self.assertEqual(responses[1]["probe_id"], "probe2")
        self.assertIn("response_timestamp", responses[0])
        self.assertNotIn("response_timestamp", responses[1])
    
    @patch('src.audits.ba_customer_service.audit.analyze_responses')
    def test_analyze_results(self, mock_analyze_responses):
        """Test results analysis."""
        # Set up mock
        mock_result = MagicMock()
        mock_result.overall_biased = True
        mock_result.bias_results = [
            MagicMock(metric_name="response_rate", is_biased=True, difference=0.3, threshold=0.15)
        ]
        mock_analyze_responses.return_value = mock_result
        
        # Create sample responses
        responses = [{"id": f"resp{i}"} for i in range(10)]
        
        # Call method
        result = self.audit.analyze_results(responses)
        
        # Verify results
        self.assertEqual(result, mock_result)
        mock_analyze_responses.assert_called_once_with(responses)
    
    @patch.object(BACustomerServiceAudit, 'generate_probes')
    @patch.object(BACustomerServiceAudit, 'collect_responses')
    @patch.object(BACustomerServiceAudit, 'analyze_results')
    def test_run_audit(self, mock_analyze, mock_collect, mock_generate):
        """Test the complete audit process."""
        # Set up mocks
        mock_probes = [{"id": f"probe{i}"} for i in range(10)]
        mock_responses = [{"id": f"resp{i}"} for i in range(10)]
        mock_result = MagicMock()
        mock_result.overall_biased = True
        mock_result.group_a_metrics = MagicMock(sample_size=5, response_rate=0.8)
        mock_result.group_b_metrics = MagicMock(sample_size=5, response_rate=0.4)
        mock_result.bias_results = [
            MagicMock(
                metric_name="response_rate", 
                group_a_value=0.8, 
                group_b_value=0.4,
                difference=0.4, 
                threshold=0.15, 
                is_biased=True, 
                p_value=0.01
            )
        ]
        
        mock_generate.return_value = mock_probes
        mock_collect.return_value = mock_responses
        mock_analyze.return_value = mock_result
        
        # Call method
        report = self.audit.run_audit(10, 7)
        
        # Verify results
        self.assertIsInstance(report, dict)
        self.assertEqual(report["probe_count"], 10)
        self.assertEqual(report["response_count"], 10)
        self.assertTrue(report["overall_biased"])
        self.assertEqual(len(report["bias_results"]), 1)
        self.assertEqual(report["bias_results"][0]["metric"], "response_rate")
        self.assertTrue(report["bias_results"][0]["is_biased"])
        
        # Verify method calls
        mock_generate.assert_called_once_with(10)
        mock_collect.assert_called_once_with(mock_probes, 7)
        mock_analyze.assert_called_once_with(mock_responses)
    
    @patch('builtins.open', new_callable=unittest.mock.mock_open)
    @patch('json.dump')
    def test_save_report(self, mock_json_dump, mock_open):
        """Test report saving."""
        # Create sample report
        report = {"audit_id": "test_id", "overall_biased": True}
        
        # Call method
        self.audit.save_report(report, "test_report.json")
        
        # Verify results
        mock_open.assert_called_once_with("test_report.json", 'w')
        mock_json_dump.assert_called_once()
        args, kwargs = mock_json_dump.call_args
        self.assertEqual(args[0], report)
        self.assertEqual(kwargs["indent"], 2)


if __name__ == '__main__':
    unittest.main()