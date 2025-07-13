import argparse
import datetime
from probe_generator import generate_probes
# ... other imports ...

MAX_CALLS_DEFAULT = 200
QPM_DEFAULT = 60

def main(api_key, num_probes=MAX_CALLS_DEFAULT, qpm=QPM_DEFAULT):
    probes = generate_probes(num_probes)
    results = []
    for idx, probe in enumerate(probes):
        # ... run audit for each probe ...
        result = {
            "probe_idx": idx,
            "prompt": probe["prompt"],
            "name": probe["name"],
            "english_level": probe["english_level"],
            "seed": probe["seed"],
            # ... all other extracted metrics ...
            "date": datetime.datetime.utcnow().strftime('%Y-%m-%d %H:%M:%S')
        }
        results.append(result)
        # ... rate limiting logic ...
    # ... save results to Parquet/CSV ...
    return results

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description='Run Gemini linguistic bias audit.')
    parser.add_argument('api_key', help='Your Gemini API key')
    parser.add_argument('--num_probes', type=int, default=MAX_CALLS_DEFAULT, help='Number of probes to run')
    parser.add_argument('--qpm', type=int, default=QPM_DEFAULT, help='Queries per minute rate limit')
    args = parser.parse_args()
    main(args.api_key, args.num_probes, args.qpm)