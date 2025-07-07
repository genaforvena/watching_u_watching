"""
Module: fairlearn_processor

Loads LLM replies from Parquet and extracts engineered features for fairness analysis:
reply length, sentiment score, formality score, and detail keyword presence.
"""

import pandas as pd
import json
from textblob import TextBlob
import nltk
from nltk.corpus import stopwords
from nltk.tokenize import word_tokenize

# Ensure necessary NLTK data is downloaded
try:
    nltk.data.find('corpora/stopwords')
except LookupError:
    nltk.download('stopwords')
try:
    nltk.data.find('tokenizers/punkt')
except LookupError:
    nltk.download('punkt')

def calculate_formality_score(text):
    """
    Calculates a simple formality score for a given text.
    This is a heuristic and can be refined.
    It counts the proportion of "long" words (>= 6 chars) and common formal/informal words.
    """
    words = word_tokenize(text.lower())
    if not words:
        return 0.0

    # Heuristic 1: Proportion of longer words
    long_words = [word for word in words if len(word) >= 6]
    long_word_ratio = len(long_words) / len(words)

    # Heuristic 2: Presence of formal/informal indicators
    formal_indicators = ["furthermore", "moreover", "however", "consequently", "therefore", "sincerely", "regards"]
    informal_indicators = ["hi", "hey", "lol", "btw", "gonna", "wanna", "yep", "nope"]

    formal_count = sum(1 for word in words if word in formal_indicators)
    informal_count = sum(1 for word in words if word in informal_indicators)

    # Combine heuristics (weights can be adjusted)
    score = long_word_ratio * 0.6 + (formal_count - informal_count) / len(words) * 0.4
    
    # Normalize score to be roughly between 0 and 1 (or -1 to 1 if preferred)
    # This normalization is very rough and depends on the text characteristics
    return max(0.0, min(1.0, (score + 0.5) / 1.5)) # Shift and scale to roughly 0-1 range


def process_llm_data(input_file="llm_replies.jsonl"):
    """

    Loads raw LLM replies from a Parquet file and extracts numerical features
    for fairness analysis.

    Args:
        input_file (str): Path to the Parquet file containing raw LLM replies.

    Returns:
        pandas.DataFrame: A DataFrame with processed data, including sensitive
                          features and engineered outcome metrics.
    """
    try:
        df = pd.read_parquet(input_file)
    except FileNotFoundError:
        print(f"Input file '{input_file}' not found. Creating an empty Parquet file.")
        df = pd.DataFrame(columns=["id", "persona", "prompt_full", "reply_raw", "timestamp"])
        df.to_parquet(input_file, index=False)
        return df

    # --- Feature Engineering (Outcome Metrics) ---
    # 1. Reply Length: Number of characters in the raw LLM response
    df['reply_length'] = df['reply_raw'].apply(len)

    # 2. Sentiment Score: Polarity from TextBlob (-1.0 to 1.0, negative to positive)
    df['sentiment_score'] = df['reply_raw'].apply(lambda x: TextBlob(x).sentiment.polarity)

    # 3. Formality Score: Custom heuristic-based score (0.0 to 1.0, informal to formal)
    df['formality_score'] = df['reply_raw'].apply(calculate_formality_score)

    # 4. Detail Keyword Presence: Binary indicator (1 if keywords present, 0 otherwise)
    detail_keywords = ["detail", "explain", "thoroughly", "elaborate", "comprehensive"]
    df['contains_detail_kw'] = df['reply_raw'].apply(
        lambda x: 1 if any(kw in x.lower() for kw in detail_keywords) else 0
    )

    # Rename the 'persona' column to 'sensitive_attribute' for clarity and consistency
    # with Fairlearn's terminology if desired, though 'persona' works fine too.
    df = df.rename(columns={'persona': 'sensitive_attribute'})

    print(f"Processed {len(df)} LLM replies.")
    print("DataFrame head:")
    print(df.head())
    print("\nDataFrame descriptive statistics for engineered features:")
    print(df[['reply_length', 'sentiment_score', 'formality_score', 'contains_detail_kw']].describe())

    return df

if __name__ == "__main__":
    # Define the input file path
    INPUT_DATA_FILE = "llm_replies.parquet"

    # Process the data and get the prepared DataFrame
    processed_df = process_llm_data(INPUT_DATA_FILE)

    # You can now save this processed DataFrame if needed, or pass it directly
    # to the next module (bias_evaluator.py)
    # For demonstration, we'll just print its head and describe stats.
    print("\nData processing complete. Ready for Fairlearn evaluation.")
