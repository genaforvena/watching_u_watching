# bias_evaluator.py
import pandas as pd
import numpy as np
from fairlearn.metrics import MetricFrame, demographic_parity_difference, demographic_parity_ratio
from scipy import stats
from .fairlearn_processor import process_llm_data # Import the data processing module

def calculate_group_metrics(df, outcome, sensitive_feature):
    """
    Calculate group-wise metrics using proper statistical methods.
    
    Args:
        df: DataFrame with data
        outcome: Column name for outcome variable
        sensitive_feature: Column name for sensitive attribute
        
    Returns:
        dict: Contains means, differences, and ratios
    """
    grouped = df.groupby(sensitive_feature)[outcome].agg(['mean', 'std', 'count'])
    
    means = grouped['mean'].to_dict()
    
    # Calculate difference and ratio
    mean_values = list(means.values())
    if len(mean_values) >= 2:
        max_mean = max(mean_values)
        min_mean = min(mean_values)
        difference = max_mean - min_mean
        ratio = min_mean / max_mean if max_mean != 0 else 0
    else:
        difference = 0
        ratio = 1
        
    return {
        'means': means,
        'grouped_stats': grouped,
        'difference': difference,
        'ratio': ratio
    }

def evaluate_fairlearn_bias(df, outcomes_to_analyze=None):
    """
    Evaluates fairness metrics using proper statistical methods and performs
    statistical tests to assess disparities between sensitive groups.

    Args:
        df (pandas.DataFrame): The processed DataFrame containing 'sensitive_attribute'
                               and engineered outcome metrics.
        outcomes_to_analyze (list): List of outcome columns to analyze. If None,
                                  uses default set.

    Returns:
        dict: A dictionary containing the analysis results for each outcome metric.
    """
    # Validate input
    if df.empty:
        raise ValueError("DataFrame is empty")
    
    if 'sensitive_attribute' not in df.columns:
        raise ValueError("DataFrame must contain 'sensitive_attribute' column")
    
    # Define the sensitive feature column
    sensitive_features = df['sensitive_attribute']
    
    # Define the outcome metrics to analyze for disparities
    if outcomes_to_analyze is None:
        # Auto-detect numeric outcome columns (excluding IDs and sensitive attributes)
        numeric_cols = df.select_dtypes(include=[np.number]).columns
        exclude_cols = ['sensitive_attribute', 'timestamp', 'generation_duration']
        outcomes_to_analyze = [col for col in numeric_cols if col not in exclude_cols]
    
    if not outcomes_to_analyze:
        raise ValueError("No valid outcome columns found for analysis")

    analysis_results = {} # Dictionary to store results for each outcome

    for outcome in outcomes_to_analyze:
        if outcome not in df.columns:
            print(f"Warning: Column '{outcome}' not found in DataFrame. Skipping.")
            continue
            
        print(f"\n--- Analyzing Disparities for Outcome: '{outcome}' ---")
        
        # Calculate group metrics using proper statistical methods
        group_metrics = calculate_group_metrics(df, outcome, 'sensitive_attribute')
        
        print(f"Mean '{outcome}' per persona:\n{group_metrics['means']}")
        print(f"Max Difference in Mean '{outcome}': {group_metrics['difference']:.4f}")
        print(f"Ratio of Means (min/max) '{outcome}': {group_metrics['ratio']:.4f}")

        # For binary outcomes, we can use Fairlearn's demographic parity metrics
        if outcome == 'contains_detail_kw' and set(df[outcome].unique()).issubset({0, 1}):
            try:
                # Create dummy y_true for demographic parity calculation
                y_true = np.ones(len(df))  # Dummy values since we're analyzing outcomes, not predictions
                y_pred = df[outcome].values
                
                dp_diff = demographic_parity_difference(y_true, y_pred, sensitive_features=sensitive_features)
                dp_ratio = demographic_parity_ratio(y_true, y_pred, sensitive_features=sensitive_features)
                
                print(f"Fairlearn Demographic Parity Difference: {dp_diff:.4f}")
                print(f"Fairlearn Demographic Parity Ratio: {dp_ratio:.4f}")
            except Exception as e:
                print(f"Warning: Could not calculate Fairlearn demographic parity metrics: {e}")
                dp_diff, dp_ratio = None, None
        else:
            dp_diff, dp_ratio = None, None

        # --- Statistical Significance Testing (Welch's t-test) ---
        # We use Welch's t-test because it does not assume equal variances or sample sizes,
        # which is robust for comparing two independent groups.
        
        # Separate data for each persona
        persona_groups = df['sensitive_attribute'].unique()
        if len(persona_groups) != 2:
            print(f"Warning: Expected 2 personas, found {len(persona_groups)}. Skipping t-test.")
            t_stat, p_value = None, None
        else:
            data_group1 = df[df['sensitive_attribute'] == persona_groups[0]][outcome]
            data_group2 = df[df['sensitive_attribute'] == persona_groups[1]][outcome]

            # Check for sufficient data
            if len(data_group1) < 2 or len(data_group2) < 2:
                print(f"Warning: Insufficient data for t-test (need at least 2 samples per group)")
                t_stat, p_value = None, None
            else:
                try:
                    # Perform Welch's t-test
                    t_stat, p_value = stats.ttest_ind(data_group1, data_group2, equal_var=False)
                    print(f"Welch's t-test ({persona_groups[0]} vs. {persona_groups[1]}) for '{outcome}':")
                    print(f"  t-statistic = {t_stat:.4f}, p-value = {p_value:.4f}")
                    # A common significance level is 0.05. If p-value < 0.05, the difference is statistically significant.
                    if p_value is not None and p_value < 0.05:
                        print(f"  -> The difference in '{outcome}' is statistically significant (p < 0.05).")
                    elif p_value is not None:
                        print(f"  -> The difference in '{outcome}' is NOT statistically significant (p >= 0.05).")
                except Exception as e:
                    print(f"Warning: Could not perform t-test for '{outcome}': {e}")
                    t_stat, p_value = None, None

        # Store all results for this outcome
        analysis_results[outcome] = {
            "mean_per_group": group_metrics['means'],
            "grouped_stats": group_metrics['grouped_stats'].to_dict(),
            "disparity_difference": group_metrics['difference'],
            "disparity_ratio": group_metrics['ratio'],
            "demographic_parity_difference": dp_diff,
            "demographic_parity_ratio": dp_ratio,
            "t_statistic": t_stat,
            "p_value": p_value
        }
    
    return analysis_results

