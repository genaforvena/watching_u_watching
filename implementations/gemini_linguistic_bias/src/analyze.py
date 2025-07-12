# analyze.py
"""
Analysis module for the Gemini linguistic bias audit.

This script:
1. Loads the results from the audit
2. Performs statistical analysis on the results
3. Generates visualizations
4. Saves the analysis results
"""

import os
import json
import argparse
import logging
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
from scipy import stats
import ptitprince as pt
from typing import Dict, Any, List, Tuple, Optional

# Set up logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler("analysis.log"),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)


class BiasAnalyzer:
    """Class for analyzing bias in the audit results."""
    
    def __init__(self, config_path: str = None):
        """Initialize the analyzer with configuration."""
        # Load configuration
        if config_path and os.path.exists(config_path):
            with open(config_path, 'r') as f:
                self.config = json.load(f)
        else:
            # Default configuration
            self.config = {
                "analysis": {
                    "metrics": ["response_length", "sentiment_score", "refusal_rate", "latency"],
                    "significance_threshold": 0.05,
                    "visualization": {
                        "raincloud_height": 8,
                        "raincloud_width": 12,
                        "color_palette": ["#4C72B0", "#DD8452", "#55A868", "#C44E52"]
                    }
                },
                "output": {
                    "results_dir": "./results",
                    "data_filename": "gemini_bias_results.parquet",
                    "figures_dir": "./figures"
                }
            }
        
        # Create figures directory if it doesn't exist
        os.makedirs(os.path.join(self.config["output"]["results_dir"], self.config["output"]["figures_dir"]), exist_ok=True)
    
    def load_data(self, file_path: Optional[str] = None) -> pd.DataFrame:
        """Load the audit results data."""
        if file_path is None:
            file_path = os.path.join(self.config["output"]["results_dir"], self.config["output"]["data_filename"])
        
        logger.info(f"Loading data from {file_path}")
        df = pd.read_parquet(file_path)
        logger.info(f"Loaded {len(df)} records")
        
        return df
    
    def compute_statistics(self, df: pd.DataFrame) -> Dict[str, Any]:
        """Compute statistics on the audit results."""
        stats_results = {}
        
        # Compute statistics for English level (perfect vs. L2)
        stats_results["english_level"] = self._compute_group_statistics(
            df, "english_level", ["perfect", "L2"]
        )
        
        # Compute statistics for name type (anglo vs. non_anglo)
        stats_results["name_type"] = self._compute_group_statistics(
            df, "name_type", ["anglo", "non_anglo"]
        )
        
        # Compute statistics for interaction effects
        stats_results["interaction"] = self._compute_interaction_statistics(df)
        
        return stats_results
    
    def _compute_group_statistics(self, df: pd.DataFrame, group_col: str, group_values: List[str]) -> Dict[str, Any]:
        """Compute statistics comparing two groups."""
        results = {}
        
        for metric in self.config["analysis"]["metrics"]:
            if metric == "refusal_rate":
                # For refusal rate, we need to compute the mean of the refusal column
                group1_data = df[df[group_col] == group_values[0]]["refusal"].astype(int)
                group2_data = df[df[group_col] == group_values[1]]["refusal"].astype(int)
            else:
                group1_data = df[df[group_col] == group_values[0]][metric]
                group2_data = df[df[group_col] == group_values[1]][metric]
            
            # Compute basic statistics
            group1_mean = group1_data.mean()
            group2_mean = group2_data.mean()
            group1_std = group1_data.std()
            group2_std = group2_data.std()
            
            # Compute t-test
            t_stat, p_value = stats.ttest_ind(
                group1_data.dropna(),
                group2_data.dropna(),
                equal_var=False  # Welch's t-test
            )
            
            # Compute Cohen's d effect size
            pooled_std = np.sqrt((group1_std**2 + group2_std**2) / 2)
            cohens_d = (group1_mean - group2_mean) / pooled_std if pooled_std != 0 else 0
            
            # Determine significance
            significant = p_value < self.config["analysis"]["significance_threshold"]
            
            results[metric] = {
                f"{group_values[0]}_mean": group1_mean,
                f"{group_values[1]}_mean": group2_mean,
                f"{group_values[0]}_std": group1_std,
                f"{group_values[1]}_std": group2_std,
                "difference": group1_mean - group2_mean,
                "percent_difference": ((group1_mean - group2_mean) / group1_mean) * 100 if group1_mean != 0 else 0,
                "t_statistic": t_stat,
                "p_value": p_value,
                "cohens_d": cohens_d,
                "significant": significant
            }
        
        return results