import pandas as pd
from scipy.stats import ttest_ind

def groupwise_metrics(df):
    """
    Compute refusal rate, average sentiment, and average latency for each group+article combo.
    Returns a dict: result[group][has_article]
    """
    result = {}
    for group in sorted(df["group"].unique()):
        result[group] = {}
        for article_present in [True, False]:
            group_df = df[(df["group"] == group) & (df["article_present"] == article_present)]
            result[group][article_present] = {
                "refusal_rate": group_df["refusal"].mean(),
                "avg_sentiment": group_df["sentiment"].mean(),
                "avg_latency": group_df["latency"].mean(),
                "n": len(group_df)
            }
    return result

def compare_groups(df):
    """
    Compare refusal rates and sentiment between A/B groups and article/no-article sets.
    Returns t-test results for sentiment.
    """
    results = {}
    for article_present in [True, False]:
        group_a = df[(df["group"] == "A") & (df["article_present"] == article_present)]
        group_b = df[(df["group"] == "B") & (df["article_present"] == article_present)]
        group_a_sent = group_a["sentiment"].dropna()
        group_b_sent = group_b["sentiment"].dropna()

        t_stat, p_val = (float('nan'), float('nan'))
        if len(group_a_sent) > 1 and len(group_b_sent) > 1:
            t_stat, p_val = ttest_ind(group_a_sent, group_b_sent, equal_var=False)

        results[article_present] = {
            "refusal_rate_A": group_a["refusal"].mean(),
            "refusal_rate_B": group_b["refusal"].mean(),
            "sentiment_A": group_a_sent.mean(),
            "sentiment_B": group_b_sent.mean(),
            "sentiment_ttest": {"t_stat": t_stat, "p_value": p_val}
        }
    return results

def analyze_pairs(df):
    """
    Analyze paired differences for each prompt pair (A vs B), split by article/no-article.
    """
    pair_results = []
    for pair_id in sorted(df["pair_id"].unique()):
        for article_present in [True, False]:
            pair_df = df[(df["pair_id"] == pair_id) & (df["article_present"] == article_present)]
            a_row = pair_df[pair_df["group"] == "A"]
            b_row = pair_df[pair_df["group"] == "B"]
            if not a_row.empty and not b_row.empty:
                result = {
                    "pair_id": pair_id,
                    "article_present": article_present,
                    "prompt_A": a_row.iloc[0]["variant_content"],
                    "prompt_B": b_row.iloc[0]["variant_content"],
                    "sentiment_A": a_row.iloc[0]["sentiment"],
                    "sentiment_B": b_row.iloc[0]["sentiment"],
                    "refusal_A": a_row.iloc[0]["refusal"],
                    "refusal_B": b_row.iloc[0]["refusal"],
                    "latency_A": a_row.iloc[0]["latency"],
                    "latency_B": b_row.iloc[0]["latency"]
                }
                pair_results.append(result)
    return pair_results

def main(input_file, report_file):
    df = pd.read_parquet(input_file)
    metrics = groupwise_metrics(df)
    comparison = compare_groups(df)
    pairs = analyze_pairs(df)
    with open(report_file, "w", encoding="utf-8") as f:
        f.write("# Gemini Linguistic Bias Audit - A/B Group Analysis\n\n")
        f.write("## Groupwise Metrics (with and without articles)\n")
        for group in metrics:
            for article_present in [True, False]:
                vals = metrics[group][article_present]
                f.write(f"### Group {group} ({'with' if article_present else 'without'} articles)\n")
                for k, v in vals.items():
                    f.write(f"- {k}: {v}\n")
                f.write("\n")
        f.write("## Group Comparison (sentiment t-test)\n")
        for article_present in [True, False]:
            comp = comparison[article_present]
            f.write(f"- {'With' if article_present else 'Without'} articles:\n")
            f.write(f"    - Refusal rate: {comp['refusal_rate_A']} (A) vs {comp['refusal_rate_B']} (B)\n")
            f.write(f"    - Sentiment: {comp['sentiment_A']} (A) vs {comp['sentiment_B']} (B)\n")
            f.write(f"    - Sentiment t-test: t={comp['sentiment_ttest']['t_stat']}, p={comp['sentiment_ttest']['p_value']}\n")
            f.write("\n")
        f.write("## Paired Results (A vs B, with and without articles)\n")
        for result in pairs:
            f.write(f"- Pair {result['pair_id']} ({'with' if result['article_present'] else 'without'} articles):\n")
            f.write(f"    - Prompt A: {result['prompt_A']}\n")
            f.write(f"    - Prompt B: {result['prompt_B']}\n")
            f.write(f"    - Sentiment A: {result['sentiment_A']}\n")
            f.write(f"    - Sentiment B: {result['sentiment_B']}\n")
            f.write(f"    - Refusal A: {result['refusal_A']}\n")
            f.write(f"    - Refusal B: {result['refusal_B']}\n")
            f.write(f"    - Latency A: {result['latency_A']}\n")
            f.write(f"    - Latency B: {result['latency_B']}\n")
            f.write("\n")

if __name__ == "__main__":
    import argparse
    parser = argparse.ArgumentParser(description='Analyze Gemini linguistic bias audit results (A/B group, articles control).')
    parser.add_argument('--input_file', type=str, required=True, help='Input Parquet file')
    parser.add_argument('--report_file', type=str, required=True, help='Output Markdown report file')
    args = parser.parse_args()
    main(args.input_file, args.report_file)