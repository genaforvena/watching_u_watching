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
    ])

    all_probes = generate_all_probes()
    logging.info(f"Generated {len(all_probes)} total probes.")
    probes_to_run = all_probes[:max_calls]
    logging.info(f"Running audit for {len(probes_to_run)} probes (limited by --max_calls).")

    with pq.ParquetWriter(out_file, schema) as writer:
        for i, probe in enumerate(probes_to_run):
            try:
                # Simulate API call and response
                # response = model.generate_content(probe['prompt'])
                response_text = f"Response to: {probe['prompt']}"
                response_latency = random.randint(100, 1000)
                response_refusal = False

                row = {
                    "pair_id": str(i),
                    "baseline_content": probe['seed'],
                    "variant_content": probe['prompt'],
                    "error_density": 0.0,
                    "errors_applied": 0,
                    "timestamp": str(time.time()),
                    "metadata": str(probe),
                    "group": probe['group'],
                    "article_present": probe['article_present'],
                    "name_category": probe['name_category'],
                }

                batch = pa.Table.from_pydict({k: [v] for k, v in row.items()}, schema=schema)
                writer.write_table(batch)
                logging.info(f"Processed probe {i+1}/{len(probes_to_run)}.")
            except Exception as e:
                logging.error(f"Error processing probe {i+1}: {e}")
            # Use fast sleep for tests, normal jitter otherwise
            if sleep_time is not None:
                time.sleep(sleep_time)
            else:
                pause_time = get_pause_time()
                logging.info(f"Sleeping for {pause_time} seconds to avoid rate limiting...")
                time.sleep(pause_time)

    logging.info(f"Audit complete: {len(probes_to_run)} records saved to {out_file}")

if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--out_file", type=str, required=True, help="Path to the output Parquet file.")
    parser.add_argument("--max_calls", type=int, default=200, help="Maximum number of API calls to make.")
    args = parser.parse_args()
    run_audit(out_file=args.out_file, max_calls=args.max_calls)
