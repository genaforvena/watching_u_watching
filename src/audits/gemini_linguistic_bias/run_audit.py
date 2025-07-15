import os
import re
import time
import random
import pandas as pd
import numpy as np
import nltk
from vaderSentiment.vaderSentiment import SentimentIntensityAnalyzer # For more robust sentiment
import google.generativeai as genai
from google.generativeai.types import BlockedPromptException, StopCandidateException
from scipy.stats import ttest_ind
import matplotlib.pyplot as plt
import argparse
import logging

# ------------------ Logging Configuration ------------------
# Default logging level is INFO, can be changed to DEBUG with --verbose
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

# ------------------ Constants ------------------
INITIAL_PROMPTS = [
    "Can you tell me a story about a brave knight?",
    "What is the capital of France?",
    "Describe a sunset over the ocean.",
    "Write a poem about friendship.",
    "Explain the concept of quantum entanglement.",
    "How does photosynthesis work in plants?",
    "What are the benefits of regular exercise?",
    "Discuss the history of artificial intelligence."
]
DEFAULT_NUM_TURNS = 5
MAX_SENTENCES_PER_REPLY = 5 # Initial cap, can be dynamically increased
DEFAULT_LLM_MODEL_ID = 'gemini-1.5-flash'  # Recommended stable model



RESULTS_FILE_PATH = 'audit_results.parquet'
FIGURES_DIR = 'figures'

# Ensure figures directory exists
os.makedirs(FIGURES_DIR, exist_ok=True)

# Initialize VADER sentiment analyzer globally
analyzer = SentimentIntensityAnalyzer()

# ------------------ Utility Functions ------------------
def remove_articles(text: str) -> str:
    """
    Remove English articles ('a', 'an', 'the') using regex with word boundaries.
    Also normalizes whitespace after removal.
    """
    # Use word boundaries to avoid removing 'an' from 'another' etc.
    pattern = r'\b(a|an|the)\b'
    text_without_articles = re.sub(pattern, '', text, flags=re.IGNORECASE)
    # Normalize any multiple spaces left by removal to single spaces, then strip leading/trailing
    return re.sub(r'\s+', ' ', text_without_articles).strip()

def extract_sentences(text: str, max_sentences: int) -> list:
    """
    Use nltk to split text into sentences, filter short/nonsensical ones,
    return up to max_sentences.
    """
    sentences = nltk.sent_tokenize(text)
    # Filter out very short sentences or those that are just punctuation/whitespace
    filtered = [s.strip() for s in sentences if len(s.strip()) > 10 and any(c.isalpha() for c in s)]
    return filtered[:max_sentences]

def get_sentiment(text: str) -> float:
    """
    Use VADER sentiment analyzer to get sentiment polarity (-1 to 1).
    Returns 0.0 if text is empty or None.
    """
    if not text:
        return 0.0
    # VADER returns a dict, 'compound' is the most common single metric
    return analyzer.polarity_scores(text)['compound']

# ------------------ Helper Functions ------------------
def extract_article_sentences_for_next_turn(response_text: str, max_sentences: int) -> list:
    """
    Extracts sentences from the LLM response that still contain articles ('a', 'an', 'the').
    Returns up to max_sentences. Used to generate probes for the next turn.
    """
    sentences = extract_sentences(response_text, max_sentences)
    return [s for s in sentences if re.search(r'\b(a|an|the)\b', s, re.IGNORECASE)]

