import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
from ptitprince import RainCloud
import logging

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s %(levelname)s %(message)s"
)

def main():
    date_str = pd.Timestamp.now().strftime('%Y%m%d')
    try:
        df = pd.read_parquet(f"data/gemini_bias_{date_str}.parquet")
    except (IOError, FileNotFoundError) as e:
        logging.error(f"Could not read parquet file: {e}")
        return
    plt.figure(figsize=(10, 6))
    RainCloud(data=df, x='english_level', y='sentiment', hue='name', width_viol=0.8, palette="Set2")
    plt.title("Sentiment by English Level and Name")
    try:
        plt.savefig(f"figures/sentiment_raincloud_{date_str}.png", dpi=300)
        logging.info(f"Figure saved to figures/sentiment_raincloud_{date_str}.png")
    except Exception as e:
        logging.error(f"Failed to save figure: {e}")
    plt.close()