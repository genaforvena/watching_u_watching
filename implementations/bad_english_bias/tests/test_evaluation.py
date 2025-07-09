import unittest
import sys
import os
import tempfile
import shutil
from unittest.mock import patch, MagicMock

# Add the src directory to the Python path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '../src')))

from eval import evaluate_bad_english_bias, LLMTarget
from probe_generator import ProbeType
from error_injector import ErrorDensity, ErrorType

class TestEvaluation(unittest.TestCase):

    def setUp(self):
        """Set up test fixtures."""
        self.temp_dir = tempfile.mkdtemp()
        
    def tearDown(self):
        """Clean up test fixtures."""
        shutil.rmtree(self.temp_dir, ignore_errors=True)

    def test_evaluate_bad_english_bias_basic(self):
        """Test basic evaluation pipeline execution."""
        results = evaluate_bad_english_bias(
            probe_type=ProbeType.LLM_QUESTION,
            probe_count=3,
            error_density=ErrorDensity.MEDIUM,
            error_types=[ErrorType.TYPO, ErrorType.GRAMMAR],
            output_dir=self.temp_dir
        )

        # Verify results structure
        self.assertIsNotNone(results)
        self.assertIn('evaluation_config', results)
        self.assertIn('probe_pairs', results)
        self.assertIn('baseline_responses', results)
        self.assertIn('variant_responses', results)
        self.assertIn('bias_analysis', results)
        self.assertIn('results_file', results)

        # Verify evaluation config
        config = results['evaluation_config']
        self.assertEqual(config['probe_type'], 'llm_question')
        self.assertEqual(config['probe_count'], 3)
        self.assertEqual(config['error_density'], 'medium')
        self.assertEqual(config['error_types'], ['typo', 'grammar'])

        # Verify probe pairs generated
        self.assertEqual(len(results['probe_pairs']), 3)
        self.assertEqual(len(results['baseline_responses']), 3)
        self.assertEqual(len(results['variant_responses']), 3)

        # Verify bias analysis structure
        bias_analysis = results['bias_analysis']
        expected_metrics = ['helpfulness_score', 'response_time', 'response_length', 'sentiment_score', 'formality_score']
        for metric in expected_metrics:
            self.assertIn(metric, bias_analysis)

        # Verify results file was created
        self.assertTrue(os.path.exists(results['results_file']))

    def test_different_probe_types(self):
        """Test evaluation with different probe types."""
        probe_types = [ProbeType.JOB_APPLICATION, ProbeType.CUSTOMER_SERVICE, ProbeType.EMAIL_INQUIRY]
        
        for probe_type in probe_types:
            with self.subTest(probe_type=probe_type):
                results = evaluate_bad_english_bias(
                    probe_type=probe_type,
                    probe_count=2,
                    output_dir=self.temp_dir
                )
                
                self.assertIsNotNone(results)
                self.assertEqual(results['evaluation_config']['probe_type'], probe_type.value)
                self.assertEqual(len(results['probe_pairs']), 2)

    def test_different_error_densities(self):
        """Test evaluation with different error densities."""
        densities = [ErrorDensity.LOW, ErrorDensity.MEDIUM, ErrorDensity.HIGH]
        
        for density in densities:
            with self.subTest(density=density):
                results = evaluate_bad_english_bias(
                    probe_count=2,
                    error_density=density,
                    output_dir=self.temp_dir
                )
                
                self.assertIsNotNone(results)
                self.assertEqual(results['evaluation_config']['error_density'], density.value)

    def test_custom_target_system(self):
        """Test evaluation with custom target system."""
        # Create a mock target system
        mock_target = MagicMock()
        mock_target.query.return_value = {
            'response': 'Mock response',
            'response_time': 1.0,
            'timestamp': 1234567890.0
        }

        results = evaluate_bad_english_bias(
            probe_count=2,
            target_system=mock_target,
            output_dir=self.temp_dir
        )

        self.assertIsNotNone(results)
        # Verify mock was called
        self.assertEqual(mock_target.query.call_count, 4)  # 2 pairs × 2 queries each

    def test_llm_target_bias_simulation(self):
        """Test LLMTarget bias simulation."""
        target = LLMTarget()
        
        # Test with clean text (should get helpful response)
        clean_result = target.query("Can you please explain machine learning?")
        
        # Test with text containing errors (should get less helpful response)
        error_result = target.query("Can you please explain machien learing? I are interested.")
        
        # Verify different responses (bias simulation working)
        self.assertNotEqual(clean_result['response'], error_result['response'])
        # Error response should be faster (less thoughtful)
        self.assertLess(error_result['response_time'], clean_result['response_time'])

    def test_error_handling(self):
        """Test error handling in evaluation pipeline."""
        # Test with invalid probe type should be handled gracefully by enum validation
        with self.assertRaises(ValueError):
            ProbeType("invalid_type")

        # Test with invalid error density
        with self.assertRaises(ValueError):
            ErrorDensity("invalid_density")

    @patch('eval.logging')
    def test_logging_integration(self, mock_logging):
        """Test that logging is properly integrated."""
        results = evaluate_bad_english_bias(
            probe_count=1,
            output_dir=self.temp_dir
        )
        
        self.assertIsNotNone(results)
        # Verify logging was configured (mock_logging.basicConfig should be called)
        mock_logging.basicConfig.assert_called()

    def test_parquet_file_creation(self):
        """Test that Parquet file is created with correct structure."""
        results = evaluate_bad_english_bias(
            probe_count=2,
            output_dir=self.temp_dir
        )

        # Load the Parquet file
        import pandas as pd
        df = pd.read_parquet(results['results_file'])

        # Verify DataFrame structure
        expected_columns = [
            'pair_id', 'probe_type', 'error_density', 'errors_applied',
            'baseline_content', 'variant_content', 'baseline_response', 'variant_response',
            'baseline_helpful', 'variant_helpful', 'baseline_response_time', 'variant_response_time',
            'baseline_length', 'variant_length', 'timestamp'
        ]
        
        for col in expected_columns:
            self.assertIn(col, df.columns)

        # Verify data integrity
        self.assertEqual(len(df), 2)  # Should have 2 rows for 2 probe pairs
        self.assertTrue(all(df['probe_type'] == 'llm_question'))
        self.assertTrue(all(df['error_density'] == 'medium'))

if __name__ == '__main__':
    unittest.main()