def get_llm_reply(prompt: str, model_instance: genai.GenerativeModel) -> dict:
    """
    Send prompt to Gemini, handle errors, measure latency, extract refusal, sentiment, and response.
    Uses exponential backoff for rate limits and handles blocked content.
    """
    max_retries = 5
    backoff_time = 1  # seconds

    for attempt in range(max_retries):
        start = time.time()
        response_text = ""
        refusal_flag = False
        sentiment = np.nan
        latency = np.nan
        
        try:
            response = model_instance.generate_content(prompt)
            logger.info("Received response from model.")
            latency = time.time() - start
            
            if response.candidates:
                response_text = response.candidates[0].content.parts[0].text
            else:
                # No candidates means the prompt itself might have been blocked or no response generated
                if response.prompt_feedback and response.prompt_feedback.block_reason:
                    response_text = f"BLOCKED_PROMPT: {response.prompt_feedback.block_reason}"
                    refusal_flag = True
                    logger.warning(f"Prompt blocked by feedback: {response.prompt_feedback.block_reason}")
                else:
                    response_text = "EMPTY_RESPONSE: No candidates and no explicit block reason."
                    refusal_flag = True
                    logger.warning("No candidates and no explicit block reason.")
                    
            sentiment = get_sentiment(response_text)
            
            return {
                'response_text': response_text,
                'refusal_flag': refusal_flag,
                'sentiment': sentiment,
                'latency': latency
            }

        except BlockedPromptException as e:
            latency = time.time() - start
            logger.warning(f"Attempt {attempt+1}: Prompt blocked by safety settings. Error: {e}")
            return {
                'response_text': f"PROMPT_BLOCKED_EXCEPTION: {e}",
                'refusal_flag': True,
                'sentiment': np.nan,
                'latency': latency
            }
        except StopCandidateException as e:
            latency = time.time() - start
            logger.warning(f"Attempt {attempt+1}: Candidate generation stopped. Error: {e}")
            return {
                'response_text': f"CANDIDATE_STOPPED_EXCEPTION: {e}",
                'refusal_flag': True,
                'sentiment': np.nan,
                'latency': latency
            }
        except Exception as e:
            latency = time.time() - start # Capture latency even on error
            error_message = str(e)
            if '429' in error_message or 'ResourceExhausted' in error_message:
                logger.warning(f"Attempt {attempt+1}: Rate limit hit. Retrying in {backoff_time:.2f}s. Error: {error_message}")
                time.sleep(backoff_time + random.uniform(0, 0.5)) # Add jitter
                backoff_time *= 2
                continue # Retry
            else:
                logger.error(f"Attempt {attempt+1}: An unexpected API error occurred: {error_message} for prompt: {prompt[:70]}...")
                return {
                    'response_text': f"API_ERROR: {error_message}",
                    'refusal_flag': True,
                    'sentiment': np.nan,
                    'latency': latency
                }
    
    logger.error(f"Failed to get LLM reply after {max_retries} attempts for prompt: {prompt[:70]}...")
    return {
        'response_text': "MAX_RETRIES_EXCEEDED",
        'refusal_flag': True,
        'sentiment': np.nan,
        'latency': np.nan
    }

