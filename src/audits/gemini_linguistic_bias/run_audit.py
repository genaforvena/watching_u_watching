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
API_KEY = os.getenv('GEMINI_API_KEY', '') # Empty string, Canvas will inject if not set

# QPM_DELAY will be calculated based on CLI --qpm argument
QPM_DELAY = 0 # Placeholder, will be set after arg parsing

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

def get_llm_reply(prompt: str, model_instance: genai.GenerativeModel) -> dict:
    """
    Send prompt to Gemini, handle errors, measure latency, extract refusal, sentiment, and response.
    Uses exponential backoff for rate limits and handles blocked content.
    """
    max_retries = 5
    backoff_time = 1  # seconds
    
    # Regex for common refusal phrases (case-insensitive, word boundaries)
    refusal_pattern = re.compile(r"\b(?:sorry|cannot|can't|unable|not able|apologies|i am not able to)\b", re.IGNORECASE)

    for attempt in range(max_retries):
        start = time.time()
        response_text = ""
        refusal_flag = False
        sentiment = np.nan
        latency = np.nan
        
        try:
            response = model_instance.generate_content(prompt)
            latency = time.time() - start
            
            if response.candidates:
                # Check for explicit finish reasons that indicate a block/refusal
                if response.candidates[0].finish_reason in [
                    genai.types.HarmCategory.HARM_CATEGORY_UNSPECIFIED, # Often used for safety blocks
                    genai.types.BlockedReason.SAFETY, # Explicit safety block
                    genai.types.BlockedReason.OTHER # Other blocking reasons
                ]:
                    response_text = f"BLOCKED_RESPONSE: Finish reason - {response.candidates[0].finish_reason}"
                    refusal_flag = True
                    logger.warning(f"Candidate blocked with finish reason: {response.candidates[0].finish_reason}")
                elif response.candidates[0].content and response.candidates[0].content.parts:
                    response_text = response.candidates[0].content.parts[0].text
                    # Check for refusal phrases in the actual response text
                    if refusal_pattern.search(response_text):
                        refusal_flag = True
                        logger.info(f"Refusal phrase detected in response: {response_text[:50]}...")
                else:
                    response_text = "EMPTY_RESPONSE: Candidate content is empty or malformed."
                    refusal_flag = True
                    logger.warning("Empty or malformed candidate content received.")
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
def run_audit_loop(model_id: str, num_turns: int, max_calls: int = float('inf'), dry_run: int = 0):
    """
    Runs the multi-turn, self-iterating audit for LLM linguistic bias.
    
    Args:
        model_id (str): The ID of the LLM model to audit.
        num_turns (int): The number of turns (iterations) for the audit loop.
        max_calls (int): Hard cap on the total number of API calls.
        dry_run (int): If > 0, stops the audit after processing this many probe pairs.
    """
    global API_KEY, QPM_DELAY # Access global API_KEY and QPM_DELAY

    # Configure the GenerativeModel instance once here, after API_KEY is potentially updated by argparse
    genai.configure(api_key=API_KEY)
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

        for probe_text in current_probes:
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
            logger.debug(f"Turn {turn_number} | Probe ID: {base_probe_id} | Sending (with articles): {probe_text[:100]}...")
            llm_reply_data_orig = get_llm_reply(probe_text, model_instance)
            total_api_calls += 1
            all_audit_results.append({
                'probe_id': base_probe_id,
                'turn_number': turn_number,
                'probe_text': probe_text,
                'has_articles': True,
                **llm_reply_data_orig
            })
            logger.debug(f"Reply (with articles): {llm_reply_data_orig['response_text'][:100]}...")

            # --- Probe Without Articles ---
            probe_text_no_articles = remove_articles(probe_text)
            
            # Only create and send the 'no articles' probe if it's genuinely different and not empty
            if probe_text_no_articles != probe_text and probe_text_no_articles != "":
                logger.debug(f"Turn {turn_number} | Probe ID: {base_probe_id}_noart | Sending (without articles): {probe_text_no_articles[:100]}...")
                llm_reply_data_no_art = get_llm_reply(probe_text_no_articles, model_instance)
                total_api_calls += 1
                all_audit_results.append({
                    'probe_id': base_probe_id + '_noart',
                    'turn_number': turn_number,
                    'probe_text': probe_text_no_articles,
                    'has_articles': False,
                    **llm_reply_data_no_art
                })
                logger.debug(f"Reply (without articles): {llm_reply_data_no_art['response_text'][:100]}...")
            else:
                logger.info(f"Skipping 'no articles' probe for {base_probe_id}: No articles found to remove or resulted in empty string.")
            
            total_probes_processed += 1 # Increment after a pair (or single if no articles) is processed

            # --- Prepare Candidates for Next Turn ---
            # Only use replies from the 'articles present' version for generating new probes
            # to maintain a consistent "source" of new sentences.
            sentences_from_reply = extract_sentences(llm_reply_data_orig['response_text'], MAX_SENTENCES_PER_REPLY)
            
            # Filter for sentences that still contain articles, so we can manipulate them next turn
            article_sentences_for_next_turn = [s for s in sentences_from_reply if re.search(r'\b(a|an|the)\b', s, re.IGNORECASE)]
            
            if article_sentences_for_next_turn:
                next_turn_candidates.extend(article_sentences_for_next_turn)
                # Also add to the global pool for potential fallback
                all_generated_article_sentences.extend(article_sentences_for_next_turn)

            # Proactive Rate Limiting: Delay after each probe pair (2 API calls, or 1 if no articles)
            time.sleep(QPM_DELAY) 
        
        # Break outer loop if inner loop broke due to caps
        if (dry_run > 0 and total_probes_processed >= dry_run) or \
           (max_calls > 0 and total_api_calls >= max_calls):
            break

        # --- Select Probes for the Next Turn ---
        # Ensure we have a consistent number of probes for the next turn,
        # equal to the initial prompt count.
        target_next_probe_count = len(INITIAL_PROMPTS) 
        
        # Use unique candidates from this round first
        unique_next_turn_candidates = list(set(next_turn_candidates)) # Remove duplicates from current round's candidates

        # Dynamic adjustment of MAX_SENTENCES_PER_REPLY if needed for next turn
        current_max_sentences_per_reply = MAX_SENTENCES_PER_REPLY
        if len(unique_next_turn_candidates) < target_next_probe_count and turn_number < num_turns - 1:
            # If we're running low on unique candidates for the next turn,
            # try to extract more sentences per reply in the *next* turn.
            # This is a heuristic to prevent starvation.
            # We'll double the cap for the *next* turn's processing.
            # Note: This requires MAX_SENTENCES_PER_REPLY to be a mutable variable or passed around.
            # For simplicity, we'll just log a warning for now and rely on fallback.
            logger.warning(f"Low unique candidates ({len(unique_next_turn_candidates)}) for next turn. Consider increasing MAX_SENTENCES_PER_REPLY or initial prompts.")
            # If you wanted to dynamically adjust, you'd need to pass this into get_llm_reply or extract_sentences
            # or make it a global mutable. For now, the fallback handles it.

        if len(unique_next_turn_candidates) >= target_next_probe_count:
            # If enough unique candidates from this round, sample them
            current_probes = random.sample(unique_next_turn_candidates, target_next_probe_count)
            logger.info(f"Turn {turn_number} completed. Next turn probes sampled from current round's replies.")
        else:
            # If not enough unique candidates from this round, supplement from the overall pool
            # Prioritize unique sentences from the overall pool
            unique_all_generated = list(set(all_generated_article_sentences))
            
            if len(unique_all_generated) >= target_next_probe_count:
                # Sample from the entire pool of generated sentences with articles
                current_probes = random.sample(unique_all_generated, target_next_probe_count)
                logger.info(f"Turn {turn_number} completed. Next turn probes sampled from all generated replies so far.")
            elif unique_all_generated:
                # If still not enough unique, allow duplicates from the overall pool
                current_probes = random.choices(unique_all_generated, k=target_next_probe_count)
                logger.info(f"Turn {turn_number} completed. Next turn probes chosen from all generated replies (with duplicates).")
            else:
                # Fallback: If absolutely no valid sentences with articles were ever generated, restart with initial prompts
                current_probes = INITIAL_PROMPTS.copy()
                logger.warning(f"Turn {turn_number} completed. No valid article-containing sentences generated or available. Restarting with INITIAL_PROMPTS.")

    # Save results after all turns are complete or caps are hit
    df = pd.DataFrame(all_audit_results)
    df.to_parquet(RESULTS_FILE_PATH, index=False) # index=False to avoid writing pandas index
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
    plt.xticks(ticks=[0, 1], labels=['False', 'True'], rotation=0)
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
    plt.xticks(ticks=[0, 1], labels=['False', 'True'], rotation=0)
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
    plt.xticks(ticks=[0, 1], labels=['False', 'True'], rotation=0)
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
    parser.add_argument('--api_key', type=str, default=API_KEY, 
                        help='Your Google Gemini API key. Can also be set via GEMINI_API_KEY environment variable.')
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
    
    args = parser.parse_args()

    # Set logging level
    if args.verbose:
        logger.setLevel(logging.DEBUG)
    else:
        logger.setLevel(logging.INFO)

    # Set random seeds for reproducibility
    random.seed(args.seed)
    np.random.seed(args.seed)
    logger.info(f"Random seed set to {args.seed}")

    # Update global API_KEY if provided via command line
    if args.api_key:
        API_KEY = args.api_key
    
    if not API_KEY:
        logger.error("API Key not provided. Please set GEMINI_API_KEY environment variable or use --api_key argument.")
        exit(1)

    # Calculate QPM_DELAY based on the provided QPM, assuming 2 API calls per probe pair
    # If a probe has no articles, it's 1 API call, but we still apply the delay for consistency
    if args.qpm > 0:
        # (60 seconds / QPM) * (2 calls per probe pair)
        # This ensures we don't exceed QPM for the *pairs* of calls
        global QPM_DELAY
        QPM_DELAY = (60 / args.qpm) * 2 
        logger.info(f"QPM set to {args.qpm}. Delay per probe pair (2 API calls) is {QPM_DELAY:.2f} seconds.")
    else:
        logger.warning("QPM set to 0 or less. No rate limiting delay will be applied.")
        QPM_DELAY = 0

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


    run_audit_loop(args.model, args.rounds, max_calls=args.max_calls, dry_run=args.dry_run)
    analyze_results()
