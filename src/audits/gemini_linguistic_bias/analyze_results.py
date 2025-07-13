import pandas as pd
from scipy.stats import ttest_ind

def groupwise_metrics(df):
    result = {}
    for group in df["group"].unique():
        group_df = df[df["group"] == group]
        result[group] = {
            "refusal_rate": group_df["refusal"].mean(),
            "avg_sentiment": group_df["sentiment"].mean(),
            "avg_latency": group_df["latency"].mean(),
            "n": len(group_df)
        }
    return result

def compare_groups(df):
    group_a = df[df["group"] == "A"]
    group_b = df[df["group"] == "B"]
    # Refusal rate difference
    refusal_a = group_a["refusal"].mean()
    refusal_b = group_b["refusal"].mean()
    # Sentiment difference (t-test)
    sentiment_a = group_a["sentiment"]
    sentiment_b = group_b["sentiment"]
    t_stat, p_val = ttest_ind(sentiment_a, sentiment_b, equal_var=False)
    return {
        "refusal_rate_A": refusal_a,
        "refusal_rate_B": refusal_b,
        "sentiment_A": sentiment_a.mean(),
        "sentiment_B": sentiment_b.mean(),
        "sentiment_ttest": {"t_stat": t_stat, "p_value": p_val}
    }

def main(input_file, report_file):
    df = pd.read_parquet(input_file)
    metrics = groupwise_metrics(df)
    comparison = compare_groups(df)
    with open(report_file, "w") as f:
        f.write("# Gemini Linguistic Bias Audit - A/B Group Analysis\n\n")
        f.write("## Groupwise Metrics\n")
        for group, vals in metrics.items():
            f.write(f"### Group {group}\n")
            for k, v in vals.items():
                f.write(f"- {k}: {v}\n")
            f.write("\n")
        f.write("## Group Comparison\n")
        f.write(f"- Refusal rate difference: {comparison['refusal_rate_A']} (A) vs {comparison['refusal_rate_B']} (B)\n")
        f.write(f"- Sentiment (mean): {comparison['sentiment_A']} (A) vs {comparison['sentiment_B']} (B)\n")
        f.write(f"- Sentiment t-test: t={comparison['sentiment_ttest']['t_stat']}, p={comparison['sentiment_ttest']['p_value']}\n")

if __name__ == "__main__":
    import argparse
    parser = argparse.ArgumentParser(description='Analyze Gemini linguistic bias audit results (A/B group).')
    parser.add_argument('--input_file', type=str, required=True, help='Input Parquet file')
    parser.add_argument('--report_file', type=str, required=True, help='Output Markdown report file')
    args = parser.parse_args()
    main(args.input_file, args.report_file)