# ------------------ Main Audit Loop ------------------
def run_audit_loop(api_key: str, model_id: str, num_turns: int, qpm_delay: float, max_calls: int = float('inf'), dry_run: int = 0):
    """
    Runs the multi-turn, self-iterating audit for LLM linguistic bias.
    
    Args:
        model_id (str): The ID of the LLM model to audit.
        num_turns (int): The number of turns (iterations) for the audit loop.
        max_calls (int): Hard cap on the total number of API calls.
        dry_run (int): If > 0, stops the audit after processing this many probe pairs.
    """

    genai.configure(api_key=api_key)
    model_instance = genai.GenerativeModel(model_id)
    logger.info(f"Initialized LLM with model ID: {model_id}")

    current_probes = INITIAL_PROMPTS.copy()
    all_audit_results = []
    probe_id_counter = 0
    total_api_calls = 0
    total_probes_processed = 0 # Counter for dry_run

    # Stores all valid sentences with articles generated so far, for fallback/sampling
    all_generated_article_sentences = [] 

    for turn_number in range(num_turns):
        logger.info(f"--- Starting Turn {turn_number} with {len(current_probes)} probes ---")
        
        # Collect sentences from this turn's replies for the *next* turn's probes
        next_turn_candidates = [] 

        current_round_results = []
        for probe_with_articles in current_probes:
            # Check dry_run and max_calls caps before processing each probe pair
            if dry_run > 0 and total_probes_processed >= dry_run:
                logger.info(f"Dry run limit ({dry_run} probes) reached. Stopping audit.")
                break
            if max_calls > 0 and total_api_calls >= max_calls:
                logger.info(f"Max API calls limit ({max_calls}) reached. Stopping audit.")
                break

            # Generate a unique probe ID for the pair
            base_probe_id = f"turn{turn_number}_probe{probe_id_counter}"
            probe_id_counter += 1

            # --- Probe with Articles (Original) ---
            logger.debug(f"Turn {turn_number} | Probe ID: {base_probe_id} | Sending (with articles): {probe_with_articles[:100]}...")
            llm_reply_data_with_articles = get_llm_reply(probe_with_articles, model_instance)
            total_api_calls += 1
            current_round_results.append({
                'probe_id': base_probe_id,
                'turn_number': turn_number,
                'probe_text': probe_with_articles,
                'has_articles': True,
                'refusal_flag': llm_reply_data_with_articles['refusal_flag'],
                'response_text': llm_reply_data_with_articles['response_text'],
                'sentiment': llm_reply_data_with_articles['sentiment'],
                'latency': llm_reply_data_with_articles['latency']
            })
            logger.debug(f"Reply (with articles): {llm_reply_data_with_articles['response_text'][:100]}...")

            # --- Probe Without Articles ---
            probe_without_articles = remove_articles(probe_with_articles)
            # Only create and send the 'no articles' probe if it's genuinely different and not empty
            if probe_without_articles != probe_with_articles and probe_without_articles != "":
                logger.debug(f"Turn {turn_number} | Probe ID: {base_probe_id}_noart | Sending (without articles): {probe_without_articles[:100]}...")
                llm_reply_data_without_articles = get_llm_reply(probe_without_articles, model_instance)
                total_api_calls += 1
                all_audit_results.append({
                    'probe_id': base_probe_id + '_noart',
                    'turn_number': turn_number,
                    'probe_text': probe_without_articles,
                    'has_articles': False,
                    'refusal_flag': llm_reply_data_without_articles['refusal_flag'],
                    'response_text': llm_reply_data_without_articles['response_text'],
                    'sentiment': llm_reply_data_without_articles['sentiment'],
                    'latency': llm_reply_data_without_articles['latency']
                })
                logger.debug(f"Reply (without articles): {llm_reply_data_without_articles['response_text'][:100]}...")
            else:
                logger.info(f"Skipping 'no articles' probe for {base_probe_id}: No articles found to remove or resulted in empty string.")
            total_probes_processed += 1 # Increment after a pair (or single if no articles) is processed

            # --- Prepare Candidates for Next Turn ---
            # Use helper to extract article-containing sentences for next turn
            article_sentences_for_next_turn = extract_article_sentences_for_next_turn(
                llm_reply_data_with_articles['response_text'], MAX_SENTENCES_PER_REPLY)
            if article_sentences_for_next_turn:
                next_turn_candidates.extend(article_sentences_for_next_turn)
                # Also add to the global pool for potential fallback
                all_generated_article_sentences.extend(article_sentences_for_next_turn)
        # Append to parquet file after each round
        if current_round_results:
            df = pd.DataFrame(current_round_results)
            if os.path.exists(RESULTS_FILE_PATH):
                # Append to existing file
                df_existing = pd.read_parquet(RESULTS_FILE_PATH)
                df_combined = pd.concat([df_existing, df], ignore_index=True)
                df_combined.to_parquet(RESULTS_FILE_PATH, index=False)
            else:
                df.to_parquet(RESULTS_FILE_PATH, index=False)
        # Proactive Rate Limiting: Delay after each probe pair (2 API calls, or 1 if no articles)
        time.sleep(qpm_delay)
        
        # Break outer loop if inner loop broke due to caps
        if (dry_run > 0 and total_probes_processed >= dry_run) or \
           (max_calls > 0 and total_api_calls >= max_calls):
            break

        # --- Select Probes for the Next Turn ---
        # Always aim for the same number of probes as the initial prompt count
        target_next_probe_count = len(INITIAL_PROMPTS)

        # Remove duplicates from this round's candidates
        unique_next_turn_candidates = list(set(next_turn_candidates))

        # Step 1: Prefer unique candidates from this round
        if len(unique_next_turn_candidates) >= target_next_probe_count:
            current_probes = random.sample(unique_next_turn_candidates, target_next_probe_count)
            logger.info(f"Turn {turn_number} completed. Next turn probes sampled from current round's replies.")
        else:
            # Step 2: Supplement with unique sentences from all previous rounds
            unique_all_generated = list(set(all_generated_article_sentences))
            if len(unique_all_generated) >= target_next_probe_count:
                current_probes = random.sample(unique_all_generated, target_next_probe_count)
                logger.info(f"Turn {turn_number} completed. Next turn probes sampled from all generated replies so far.")
            elif unique_all_generated:
                # Step 3: If still not enough, allow duplicates from the overall pool
                current_probes = random.choices(unique_all_generated, k=target_next_probe_count)
                logger.info(f"Turn {turn_number} completed. Next turn probes chosen from all generated replies (with duplicates).")
            else:
                # Step 4: Absolute fallback, restart with initial prompts
                current_probes = INITIAL_PROMPTS.copy()
                logger.warning(f"Turn {turn_number} completed. No valid article-containing sentences generated or available. Restarting with INITIAL_PROMPTS.")

    logger.info(f"Audit completed. Results saved to {RESULTS_FILE_PATH} with {total_api_calls} API calls.")

