"""
test_employment_bias_evaluator.py

Unit tests for the EmploymentBiasEvaluator class.
"""

import os
import json
import unittest
import tempfile
import shutil
from unittest.mock import patch, MagicMock

import pandas as pd
import numpy as np

from src.employment_bias_evaluator import EmploymentBiasEvaluator


class TestEmploymentBiasEvaluator(unittest.TestCase):
    """Test cases for the EmploymentBiasEvaluator class."""

    def setUp(self):
        """Set up test fixtures."""
        # Create a temporary directory for test outputs
        self.test_dir = tempfile.mkdtemp()
        
        # Create a test config file
        self.config_path = os.path.join(self.test_dir, "test_config.json")
        self.config = {
            "experiment_settings": {
                "num_pairs": 10,
                "rate_limit_requests": 10,
                "rate_limit_period": 1,
                "run_id": "test_run",
                "output_dir": self.test_dir
            },
            "protected_characteristics": {
                "race": {
                    "privileged": ["European descent"],
                    "marginalized": ["Afro-Brazilian"]
                },
                "gender": {
                    "privileged": ["Male"],
                    "marginalized": ["Female"]
                }
            },
            "employment_sectors": ["Technology", "Finance"],
            "job_levels": ["Entry-level", "Senior"]
        }
        
        with open(self.config_path, "w") as f:
            json.dump(self.config, f)
        
        # Initialize the evaluator
        self.evaluator = EmploymentBiasEvaluator(self.config_path)

    def tearDown(self):
        """Tear down test fixtures."""
        # Remove the temporary directory
        shutil.rmtree(self.test_dir)

    def test_init(self):
        """Test initialization of EmploymentBiasEvaluator."""
        self.assertEqual(self.evaluator.run_id, "test_run")
        self.assertEqual(self.evaluator.output_dir, self.test_dir)
        self.assertEqual(self.evaluator.config, self.config)

    def test_generate_job_applications(self):
        """Test generation of job applications."""
        num_pairs = 5
        applications = self.evaluator.generate_job_applications(num_pairs)
        
        # Check that the correct number of applications was generated
        self.assertEqual(len(applications), num_pairs * 2)
        
        # Check that applications are paired (privileged and marginalized)
        privileged_count = sum(1 for app in applications if app["group"] == "privileged")
        marginalized_count = sum(1 for app in applications if app["group"] == "marginalized")
        self.assertEqual(privileged_count, num_pairs)
        self.assertEqual(marginalized_count, num_pairs)
        
        # Check that each application has the required fields
        required_fields = ["application_id", "sector", "job_level", "education", "years_experience", "skills", "timestamp", "protected_characteristic", "characteristic_value", "group"]
        for app in applications:
            for field in required_fields:
                self.assertIn(field, app)

    def test_generate_base_application(self):
        """Test generation of base application."""
        sector = "Technology"
        job_level = "Senior"
        base_app = self.evaluator._generate_base_application(sector, job_level)
        
        # Check that the base application has the required fields
        self.assertIn("application_id", base_app)
        self.assertEqual(base_app["sector"], sector)
        self.assertEqual(base_app["job_level"], job_level)
        self.assertIn("education", base_app)
        self.assertIn("years_experience", base_app)
        self.assertIn("skills", base_app)
        self.assertIn("timestamp", base_app)
        
        # Check that skills are appropriate for the sector
        self.assertEqual(len(base_app["skills"]), 3)

    @patch("pandas.DataFrame.to_csv")
    def test_collect_responses(self, mock_to_csv):
        """Test collection of responses."""
        # Create test applications
        applications = [
            {"application_id": "1", "group": "privileged", "sector": "Technology", "job_level": "Senior"},
            {"application_id": "2", "group": "marginalized", "sector": "Technology", "job_level": "Senior"}
        ]
        
        # Collect responses
        responses_df = self.evaluator.collect_responses(applications)
        
        # Check that responses were collected for all applications
        self.assertEqual(len(responses_df), len(applications))
        
        # Check that responses have the required fields
        self.assertIn("selected", responses_df.columns)
        self.assertIn("interview_score", responses_df.columns)
        self.assertIn("response_time", responses_df.columns)
        
        # Check that to_csv was called
        mock_to_csv.assert_called_once()

    @patch("json.dump")
    def test_analyze_bias(self, mock_json_dump):
        """Test bias analysis."""
        # Create test responses DataFrame
        responses_data = {
            "application_id": ["1", "2", "3", "4"],
            "group": ["privileged", "marginalized", "privileged", "marginalized"],
            "protected_characteristic": ["race", "race", "gender", "gender"],
            "selected": [True, False, True, False],
            "interview_score": [8.0, 6.0, 8.5, 6.5]
        }
        responses_df = pd.DataFrame(responses_data)
        
        # Analyze bias
        analysis_results = self.evaluator.analyze_bias(responses_df)
        
        # Check that analysis results have the required fields
        self.assertIn("selection_rate", analysis_results)
        self.assertIn("interview_score", analysis_results)
        self.assertIn("by_characteristic", analysis_results)
        
        # Check that selection_rate analysis has the required fields
        self.assertIn("overall", analysis_results["selection_rate"])
        self.assertIn("by_group", analysis_results["selection_rate"])
        self.assertIn("difference", analysis_results["selection_rate"])
        self.assertIn("ratio", analysis_results["selection_rate"])
        self.assertIn("p_value", analysis_results["selection_rate"])
        self.assertIn("statistically_significant", analysis_results["selection_rate"])
        
        # Check that json.dump was called
        mock_json_dump.assert_called_once()

    def test_generate_report(self):
        """Test report generation."""
        # Create test analysis results
        analysis_results = {
            "selection_rate": {
                "overall": 0.5,
                "by_group": {"privileged": 0.8, "marginalized": 0.6},
                "difference": 0.2,
                "ratio": 0.75,
                "p_value": 0.04,
                "statistically_significant": True
            },
            "interview_score": {
                "overall": 7.0,
                "by_group": {"privileged": 8.0, "marginalized": 6.0},
                "difference": 2.0,
                "ratio": 0.75,
                "p_value": 0.03,
                "statistically_significant": True
            },
            "by_characteristic": {
                "race": {
                    "selection_rate": {
                        "by_group": {"privileged": 0.8, "marginalized": 0.6},
                        "difference": 0.2,
                        "ratio": 0.75,
                        "p_value": 0.04,
                        "statistically_significant": True
                    }
                }
            }
        }
        
        # Generate report
        report = self.evaluator.generate_report(analysis_results)
        
        # Check that report is a string
        self.assertIsInstance(report, str)
        
        # Check that report contains key sections
        self.assertIn("# Employment Bias Analysis Report", report)
        self.assertIn("## Overall Results", report)
        self.assertIn("### Selection Rate", report)
        self.assertIn("### Interview Score", report)
        self.assertIn("## Results by Protected Characteristic", report)
        self.assertIn("## Compliance with Brazil's AI Act", report)

    @patch("src.employment_bias_evaluator.EmploymentBiasEvaluator.generate_job_applications")
    @patch("src.employment_bias_evaluator.EmploymentBiasEvaluator.collect_responses")
    @patch("src.employment_bias_evaluator.EmploymentBiasEvaluator.analyze_bias")
    @patch("src.employment_bias_evaluator.EmploymentBiasEvaluator.generate_report")
    def test_run_evaluation(self, mock_generate_report, mock_analyze_bias, mock_collect_responses, mock_generate_job_applications):
        """Test the full evaluation pipeline."""
        # Set up mocks
        mock_applications = [{"id": "1"}, {"id": "2"}]
        mock_responses_df = pd.DataFrame({"id": ["1", "2"]})
        mock_analysis_results = {"key": "value"}
        mock_report = "Report text"
        
        mock_generate_job_applications.return_value = mock_applications
        mock_collect_responses.return_value = mock_responses_df
        mock_analyze_bias.return_value = mock_analysis_results
        mock_generate_report.return_value = mock_report
        
        # Run evaluation
        results = self.evaluator.run_evaluation(num_pairs=5)
        
        # Check that all methods were called
        mock_generate_job_applications.assert_called_once_with(5)
        mock_collect_responses.assert_called_once_with(mock_applications)
        mock_analyze_bias.assert_called_once_with(mock_responses_df)
        mock_generate_report.assert_called_once_with(mock_analysis_results)
        
        # Check that results have the expected structure
        self.assertEqual(results["applications"], mock_applications)
        self.assertEqual(results["responses_df"].equals(mock_responses_df), True)
        self.assertEqual(results["analysis_results"], mock_analysis_results)
        self.assertEqual(results["report"], mock_report)


if __name__ == "__main__":
    unittest.main()