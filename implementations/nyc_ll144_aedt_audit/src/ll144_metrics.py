#!/usr/bin/env python3
"""
LL144 Metrics Calculator for NYC Local Law 144 Audits.

This module calculates metrics required by NYC Local Law 144 for bias auditing
of Automated Employment Decision Tools (AEDTs).
"""

import logging
import math
from typing import Dict, List, Optional, Tuple, Union

import numpy as np
import scipy.stats as stats

# Configure logging
logger = logging.getLogger(__name__)


class LL144MetricsCalculator:
    """Calculates metrics required by NYC Local Law 144 for bias auditing."""
    
    def __init__(
        self,
        metrics: Dict[str, bool],
        thresholds: Dict[str, float]
    ):
        """Initialize the metrics calculator.
        
        Args:
            metrics: Dict of metrics to calculate
            thresholds: Dict of thresholds for metrics
        """
        self.metrics = metrics
        self.thresholds = thresholds
        
        logger.info(f"Initialized LL144MetricsCalculator with metrics: {metrics}")
    
    def calculate_disparate_impact_ratio(
        self,
        selection_rates: Dict[str, Tuple[int, int]]
    ) -> Dict[str, Dict[str, float]]:
        """Calculate disparate impact ratio.
        
        Args:
            selection_rates: Dict mapping group names to tuples of (selected, total)
            
        Returns:
            Dict mapping group pairs to disparate impact ratios
        """
        # Calculate selection rate for each group
        rates = {}
        for group, (selected, total) in selection_rates.items():
            if total == 0:
                rates[group] = 0.0
            else:
                rates[group] = selected / total
        
        # Find the group with the highest selection rate
        reference_group = max(rates.items(), key=lambda x: x[1])
        reference_name, reference_rate = reference_group
        
        # Calculate disparate impact ratio for each group
        ratios = {}
        for group, rate in rates.items():
            if group == reference_name:
                continue
                
            if reference_rate == 0:
                ratio = float('inf') if rate > 0 else 1.0
            else:
                ratio = rate / reference_rate
                
            ratios[f"{group}_vs_{reference_name}"] = {
                "ratio": ratio,
                "adverse_impact": ratio < self.thresholds["disparate_impact"]
            }
        
        return ratios
    
    def calculate_statistical_significance(
        self,
        selection_rates: Dict[str, Tuple[int, int]]
    ) -> Dict[str, Dict[str, float]]:
        """Calculate statistical significance of disparate impact.
        
        Args:
            selection_rates: Dict mapping group names to tuples of (selected, total)
            
        Returns:
            Dict mapping group pairs to p-values
        """
        results = {}
        groups = list(selection_rates.keys())
        
        for i in range(len(groups)):
            for j in range(i + 1, len(groups)):
                group1 = groups[i]
                group2 = groups[j]
                
                selected1, total1 = selection_rates[group1]
                selected2, total2 = selection_rates[group2]
                
                # Fisher's exact test
                table = [[selected1, total1 - selected1], [selected2, total2 - selected2]]
                odds_ratio, p_value = stats.fisher_exact(table)
                
                results[f"{group1}_vs_{group2}"] = {
                    "p_value": p_value,
                    "significant": p_value < self.thresholds["p_value"],
                    "odds_ratio": odds_ratio
                }
        
        return results
    
    def calculate_confidence_intervals(
        self,
        selection_rates: Dict[str, Tuple[int, int]]
    ) -> Dict[str, Dict[str, float]]:
        """Calculate confidence intervals for selection rates.
        
        Args:
            selection_rates: Dict mapping group names to tuples of (selected, total)
            
        Returns:
            Dict mapping groups to confidence intervals
        """
        results = {}
        confidence_level = self.thresholds["confidence_level"]
        z_score = stats.norm.ppf((1 + confidence_level) / 2)
        
        for group, (selected, total) in selection_rates.items():
            if total == 0:
                results[group] = {
                    "rate": 0.0,
                    "lower_bound": 0.0,
                    "upper_bound": 0.0,
                    "confidence_level": confidence_level
                }
                continue
                
            rate = selected / total
            
            # Wilson score interval
            denominator = 1 + z_score**2 / total
            center = (rate + z_score**2 / (2 * total)) / denominator
            margin = z_score * math.sqrt(rate * (1 - rate) / total + z_score**2 / (4 * total**2)) / denominator
            
            lower_bound = max(0, center - margin)
            upper_bound = min(1, center + margin)
            
            results[group] = {
                "rate": rate,
                "lower_bound": lower_bound,
                "upper_bound": upper_bound,
                "confidence_level": confidence_level
            }
        
        return results
    
    def calculate_all_metrics(
        self,
        selection_rates: Dict[str, Tuple[int, int]]
    ) -> Dict[str, Dict]:
        """Calculate all requested metrics.
        
        Args:
            selection_rates: Dict mapping group names to tuples of (selected, total)
            
        Returns:
            Dict of all calculated metrics
        """
        results = {
            "selection_rates": {
                group: {
                    "selected": selected,
                    "total": total,
                    "rate": selected / total if total > 0 else 0.0
                }
                for group, (selected, total) in selection_rates.items()
            }
        }
        
        if self.metrics.get("disparate_impact_ratio", False):
            results["disparate_impact"] = self.calculate_disparate_impact_ratio(selection_rates)
            
        if self.metrics.get("statistical_significance", False):
            results["statistical_significance"] = self.calculate_statistical_significance(selection_rates)
            
        if self.metrics.get("confidence_intervals", False):
            results["confidence_intervals"] = self.calculate_confidence_intervals(selection_rates)
        
        return results
    
    def format_ll144_report(
        self,
        metrics_results: Dict[str, Dict],
        audit_metadata: Dict
    ) -> Dict:
        """Format metrics results as an LL144-compliant report.
        
        Args:
            metrics_results: Dict of calculated metrics
            audit_metadata: Dict of audit metadata
            
        Returns:
            Dict formatted as an LL144-compliant report
        """
        # Extract basic information
        selection_rates = metrics_results["selection_rates"]
        disparate_impact = metrics_results.get("disparate_impact", {})
        
        # Format the report according to LL144 requirements
        report = {
            "audit_metadata": {
                "audit_date": audit_metadata.get("audit_date", ""),
                "audit_provider": "watching_u_watching (Open Source)",
                "aedt_name": audit_metadata.get("aedt_name", ""),
                "aedt_version": audit_metadata.get("aedt_version", ""),
                "methodology": "Automated correspondence testing with synthetic applications"
            },
            "summary": {
                "disparate_impact_detected": any(
                    impact.get("adverse_impact", False)
                    for impact in disparate_impact.values()
                ),
                "protected_characteristics_tested": list(selection_rates.keys()),
                "sample_size": sum(data["total"] for data in selection_rates.values())
            },
            "detailed_results": {
                "selection_rates": {
                    group: {
                        "selected": data["selected"],
                        "total": data["total"],
                        "rate": data["rate"]
                    }
                    for group, data in selection_rates.items()
                },
                "disparate_impact": {
                    pair: {
                        "ratio": impact["ratio"],
                        "adverse_impact": impact["adverse_impact"],
                        "threshold": self.thresholds["disparate_impact"]
                    }
                    for pair, impact in disparate_impact.items()
                }
            }
        }
        
        # Add statistical significance if available
        if "statistical_significance" in metrics_results:
            report["detailed_results"]["statistical_significance"] = {
                pair: {
                    "p_value": sig["p_value"],
                    "significant": sig["significant"],
                    "threshold": self.thresholds["p_value"]
                }
                for pair, sig in metrics_results["statistical_significance"].items()
            }
        
        # Add confidence intervals if available
        if "confidence_intervals" in metrics_results:
            report["detailed_results"]["confidence_intervals"] = {
                group: {
                    "lower_bound": ci["lower_bound"],
                    "upper_bound": ci["upper_bound"],
                    "confidence_level": ci["confidence_level"]
                }
                for group, ci in metrics_results["confidence_intervals"].items()
            }
        
        return report


if __name__ == "__main__":
    # Simple demonstration
    logging.basicConfig(level=logging.INFO)
    
    calculator = LL144MetricsCalculator(
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
    
    # Example selection rates: (selected, total)
    selection_rates = {
        "white": (80, 100),
        "black": (60, 100),
        "hispanic": (70, 100),
        "asian": (75, 100)
    }
    
    results = calculator.calculate_all_metrics(selection_rates)
    
    print("Selection Rates:")
    for group, data in results["selection_rates"].items():
        print(f"  {group}: {data['selected']}/{data['total']} = {data['rate']:.2f}")
    
    print("\nDisparate Impact:")
    for pair, impact in results["disparate_impact"].items():
        print(f"  {pair}: {impact['ratio']:.2f} (Adverse Impact: {impact['adverse_impact']})")
    
    print("\nStatistical Significance:")
    for pair, sig in results["statistical_significance"].items():
        print(f"  {pair}: p={sig['p_value']:.4f} (Significant: {sig['significant']})")
    
    print("\nConfidence Intervals:")
    for group, ci in results["confidence_intervals"].items():
        print(f"  {group}: {ci['rate']:.2f} [{ci['lower_bound']:.2f}, {ci['upper_bound']:.2f}]")