"""
brazil_aia_generator.py

This module provides tools for generating Algorithmic Impact Assessments (AIAs)
as required by Brazil's AI Act for high-risk AI systems.
"""

import os
import json
import logging
import time
import uuid
from typing import Dict, List, Any, Optional
import argparse

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    handlers=[
        logging.FileHandler("brazil_aia_generator.log"),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)


class BrazilAIAGenerator:
    """
    A class for generating Algorithmic Impact Assessments (AIAs)
    as required by Brazil's AI Act for high-risk AI systems.
    """

    def __init__(self, config_path: str = "config.json", bias_analysis_path: Optional[str] = None):
        """
        Initialize the BrazilAIAGenerator with configuration settings.

        Args:
            config_path: Path to the configuration file
            bias_analysis_path: Optional path to bias analysis results
        """
        self.config = self._load_config(config_path)
        self.run_id = self.config["experiment_settings"].get("run_id", str(uuid.uuid4()))
        self.output_dir = self.config["experiment_settings"].get("output_dir", "output")
        
        # Create output directory if it doesn't exist
        os.makedirs(self.output_dir, exist_ok=True)
        
        # Load bias analysis results if provided
        self.bias_analysis = None
        if bias_analysis_path:
            self.bias_analysis = self._load_bias_analysis(bias_analysis_path)
        
        logger.info(f"Initialized BrazilAIAGenerator with run_id: {self.run_id}")

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

    def _load_bias_analysis(self, bias_analysis_path: str) -> Dict:
        """
        Load bias analysis results from a JSON file.

        Args:
            bias_analysis_path: Path to the bias analysis results file

        Returns:
            Dict: Bias analysis results
        """
        try:
            with open(bias_analysis_path, "r") as f:
                bias_analysis = json.load(f)
            return bias_analysis
        except Exception as e:
            logger.error(f"Error loading bias analysis results: {e}")
            return None
            
    def generate_risk_assessment(self) -> Dict:
        """
        Generate a risk assessment for the AI system.

        Returns:
            Dict: Risk assessment results
        """
        risk_categories = self.config["aia_requirements"]["risk_assessment"]["categories"]
        severity_levels = self.config["aia_requirements"]["risk_assessment"]["severity_levels"]
        
        # Initialize risk assessment
        risk_assessment = {}
        
        # Assess risks based on bias analysis if available
        if self.bias_analysis:
            # Discrimination risk
            if "selection_rate" in self.bias_analysis and self.bias_analysis["selection_rate"]["statistically_significant"]:
                discrimination_severity = "High" if self.bias_analysis["selection_rate"]["difference"] > 0.2 else "Medium"
                risk_assessment["Discrimination Risk"] = {
                    "severity": discrimination_severity,
                    "description": f"Statistically significant disparities detected in selection rates (difference: {self.bias_analysis['selection_rate']['difference']:.2f})",
                    "impact": "Potential discrimination against marginalized groups in employment decisions",
                    "mitigation": "Implement bias detection and mitigation measures, review decision-making criteria"
                }
            else:
                risk_assessment["Discrimination Risk"] = {
                    "severity": "Low",
                    "description": "No statistically significant disparities detected in selection rates",
                    "impact": "Minimal risk of discrimination in employment decisions",
                    "mitigation": "Continue monitoring for potential bias"
                }
        else:
            # Default risk assessment if no bias analysis is available
            for category in risk_categories:
                risk_assessment[category] = {
                    "severity": "Medium",  # Default to medium severity
                    "description": f"Risk assessment for {category.lower()}",
                    "impact": f"Potential impact on {category.lower()}",
                    "mitigation": f"Implement measures to mitigate {category.lower()}"
                }
        
        # Add other risk categories
        if "Privacy Risk" not in risk_assessment:
            risk_assessment["Privacy Risk"] = {
                "severity": "Medium",
                "description": "Collection and processing of personal data for employment decisions",
                "impact": "Potential privacy violations and unauthorized data use",
                "mitigation": "Implement data minimization, encryption, and access controls"
            }
            
        if "Transparency Risk" not in risk_assessment:
            risk_assessment["Transparency Risk"] = {
                "severity": "Medium",
                "description": "Lack of transparency in decision-making processes",
                "impact": "Difficulty for individuals to understand and contest decisions",
                "mitigation": "Implement explainability mechanisms and provide clear information about decision factors"
            }
            
        if "Accountability Risk" not in risk_assessment:
            risk_assessment["Accountability Risk"] = {
                "severity": "Medium",
                "description": "Unclear responsibility for AI system decisions",
                "impact": "Difficulty in assigning responsibility for harmful outcomes",
                "mitigation": "Establish clear governance structures and accountability mechanisms"
            }
        
        return risk_assessment
        
    def generate_mitigation_measures(self, risk_assessment: Dict) -> List[Dict]:
        """
        Generate mitigation measures based on risk assessment.

        Args:
            risk_assessment: Risk assessment results

        Returns:
            List[Dict]: List of mitigation measures
        """
        mitigation_measures = []
        
        # Generate mitigation measures based on risk assessment
        for category, risk in risk_assessment.items():
            mitigation_measures.append({
                "risk_category": category,
                "risk_severity": risk["severity"],
                "measure": risk["mitigation"],
                "implementation_status": "Planned",
                "responsible_party": "AI System Owner",
                "timeline": "Q3 2023"
            })
        
        # Add additional mitigation measures from config
        for measure in self.config["aia_requirements"]["mitigation_measures"]:
            if not any(m["measure"] == measure for m in mitigation_measures):
                mitigation_measures.append({
                    "risk_category": "General",
                    "risk_severity": "Medium",
                    "measure": measure,
                    "implementation_status": "Planned",
                    "responsible_party": "AI System Owner",
                    "timeline": "Q4 2023"
                })
        
        return mitigation_measures
        
    def generate_aia_report(self) -> Dict:
        """
        Generate a complete Algorithmic Impact Assessment (AIA) report.

        Returns:
            Dict: Complete AIA report
        """
        # Generate risk assessment
        risk_assessment = self.generate_risk_assessment()
        
        # Generate mitigation measures
        mitigation_measures = self.generate_mitigation_measures(risk_assessment)
        
        # Compile AIA report
        aia_report = {
            "metadata": {
                "report_id": f"AIA-{self.run_id}",
                "date": time.strftime("%Y-%m-%d"),
                "version": "1.0",
                "system_name": "Employment Decision AI System",
                "system_purpose": "Automated screening and evaluation of job candidates",
                "system_owner": "Example Corporation",
                "report_author": "AI Ethics Team"
            },
            "system_description": {
                "functionality": "The system processes job applications and makes initial screening decisions based on candidate qualifications.",
                "data_sources": [
                    "Resumes and CVs",
                    "Cover letters",
                    "Application forms",
                    "Skills assessments"
                ],
                "decision_types": [
                    "Binary (accept/reject)",
                    "Scoring (qualification score)",
                    "Ranking (candidate ranking)"
                ],
                "deployment_context": "Human resources and recruitment",
                "human_oversight": "Human review of all rejection decisions"
            },
            "legal_basis": {
                "brazil_ai_act": {
                    "classification": "High-risk AI system (employment decisions)",
                    "applicable_articles": [
                        self.config["brazilian_regulatory_alignment"]["bias_mitigation_article"],
                        self.config["brazilian_regulatory_alignment"]["transparency_article"],
                        self.config["brazilian_regulatory_alignment"]["aia_article"]
                    ],
                    "compliance_status": "In progress"
                },
                "data_protection": {
                    "legal_basis_for_processing": "Legitimate interest",
                    "data_subject_rights": "Right to explanation, right to contest decisions",
                    "data_retention_policy": "Data retained for 6 months after decision"
                }
            },
            "risk_assessment": risk_assessment,
            "mitigation_measures": mitigation_measures,
            "monitoring_plan": {
                "metrics": [
                    "Selection rate disparities",
                    "Interview score disparities",
                    "Candidate satisfaction",
                    "Decision contestation rate"
                ],
                "frequency": "Monthly",
                "responsible_party": "AI Ethics Team",
                "reporting_mechanism": "Monthly compliance report"
            },
            "transparency_mechanisms": {
                "explanation_methods": [
                    "Factor-based explanations",
                    "Counterfactual explanations",
                    "Decision criteria disclosure"
                ],
                "contestation_process": "Online form with 30-day review period",
                "public_disclosure": self.config["aia_requirements"]["reporting_requirements"]["public_disclosure"]
            },
            "stakeholder_consultation": {
                "consulted_groups": [
                    "Job applicants",
                    "HR professionals",
                    "Civil society organizations",
                    "Data protection experts"
                ],
                "feedback_summary": "Stakeholders emphasized the importance of transparency and non-discrimination",
                "changes_made": "Enhanced explanation mechanisms and bias detection"
            }
        }
        
        # Save AIA report to file
        output_path = os.path.join(self.output_dir, f"aia_report_{self.run_id}.json")
        with open(output_path, "w") as f:
            json.dump(aia_report, f, indent=2)
        logger.info(f"Saved AIA report to {output_path}")
        
        return aia_report
        
    def generate_aia_markdown(self, aia_report: Dict) -> str:
        """
        Generate a markdown version of the AIA report.

        Args:
            aia_report: AIA report dictionary

        Returns:
            str: Markdown version of the AIA report
        """
        md = []
        
        # Title and metadata
        md.append(f"# Algorithmic Impact Assessment (AIA) Report")
        md.append(f"**Report ID:** {aia_report['metadata']['report_id']}")
        md.append(f"**Date:** {aia_report['metadata']['date']}")
        md.append(f"**Version:** {aia_report['metadata']['version']}")
        md.append(f"**System:** {aia_report['metadata']['system_name']}")
        md.append(f"**Owner:** {aia_report['metadata']['system_owner']}")
        md.append("")
        
        # System description
        md.append("## 1. System Description")
        md.append(f"**Purpose:** {aia_report['metadata']['system_purpose']}")
        md.append(f"**Functionality:** {aia_report['system_description']['functionality']}")
        md.append("")
        md.append("### Data Sources")
        for source in aia_report['system_description']['data_sources']:
            md.append(f"- {source}")
        md.append("")
        md.append("### Decision Types")
        for decision in aia_report['system_description']['decision_types']:
            md.append(f"- {decision}")
        md.append("")
        md.append(f"**Deployment Context:** {aia_report['system_description']['deployment_context']}")
        md.append(f"**Human Oversight:** {aia_report['system_description']['human_oversight']}")
        md.append("")
        
        # Legal basis
        md.append("## 2. Legal Basis")
        md.append("### Brazil AI Act")
        md.append(f"**Classification:** {aia_report['legal_basis']['brazil_ai_act']['classification']}")
        md.append("**Applicable Articles:**")
        for article in aia_report['legal_basis']['brazil_ai_act']['applicable_articles']:
            md.append(f"- {article}")
        md.append(f"**Compliance Status:** {aia_report['legal_basis']['brazil_ai_act']['compliance_status']}")
        md.append("")
        md.append("### Data Protection")
        md.append(f"**Legal Basis for Processing:** {aia_report['legal_basis']['data_protection']['legal_basis_for_processing']}")
        md.append(f"**Data Subject Rights:** {aia_report['legal_basis']['data_protection']['data_subject_rights']}")
        md.append(f"**Data Retention Policy:** {aia_report['legal_basis']['data_protection']['data_retention_policy']}")
        md.append("")
        
        # Risk assessment
        md.append("## 3. Risk Assessment")
        for category, risk in aia_report['risk_assessment'].items():
            md.append(f"### {category}")
            md.append(f"**Severity:** {risk['severity']}")
            md.append(f"**Description:** {risk['description']}")
            md.append(f"**Impact:** {risk['impact']}")
            md.append(f"**Mitigation:** {risk['mitigation']}")
            md.append("")
        
        # Mitigation measures
        md.append("## 4. Mitigation Measures")
        for measure in aia_report['mitigation_measures']:
            md.append(f"### {measure['measure']}")
            md.append(f"**Risk Category:** {measure['risk_category']}")
            md.append(f"**Risk Severity:** {measure['risk_severity']}")
            md.append(f"**Implementation Status:** {measure['implementation_status']}")
            md.append(f"**Responsible Party:** {measure['responsible_party']}")
            md.append(f"**Timeline:** {measure['timeline']}")
            md.append("")
        
        # Monitoring plan
        md.append("## 5. Monitoring Plan")
        md.append("### Metrics")
        for metric in aia_report['monitoring_plan']['metrics']:
            md.append(f"- {metric}")
        md.append("")
        md.append(f"**Frequency:** {aia_report['monitoring_plan']['frequency']}")
        md.append(f"**Responsible Party:** {aia_report['monitoring_plan']['responsible_party']}")
        md.append(f"**Reporting Mechanism:** {aia_report['monitoring_plan']['reporting_mechanism']}")
        md.append("")
        
        # Transparency mechanisms
        md.append("## 6. Transparency Mechanisms")
        md.append("### Explanation Methods")
        for method in aia_report['transparency_mechanisms']['explanation_methods']:
            md.append(f"- {method}")
        md.append("")
        md.append(f"**Contestation Process:** {aia_report['transparency_mechanisms']['contestation_process']}")
        md.append(f"**Public Disclosure:** {'Yes' if aia_report['transparency_mechanisms']['public_disclosure'] else 'No'}")
        md.append("")
        
        # Stakeholder consultation
        md.append("## 7. Stakeholder Consultation")
        md.append("### Consulted Groups")
        for group in aia_report['stakeholder_consultation']['consulted_groups']:
            md.append(f"- {group}")
        md.append("")
        md.append(f"**Feedback Summary:** {aia_report['stakeholder_consultation']['feedback_summary']}")
        md.append(f"**Changes Made:** {aia_report['stakeholder_consultation']['changes_made']}")
        
        # Save markdown to file
        md_text = "\n".join(md)
        output_path = os.path.join(self.output_dir, f"aia_report_{self.run_id}.md")
        with open(output_path, "w") as f:
            f.write(md_text)
        logger.info(f"Saved AIA markdown report to {output_path}")
        
        return md_text
        
    def generate_aia(self, output_format: str = "both") -> Dict:
        """
        Generate a complete AIA in the specified format.

        Args:
            output_format: Output format ("json", "markdown", or "both")

        Returns:
            Dict: AIA report and output paths
        """
        logger.info(f"Generating AIA report in {output_format} format")
        
        # Generate AIA report
        aia_report = self.generate_aia_report()
        
        # Generate markdown if requested
        md_text = None
        if output_format in ["markdown", "both"]:
            md_text = self.generate_aia_markdown(aia_report)
        
        logger.info("AIA generation completed")
        
        return {
            "aia_report": aia_report,
            "markdown": md_text,
            "json_path": os.path.join(self.output_dir, f"aia_report_{self.run_id}.json"),
            "markdown_path": os.path.join(self.output_dir, f"aia_report_{self.run_id}.md") if md_text else None
        }


def main():
    """Main function for command-line usage."""
    parser = argparse.ArgumentParser(description="Generate an Algorithmic Impact Assessment (AIA) for Brazil's AI Act compliance")
    parser.add_argument("--config", default="config.json", help="Path to configuration file")
    parser.add_argument("--bias-analysis", help="Path to bias analysis results file")
    parser.add_argument("--output", default="both", choices=["json", "markdown", "both"], help="Output format")
    parser.add_argument("--output-dir", help="Output directory")
    args = parser.parse_args()
    
    # Initialize AIA generator
    generator = BrazilAIAGenerator(args.config, args.bias_analysis)
    
    # Set output directory if provided
    if args.output_dir:
        generator.output_dir = args.output_dir
        os.makedirs(args.output_dir, exist_ok=True)
    
    # Generate AIA
    result = generator.generate_aia(args.output)
    
    print(f"AIA generation completed.")
    print(f"JSON report saved to: {result['json_path']}")
    if result['markdown_path']:
        print(f"Markdown report saved to: {result['markdown_path']}")


if __name__ == "__main__":
    main()