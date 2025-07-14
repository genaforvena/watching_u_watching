import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
from ptitprince import RainCloud
import logging
import argparse
import os

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s %(levelname)s %(message)s"
)

def main(in_file, out_fig):
    try:
        df = pd.read_parquet(in_file)
    except (IOError, FileNotFoundError) as e:
        logging.error(f"Could not read parquet file: {e}")
        return
    plt.figure(figsize=(10, 6))
    RainCloud(data=df, x='english_level', y='sentiment', hue='name', width_viol=0.8, palette="Set2")
    plt.title("Sentiment by English Level and Name")
    try:
        os.makedirs(os.path.dirname(out_fig), exist_ok=True)
        plt.savefig(out_fig, dpi=300)
        logging.info(f"Figure saved to {out_fig}")
    except (IOError, OSError) as e:
        logging.error(f"Failed to save figure: {e}")
    plt.close()

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description='Analyze Gemini linguistic bias audit results.')
    parser.add_argument('--in_file', type=str, default='data/gemini_bias.parquet', help='Input Parquet filename')
    parser.add_argument('--out_fig', type=str, default='figures/sentiment_raincloud.png', help='Output figure filename')
    args = parser.parse_args()
    main(args.in_file, args.out_fig)