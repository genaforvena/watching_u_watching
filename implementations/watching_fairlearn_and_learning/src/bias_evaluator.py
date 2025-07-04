# bias_evaluator.py
import pandas as pd
from fairlearn.metrics import MetricFrame, count, mean
from scipy import stats
from fairlearn_processor import process_llm_data # Import the data processing module

def evaluate_fairlearn_bias(df):
    """
    Evaluates fairness metrics using Fairlearn's MetricFrame and performs
    statistical tests to assess disparities between sensitive groups.

    Args:
        df (pandas.DataFrame): The processed DataFrame containing 'sensitive_attribute'
                               and engineered outcome metrics.

    Returns:
        dict: A dictionary containing the analysis results for each outcome metric.
    """
    # Define the sensitive feature column
    sensitive_features = df['sensitive_attribute']
    
    # Define the outcome metrics to analyze for disparities
    # These are the numerical features extracted in fairlearn_processor.py
    outcomes_to_analyze = ['reply_length', 'sentiment_score', 'formality_score', 'contains_detail_kw']

    analysis_results = {} # Dictionary to store results for each outcome

    for outcome in outcomes_to_analyze:
        print(f"\n--- Analyzing Disparities for Outcome: '{outcome}' ---")
        
        # Fairlearn's MetricFrame requires y_true and y_pred.
        # When analyzing the outcome directly (e.g., reply_length based on persona),
        # the outcome itself serves as the 'y_true' and 'y_pred' for the metric calculation.
        y_data = df[outcome]

        # Use MetricFrame to calculate the mean of the outcome for each sensitive group
        # and overall.
        grouped_metrics = MetricFrame(metrics=mean,
                                      y_true=y_data,
                                      y_pred=y_data, # Use y_data as y_pred for direct outcome analysis
                                      sensitive_features=sensitive_features)
        
        print(f"Mean '{outcome}' per persona (Fairlearn MetricFrame):\n{grouped_metrics.by_group}")
        
        # Calculate the difference and ratio of means between groups
        # 'between_groups' method finds the maximum absolute difference/ratio between any two groups
        disparity_difference = grouped_metrics.difference(method='between_groups')
        disparity_ratio = grouped_metrics.ratio(method='between_groups')

        print(f"Max Difference in Mean '{outcome}': {disparity_difference:.4f}")
        print(f"Ratio of Means (min/max) '{outcome}': {disparity_ratio:.4f}")

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

            # Perform Welch's t-test
            t_stat, p_value = stats.ttest_ind(data_group1, data_group2, equal_var=False)
            print(f"Welch's t-test ({persona_groups[0]} vs. {persona_groups[1]}) for '{outcome}':")
            print(f"  t-statistic = {t_stat:.4f}, p-value = {p_value:.4f}")
            # A common significance level is 0.05. If p-value < 0.05, the difference is statistically significant.
            if p_value is not None and p_value < 0.05:
                print(f"  -> The difference in '{outcome}' is statistically significant (p < 0.05).")
            elif p_value is not None:
                print(f"  -> The difference in '{outcome}' is NOT statistically significant (p >= 0.05).")

        # Store all results for this outcome
        analysis_results[outcome] = {
            "mean_per_group": grouped_metrics.by_group.to_dict(),
            "disparity_difference": disparity_difference,
            "disparity_ratio": disparity_ratio,
            "t_statistic": t_stat,
            "p_value": p_value
        }
    
    return analysis_results

if __name__ == "__main__":
    # Define the path to the processed data file (output from fairlearn_processor.py)
    PROCESSED_DATA_FILE = "llm_replies.jsonl" # Assuming processor writes to the same file

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
        if res['p_value'] is not None:
            print(f"  T-test p-value: {res['p_value']:.4f} (Statistically significant if < 0.05)")
        else:
            print("  T-test not performed (insufficient groups).")

    print("\nFairlearn evaluation complete. Review the results and visualizations for insights.")