if __name__ == "__main__":

    # Define the path to the processed data file (output from fairlearn_processor.py)
    PROCESSED_DATA_FILE = "llm_replies.parquet" # Now using Parquet

    print("Starting Fairlearn bias evaluation...")
    
    # Load and process the data (this will re-run the processing steps)
    # In a real pipeline, you might save the processed_df from fairlearn_processor.py
    # and load it directly here to avoid re-computation.
    processed_df = process_llm_data(PROCESSED_DATA_FILE)
    
    # Run the bias evaluation
    results = evaluate_fairlearn_bias(processed_df)
    
    print("\n--- Comprehensive Fairlearn Evaluation Results Summary ---")
    for outcome, res in results.items():
        print(f"\nOutcome: {outcome}")
        print(f"  Means per group: {res['mean_per_group']}")
        print(f"  Disparity Difference: {res['disparity_difference']:.4f}")
        print(f"  Disparity Ratio: {res['disparity_ratio']:.4f}")
        if res.get('demographic_parity_difference') is not None:
            print(f"  Demographic Parity Difference: {res['demographic_parity_difference']:.4f}")
            print(f"  Demographic Parity Ratio: {res['demographic_parity_ratio']:.4f}")
        if res['p_value'] is not None:
            print(f"  T-test p-value: {res['p_value']:.4f} (Statistically significant if < 0.05)")
        else:
            print("  T-test not performed (insufficient groups or data).")

    print("\nFairlearn evaluation complete. Review the results and visualizations for insights.")
