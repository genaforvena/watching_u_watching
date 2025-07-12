#!/usr/bin/env python3
"""
Response Analyzer for NYC Local Law 144 Audits.

This module analyzes responses from Automated Employment Decision Tools (AEDTs)
to detect bias in compliance with NYC Local Law 144.
"""

import json
import logging
from collections import defaultdict
from datetime import datetime
from typing import Dict, List, Optional, Tuple, Union

import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
import seaborn as sns

from .ll144_metrics import LL144MetricsCalculator

# Configure logging
logger = logging.getLogger(__name__)


class ResponseAnalyzer:
    """Analyzes responses from AEDTs to detect bias."""
    
    def __init__(
        self,
        metrics_calculator: LL144MetricsCalculator,
        output_format: str = "ll144_compliant"
    ):
        """Initialize the response analyzer.
        
        Args:
            metrics_calculator: Calculator for LL144 metrics
            output_format: Format for analysis output
        """
        self.metrics_calculator = metrics_calculator
        self.output_format = output_format
        
        logger.info(f"Initialized ResponseAnalyzer with output format: {output_format}")
    
    def analyze_responses(self, responses: List[Dict]) -> Dict:
        """Analyze responses from AEDTs to detect bias.
        
        Args:
            responses: List of response dictionaries
            
        Returns:
            Dict of analysis results
        """
        logger.info(f"Analyzing {len(responses)} responses")
        
        # Group responses by protected characteristic
        grouped_responses = self._group_responses_by_characteristic(responses)
        
        # Calculate selection rates for each group
        selection_rates = self._calculate_selection_rates(grouped_responses)
        
        # Calculate metrics
        metrics_results = self.metrics_calculator.calculate_all_metrics(selection_rates)
        
        # Add metadata
        analysis_results = {
            "metadata": {
                "analysis_date": datetime.now().isoformat(),
                "num_responses": len(responses),
                "num_groups": len(grouped_responses)
            },
            "metrics": metrics_results
        }
        
        logger.info(f"Analysis complete with {len(metrics_results)} metrics")
        return analysis_results
    
    def _group_responses_by_characteristic(self, responses: List[Dict]) -> Dict[str, List[Dict]]:
        """Group responses by protected characteristic.
        
        Args:
            responses: List of response dictionaries
            
        Returns:
            Dict mapping characteristic values to lists of responses
        """
        grouped = defaultdict(list)
        
        for response in responses:
            # Extract the protected characteristic from the probe content
            probe = response.get("probe", {})
            content = probe.get("content", {})
            personal_info = content.get("personal_info", {})
            
            # Check for race/ethnicity
            if "race_ethnicity" in personal_info:
                group = f"race_{personal_info['race_ethnicity']}"
                grouped[group].append(response)
            
            # Check for gender
            if "gender" in personal_info:
                group = f"gender_{personal_info['gender']}"
                grouped[group].append(response)
            
            # Check for intersectional characteristics
            if "race_ethnicity" in personal_info and "gender" in personal_info:
                group = f"intersect_{personal_info['race_ethnicity']}_{personal_info['gender']}"
                grouped[group].append(response)
        
        return dict(grouped)
    
    def _calculate_selection_rates(self, grouped_responses: Dict[str, List[Dict]]) -> Dict[str, Tuple[int, int]]:
        """Calculate selection rates for each group.
        
        Args:
            grouped_responses: Dict mapping characteristic values to lists of responses
            
        Returns:
            Dict mapping characteristic values to tuples of (selected, total)
        """
        selection_rates = {}
        
        for group, responses in grouped_responses.items():
            total = len(responses)
            selected = sum(1 for r in responses if self._is_selected(r))
            selection_rates[group] = (selected, total)
        
        return selection_rates
    
    def _is_selected(self, response: Dict) -> bool:
        """Determine if a response indicates selection.
        
        Args:
            response: Response dictionary
            
        Returns:
            True if the response indicates selection, False otherwise
        """
        # This is a placeholder for a more sophisticated selection determination
        # In a real implementation, this would be based on the specific AEDT response format
        
        # Check for explicit selection status
        if "selected" in response:
            return response["selected"]
        
        # Check for response type
        response_type = response.get("response_type", "").lower()
        if response_type in ["accepted", "interview", "shortlisted", "selected"]:
            return True
        if response_type in ["rejected", "declined", "not_selected"]:
            return False
        
        # Check for response content
        content = response.get("content", "").lower()
        positive_indicators = ["interview", "next step", "selected", "congratulations", "proceed"]
        negative_indicators = ["regret", "unfortunately", "not proceed", "other candidates", "not selected"]
        
        if any(indicator in content for indicator in positive_indicators):
            return True
        if any(indicator in content for indicator in negative_indicators):
            return False
        
        # Default to not selected if we can't determine
        return False
    
    def generate_report(self, analysis_results: Dict) -> Dict:
        """Generate a report from analysis results.
        
        Args:
            analysis_results: Dict of analysis results
            
        Returns:
            Dict containing the report
        """
        if self.output_format == "ll144_compliant":
            return self._generate_ll144_report(analysis_results)
        else:
            return self._generate_standard_report(analysis_results)
    
    def _generate_ll144_report(self, analysis_results: Dict) -> Dict:
        """Generate an LL144-compliant report.
        
        Args:
            analysis_results: Dict of analysis results
            
        Returns:
            Dict containing the LL144-compliant report
        """
        audit_metadata = {
            "audit_date": analysis_results["metadata"]["analysis_date"],
            "aedt_name": "Example AEDT",  # This would come from configuration
            "aedt_version": "1.0"  # This would come from configuration
        }
        
        return self.metrics_calculator.format_ll144_report(
            analysis_results["metrics"],
            audit_metadata
        )
    
    def _generate_standard_report(self, analysis_results: Dict) -> Dict:
        """Generate a standard report.
        
        Args:
            analysis_results: Dict of analysis results
            
        Returns:
            Dict containing the standard report
        """
        # Extract metrics
        metrics = analysis_results["metrics"]
        selection_rates = metrics["selection_rates"]
        disparate_impact = metrics.get("disparate_impact", {})
        
        # Generate summary
        summary = {
            "date": analysis_results["metadata"]["analysis_date"],
            "sample_size": analysis_results["metadata"]["num_responses"],
            "groups_analyzed": list(selection_rates.keys()),
            "disparate_impact_detected": any(
                impact.get("adverse_impact", False)
                for impact in disparate_impact.values()
            )
        }
        
        # Generate detailed results
        detailed_results = {
            "selection_rates": {
                group: {
                    "selected": data["selected"],
                    "total": data["total"],
                    "rate": data["rate"]
                }
                for group, data in selection_rates.items()
            }
        }
        
        # Add disparate impact if available
        if disparate_impact:
            detailed_results["disparate_impact"] = {
                pair: {
                    "ratio": impact["ratio"],
                    "adverse_impact": impact["adverse_impact"]
                }
                for pair, impact in disparate_impact.items()
            }
        
        # Add statistical significance if available
        if "statistical_significance" in metrics:
            detailed_results["statistical_significance"] = {
                pair: {
                    "p_value": sig["p_value"],
                    "significant": sig["significant"]
                }
                for pair, sig in metrics["statistical_significance"].items()
            }
        
        # Add confidence intervals if available
        if "confidence_intervals" in metrics:
            detailed_results["confidence_intervals"] = {
                group: {
                    "lower_bound": ci["lower_bound"],
                    "upper_bound": ci["upper_bound"]
                }
                for group, ci in metrics["confidence_intervals"].items()
            }
        
        return {
            "summary": summary,
            "detailed_results": detailed_results
        }
    
    def generate_visualizations(self, analysis_results: Dict, output_dir: str) -> List[str]:
        """Generate visualizations from analysis results.
        
        Args:
            analysis_results: Dict of analysis results
            output_dir: Directory to save visualizations
            
        Returns:
            List of paths to generated visualizations
        """
        import os
        import matplotlib.pyplot as plt
        import seaborn as sns
        
        os.makedirs(output_dir, exist_ok=True)
        
        # Extract metrics
        metrics = analysis_results["metrics"]
        selection_rates = metrics["selection_rates"]
        
        # Create a DataFrame for easier plotting
        df = pd.DataFrame([
            {
                "group": group,
                "selection_rate": data["rate"],
                "selected": data["selected"],
                "total": data["total"]
            }
            for group, data in selection_rates.items()
        ])
        
        # Generate selection rate bar chart
        plt.figure(figsize=(10, 6))
        sns.barplot(x="group", y="selection_rate", data=df)
        plt.title("Selection Rates by Group")
        plt.xlabel("Group")
        plt.ylabel("Selection Rate")
        plt.xticks(rotation=45)
        plt.tight_layout()
        
        selection_rate_path = os.path.join(output_dir, "selection_rates.png")
        plt.savefig(selection_rate_path)
        plt.close()
        
        # Generate disparate impact visualization if available
        if "disparate_impact" in metrics:
            disparate_impact = metrics["disparate_impact"]
            
            df_impact = pd.DataFrame([
                {
                    "comparison": pair,
                    "ratio": impact["ratio"],
                    "adverse_impact": impact["adverse_impact"]
                }
                for pair, impact in disparate_impact.items()
            ])
            
            plt.figure(figsize=(10, 6))
            bars = sns.barplot(x="comparison", y="ratio", data=df_impact)
            
            # Add a horizontal line at the threshold
            threshold = self.metrics_calculator.thresholds["disparate_impact"]
            plt.axhline(y=threshold, color='r', linestyle='-', label=f"Threshold ({threshold})")
            
            # Color bars based on adverse impact
            for i, adverse_impact in enumerate(df_impact["adverse_impact"]):
                bars.patches[i].set_facecolor("red" if adverse_impact else "green")
            
            plt.title("Disparate Impact Ratios")
            plt.xlabel("Comparison")
            plt.ylabel("Ratio")
            plt.xticks(rotation=45)
            plt.legend()
            plt.tight_layout()
            
            disparate_impact_path = os.path.join(output_dir, "disparate_impact.png")
            plt.savefig(disparate_impact_path)
            plt.close()
            
            return [selection_rate_path, disparate_impact_path]
        
        return [selection_rate_path]


