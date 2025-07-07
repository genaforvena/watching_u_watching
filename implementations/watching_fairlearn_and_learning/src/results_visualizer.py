"""
Module: results_visualizer

Generates plots to compare outcome metrics across sensitive groups and
provides interpretive text for Fairlearn analysis results.
"""

# Standard imports for plotting and processing
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
from fairlearn_processor import process_llm_data
from bias_evaluator import evaluate_fairlearn_bias

def visualize_results(df, analysis_results):
    """
    Generates comparative visualizations of outcome metrics across sensitive groups
    and provides a framework for interpreting Fairlearn's findings.

    Args:
        df (pandas.DataFrame): The processed DataFrame.
        analysis_results (dict): The results dictionary from bias_evaluator.py.
    """
    sensitive_attribute_col = 'sensitive_attribute'
    outcomes_to_visualize = ['reply_length', 'sentiment_score', 'formality_score', 'contains_detail_kw']
    
    print("\n--- Generating Visualizations ---")

    # Set a consistent style for plots
    sns.set_theme(style="whitegrid")
    plt.style.use('seaborn-v0_8-darkgrid')

    # Create a figure to hold multiple subplots
    fig, axes = plt.subplots(len(outcomes_to_visualize), 2, figsize=(14, 5 * len(outcomes_to_visualize)))
    
    # Ensure axes is always a 2D array for consistent indexing
    if len(outcomes_to_visualize) == 1:
        axes = [axes] # Make it a list of 1 row, so axes[0] works

    for i, outcome in enumerate(outcomes_to_visualize):
        # --- Histogram/KDE Plot ---
        # Shows the distribution of the outcome for each persona
        sns.histplot(data=df, x=outcome, hue=sensitive_attribute_col, kde=True, ax=axes[i][0], alpha=0.7, palette="viridis")
        axes[i][0].set_title(f'Distribution of {outcome.replace("_", " ").title()} by Persona')
        axes[i][0].set_xlabel(outcome.replace("_", " ").title())
        axes[i][0].set_ylabel('Density / Count')
        axes[i][0].legend(title="Persona")

        # --- Box Plot ---
        # Shows median, quartiles, and outliers for each persona
        sns.boxplot(data=df, x=sensitive_attribute_col, y=outcome, ax=axes[i][1], palette="viridis")
        axes[i][1].set_title(f'Box Plot of {outcome.replace("_", " ").title()} by Persona')
        axes[i][1].set_xlabel('Persona')
        axes[i][1].set_ylabel(outcome.replace("_", " ").title())

        # Add Fairlearn disparity metrics and p-value to the plot titles/annotations
        res = analysis_results.get(outcome, {})
        diff = res.get('disparity_difference', 'N/A')
        ratio = res.get('disparity_ratio', 'N/A')
        p_value = res.get('p_value', 'N/A')

        # Add text annotations to the box plot
        if p_value != 'N/A':
            axes[i][1].text(0.05, 0.95, f'Diff: {diff:.4f}\nRatio: {ratio:.4f}\nP-value: {p_value:.4f}', 
                            transform=axes[i][1].transAxes, 
                            fontsize=10, verticalalignment='top', bbox=dict(boxstyle='round,pad=0.5', fc='yellow', alpha=0.5))
        else:
            axes[i][1].text(0.05, 0.95, f'Diff: {diff}\nRatio: {ratio}', 
                            transform=axes[i][1].transAxes, 
                            fontsize=10, verticalalignment='top', bbox=dict(boxstyle='round,pad=0.5', fc='yellow', alpha=0.5))


    plt.tight_layout() # Adjust layout to prevent overlapping titles/labels
    plt.show()

    print("\n--- Interpretation Framework for Fairlearn's 'Bias' in Evaluation ---")
    print("This section guides the critical analysis of Fairlearn's outputs, focusing on what they reveal about the bias detection tool itself, rather than solely the LLM.")

    for outcome in outcomes_to_visualize:
        res = analysis_results.get(outcome, {})
        print(f"\n### Outcome: {outcome.replace('_', ' ').title()}")
        print(f"  - Mean per group: {res.get('mean_per_group', 'N/A')}")
        print(f"  - Disparity Difference (Max Abs): {res.get('disparity_difference', 'N/A'):.4f}")
        print(f"  - Disparity Ratio (Min/Max): {res.get('disparity_ratio', 'N/A'):.4f}")
        if res.get('p_value') is not None:
            print(f"  - Statistical P-value (t-test): {res.get('p_value', 'N/A'):.4f}")
            if res['p_value'] < 0.05:
                print("    **Observation:** The difference is statistically significant (p < 0.05).")
            else:
                print("    **Observation:** The difference is NOT statistically significant (p >= 0.05).")
        else:
            print("  - Statistical P-value: N/A (t-test not performed)")

        print("\n  **Critical Questions for Fairlearn's Evaluation:**")
        print("  1. **Accuracy of Detection:** Does Fairlearn's quantitative assessment (difference/ratio, p-value) align with visual inspection of the plots? If the plots show very similar distributions, does Fairlearn correctly report no significant disparity? If there's a visible difference, does Fairlearn flag it?")
        print("  2. **Sensitivity vs. Practical Significance:** If a disparity is statistically significant (low p-value), is the *magnitude* of the difference (e.g., disparity_difference) practically meaningful? With 10,000 samples per group, even tiny, practically irrelevant differences can be statistically significant. Does Fairlearn's output highlight this distinction, or could it be misinterpreted as a major 'bias'?")
        print("  3. **Interpretability of Metrics:** Do the chosen metrics (length, sentiment, formality, keyword presence) truly capture the nuances of 'fairness' in LLM responses in this context? Are they robust enough, or do they oversimplify complex aspects of language? For example, is our 'formality_score' truly indicative of a 'fair' or 'biased' response?")
        print("  4. **Fairlearn's Role:** In cases where disparities are found, does Fairlearn's output clearly indicate *what* is different, allowing for a deeper investigation into the LLM's behavior (e.g., specific word choices, sentence structures)? Or does it just provide a number without sufficient context for root cause analysis?")
        print("  5. **Limitations of Group Fairness:** Fairlearn focuses on group fairness. Does this experiment highlight any limitations of group-level metrics in capturing individual-level nuances or complex intersectional biases that might exist?")
        print("\n  **Conclusion for this Outcome:** Based on the above, what does this specific outcome tell us about Fairlearn's strengths and limitations in detecting this type of disparity?")

    print("\n--- Overall Experiment Conclusion ---")
    print("This experiment serves as a meta-analysis, using a controlled LLM scenario to probe the behavior of Fairlearn itself. The insights gained here are crucial for understanding the practical application and potential pitfalls of fairness assessment tools in real-world AI development.")
    print("Further research could involve more complex persona definitions, advanced NLP metrics, and testing Fairlearn's mitigation strategies in similar controlled environments.")

if __name__ == "__main__":

    # Define the path to the processed data file
    PROCESSED_DATA_FILE = "llm_replies.parquet"

    print("Starting visualization and interpretation...")
    
    # Load and process the data (re-runs processing for self-contained execution)
    processed_df = process_llm_data(PROCESSED_DATA_FILE)
    
    # Evaluate bias to get the results for visualization and interpretation
    analysis_results = evaluate_fairlearn_bias(processed_df)
    
    # Generate visualizations and provide interpretation framework
    visualize_results(processed_df, analysis_results)

    print("\nVisualization and interpretation complete.")
