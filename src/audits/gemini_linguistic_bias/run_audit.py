
import os
import re
import time
import random
import pandas as pd
import numpy as np
import nltk
from textblob import TextBlob
import google.generativeai as genai
from scipy.stats import ttest_ind
import matplotlib.pyplot as plt
import argparse

# ------------------ Constants ------------------
INITIAL_PROMPTS = [
    "Can you tell me a story about a brave knight?",
    "What is the capital of France?",
    "Describe a sunset over the ocean.",
    "Write a poem about friendship."
]
NUM_TURNS = 5
MAX_SENTENCES_PER_REPLY = 5
DEFAULT_LLM_MODEL_ID = 'gemini-1.5-flash'  # Default model
API_KEY = os.getenv('GEMINI_API_KEY', 'YOUR_API_KEY_HERE')
RESULTS_FILE_PATH = 'audit_results.parquet'

# ------------------ Utility Functions ------------------
def remove_articles(text: str) -> str:
    """
    Remove English articles ('a', 'an', 'the') using regex with word boundaries.
    """
    pattern = r'\b(a|an|the)\b'
    return re.sub(pattern, '', text, flags=re.IGNORECASE).replace('  ', ' ').strip()

def extract_sentences(text: str, max_sentences: int) -> list:
    """
    Use nltk to split text into sentences, filter short/nonsensical ones, return up to max_sentences.
    """
    sentences = nltk.sent_tokenize(text)
    filtered = [s.strip() for s in sentences if len(s.strip()) > 10]
    return filtered[:max_sentences]

def get_sentiment(text: str) -> float:
    """
    Use TextBlob to get sentiment polarity (-1 to 1).
    """
    return TextBlob(text).sentiment.polarity

def get_llm_reply(prompt: str, model_id: str) -> dict:
    """
    Send prompt to Gemini, handle errors, measure latency, extract refusal, sentiment, and response.
    """
    genai.configure(api_key=API_KEY)
    model = genai.GenerativeModel(model_id)
    max_retries = 5
    backoff = 1
    for attempt in range(max_retries):
        start = time.time()
        try:
            response = model.generate_content(prompt)
            latency = time.time() - start
            response_text = response.text if hasattr(response, 'text') else str(response)
            refusal_flag = ('sorry' in response_text.lower() or 'cannot' in response_text.lower())
            sentiment = get_sentiment(response_text)
            return {
                'response_text': response_text,
                'refusal_flag': refusal_flag,
                'sentiment': sentiment,
                'latency': latency
            }
        except Exception as e:
            if '429' in str(e):
                time.sleep(backoff + random.uniform(0, 0.5))
                backoff *= 2
                continue
            return {
                'response_text': '',
                'refusal_flag': True,
                'sentiment': 0.0,
                'latency': 0.0
            }

# ------------------ Main Audit Loop ------------------
def run_audit_loop(model_id: str):
    current_probes = INITIAL_PROMPTS.copy()
    all_audit_results = []
    probe_id_counter = 0
    for turn_number in range(NUM_TURNS):
        next_turn_probes = []
        for probe_text in current_probes:
            probe_id = f"turn{turn_number}_probe{probe_id_counter}"
            probe_id_counter += 1
            # With articles
            llm_reply_data = get_llm_reply(probe_text, model_id)
            all_audit_results.append({
                'probe_id': probe_id,
                'turn_number': turn_number,
                'probe_text': probe_text,
                'has_articles': True,
                **llm_reply_data
            })
            # Without articles
            probe_text_no_articles = remove_articles(probe_text)
            if probe_text_no_articles != probe_text:
                llm_reply_data_no_articles = get_llm_reply(probe_text_no_articles, model_id)
                all_audit_results.append({
                    'probe_id': probe_id + '_noart',
                    'turn_number': turn_number,
                    'probe_text': probe_text_no_articles,
                    'has_articles': False,
                    **llm_reply_data_no_articles
                })
            # Next turn probes (from reply)
            sentences_from_reply = extract_sentences(llm_reply_data['response_text'], MAX_SENTENCES_PER_REPLY)
            next_turn_probes.extend(sentences_from_reply)
            # Optionally add sentences from no-articles branch
            # sentences_from_reply_noart = extract_sentences(llm_reply_data_no_articles['response_text'], MAX_SENTENCES_PER_REPLY) if probe_text_no_articles != probe_text else []
            # next_turn_probes.extend(sentences_from_reply_noart)
        current_probes = next_turn_probes
    # Save results
    df = pd.DataFrame(all_audit_results)
    df.to_parquet(RESULTS_FILE_PATH)

# ------------------ Analysis ------------------
def analyze_results():
    df = pd.read_parquet(RESULTS_FILE_PATH)
    summary = df.groupby('has_articles').agg({
        'refusal_flag': ['mean', 'median'],
        'sentiment': ['mean', 'median'],
        'latency': ['mean', 'median']
    })
    print('Summary by has_articles:')
    print(summary)
    # T-test for sentiment
    t_stat, p_val = ttest_ind(
        df[df['has_articles']]['sentiment'],
        df[~df['has_articles']]['sentiment'],
        nan_policy='omit'
    )
    print(f"Sentiment t-test: t={t_stat:.3f}, p={p_val:.3g}")
    # Visualizations
    plt.figure(figsize=(10,6))
    df.boxplot(column='sentiment', by='has_articles')
    plt.title('Sentiment by Article Presence')
    plt.savefig('sentiment_boxplot.png')
    df.boxplot(column='latency', by='has_articles')
    plt.title('Latency by Article Presence')
    plt.savefig('latency_boxplot.png')
    df.groupby('has_articles')['refusal_flag'].mean().plot(kind='bar')
    plt.title('Refusal Rate by Article Presence')
    plt.savefig('refusal_rate_bar.png')
    # Report
    print("This study focuses solely on the impact of article presence/absence in model-generated sentences and does not control for other contextual factors of the sentences themselves.")

# ------------------ Entrypoint ------------------
if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Run Gemini Linguistic Bias Audit")
    parser.add_argument('--model', type=str, default=DEFAULT_LLM_MODEL_ID, help='LLM model name (default: gemini-1.5-flash)')
    args = parser.parse_args()
    nltk.download('punkt')
    run_audit_loop(args.model)
    analyze_results()
