import argparse
import time
import logging
import pandas as pd
import random
from probe_generator import ProbeGenerator, ProbeType, ErrorDensity, ErrorType

logging.basicConfig(level=logging.INFO, format='%(asctime)s [%(levelname)s] %(message)s')

def get_pause_time():
    """
    Generate a random pause time using a mix of operations
    to avoid explicit patterns. Maximum pause = 30 sec, minimum = 2 sec.
    """
    base = random.randint(2, 8)
    mod = random.randint(1, 5)
    add = random.randint(0, 10)
    sub = random.randint(0, 6)
    mul = random.randint(1, 3)
    div = max(1, random.randint(1, 3))  # avoid division by zero
    pause = ((base * mul + add - sub) // div) + 2
    # Cap at 30 seconds
    return min(max(pause, 2), 30)

def run_audit(mode, out_file, probe_type=ProbeType.LLM_QUESTION, expected_count=60, error_density=ErrorDensity.MEDIUM):
    generator = ProbeGenerator(seed=42)
    error_types = [ErrorType.TYPO, ErrorType.GRAMMAR, ErrorType.NON_STANDARD, ErrorType.ARTICLE_OMISSION]
    all_pairs = []

    logging.info(f"Starting audit in '{mode}' mode: Short run: up to 20 minutes and covers both missing/present articles.")

    for i in range(expected_count):
        include_missing = (i % 2 == 1)
        pairs = generator.generate_probe_pairs(
            probe_type=probe_type,
            count=1,
            error_density=error_density,
            error_types=error_types,
            include_missing=include_missing
        )
        all_pairs.extend(pairs)
        logging.info(f"Collecting probe {i+1}/{expected_count}...")

        pause_time = get_pause_time()
        logging.info(f"Sleeping for {pause_time} seconds to avoid rate limiting...")
        time.sleep(pause_time)

    logging.info(f"Collection complete: {len(all_pairs)}/{expected_count} probes gathered.")
    df = pd.DataFrame([{
        "pair_id": p.pair_id,
        "probe_type": p.probe_type,
        "baseline_content": p.baseline_content,
        "variant_content": p.variant_content,
        "error_density": str(p.error_density),
        "errors_applied": str(p.errors_applied),
        "timestamp": p.timestamp,
        "metadata": p.metadata
    } for p in all_pairs])
    df.to_parquet(out_file)
    logging.info(f"Audit complete: {len(all_pairs)} records saved to {out_file}")

if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--mode", type=str, default="short")
    parser.add_argument("--out_file", type=str, required=True)
    args = parser.parse_args()
    run_audit(mode=args.mode, out_file=args.out_file)