"""
Test suite for British Airways Customer Service Responsiveness Bias Audit response analysis.

This module tests the response analysis functionality, including response rate calculation,
response time analysis, sentiment analysis, and bias detection.
"""

import unittest
from unittest.mock import patch, MagicMock
import time
from datetime import datetime

# Import the response analysis module
from src.audits.ba_customer_service.response_analysis import (
    Response,
    calculate_response_rate,
    calculate_response_time_stats,
    calculate_sentiment_stats,
    analyze_response_text,
    process_response,
    detect_bias,
    calculate_minimum_sample_size,
    SentimentCategory
)


class TestResponseAnalysis(unittest.TestCase):
    """Test cases for response analysis functionality."""
    
    def setUp(self):
        """Set up test fixtures."""
        # Create sample responses
        self.responses = [
            # Western responses
            Response(
                probe_id="test1_western",
                received=True,
                timestamp=time.time(),
                response_time_hours=2.5,
                sentiment_score=0.6,
                sentiment_category=SentimentCategory.POSITIVE,
                metadata={"variation": "western", "name": "James Wilson"}
            ),
            Response(
                probe_id="test2_western",
                received=True,
                timestamp=time.time(),
                response_time_hours=1.8,
                sentiment_score=0.2,
                sentiment_category=SentimentCategory.POSITIVE,
                metadata={"variation": "western", "name": "Emma Thompson"}
            ),
            Response(
                probe_id="test3_western",
                received=False,
                metadata={"variation": "western", "name": "Robert Johnson"}
            ),
            
            # Non-western responses
            Response(
                probe_id="test1_non_western",
                received=True,
                timestamp=time.time(),
                response_time_hours=4.2,
                sentiment_score=0.3,
                sentiment_category=SentimentCategory.POSITIVE,
                metadata={"variation": "non_western", "name": "Mohammed Ahmed"}
            ),
            Response(
                probe_id="test2_non_western",
                received=False,
                metadata={"variation": "non_western", "name": "Aisha Khan"}
            ),
            Response(
                probe_id="test3_non_western",
                received=False,
                metadata={"variation": "non_western", "name": "Wei Zhang"}
            )
        ]
    
    def test_calculate_response_rate(self):
        """Test response rate calculation."""
        # Calculate response rates
        western_rate = calculate_response_rate(self.responses, "western")
        non_western_rate = calculate_response_rate(self.responses, "non_western")
        
        # Verify results
        self.assertEqual(western_rate, 2/3)  # 2 out of 3 western probes received responses
        self.assertEqual(non_western_rate, 1/3)  # 1 out of 3 non-western probes received responses
    
    def test_calculate_response_time_stats(self):
        """Test response time statistics calculation."""
        # Calculate response time stats
        western_stats = calculate_response_time_stats(self.responses, "western")
        non_western_stats = calculate_response_time_stats(self.responses, "non_western")
        
        # Verify western stats
        self.assertAlmostEqual(western_stats["mean"], 2.15)  # (2.5 + 1.8) / 2
        self.assertAlmostEqual(western_stats["median"], 2.15)  # (2.5 + 1.8) / 2
        self.assertAlmostEqual(western_stats["min"], 1.8)
        self.assertAlmostEqual(western_stats["max"], 2.5)
        
        # Verify non-western stats
        self.assertEqual(non_western_stats["mean"], 4.2)  # Only one response
        self.assertEqual(non_western_stats["median"], 4.2)  # Only one response
        self.assertEqual(non_western_stats["min"], 4.2)
        self.assertEqual(non_western_stats["max"], 4.2)
    
    def test_calculate_sentiment_stats(self):
        """Test sentiment statistics calculation."""
        # Calculate sentiment stats
        western_stats = calculate_sentiment_stats(self.responses, "western")
        non_western_stats = calculate_sentiment_stats(self.responses, "non_western")
        
        # Verify western stats
        self.assertAlmostEqual(western_stats["mean"], 0.4)  # (0.6 + 0.2) / 2
        self.assertAlmostEqual(western_stats["median"], 0.4)  # (0.6 + 0.2) / 2
        self.assertEqual(western_stats["category_counts"][SentimentCategory.POSITIVE.value], 2)
        
        # Verify non-western stats
        self.assertEqual(non_western_stats["mean"], 0.3)  # Only one response
        self.assertEqual(non_western_stats["median"], 0.3)  # Only one response
        self.assertEqual(non_western_stats["category_counts"][SentimentCategory.POSITIVE.value], 1)
    
    @patch('src.audits.ba_customer_service.response_analysis.sentiment_analyzer')
    def test_analyze_response_text(self, mock_sentiment_analyzer):
        """Test sentiment analysis of response text."""
        # Configure the mock
        mock_sentiment_analyzer.analyze.return_value = 0.7
        
        # Analyze a sample response
        score, category = analyze_response_text("Thank you for your inquiry. We're happy to help!")
        
        # Verify results
        self.assertEqual(score, 0.7)
        self.assertEqual(category, SentimentCategory.POSITIVE)
        
        # Verify that the sentiment analyzer was called
        mock_sentiment_analyzer.analyze.assert_called_once()
    
    @patch('src.audits.ba_customer_service.response_analysis.analyze_response_text')
    def test_process_response(self, mock_analyze):
        """Test response processing."""
        # Configure the mock
        mock_analyze.return_value = (0.5, SentimentCategory.POSITIVE)
        
        # Process a sample response
        probe_timestamp = time.time() - 3600  # 1 hour ago
        response = process_response(
            probe_id="test_probe",
            response_text="Thank you for your inquiry.",
            received_timestamp=time.time(),
            probe_metadata={
                "variation": "western",
                "name": "James Wilson",
                "timestamp": probe_timestamp
            }
        )
        
        # Verify results
        self.assertEqual(response.probe_id, "test_probe")
        self.assertTrue(response.received)
        self.assertAlmostEqual(response.response_time_hours, 1.0, delta=0.1)  # About 1 hour
        self.assertEqual(response.sentiment_score, 0.5)
        self.assertEqual(response.sentiment_category, SentimentCategory.POSITIVE)
        self.assertEqual(response.metadata["variation"], "western")
        self.assertEqual(response.metadata["name"], "James Wilson")
    
    @patch('src.audits.ba_customer_service.response_analysis.calculate_statistical_significance')
    def test_detect_bias(self, mock_significance):
        """Test bias detection."""
        # Configure the mock
        mock_significance.return_value = {
            "significant": True,
            "p_value": 0.03,
            "confidence_interval": (0.05, 0.35)
        }
        
        # Detect bias
        results = detect_bias(self.responses)
        
        # Verify results
        self.assertIn("bias_detected", results)
        self.assertIn("metrics", results)
        self.assertIn("response_rate", results["metrics"])
        self.assertIn("response_time", results["metrics"])
        self.assertIn("sentiment", results["metrics"])
        
        # Verify response rate metrics
        self.assertEqual(results["metrics"]["response_rate"]["western"], 2/3)
        self.assertEqual(results["metrics"]["response_rate"]["non_western"], 1/3)
        self.assertEqual(results["metrics"]["response_rate"]["difference"], 1/3)
        
        # Verify that statistical significance was calculated
        mock_significance.assert_called()
    
    def test_calculate_minimum_sample_size(self):
        """Test minimum sample size calculation."""
        # Calculate minimum sample size
        sample_size = calculate_minimum_sample_size(effect_size=0.15, power=0.8, alpha=0.05)
        
        # Verify that the result is a positive integer
        self.assertIsInstance(sample_size, int)
        self.assertGreater(sample_size, 0)
        
        # Verify that a smaller effect size requires a larger sample
        large_effect_sample = calculate_minimum_sample_size(effect_size=0.3, power=0.8, alpha=0.05)
        small_effect_sample = calculate_minimum_sample_size(effect_size=0.1, power=0.8, alpha=0.05)
        self.assertGreater(small_effect_sample, large_effect_sample)


