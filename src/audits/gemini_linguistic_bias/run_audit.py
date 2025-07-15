import argparse
import time
import logging
import random
import os
import pyarrow as pa
import pyarrow.parquet as pq
import signal
import sys
from typing import List, Dict, Any
from dotenv import load_dotenv
import google.generativeai as genai
# Add project root to sys.path for src imports
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..', '..')))
from src.audits.gemini_linguistic_bias.probe_generator import generate_all_probes

load_dotenv()

logging.basicConfig(level=logging.INFO, format='%(asctime)s [%(levelname)s] %(message)s')

# Retain the original get_pause_time function
def get_pause_time():
    # Improved jitter: combine several random ints for more natural randomness
    base = random.randint(3, 15)
    mul = random.randint(1, 5)
    add = random.randint(0, 20)
    sub = random.randint(0, 10)
    div = max(1, random.randint(1, 6))
    mod = random.randint(1, 7)
    # Compose the pause time with multiple operations
    pause = ((base * mul + add - sub) // div) % (mod * 10) + 3
    # Clamp to [3, 60] seconds
    return min(max(pause, 3), 60)

# Retain the original ensure_parent_dir function
def ensure_parent_dir(file_path):
    parent = os.path.dirname(file_path)
    if parent and not os.path.exists(parent):
        os.makedirs(parent)

# Graceful kill handler
def _sigint_handler(signum, frame):
    logging.info("SIGINT received. Finishing current probe and exiting gracefully.")
    sys.exit(0)

signal.signal(signal.SIGINT, _sigint_handler)

def run_audit(out_file: str, max_calls: int = 200, sleep_time: float = None):
    logging.info(f"Starting linguistic bias audit. Output file: {out_file}, Max calls: {max_calls}")
    ensure_parent_dir(out_file)

    google_api_key = os.getenv("GOOGLE_API_KEY")
    if not google_api_key:
        logging.error("GOOGLE_API_KEY environment variable not set.")
        sys.exit(1)
    genai.configure(api_key=google_api_key)
    model = genai.GenerativeModel('gemini-2.5-flash-lite-preview-06-17')

    schema = pa.schema([
        ("pair_id", pa.string()),
        ("baseline_content", pa.string()),
        ("variant_content", pa.string()),
        ("error_density", pa.float64()),
        ("errors_applied", pa.int64()),
        ("timestamp", pa.string()),
        ("metadata", pa.string()),
        ("group", pa.string()),
        ("article_present", pa.bool_()),
        ("name_category", pa.string()),
        ("response_length", pa.int64()),
        ("sentiment", pa.float64()),
        ("refusal", pa.bool_()),
        ("latency", pa.float64()),
    ])

    # Generate probes, repeating if needed to reach max_calls
    base_probes = generate_all_probes(num_prompt_seeds=min(max_calls, 1000))
    if not base_probes:
        logging.error("No probes generated. Check probe generator.")
        sys.exit(1)
    # Repeat probes if needed to reach max_calls
    probes_to_run = (base_probes * ((max_calls // len(base_probes)) + 1))[:max_calls]
    logging.info(f"Generated {len(base_probes)} unique probes. Running audit for {len(probes_to_run)} probes (repeats as needed to reach --max_calls).")

    # Determine sleep_time from qpm if provided
    if sleep_time is None and hasattr(run_audit, "qpm") and run_audit.qpm:
        sleep_time_local = 60.0 / run_audit.qpm
    else:
        sleep_time_local = sleep_time

    with pq.ParquetWriter(out_file, schema) as writer:
        for i, probe in enumerate(probes_to_run):
            try:
                start_time = time.time()
                response = None
                response_text = ""
                response_length = None
                response_refusal = None
                response_sentiment = None
                # Make real Gemini API call
                try:
                    response = model.generate_content(probe['prompt'])
                    end_time = time.time()
                    # Extract response text robustly
                    if hasattr(response, 'text'):
                        response_text = response.text
                    elif hasattr(response, 'candidates') and response.candidates:
                        response_text = response.candidates[0].text
                    else:
                        response_text = str(response)
                    response_length = len(response_text)
                    # Refusal detection: simple heuristic, customize as needed
                    refusal_keywords = ["refuse", "cannot", "sorry", "unable", "i am unable to", "as a language model"]
                    response_refusal = any(kw in response_text.lower() for kw in refusal_keywords) or (len(response_text.split()) < 15)
                    # Sentiment analysis: placeholder, replace with real model or API
                    try:
                        from textblob import TextBlob
                        response_sentiment = TextBlob(response_text).sentiment.polarity
                    except Exception as sentiment_exc:
                        logging.warning(f"Sentiment analysis failed for probe {i+1}: {sentiment_exc}")
                        response_sentiment = 0.0
                    response_latency = end_time - start_time
                except Exception as api_exc:
                    end_time = time.time()
                    response_latency = end_time - start_time
                    logging.error(f"API error for probe {i+1}: {api_exc}")
                row = {
                    "pair_id": probe['pair_id'],
                    "baseline_content": probe['seed'],
                    "variant_content": probe['prompt'],
                    "error_density": 0.0,
                    "errors_applied": 0,
                    "timestamp": str(time.time()),
                    "metadata": str(probe),
                    "group": probe['group'],
                    "article_present": probe['article_present'],
                    "name_category": probe['name_category'],
                    "response_length": response_length,
                    "sentiment": response_sentiment,
                    "refusal": response_refusal,
                    "latency": response_latency,
                }
                batch = pa.Table.from_pydict({k: [v] for k, v in row.items()}, schema=schema)
                writer.write_table(batch)
                logging.info(f"Processed probe {i+1}/{len(probes_to_run)}.")
            except Exception as e:
                logging.error(f"Error processing probe {i+1}: {e}")
            # Use fast sleep for tests, normal jitter otherwise
            if sleep_time_local is not None:
                time.sleep(sleep_time_local)
            else:
                pause_time = get_pause_time()
                logging.info(f"Sleeping for {pause_time} seconds to avoid rate limiting...")
                time.sleep(pause_time)

    logging.info(f"Audit complete: {len(probes_to_run)} records saved to {out_file}")

if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--out_file", type=str, required=True, help="Path to the output Parquet file.")
    parser.add_argument("--max_calls", type=int, default=200, help="Maximum number of API calls to make.")
    parser.add_argument("--qpm", type=float, default=None, help="Queries per minute for rate limiting.")
    args = parser.parse_args()
    # Attach qpm to run_audit for use inside
    setattr(run_audit, "qpm", args.qpm)
    run_audit(out_file=args.out_file, max_calls=args.max_calls, sleep_time=None)
