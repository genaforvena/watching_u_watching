import pandas as pd
from matplotlib.pyplot import figure, close, title, savefig
import seaborn as sns
from ptitprince import RainCloud
import logging
import os

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(message)s"
)

def main():
    date_str = pd.Timestamp.now().strftime('%Y%m%d')
    parquet_path = f"data/gemini_bias_{date_str}.parquet"
    fig_dir = "figures"
    fig_path = f"{fig_dir}/sentiment_raincloud_{date_str}.png"
    try:
        df = pd.read_parquet(parquet_path)
    except (IOError, FileNotFoundError) as e:
        logging.error(f"Error reading Parquet file: {e}")
        return
    if not os.path.exists(fig_dir):
        os.makedirs(fig_dir, exist_ok=True)
    fig = figure(figsize=(10, 6))
    RainCloud(data=df, x='english_level', y='sentiment', hue='name', width_viol=0.8, palette="Set2")
    title("Sentiment by English Level and Name")
    savefig(fig_path, dpi=300)
    close(fig)
    logging.info(f"Figure saved to {fig_path}")

if __name__ == "__main__":
    main()