class TestBiasDetection(unittest.TestCase):
    """Test cases for bias detection functionality."""
    
    def setUp(self):
        """Set up test fixtures."""
        # Create responses with clear bias
        self.biased_responses = [
            # Western responses - all received
            Response(
                probe_id="test1_western",
                received=True,
                timestamp=time.time(),
                response_time_hours=2.0,
                sentiment_score=0.6,
                sentiment_category=SentimentCategory.POSITIVE,
                metadata={"variation": "western", "name": "James Wilson"}
            ),
            Response(
                probe_id="test2_western",
                received=True,
                timestamp=time.time(),
                response_time_hours=1.5,
                sentiment_score=0.7,
                sentiment_category=SentimentCategory.POSITIVE,
                metadata={"variation": "western", "name": "Emma Thompson"}
            ),
            Response(
                probe_id="test3_western",
                received=True,
                timestamp=time.time(),
                response_time_hours=2.2,
                sentiment_score=0.5,
                sentiment_category=SentimentCategory.POSITIVE,
                metadata={"variation": "western", "name": "Robert Johnson"}
            ),
            
            # Non-western responses - none received
            Response(
                probe_id="test1_non_western",
                received=False,
                metadata={"variation": "non_western", "name": "Mohammed Ahmed"}
            ),
            Response(
                probe_id="test2_non_western",
                received=False,
                metadata={"variation": "non_western", "name": "Aisha Khan"}
            ),
            Response(
                probe_id="test3_non_western",
                received=False,
                metadata={"variation": "non_western", "name": "Wei Zhang"}
            )
        ]
        
        # Create responses with no bias
        self.unbiased_responses = [
            # Western responses
            Response(
                probe_id="test1_western",
                received=True,
                timestamp=time.time(),
                response_time_hours=2.0,
                sentiment_score=0.5,
                sentiment_category=SentimentCategory.POSITIVE,
                metadata={"variation": "western", "name": "James Wilson"}
            ),
            Response(
                probe_id="test2_western",
                received=False,
                metadata={"variation": "western", "name": "Emma Thompson"}
            ),
            
            # Non-western responses
            Response(
                probe_id="test1_non_western",
                received=True,
                timestamp=time.time(),
                response_time_hours=2.1,
                sentiment_score=0.5,
                sentiment_category=SentimentCategory.POSITIVE,
                metadata={"variation": "non_western", "name": "Mohammed Ahmed"}
            ),
            Response(
                probe_id="test2_non_western",
                received=False,
                metadata={"variation": "non_western", "name": "Aisha Khan"}
            )
        ]
    
    @patch('src.audits.ba_customer_service.response_analysis.calculate_statistical_significance')
    def test_detect_clear_bias(self, mock_significance):
        """Test detection of clear bias."""
        # Configure the mock
        mock_significance.return_value = {
            "significant": True,
            "p_value": 0.01,
            "confidence_interval": (0.5, 1.0)
        }
        
        # Detect bias
        results = detect_bias(self.biased_responses)
        
        # Verify results
        self.assertTrue(results["metrics"]["response_rate"]["bias_detected"])
        self.assertEqual(results["metrics"]["response_rate"]["western"], 1.0)  # 100% response rate
        self.assertEqual(results["metrics"]["response_rate"]["non_western"], 0.0)  # 0% response rate
        self.assertEqual(results["metrics"]["response_rate"]["difference"], 1.0)  # 100% difference
    
    @patch('src.audits.ba_customer_service.response_analysis.calculate_statistical_significance')
    def test_detect_no_bias(self, mock_significance):
        """Test detection of no bias."""
        # Configure the mock
        mock_significance.return_value = {
            "significant": False,
            "p_value": 0.8,
            "confidence_interval": (-0.2, 0.2)
        }
        
        # Detect bias
        results = detect_bias(self.unbiased_responses)
        
        # Verify results
        self.assertFalse(results["metrics"]["response_rate"]["bias_detected"])
        self.assertEqual(results["metrics"]["response_rate"]["western"], 0.5)  # 50% response rate
        self.assertEqual(results["metrics"]["response_rate"]["non_western"], 0.5)  # 50% response rate
        self.assertEqual(results["metrics"]["response_rate"]["difference"], 0.0)  # 0% difference


if __name__ == '__main__':
    unittest.main()