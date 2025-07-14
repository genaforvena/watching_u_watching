import argparse
import time
import logging
import random
import os
import pyarrow as pa
import pyarrow.parquet as pq
from probe_generator import ProbeGenerator, ProbeType, ErrorDensity, ErrorType

logging.basicConfig(level=logging.INFO, format='%(asctime)s [%(levelname)s] %(message)s')

def get_pause_time():
    base = random.randint(2, 8)
    mod = random.randint(1, 5)
    add = random.randint(0, 10)
    sub = random.randint(0, 6)
    mul = random.randint(1, 3)
    div = max(1, random.randint(1, 3))
    pause = ((base * mul + add - sub) // div) + 2
    return min(max(pause, 2), 30)

def ensure_parent_dir(file_path):
    parent = os.path.dirname(file_path)
    if parent and not os.path.exists(parent):
        os.makedirs(parent)

def run_audit(mode, out_file, probe_type=ProbeType.LLM_QUESTION, expected_count=60, error_density=ErrorDensity.MEDIUM):
    generator = ProbeGenerator(seed=42)
    error_types = [ErrorType.TYPO, ErrorType.GRAMMAR, ErrorType.NON_STANDARD, ErrorType.ARTICLE_OMISSION]
    logging.info(f"Starting audit in '{mode}' mode: Short run: up to 20 minutes and covers both missing/present articles.")
    ensure_parent_dir(out_file)

    # Define schema for Parquet
    schema = pa.schema([
        ("pair_id", pa.string()),
        ("probe_type", pa.string()),
        ("baseline_content", pa.string()),
        ("variant_content", pa.string()),
        ("error_density", pa.string()),
        ("errors_applied", pa.string()),
        ("timestamp", pa.float64()),
        ("metadata", pa.string()),
        ("group", pa.string()) # Fix: Added parentheses here
    ])

    with pq.ParquetWriter(out_file, schema) as writer:
        for i in range(expected_count):
            include_missing = (i % 2 == 1)
            pairs = generator.generate_probe_pairs(
                probe_type=probe_type,
                count=1,
                error_density=error_density,
                error_types=error_types,
                include_missing=include_missing
            )
            for p in pairs:
                row = {
                    "pair_id": p.pair_id,
                    "probe_type": p.probe_type,
                    "baseline_content": p.baseline_content,
                    "variant_content": p.variant_content,
                    "error_density": str(p.error_density),
                    "errors_applied": str(p.errors_applied),
                    "timestamp": p.timestamp,
                    "metadata": str(p.metadata), # Fix: Explicitly convert metadata to string
                    "group": f"{p.probe_type}_{'missing_article' if p.metadata.get('missing_article') else 'present_article'}"
                } # Fix: Removed the erroneous " for p in pairs)" here
                batch = pa.Table.from_pydict({k: [v] for k, v in row.items()}, schema=schema)
                writer.write_table(batch)
            logging.info(f"Collecting probe {i+1}/{expected_count}...")
            pause_time = get_pause_time()
            logging.info(f"Sleeping for {pause_time} seconds to avoid rate limiting...")
            time.sleep(pause_time)

    logging.info(f"Audit complete: {expected_count} records saved to {out_file}")

if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--mode", type=str, default="short")
    parser.add_argument("--out_file", type=str, required=True)
    args = parser.parse_args()
    run_audit(mode=args.mode, out_file=args.out_file)
