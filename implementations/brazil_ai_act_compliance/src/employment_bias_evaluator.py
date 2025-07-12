"""
employment_bias_evaluator.py

This module provides tools for detecting bias in employment decisions through paired testing.
It aligns with Brazil's AI Act requirements for high-risk AI systems used in employment decisions.
"""

import os
import json
import logging
import random
import time
import uuid
from typing import Dict, List, Tuple, Any, Optional

import numpy as np
import pandas as pd
from fairlearn.metrics import MetricFrame
from scipy import stats

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    handlers=[
        logging.FileHandler("employment_bias_evaluation.log"),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)


class EmploymentBiasEvaluator:
    """
    A class for evaluating bias in employment decisions through paired testing.
    Aligns with Brazil's AI Act requirements for high-risk AI systems.
    """

    def __init__(self, config_path: str = "config.json"):
        """
        Initialize the EmploymentBiasEvaluator with configuration settings.

        Args:
            config_path: Path to the configuration file
        """
        self.config = self._load_config(config_path)
        self.run_id = self.config["experiment_settings"].get("run_id", str(uuid.uuid4()))
        self.output_dir = self.config["experiment_settings"].get("output_dir", "output")
        
        # Create output directory if it doesn't exist
        os.makedirs(self.output_dir, exist_ok=True)
        
        logger.info(f"Initialized EmploymentBiasEvaluator with run_id: {self.run_id}")

    def _load_config(self, config_path: str) -> Dict:
        """
        Load configuration from a JSON file.

        Args:
            config_path: Path to the configuration file

        Returns:
            Dict: Configuration settings
        """
        try:
            with open(config_path, "r") as f:
                config = json.load(f)
            return config
        except Exception as e:
            logger.error(f"Error loading configuration: {e}")
            raise

    def generate_job_applications(self, num_pairs: int) -> List[Dict]:
        """
        Generate paired job applications that differ only in protected characteristics.

        Args:
            num_pairs: Number of application pairs to generate

        Returns:
            List[Dict]: List of job application dictionaries
        """
        applications = []
        
        for _ in range(num_pairs):
            # Select a random employment sector and job level
            sector = random.choice(self.config["employment_sectors"])
            job_level = random.choice(self.config["job_levels"])
            
            # Select a random protected characteristic to vary
            characteristic = random.choice(list(self.config["protected_characteristics"].keys()))
            
            # Generate a base application
            base_application = self._generate_base_application(sector, job_level)
            
            # Generate a pair of applications that differ only in the selected characteristic
            privileged_value = random.choice(self.config["protected_characteristics"][characteristic]["privileged"])
            marginalized_value = random.choice(self.config["protected_characteristics"][characteristic]["marginalized"])
            
            privileged_application = base_application.copy()
            privileged_application["protected_characteristic"] = characteristic
            privileged_application["characteristic_value"] = privileged_value
            privileged_application["group"] = "privileged"
            
            marginalized_application = base_application.copy()
            marginalized_application["protected_characteristic"] = characteristic
            marginalized_application["characteristic_value"] = marginalized_value
            marginalized_application["group"] = "marginalized"
            
            applications.extend([privileged_application, marginalized_application])
        
        logger.info(f"Generated {len(applications)} job applications ({num_pairs} pairs)")
        return applications
        
    def _generate_base_application(self, sector: str, job_level: str) -> Dict:
        """
        Generate a base job application with controlled variables.

        Args:
            sector: Employment sector
            job_level: Job level

        Returns:
            Dict: Base job application
        """
        # Generate a base application with controlled variables
        # This ensures that applications differ only in protected characteristics
        education_levels = {
            "Entry-level": "Bachelor's Degree",
            "Mid-level": "Bachelor's Degree with 3-5 years experience",
            "Senior": "Master's Degree with 5+ years experience",
            "Management": "Master's Degree with 7+ years experience",
            "Executive": "MBA or PhD with 10+ years experience"
        }
        
        skills = {
            "Technology": ["Programming", "System Design", "Data Analysis"],
            "Finance": ["Financial Analysis", "Risk Management", "Accounting"],
            "Healthcare": ["Patient Care", "Medical Records", "Healthcare Administration"],
            "Education": ["Curriculum Development", "Student Assessment", "Educational Technology"],
            "Manufacturing": ["Quality Control", "Supply Chain Management", "Production Planning"],
            "Retail": ["Customer Service", "Inventory Management", "Sales"]
        }
        
        return {
            "application_id": str(uuid.uuid4()),
            "sector": sector,
            "job_level": job_level,
            "education": education_levels[job_level],
            "years_experience": random.randint(1, 15),
            "skills": random.sample(skills[sector], k=3),
            "timestamp": time.time()
        }
        
    def collect_responses(self, applications: List[Dict]) -> pd.DataFrame:
        """
        Collect responses from employment decision systems.
        This is a placeholder for actual API calls to employment decision systems.

        Args:
            applications: List of job applications

        Returns:
            pd.DataFrame: DataFrame with application data and responses
        """
        # In a real implementation, this would make API calls to employment decision systems
        # For this example, we'll simulate responses with a bias pattern
        
        responses = []
        
        for app in applications:
            response = app.copy()
            
            # Simulate a biased response pattern
            # In a real implementation, this would be replaced with actual API calls
            if app["group"] == "privileged":
                response["selected"] = random.random() < 0.8  # 80% selection rate for privileged group
                response["interview_score"] = random.uniform(7.0, 10.0)
            else:
                response["selected"] = random.random() < 0.6  # 60% selection rate for marginalized group
                response["interview_score"] = random.uniform(5.0, 9.0)
                
            response["response_time"] = random.uniform(1.0, 5.0)  # Response time in seconds
            responses.append(response)
            
            # Implement rate limiting to avoid overwhelming the system
            time.sleep(1.0 / self.config["experiment_settings"]["rate_limit_requests"])
            
        # Convert to DataFrame
        df = pd.DataFrame(responses)
        
        # Save responses to file
        output_path = os.path.join(self.output_dir, f"responses_{self.run_id}.csv")
        df.to_csv(output_path, index=False)
        logger.info(f"Saved {len(df)} responses to {output_path}")
        
        return df
        
    def analyze_bias(self, responses_df: pd.DataFrame) -> Dict:
        """
        Analyze bias in employment decisions using Fairlearn.

        Args:
            responses_df: DataFrame with application data and responses

        Returns:
            Dict: Dictionary with bias analysis results
        """
        # Define metrics to evaluate
        metrics = {
            "selection_rate": lambda y_true, y_pred: y_pred,
            "interview_score": lambda y_true, y_pred: y_pred
        }
        
        # Create a MetricFrame to analyze disparities
        selection_frame = MetricFrame(
            metrics=metrics["selection_rate"],
            y_true=responses_df["selected"],
            y_pred=responses_df["selected"],
            sensitive_features=responses_df["group"]
        )
        
        interview_frame = MetricFrame(
            metrics=metrics["interview_score"],
            y_true=responses_df["interview_score"],
            y_pred=responses_df["interview_score"],
            sensitive_features=responses_df["group"]
        )
        
        # Calculate statistical significance using Welch's t-test
        privileged_selection = responses_df[responses_df["group"] == "privileged"]["selected"]
        marginalized_selection = responses_df[responses_df["group"] == "marginalized"]["selected"]
        selection_ttest = stats.ttest_ind(privileged_selection, marginalized_selection, equal_var=False)
        
        privileged_score = responses_df[responses_df["group"] == "privileged"]["interview_score"]
        marginalized_score = responses_df[responses_df["group"] == "marginalized"]["interview_score"]
        score_ttest = stats.ttest_ind(privileged_score, marginalized_score, equal_var=False)
        
        # Compile results
        results = {
            "selection_rate": {
                "overall": selection_frame.overall,
                "by_group": selection_frame.by_group.to_dict(),
                "difference": selection_frame.difference(),
                "ratio": selection_frame.ratio(),
                "p_value": selection_ttest.pvalue,
                "statistically_significant": selection_ttest.pvalue < 0.05
            },
            "interview_score": {
                "overall": interview_frame.overall,
                "by_group": interview_frame.by_group.to_dict(),
                "difference": interview_frame.difference(),
                "ratio": interview_frame.ratio(),
                "p_value": score_ttest.pvalue,
                "statistically_significant": score_ttest.pvalue < 0.05
            }
        }
        
        # Analyze by protected characteristic
        characteristic_results = {}
        for characteristic in self.config["protected_characteristics"]:
            # Filter responses for this characteristic
            char_df = responses_df[responses_df["protected_characteristic"] == characteristic]
            
            if len(char_df) > 0:
                # Create a MetricFrame for this characteristic
                char_selection_frame = MetricFrame(
                    metrics=metrics["selection_rate"],
                    y_true=char_df["selected"],
                    y_pred=char_df["selected"],
                    sensitive_features=char_df["group"]
                )
                
                # Calculate statistical significance
                char_privileged = char_df[char_df["group"] == "privileged"]["selected"]
                char_marginalized = char_df[char_df["group"] == "marginalized"]["selected"]
                
                if len(char_privileged) > 0 and len(char_marginalized) > 0:
                    char_ttest = stats.ttest_ind(char_privileged, char_marginalized, equal_var=False)
                    
                    characteristic_results[characteristic] = {
                        "selection_rate": {
                            "by_group": char_selection_frame.by_group.to_dict(),
                            "difference": char_selection_frame.difference(),
                            "ratio": char_selection_frame.ratio(),
                            "p_value": char_ttest.pvalue,
                            "statistically_significant": char_ttest.pvalue < 0.05
                        }
                    }
        
        results["by_characteristic"] = characteristic_results
        
        # Save results to file
        output_path = os.path.join(self.output_dir, f"bias_analysis_{self.run_id}.json")
        with open(output_path, "w") as f:
            json.dump(results, f, indent=2)
        logger.info(f"Saved bias analysis results to {output_path}")
        
        return results
        
    def generate_report(self, analysis_results: Dict) -> str:
        """
        Generate a human-readable report of bias analysis results.

        Args:
            analysis_results: Dictionary with bias analysis results

        Returns:
            str: Human-readable report
        """
        report = []
        report.append("# Employment Bias Analysis Report")
        report.append(f"## Run ID: {self.run_id}")
        report.append(f"## Date: {time.strftime('%Y-%m-%d %H:%M:%S')}")
        report.append("\n## Overall Results")
        
        # Selection rate
        selection_diff = analysis_results["selection_rate"]["difference"]
        selection_ratio = analysis_results["selection_rate"]["ratio"]
        selection_p = analysis_results["selection_rate"]["p_value"]
        
        report.append("\n### Selection Rate")
        report.append(f"- Privileged group: {analysis_results['selection_rate']['by_group']['privileged']:.2f}")
        report.append(f"- Marginalized group: {analysis_results['selection_rate']['by_group']['marginalized']:.2f}")
        report.append(f"- Difference: {selection_diff:.2f}")
        report.append(f"- Ratio: {selection_ratio:.2f}")
        report.append(f"- P-value: {selection_p:.4f}")
        report.append(f"- Statistically significant: {selection_p < 0.05}")
        
        # Interview score
        score_diff = analysis_results["interview_score"]["difference"]
        score_ratio = analysis_results["interview_score"]["ratio"]
        score_p = analysis_results["interview_score"]["p_value"]
        
        report.append("\n### Interview Score")
        report.append(f"- Privileged group: {analysis_results['interview_score']['by_group']['privileged']:.2f}")
        report.append(f"- Marginalized group: {analysis_results['interview_score']['by_group']['marginalized']:.2f}")
        report.append(f"- Difference: {score_diff:.2f}")
        report.append(f"- Ratio: {score_ratio:.2f}")
        report.append(f"- P-value: {score_p:.4f}")
        report.append(f"- Statistically significant: {score_p < 0.05}")
        
        # Results by characteristic
        report.append("\n## Results by Protected Characteristic")
        
        for characteristic, results in analysis_results["by_characteristic"].items():
            report.append(f"\n### {characteristic.capitalize()}")
            
            char_diff = results["selection_rate"]["difference"]
            char_ratio = results["selection_rate"]["ratio"]
            char_p = results["selection_rate"]["p_value"]
            
            report.append(f"- Privileged group: {results['selection_rate']['by_group']['privileged']:.2f}")
            report.append(f"- Marginalized group: {results['selection_rate']['by_group']['marginalized']:.2f}")
            report.append(f"- Difference: {char_diff:.2f}")
            report.append(f"- Ratio: {char_ratio:.2f}")
            report.append(f"- P-value: {char_p:.4f}")
            report.append(f"- Statistically significant: {char_p < 0.05}")
        
        # Compliance with Brazil's AI Act
        report.append("\n## Compliance with Brazil's AI Act")
        
        # Determine compliance based on analysis results
        has_significant_bias = (
            analysis_results["selection_rate"]["statistically_significant"] or
            analysis_results["interview_score"]["statistically_significant"]
        )
        
        if has_significant_bias:
            report.append("\n### Potential Non-Compliance Issues")
            report.append("The analysis detected statistically significant disparities in employment decisions, which may indicate non-compliance with Brazil's AI Act requirements for high-risk AI systems.")
            report.append("\nRecommended Actions:")
            report.append("1. Review the decision-making process for potential sources of bias")
            report.append("2. Implement bias mitigation measures")
            report.append("3. Conduct a more comprehensive Algorithmic Impact Assessment")
            report.append("4. Enhance transparency and explainability mechanisms")
        else:
            report.append("\n### Compliance Status")
            report.append("The analysis did not detect statistically significant disparities in employment decisions, suggesting potential compliance with Brazil's AI Act requirements for high-risk AI systems.")
            report.append("\nRecommended Actions:")
            report.append("1. Continue monitoring for potential bias")
            report.append("2. Regularly update the Algorithmic Impact Assessment")
            report.append("3. Maintain transparency and explainability mechanisms")
        
        # Save report to file
        report_text = "\n".join(report)
        output_path = os.path.join(self.output_dir, f"bias_report_{self.run_id}.md")
        with open(output_path, "w") as f:
            f.write(report_text)
        logger.info(f"Saved bias report to {output_path}")
        
        return report_text
        
    def run_evaluation(self, num_pairs: int = 100) -> Dict:
        """
        Run the full evaluation pipeline.

        Args:
            num_pairs: Number of application pairs to generate

        Returns:
            Dict: Dictionary with evaluation results
        """
        logger.info(f"Starting employment bias evaluation with {num_pairs} pairs")
        
        # Generate job applications
        applications = self.generate_job_applications(num_pairs)
        
        # Collect responses
        responses_df = self.collect_responses(applications)
        
        # Analyze bias
        analysis_results = self.analyze_bias(responses_df)
        
        # Generate report
        report = self.generate_report(analysis_results)
        
        logger.info("Employment bias evaluation completed")
        
        return {
            "applications": applications,
            "responses_df": responses_df,
            "analysis_results": analysis_results,
            "report": report
        }


if __name__ == "__main__":
    # Example usage
    evaluator = EmploymentBiasEvaluator("config.json")
    results = evaluator.run_evaluation(num_pairs=50)
    print(results["report"])