"""
Unit tests for the response analysis module.
"""

import unittest
from datetime import datetime, timedelta
from unittest.mock import patch, MagicMock

from src.audits.ba_customer_service.response_analysis import (
    ResponseAnalyzer,
    ResponseMetrics,
    BiasResult,
    AuditResult,
    analyze_responses
)


class TestResponseAnalyzer(unittest.TestCase):
    """Test cases for the ResponseAnalyzer class."""
    
    def setUp(self):
        """Set up test fixtures."""
        self.analyzer = ResponseAnalyzer()
        
        # Sample responses for testing
        self.sample_responses = [
            # Group A responses
            {
                "id": "resp1",
                "probe_id": "probe1",
                "group": "group_a",
                "name": "James Wilson",
                "email": "james.wilson@example.com",
                "inquiry_type": "booking information",
                "timestamp": "2023-01-01T10:00:00",
                "received_response": True,
                "response_timestamp": "2023-01-02T14:00:00",
                "response_text": "Thank you for your inquiry. We're happy to assist you with your request."
            },
            {
                "id": "resp2",
                "probe_id": "probe2",
                "group": "group_a",
                "name": "Emma Thompson",
                "email": "emma.thompson@example.com",
                "inquiry_type": "baggage allowance",
                "timestamp": "2023-01-01T11:00:00",
                "received_response": True,
                "response_timestamp": "2023-01-02T16:00:00",
                "response_text": "We appreciate your interest in British Airways and look forward to welcoming you onboard."
            },
            {
                "id": "resp3",
                "probe_id": "probe3",
                "group": "group_a",
                "name": "William Parker",
                "email": "william.parker@example.com",
                "inquiry_type": "special assistance",
                "timestamp": "2023-01-01T12:00:00",
                "received_response": False
            },
            
            # Group B responses
            {
                "id": "resp4",
                "probe_id": "probe4",
                "group": "group_b",
                "name": "Mohammed Ahmed",
                "email": "mohammed.ahmed@example.com",
                "inquiry_type": "booking information",
                "timestamp": "2023-01-01T10:30:00",
                "received_response": True,
                "response_timestamp": "2023-01-03T10:30:00",
                "response_text": "Thank you for contacting us. We have received your inquiry."
            },
            {
                "id": "resp5",
                "probe_id": "probe5",
                "group": "group_b",
                "name": "Fatima Khan",
                "email": "fatima.khan@example.com",
                "inquiry_type": "baggage allowance",
                "timestamp": "2023-01-01T11:30:00",
                "received_response": False
            },
            {
                "id": "resp6",
                "probe_id": "probe6",
                "group": "group_b",
                "name": "Raj Patel",
                "email": "raj.patel@example.com",
                "inquiry_type": "special assistance",
                "timestamp": "2023-01-01T12:30:00",
                "received_response": False
            }
        ]
    
    def test_calculate_response_rate(self):
        """Test calculation of response rate."""
        # Group A: 2 out of 3 responded
        group_a_responses = [r for r in self.sample_responses if r["group"] == "group_a"]
        self.assertAlmostEqual(self.analyzer.calculate_response_rate(group_a_responses), 2/3)
        
        # Group B: 1 out of 3 responded
        group_b_responses = [r for r in self.sample_responses if r["group"] == "group_b"]
        self.assertAlmostEqual(self.analyzer.calculate_response_rate(group_b_responses), 1/3)
        
        # Empty list should return 0
        self.assertEqual(self.analyzer.calculate_response_rate([]), 0.0)
    
    def test_calculate_average_response_time(self):
        """Test calculation of average response time."""
        # Group A: Two responses with specific times
        group_a_responses = [r for r in self.sample_responses if r["group"] == "group_a"]
        
        # Calculate expected time differences in seconds
        time1 = (datetime.fromisoformat("2023-01-02T14:00:00") - 
                datetime.fromisoformat("2023-01-01T10:00:00")).total_seconds()
        time2 = (datetime.fromisoformat("2023-01-02T16:00:00") - 
                datetime.fromisoformat("2023-01-01T11:00:00")).total_seconds()
        expected_avg = (time1 + time2) / 2
        
        self.assertAlmostEqual(self.analyzer.calculate_average_response_time(group_a_responses), expected_avg)
        
        # Group B: One response
        group_b_responses = [r for r in self.sample_responses if r["group"] == "group_b"]
        
        # Calculate expected time difference in seconds
        time3 = (datetime.fromisoformat("2023-01-03T10:30:00") - 
                datetime.fromisoformat("2023-01-01T10:30:00")).total_seconds()
        
        self.assertAlmostEqual(self.analyzer.calculate_average_response_time(group_b_responses), time3)
        
        # No responses should return -1
        no_responses = [r for r in self.sample_responses if r["group"] == "group_b" and not r["received_response"]]
        self.assertEqual(self.analyzer.calculate_average_response_time(no_responses), -1.0)
    
    def test_analyze_sentiment(self):
        """Test sentiment analysis."""
        # Positive text
        positive_text = "Thank you for your inquiry. We're happy to assist you with your request. " + \
                       "We appreciate your interest and look forward to helping you."
        self.assertGreater(self.analyzer.analyze_sentiment(positive_text), 0)
        
        # Negative text
        negative_text = "Unfortunately, we cannot process your request at this time. " + \
                       "We apologize for the inconvenience and regret any problems this may cause."
        self.assertLess(self.analyzer.analyze_sentiment(negative_text), 0)
        
        # Neutral text
        neutral_text = "Your request has been received. A representative will contact you."
        self.assertEqual(self.analyzer.analyze_sentiment(neutral_text), 0.0)
    
    def test_calculate_average_sentiment(self):
        """Test calculation of average sentiment."""
        # Group A responses
        group_a_responses = [r for r in self.sample_responses if r["group"] == "group_a"]
        self.assertGreater(self.analyzer.calculate_average_sentiment(group_a_responses), 0)
        
        # Group B responses
        group_b_responses = [r for r in self.sample_responses if r["group"] == "group_b"]
        sentiment = self.analyzer.calculate_average_sentiment(group_b_responses)
        self.assertIsInstance(sentiment, float)
        
        # No responses should return 0
        no_responses = [r for r in self.sample_responses if not r.get("received_response", False)]
        self.assertEqual(self.analyzer.calculate_average_sentiment(no_responses), 0.0)
    
    def test_calculate_confidence_interval(self):
        """Test calculation of confidence intervals."""
        # Test with typical values
        ci = self.analyzer.calculate_confidence_interval(0.7, 100)
        self.assertIsInstance(ci, tuple)
        self.assertEqual(len(ci), 2)
        self.assertLess(ci[0], 0.7)
        self.assertGreater(ci[1], 0.7)
        
        # Test with edge cases
        self.assertEqual(self.analyzer.calculate_confidence_interval(0.5, 0), (0.0, 0.0))
        self.assertEqual(self.analyzer.calculate_confidence_interval(0.0, 100)[0], 0.0)
        self.assertEqual(self.analyzer.calculate_confidence_interval(1.0, 100)[1], 1.0)
    
    def test_calculate_p_value(self):
        """Test calculation of p-values."""
        # Test with significant difference
        p_value = self.analyzer.calculate_p_value(0.8, 0.4, 100, 100)
        self.assertLess(p_value, 0.05)
        
        # Test with no difference
        p_value = self.analyzer.calculate_p_value(0.5, 0.5, 100, 100)
        self.assertGreater(p_value, 0.05)
        
        # Test edge cases
        self.assertEqual(self.analyzer.calculate_p_value(0.5, 0.5, 0, 100), 1.0)
        self.assertEqual(self.analyzer.calculate_p_value(0.5, 0.5, 100, 0), 1.0)
    
    def test_compute_metrics(self):
        """Test computation of metrics for a group."""
        # Group A metrics
        metrics_a = self.analyzer.compute_metrics(self.sample_responses, "group_a")
        self.assertIsInstance(metrics_a, ResponseMetrics)
        self.assertAlmostEqual(metrics_a.response_rate, 2/3)
        self.assertGreater(metrics_a.avg_response_time, 0)
        
        # Group B metrics
        metrics_b = self.analyzer.compute_metrics(self.sample_responses, "group_b")
        self.assertIsInstance(metrics_b, ResponseMetrics)
        self.assertAlmostEqual(metrics_b.response_rate, 1/3)
        self.assertGreater(metrics_b.avg_response_time, 0)
        
        # Non-existent group
        metrics_none = self.analyzer.compute_metrics(self.sample_responses, "non_existent")
        self.assertIsInstance(metrics_none, ResponseMetrics)
        self.assertEqual(metrics_none.response_rate, 0.0)
        self.assertEqual(metrics_none.avg_response_time, -1.0)
    
    def test_detect_bias(self):
        """Test bias detection between groups."""
        # Create metrics with significant bias
        metrics_a = ResponseMetrics(
            response_rate=0.8,
            avg_response_time=24*3600,  # 24 hours in seconds
            sentiment_score=0.7,
            sample_size=100,
            confidence_interval=(0.75, 0.85)
        )
        
        metrics_b = ResponseMetrics(
            response_rate=0.5,
            avg_response_time=48*3600,  # 48 hours in seconds
            sentiment_score=0.3,
            sample_size=100,
            confidence_interval=(0.45, 0.55)
        )
        
        bias_results = self.analyzer.detect_bias(metrics_a, metrics_b)
        self.assertIsInstance(bias_results, list)
        self.assertTrue(any(result.is_biased for result in bias_results))
        
        # Create metrics with no bias
        metrics_a2 = ResponseMetrics(
            response_rate=0.75,
            avg_response_time=24*3600,
            sentiment_score=0.5,
            sample_size=100,
            confidence_interval=(0.7, 0.8)
        )
        
        metrics_b2 = ResponseMetrics(
            response_rate=0.7,
            avg_response_time=26*3600,
            sentiment_score=0.45,
            sample_size=100,
            confidence_interval=(0.65, 0.75)
        )
        
        bias_results2 = self.analyzer.detect_bias(metrics_a2, metrics_b2)
        self.assertIsInstance(bias_results2, list)
        # May or may not detect bias depending on thresholds
    
    def test_analyze_responses(self):
        """Test the complete response analysis process."""
        result = self.analyzer.analyze_responses(self.sample_responses)
        self.assertIsInstance(result, AuditResult)
        self.assertEqual(result.group_a_metrics.sample_size, 3)
        self.assertEqual(result.group_b_metrics.sample_size, 3)
        self.assertIsInstance(result.overall_biased, bool)
        self.assertIsInstance(result.bias_results, list)
    
    def test_convenience_function(self):
        """Test the convenience function for response analysis."""
        with patch('src.audits.ba_customer_service.response_analysis.ResponseAnalyzer') as MockAnalyzer:
            mock_instance = MockAnalyzer.return_value
            mock_instance.analyze_responses.return_value = "mock_result"
            
            result = analyze_responses(self.sample_responses)
            
            MockAnalyzer.assert_called_once()
            mock_instance.analyze_responses.assert_called_once_with(self.sample_responses)
            self.assertEqual(result, "mock_result")


if __name__ == '__main__':
    unittest.main()