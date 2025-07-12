"""
test_explanation_generator.py

Unit tests for the ExplanationGenerator class.
"""

import os
import json
import unittest
import tempfile
import shutil
from unittest.mock import patch, MagicMock

from src.explanation_generator import ExplanationGenerator


class TestExplanationGenerator(unittest.TestCase):
    """Test cases for the ExplanationGenerator class."""

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
            "explanation_requirements": {
                "minimum_factors": 3,
                "language_options": ["Portuguese", "English"],
                "format_options": ["Text", "PDF", "JSON"]
            }
        }
        
        with open(self.config_path, "w") as f:
            json.dump(self.config, f)
        
        # Create a test decision data
        self.decision_data = {
            "application_id": "test-app-1",
            "education": "Bachelor's Degree with 3-5 years experience",
            "years_experience": 4,
            "skills": ["Programming", "System Design", "Data Analysis"],
            "selected": True,
            "interview_score": 8.5
        }
        
        # Initialize the generator
        self.generator = ExplanationGenerator(self.config_path)

    def tearDown(self):
        """Tear down test fixtures."""
        # Remove the temporary directory
        shutil.rmtree(self.test_dir)

    def test_init(self):
        """Test initialization of ExplanationGenerator."""
        self.assertEqual(self.generator.run_id, "test_run")
        self.assertEqual(self.generator.output_dir, self.test_dir)
        self.assertEqual(self.generator.config, self.config)

    def test_generate_factor_based_explanation(self):
        """Test generation of factor-based explanation."""
        explanation = self.generator.generate_factor_based_explanation(self.decision_data)
        
        # Check that explanation has the required fields
        self.assertEqual(explanation["decision_id"], self.decision_data["application_id"])
        self.assertEqual(explanation["decision_type"], "employment_screening")
        self.assertEqual(explanation["decision_outcome"], "selected")
        self.assertEqual(explanation["decision_score"], self.decision_data["interview_score"])
        self.assertEqual(explanation["explanation_type"], "factor_based")
        self.assertEqual(explanation["language"], "en")
        
        # Check that factors were extracted correctly
        self.assertEqual(len(explanation["factors"]), 3)  # Education, experience, skills
        
        # Check that each factor has the required fields
        for factor in explanation["factors"]:
            self.assertIn("factor", factor)
            self.assertIn("value", factor)
            self.assertIn("impact", factor)
            self.assertIn("weight", factor)

    def test_generate_counterfactual_explanation(self):
        """Test generation of counterfactual explanation."""
        # Test with selected application (should have no counterfactuals)
        explanation = self.generator.generate_counterfactual_explanation(self.decision_data)
        self.assertEqual(len(explanation["counterfactuals"]), 0)
        
        # Test with rejected application (should have counterfactuals)
        rejected_data = self.decision_data.copy()
        rejected_data["selected"] = False
        rejected_data["years_experience"] = 2
        
        explanation = self.generator.generate_counterfactual_explanation(rejected_data)
        self.assertGreater(len(explanation["counterfactuals"]), 0)
        
        # Check that each counterfactual has the required fields
        for cf in explanation["counterfactuals"]:
            self.assertIn("factor", cf)
            self.assertIn("current_value", cf)
            self.assertIn("counterfactual_value", cf)
            self.assertIn("outcome_change", cf)

    def test_generate_human_readable_explanation_en(self):
        """Test generation of human-readable explanation in English."""
        explanation = self.generator.generate_human_readable_explanation(self.decision_data, "en")
        
        # Check that explanation is a string
        self.assertIsInstance(explanation, str)
        
        # Check that explanation contains key sections
        self.assertIn("# Decision Explanation", explanation)
        self.assertIn("## Factors that Influenced the Decision", explanation)
        self.assertIn("## Right to Contest", explanation)
        
        # Check that explanation contains decision details
        self.assertIn(self.decision_data["application_id"], explanation)
        self.assertIn("Selected", explanation)

    def test_generate_human_readable_explanation_pt(self):
        """Test generation of human-readable explanation in Portuguese."""
        explanation = self.generator.generate_human_readable_explanation(self.decision_data, "pt")
        
        # Check that explanation is a string
        self.assertIsInstance(explanation, str)
        
        # Check that explanation contains key sections in Portuguese
        self.assertIn("# Explicação da Decisão", explanation)
        self.assertIn("## Fatores que Influenciaram a Decisão", explanation)
        self.assertIn("## Direito de Contestação", explanation)
        
        # Check that explanation contains decision details
        self.assertIn(self.decision_data["application_id"], explanation)
        self.assertIn("Selecionado", explanation)

    @patch("json.dump")
    def test_generate_explanation_for_decision(self, mock_json_dump):
        """Test generation of all explanation types for a decision."""
        # Test with all explanation types
        explanations = self.generator.generate_explanation_for_decision(self.decision_data, "all", "en")
        
        # Check that all explanation types were generated
        self.assertIn("factor_based", explanations)
        self.assertIn("counterfactual", explanations)
        self.assertIn("human_readable", explanations)
        
        # Check that json.dump was called
        mock_json_dump.assert_called_once()
        
        # Test with specific explanation type
        explanations = self.generator.generate_explanation_for_decision(self.decision_data, "factor_based", "en")
        
        # Check that only the requested explanation type was generated
        self.assertIn("factor_based", explanations)
        self.assertNotIn("counterfactual", explanations)
        self.assertNotIn("human_readable", explanations)


if __name__ == "__main__":
    unittest.main()