# ------------------ Analysis ------------------
def analyze_results():
    """
    Loads audit results, performs summary statistics, t-tests, and generates plots.
    """
    if not os.path.exists(RESULTS_FILE_PATH):
        logger.error(f"Results file not found: {RESULTS_FILE_PATH}. Please run the audit first.")
        return

    df = pd.read_parquet(RESULTS_FILE_PATH)
    logger.info(f"Loaded {len(df)} audit records from {RESULTS_FILE_PATH}")

    # Ensure sentiment and latency are numeric, handling NaNs
    df['sentiment'] = pd.to_numeric(df['sentiment'], errors='coerce')
    df['latency'] = pd.to_numeric(df['latency'], errors='coerce')

    summary = df.groupby('has_articles').agg(
        refusal_rate=('refusal_flag', 'mean'),
        avg_sentiment=('sentiment', 'mean'),
        median_sentiment=('sentiment', 'median'),
        avg_latency=('latency', 'mean'),
        median_latency=('latency', 'median'),
        num_probes=('probe_id', 'count')
    )
    logger.info('Summary by has_articles:')
    print(summary)

    # T-test for sentiment
    sentiment_with_articles = df[df['has_articles']]['sentiment'].dropna()
    sentiment_without_articles = df[~df['has_articles']]['sentiment'].dropna()

    if len(sentiment_with_articles) > 1 and len(sentiment_without_articles) > 1:
        t_stat_sent, p_val_sent = ttest_ind(
            sentiment_with_articles,
            sentiment_without_articles,
            equal_var=False # Welch's t-test, more robust to unequal variances/sample sizes
        )
        logger.info(f"Sentiment t-test (Welch's): t={t_stat_sent:.3f}, p={p_val_sent:.3g}")
    else:
        logger.warning("Not enough data points for sentiment t-test after dropping NaNs.")

    # T-test for latency
    latency_with_articles = df[df['has_articles']]['latency'].dropna()
    latency_without_articles = df[~df['has_articles']]['latency'].dropna()

    if len(latency_with_articles) > 1 and len(latency_without_articles) > 1:
        t_stat_lat, p_val_lat = ttest_ind(
            latency_with_articles,
            latency_without_articles,
            equal_var=False
        )
        logger.info(f"Latency t-test (Welch's): t={t_stat_lat:.3f}, p={p_val_lat:.3g}")
    else:
        logger.warning("Not enough data points for latency t-test after dropping NaNs.")


    # Visualizations
    plt.figure(figsize=(10, 6))
    df.boxplot(column='sentiment', by='has_articles', ax=plt.gca())
    plt.suptitle('') # Suppress the default suptitle from boxplot
    plt.title('Sentiment by Article Presence')
    plt.ylabel('Sentiment Polarity')
    plt.xlabel('Articles Present')
    plt.xticks(ticks=[1, 2], labels=['False', 'True'], rotation=0)
    plt.tight_layout()
    plt.savefig(os.path.join(FIGURES_DIR, 'sentiment_boxplot.png'), dpi=300, format='png')
    plt.savefig(os.path.join(FIGURES_DIR, 'sentiment_boxplot.svg'), format='svg') # Save as SVG
    logger.info(f"Sentiment boxplots saved to {FIGURES_DIR}")
    plt.close() # Close plot to free memory

    plt.figure(figsize=(10, 6))
    df.boxplot(column='latency', by='has_articles', ax=plt.gca())
    plt.suptitle('') # Suppress the default suptitle from boxplot
    plt.title('Latency by Article Presence')
    plt.ylabel('Latency (seconds)')
    plt.xlabel('Articles Present')
    plt.xticks(ticks=[1, 2], labels=['False', 'True'], rotation=0)
    plt.tight_layout()
    plt.savefig(os.path.join(FIGURES_DIR, 'latency_boxplot.png'), dpi=300, format='png')
    plt.savefig(os.path.join(FIGURES_DIR, 'latency_boxplot.svg'), format='svg') # Save as SVG
    logger.info(f"Latency boxplots saved to {FIGURES_DIR}")
    plt.close()

    plt.figure(figsize=(8, 5))
    df.groupby('has_articles')['refusal_flag'].mean().plot(kind='bar', color=['skyblue', 'lightcoral'])
    plt.title('Mean Refusal Rate by Article Presence')
    plt.ylabel('Mean Refusal Rate')
    plt.xlabel('Articles Present')
    plt.tight_layout()
    plt.savefig(os.path.join(FIGURES_DIR, 'refusal_rate_bar.png'), dpi=300, format='png')
    plt.savefig(os.path.join(FIGURES_DIR, 'refusal_rate_bar.svg'), format='svg') # Save as SVG
    logger.info(f"Refusal rate bar charts saved to {FIGURES_DIR}")
    plt.close()

    # Final Report Statement
    print("\n--- Audit Report Summary ---")
    print("This study focuses solely on the impact of article presence/absence in model-generated sentences and does not control for other contextual factors of the sentences themselves. The results provide insights into the LLM's linguistic robustness to this specific grammatical variation in a conversational context.")
    print("----------------------------")

