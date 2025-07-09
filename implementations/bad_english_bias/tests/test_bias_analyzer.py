import unittest
import sys
import os
import time
import pandas as pd

# Add the src directory to the Python path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '../src')))

from bias_analyzer import BiasAnalyzer, ResponseMetrics, analyze_bias_with_statistics
from error_injector import ErrorDensity

class TestBiasAnalyzer(unittest.TestCase):

    def setUp(self):
        """Set up test fixtures."""
        self.analyzer = BiasAnalyzer()

    def test_extract_response_metrics_basic(self):
        """Test basic response metrics extraction."""
        response_text = "Thank you for your question. I would be happy to help you with detailed information."
        response_time = 1.2
        probe_id = "test_probe_1"
        response_id = "resp_1"

        metrics = self.analyzer.extract_response_metrics(
            response_text=response_text,
            response_time=response_time,
            probe_id=probe_id,
            response_id=response_id
        )

        # Verify basic fields
        self.assertEqual(metrics.response_id, response_id)
        self.assertEqual(metrics.probe_id, probe_id)
        self.assertEqual(metrics.response_text, response_text)
        self.assertEqual(metrics.response_time, response_time)
        self.assertEqual(metrics.response_length, len(response_text))

        # Verify metrics are within expected ranges
        self.assertTrue(-1.0 <= metrics.sentiment_score <= 1.0)
        self.assertTrue(0.0 <= metrics.formality_score <= 1.0)
        self.assertTrue(0.0 <= metrics.helpfulness_score <= 1.0)
        self.assertTrue(isinstance(metrics.is_helpful, bool))

    def test_helpful_vs_unhelpful_responses(self):
        """Test that helpful and unhelpful responses are properly classified."""
        helpful_text = "I would be happy to provide you with a comprehensive explanation and detailed examples."
        unhelpful_text = "I don't understand. Please clarify your request."

        helpful_metrics = self.analyzer.extract_response_metrics(
            helpful_text, 1.0, "helpful_probe", "helpful_resp"
        )
        unhelpful_metrics = self.analyzer.extract_response_metrics(
            unhelpful_text, 1.0, "unhelpful_probe", "unhelpful_resp"
        )

        # Helpful response should have higher helpfulness score
        self.assertGreater(helpful_metrics.helpfulness_score, unhelpful_metrics.helpfulness_score)
        self.assertTrue(helpful_metrics.is_helpful)
        self.assertFalse(unhelpful_metrics.is_helpful)

    def test_analyze_bias_with_statistics(self):
        """Test statistical bias analysis following PR #11 pattern."""
        # Create mock baseline responses (helpful)
        baseline_responses = []
        for i in range(5):
            metrics = self.analyzer.extract_response_metrics(
                "Thank you for your inquiry. I'll provide comprehensive information.",
                1.2, f"baseline_{i}", f"resp_baseline_{i}"
            )
            baseline_responses.append(metrics)

        # Create mock variant responses (less helpful)
        variant_responses = []
        for i in range(5):
            metrics = self.analyzer.extract_response_metrics(
                "I don't understand your question clearly.",
                0.8, f"variant_{i}", f"resp_variant_{i}"
            )
            variant_responses.append(metrics)

        # Perform statistical analysis
        results = analyze_bias_with_statistics(baseline_responses, variant_responses)

        # Verify structure of results
        self.assertIsInstance(results, dict)
        expected_metrics = ['helpfulness_score', 'response_time', 'response_length', 'sentiment_score', 'formality_score']
        
        for metric in expected_metrics:
            self.assertIn(metric, results)
            result = results[metric]
            
            # Verify each metric result has required fields
            self.assertIn('baseline_mean', result)
            self.assertIn('variant_mean', result)
            self.assertIn('difference', result)
            self.assertIn('ratio', result)
            self.assertIn('t_statistic', result)
            self.assertIn('p_value', result)
            self.assertIn('effect_size', result)
            self.assertIn('bias_detected', result)

        # For helpfulness, should detect significant difference
        helpfulness_result = results['helpfulness_score']
        self.assertGreater(helpfulness_result['baseline_mean'], helpfulness_result['variant_mean'])
        
        # For response time, baseline should be higher (more thoughtful)
        time_result = results['response_time']
        self.assertGreater(time_result['baseline_mean'], time_result['variant_mean'])

    def test_analyze_bias_no_difference(self):
        """Test bias analysis when there's no significant difference."""
        # Create identical responses for both baseline and variant
        baseline_responses = []
        variant_responses = []
        
        response_text = "Thank you for your question. I'll help you with that."
        
        for i in range(5):
            baseline_metrics = self.analyzer.extract_response_metrics(
                response_text, 1.0, f"baseline_{i}", f"resp_baseline_{i}"
            )
            variant_metrics = self.analyzer.extract_response_metrics(
                response_text, 1.0, f"variant_{i}", f"resp_variant_{i}"
            )
            
            baseline_responses.append(baseline_metrics)
            variant_responses.append(variant_metrics)

        results = analyze_bias_with_statistics(baseline_responses, variant_responses)

        # Should not detect bias for identical responses
        for metric, result in results.items():
            self.assertAlmostEqual(result['baseline_mean'], result['variant_mean'], places=2)
            self.assertAlmostEqual(result['difference'], 0, places=2)
            # P-value might be NaN for identical data, but bias should not be detected
            self.assertFalse(result['bias_detected'])

    def test_edge_cases(self):
        """Test edge cases for bias analysis."""
        # Test with minimal data
        single_baseline = [self.analyzer.extract_response_metrics(
            "Test response", 1.0, "baseline_1", "resp_1"
        )]
        single_variant = [self.analyzer.extract_response_metrics(
            "Test response", 1.0, "variant_1", "resp_2"
        )]

        results = analyze_bias_with_statistics(single_baseline, single_variant)
        
        # Should handle single samples gracefully
        for metric, result in results.items():
            # With single samples, statistical tests should return None
            self.assertIsNone(result['t_statistic'])
            self.assertIsNone(result['p_value'])
            self.assertIsNone(result['effect_size'])
            self.assertFalse(result['bias_detected'])

    def test_response_metrics_property(self):
        """Test is_helpful property calculation."""
        # Test helpful response
        helpful_metrics = self.analyzer.extract_response_metrics(
            "I would be delighted to provide comprehensive assistance with detailed explanations.",
            1.0, "test_1", "resp_1"
        )
        
        # Test unhelpful response
        unhelpful_metrics = self.analyzer.extract_response_metrics(
            "I don't understand. This is unclear.",
            1.0, "test_2", "resp_2"
        )

        # Verify is_helpful property works correctly
        self.assertTrue(helpful_metrics.is_helpful)
        self.assertFalse(unhelpful_metrics.is_helpful)

if __name__ == '__main__':
    unittest.main()