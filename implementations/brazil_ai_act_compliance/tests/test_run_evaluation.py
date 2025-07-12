"""
test_run_evaluation.py

Unit tests for the run_evaluation module.
"""

import os
import json
import unittest
import tempfile
import shutil
from unittest.mock import patch, MagicMock

import pandas as pd

from src.run_evaluation import run_full_evaluation


class TestRunEvaluation(unittest.TestCase):
    """Test cases for the run_evaluation module."""

    def setUp(self):
        """Set up test fixtures."""
        # Create a temporary directory for test outputs
        self.test_dir = tempfile.mkdtemp()
        
        # Create a test config file
        self.config_path = os.path.join(self.test_dir, "test_config.json")
        self.config = {
            "experiment_settings": {
                "run_id": "test_run",
                "output_dir": self.test_dir
            },
            "protected_characteristics": {
                "race": {
                    "privileged": ["European descent"],
                    "marginalized": ["Afro-Brazilian"]
                }
            },
            "employment_sectors": ["Technology"],
            "job_levels": ["Entry-level"],
            "aia_requirements": {
                "risk_assessment": {
                    "categories": ["Discrimination Risk"],
                    "severity_levels": ["Low", "Medium", "High"]
                },
                "mitigation_measures": ["Bias Detection"],
                "reporting_requirements": {
                    "public_disclosure": True
                }
            },
            "explanation_requirements": {
                "minimum_factors": 3
            },
            "brazilian_regulatory_alignment": {
                "bias_mitigation_article": "Article X",
                "transparency_article": "Article Y",
                "aia_article": "Article Z"
            }
        }
        
        with open(self.config_path, "w") as f:
            json.dump(self.config, f)

    def tearDown(self):
        """Tear down test fixtures."""
        # Remove the temporary directory
        shutil.rmtree(self.test_dir)

    @patch("src.employment_bias_evaluator.EmploymentBiasEvaluator.run_evaluation")
    @patch("src.brazil_aia_generator.BrazilAIAGenerator.generate_aia")
    @patch("src.explanation_generator.ExplanationGenerator.generate_explanation_for_decision")
    @patch("json.dump")
    def test_run_full_evaluation(self, mock_json_dump, mock_generate_explanation, mock_generate_aia, mock_run_evaluation):
        """Test the full evaluation pipeline."""
        # Set up mocks
        mock_run_id = "test-run-id"
        mock_bias_results = {
            "applications": [{"application_id": "1"}, {"application_id": "2"}],
            "responses_df": pd.DataFrame({
                "application_id": ["1", "2", "3", "4"],
                "selected": [True, True, False, False],
                "interview_score": [8.0, 8.5, 6.0, 6.5]
            }),
            "analysis_results": {"key": "value"},
            "report": "Report text"
        }
        mock_aia_results = {
            "aia_report": {"metadata": {"report_id": "test-aia-id"}},
            "markdown": "# AIA Report",
            "json_path": os.path.join(self.test_dir, "aia_report.json"),
            "markdown_path": os.path.join(self.test_dir, "aia_report.md")
        }
        mock_explanation = {
            "factor_based": {"decision_id": "1"},
            "counterfactual": {"decision_id": "1"},
            "human_readable": "Explanation text"
        }
        
        # Configure mocks
        mock_run_evaluation.return_value = mock_bias_results
        mock_generate_aia.return_value = mock_aia_results
        mock_generate_explanation.return_value = mock_explanation
        
        # Run the full evaluation
        results = run_full_evaluation(self.config_path, self.test_dir, num_pairs=10)
        
        # Check that all components were called
        mock_run_evaluation.assert_called_once_with(10)
        mock_generate_aia.assert_called_once_with("both")
        
        # Check that explanations were generated for samples
        self.assertGreaterEqual(mock_generate_explanation.call_count, 1)
        
        # Check that results were saved
        mock_json_dump.assert_called()
        
        # Check that results have the expected structure
        self.assertIn("bias_evaluation", results)
        self.assertIn("aia", results)
        self.assertIn("explanations", results)
        self.assertIn("runtime_seconds", results)
        
        # Check that bias_evaluation has the expected fields
        self.assertIn("run_id", results["bias_evaluation"])
        self.assertIn("num_pairs", results["bias_evaluation"])
        self.assertIn("report_path", results["bias_evaluation"])
        self.assertIn("analysis_path", results["bias_evaluation"])
        
        # Check that aia has the expected fields
        self.assertIn("report_id", results["aia"])
        self.assertIn("json_path", results["aia"])
        self.assertIn("markdown_path", results["aia"])
        
        # Check that explanations has the expected structure
        self.assertIn("selected", results["explanations"])
        self.assertIn("rejected", results["explanations"])


if __name__ == "__main__":
    unittest.main()