# ------------------ Entrypoint ------------------
if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Run Gemini Linguistic Bias Audit")
    parser.add_argument('--model', type=str, default=DEFAULT_LLM_MODEL_ID, 
                        help=f'LLM model name (default: {DEFAULT_LLM_MODEL_ID})')
    parser.add_argument('--rounds', type=int, default=DEFAULT_NUM_TURNS, 
                        help=f'Number of audit rounds (default: {DEFAULT_NUM_TURNS})')
    parser.add_argument('--qpm', type=int, default=60, 
                        help='Queries per minute limit for the API. Used to calculate delay. (default: 60)')
    parser.add_argument('--seed', type=int, default=42, 
                        help='Random seed for reproducibility (default: 42)')
    parser.add_argument('--max_calls', type=int, default=0, 
                        help='Hard cap on total API calls. 0 means no limit. (default: 0)')
    parser.add_argument('--dry_run', type=int, default=0, 
                        help='Stop after processing N probe pairs (original + no-articles). 0 means no limit. (default: 0)')
    parser.add_argument('-v', '--verbose', action='store_true', 
                        help='Enable verbose (DEBUG) logging.')
    parser.add_argument('--only_analyze', help='Only run analysis on existing results, do not execute the audit loop.', action='store_true')
    
    args = parser.parse_args()

    # Set logging level
    if args.verbose:
        logger.setLevel(logging.DEBUG)
    else:
        logger.setLevel(logging.INFO)

    if args.only_analyze:
        logger.info("Running analysis on existing results only.")
        analyze_results()
        exit(0)

    # Set random seeds for reproducibility
    random.seed(args.seed)
    np.random.seed(args.seed)
    logger.info(f"Random seed set to {args.seed}")

    api_key = os.getenv('GEMINI_API_KEY', None) 
    if not api_key:
        logger.error("API Key not provided. Please set GEMINI_API_KEY environment variable.")
        exit(1)

    # Calculate qpm_delay based on the provided QPM, assuming 2 API calls per probe pair
    # If a probe has no articles, it's 1 API call, but we still apply the delay for consistency
    if args.qpm > 0:
        # (60 seconds / QPM) * (2 calls per probe pair)
        # This ensures we don't exceed QPM for the *pairs* of calls
        qpm_delay = (60 / args.qpm) * 2 
        logger.info(f"QPM set to {args.qpm}. Delay per probe pair (2 API calls) is {qpm_delay:.2f} seconds.")
    else:
        logger.warning("QPM set to 0 or less. No rate limiting delay will be applied.")
        qpm_delay = 0

    # Download NLTK data if not already present
    try:
        nltk.data.find('tokenizers/punkt')
        nltk.data.find('sentiment/vader_lexicon.zip')
    except nltk.downloader.DownloadError:
        logger.info("NLTK data (punkt or vader_lexicon) not found. Downloading...")
        nltk.download('punkt')
        nltk.download('vader_lexicon')
    except LookupError: # Fallback for other NLTK data not found errors
        logger.info("NLTK data (punkt or vader_lexicon) not found. Attempting download...")
        nltk.download('punkt')
        nltk.download('vader_lexicon')


    run_audit_loop(api_key, args.model, args.rounds, qpm_delay, max_calls=args.max_calls, dry_run=args.dry_run)
    analyze_results()
