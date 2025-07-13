import pandas as pd
import argparse

def main(input_file, report_file):
    df = pd.read_parquet(input_file)
    num_probes = len(df)
    refusal_rate = (df['refusal'].sum() / num_probes) * 100
    avg_sentiment = df['sentiment'].mean()
    avg_latency = df['latency'].mean()
    with open(report_file, 'w') as f:
        f.write(f"# Gemini Linguistic Bias Audit Report\n\n")
        f.write(f"**Total probes collected:** {num_probes}\n\n")
        f.write(f"**Refusal rate:** {refusal_rate:.2f}%\n\n")
        f.write(f"**Average sentiment:** {avg_sentiment:.3f}\n\n")
        f.write(f"**Average latency (ms):** {avg_latency:.1f}\n\n")
        # Add more analysis as needed (plots, breakdowns, etc.)

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description='Analyze Gemini audit results.')
    parser.add_argument('--input_file', type=str, required=True, help='Path to audit results Parquet file')
    parser.add_argument('--report_file', type=str, required=True, help='Output markdown report file')
    args = parser.parse_args()
    main(args.input_file, args.report_file)