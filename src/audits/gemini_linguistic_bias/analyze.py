import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
from ptitprince import RainCloud

def main():
    date_str = pd.Timestamp.now().strftime('%Y%m%d')
    df = pd.read_parquet(f"data/gemini_bias_{date_str}.parquet")
    plt.figure(figsize=(10, 6))
    RainCloud(data=df, x='english_level', y='sentiment', hue='name', width_viol=0.8, palette="Set2")
    plt.title("Sentiment by English Level and Name")
    plt.savefig(f"figures/sentiment_raincloud_{date_str}.png", dpi=300)
    print(f"Figure saved to figures/sentiment_raincloud_{date_str}.png")

    plt.figure(figsize=(10, 6))
    sns.barplot(data=df, x='english_level', y='response_length', hue='name')
    plt.title("Response Length by English Level and Name")
    plt.savefig(f"figures/response_length_bar_{date_str}.png", dpi=300)
    print(f"Figure saved to figures/response_length_bar_{date_str}.png")

if __name__ == "__main__":
    main()