if __name__ == "__main__":
    # Simple demonstration
    logging.basicConfig(level=logging.INFO)
    
    from .ll144_metrics import LL144MetricsCalculator
    
    metrics_calculator = LL144MetricsCalculator(
        metrics={
            "disparate_impact_ratio": True,
            "statistical_significance": True,
            "confidence_intervals": True
        },
        thresholds={
            "disparate_impact": 0.8,
            "p_value": 0.05,
            "confidence_level": 0.95
        }
    )
    
    analyzer = ResponseAnalyzer(
        metrics_calculator=metrics_calculator,
        output_format="ll144_compliant"
    )
    
    # Example responses
    responses = [
        {"probe": {"content": {"personal_info": {"race_ethnicity": "white"}}}, "selected": True},
        {"probe": {"content": {"personal_info": {"race_ethnicity": "white"}}}, "selected": True},
        {"probe": {"content": {"personal_info": {"race_ethnicity": "white"}}}, "selected": True},
        {"probe": {"content": {"personal_info": {"race_ethnicity": "white"}}}, "selected": False},
        {"probe": {"content": {"personal_info": {"race_ethnicity": "black"}}}, "selected": True},
        {"probe": {"content": {"personal_info": {"race_ethnicity": "black"}}}, "selected": False},
        {"probe": {"content": {"personal_info": {"race_ethnicity": "black"}}}, "selected": False},
        {"probe": {"content": {"personal_info": {"race_ethnicity": "black"}}}, "selected": False},
    ]
    
    analysis_results = analyzer.analyze_responses(responses)
    report = analyzer.generate_report(analysis_results)
    
    print(json.dumps(report, indent=2))