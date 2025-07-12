"""
test_brazil_aia_generator.py

Unit tests for the BrazilAIAGenerator class.
"""

import os
import json
import unittest
import tempfile
import shutil
from unittest.mock import patch, MagicMock

from src.brazil_aia_generator import BrazilAIAGenerator


class TestBrazilAIAGenerator(unittest.TestCase):
    """Test cases for the BrazilAIAGenerator class."""

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
            "aia_requirements": {
                "risk_assessment": {
                    "categories": [
                        "Discrimination Risk",
                        "Privacy Risk",
                        "Transparency Risk",
                        "Accountability Risk"
                    ],
                    "severity_levels": [
                        "Low",
                        "Medium",
                        "High",
                        "Critical"
                    ]
                },
                "mitigation_measures": [
                    "Bias Detection and Mitigation",
                    "Explainability Mechanisms"
                ],
                "reporting_requirements": {
                    "frequency": "Annual",
                    "public_disclosure": True,
                    "regulatory_submission": True
                }
            },
            "brazilian_regulatory_alignment": {
                "bias_mitigation_article": "Article X",
                "transparency_article": "Article Y",
                "aia_article": "Article Z"
            }
        }
        
        with open(self.config_path, "w") as f:
            json.dump(self.config, f)
        
        # Create a test bias analysis file
        self.bias_analysis_path = os.path.join(self.test_dir, "test_bias_analysis.json")
        self.bias_analysis = {
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
            }
        }
        
        with open(self.bias_analysis_path, "w") as f:
            json.dump(self.bias_analysis, f)
        
        # Initialize the generator
        self.generator = BrazilAIAGenerator(self.config_path, self.bias_analysis_path)

    def tearDown(self):
        """Tear down test fixtures."""
        # Remove the temporary directory
        shutil.rmtree(self.test_dir)

    def test_init(self):
        """Test initialization of BrazilAIAGenerator."""
        self.assertEqual(self.generator.run_id, "test_run")
        self.assertEqual(self.generator.output_dir, self.test_dir)
        self.assertEqual(self.generator.config, self.config)
        self.assertEqual(self.generator.bias_analysis, self.bias_analysis)

    def test_generate_risk_assessment(self):
        """Test generation of risk assessment."""
        risk_assessment = self.generator.generate_risk_assessment()
        
        # Check that risk assessment includes all categories
        for category in self.config["aia_requirements"]["risk_assessment"]["categories"]:
            self.assertIn(category, risk_assessment)
        
        # Check that Discrimination Risk is high due to bias analysis
        self.assertEqual(risk_assessment["Discrimination Risk"]["severity"], "High")
        self.assertTrue("statistically significant disparities" in risk_assessment["Discrimination Risk"]["description"])

    def test_generate_mitigation_measures(self):
        """Test generation of mitigation measures."""
        risk_assessment = self.generator.generate_risk_assessment()
        mitigation_measures = self.generator.generate_mitigation_measures(risk_assessment)
        
        # Check that mitigation measures were generated for each risk
        self.assertGreaterEqual(len(mitigation_measures), len(risk_assessment))
        
        # Check that each mitigation measure has the required fields
        for measure in mitigation_measures:
            self.assertIn("risk_category", measure)
            self.assertIn("risk_severity", measure)
            self.assertIn("measure", measure)
            self.assertIn("implementation_status", measure)
            self.assertIn("responsible_party", measure)
            self.assertIn("timeline", measure)

    @patch("json.dump")
    def test_generate_aia_report(self, mock_json_dump):
        """Test generation of AIA report."""
        aia_report = self.generator.generate_aia_report()
        
        # Check that AIA report has the required sections
        self.assertIn("metadata", aia_report)
        self.assertIn("system_description", aia_report)
        self.assertIn("legal_basis", aia_report)
        self.assertIn("risk_assessment", aia_report)
        self.assertIn("mitigation_measures", aia_report)
        self.assertIn("monitoring_plan", aia_report)
        self.assertIn("transparency_mechanisms", aia_report)
        self.assertIn("stakeholder_consultation", aia_report)
        
        # Check that metadata has the required fields
        self.assertIn("report_id", aia_report["metadata"])
        self.assertIn("date", aia_report["metadata"])
        self.assertIn("version", aia_report["metadata"])
        self.assertIn("system_name", aia_report["metadata"])
        
        # Check that json.dump was called
        mock_json_dump.assert_called_once()

    def test_generate_aia_markdown(self):
        """Test generation of AIA markdown."""
        aia_report = self.generator.generate_aia_report()
        md_text = self.generator.generate_aia_markdown(aia_report)
        
        # Check that markdown text is a string
        self.assertIsInstance(md_text, str)
        
        # Check that markdown text contains key sections
        self.assertIn("# Algorithmic Impact Assessment (AIA) Report", md_text)
        self.assertIn("## 1. System Description", md_text)
        self.assertIn("## 2. Legal Basis", md_text)
        self.assertIn("## 3. Risk Assessment", md_text)
        self.assertIn("## 4. Mitigation Measures", md_text)
        self.assertIn("## 5. Monitoring Plan", md_text)
        self.assertIn("## 6. Transparency Mechanisms", md_text)
        self.assertIn("## 7. Stakeholder Consultation", md_text)

    @patch("src.brazil_aia_generator.BrazilAIAGenerator.generate_aia_report")
    @patch("src.brazil_aia_generator.BrazilAIAGenerator.generate_aia_markdown")
    def test_generate_aia(self, mock_generate_aia_markdown, mock_generate_aia_report):
        """Test the full AIA generation pipeline."""
        # Set up mocks
        mock_aia_report = {"metadata": {"report_id": "test-id"}}
        mock_md_text = "# AIA Report"
        
        mock_generate_aia_report.return_value = mock_aia_report
        mock_generate_aia_markdown.return_value = mock_md_text
        
        # Generate AIA with both formats
        result = self.generator.generate_aia("both")
        
        # Check that methods were called
        mock_generate_aia_report.assert_called_once()
        mock_generate_aia_markdown.assert_called_once_with(mock_aia_report)
        
        # Check that result has the expected structure
        self.assertEqual(result["aia_report"], mock_aia_report)
        self.assertEqual(result["markdown"], mock_md_text)
        self.assertIn("json_path", result)
        self.assertIn("markdown_path", result)
        
        # Generate AIA with JSON only
        result = self.generator.generate_aia("json")
        
        # Check that markdown was not generated
        self.assertEqual(mock_generate_aia_markdown.call_count, 1)  # Still just one call from before
        self.assertIsNone(result["markdown"])
        self.assertIsNone(result["markdown_path"])


if __name__ == "__main__":
    unittest.main()