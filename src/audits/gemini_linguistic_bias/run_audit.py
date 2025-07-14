import time
import argparse
import logging
import pandas as pd
from vaderSentiment.vaderSentiment import SentimentIntensityAnalyzer
from probe_generator import generate_grouped_probes as generate_probes
from requests import post, exceptions as req_exceptions
import os
from datetime import datetime

MODE_CONFIG = {
    'dry': {
        'num_probes': 1,
        'max_minutes': 1,
        'save': False,
        'desc': "Dry run: one probe to test the pipeline."
    },
    'short': {
        'num_probes': 60,  # Should be enough for both missing/present articles, but can be tuned
        'max_minutes': 20,
        'save': True,
        'desc': "Short run: up to 20 minutes and covers both missing/present articles."
    },
    'full': {
        'num_probes': 1200,  # ~8 hours at ~25sec/probe
        'max_minutes': 480,
        'save': True,
        'desc': "Full run: gathers maximum data for up to 8 hours."
    }
}

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(message)s"
)

GEMINI_ENDPOINT = "https://generativelanguage.googleapis.com/v1beta/models/gemini-2.5-flash:generateContent"

def call_gemini_api(prompt, api_key, max_retries=5):
    url = f"{GEMINI_ENDPOINT}?key={api_key}"
    data = {"contents": [{"parts": [{"text": prompt}]}]}
    retries = 0
    while retries <= max_retries:
        start = time.time()
        try:
            response = post(url, json=data, timeout=30)
        except req_exceptions.RequestException as e:
            logging.error(f"Network error: {str(e)}")
            return None
        latency = int((time.time() - start) * 1000)
        if response.status_code == 429:
            logging.warning("Rate limit hit. Pausing for 2 minutes before retrying...")
            time.sleep(120)
            retries += 1
            continue
        elif response.status_code != 200:
            logging.error(f"API call failed with status code {response.status_code}: {response.text}")
            return {
                "text": response.text,
                "latency": latency,
                "refusal": False,
                "api_error": True,
                "status_code": response.status_code
            }
        try:
            resp_json = response.json()
        except Exception as e:
            logging.error(f"Failed to parse response as JSON: {str(e)}")
            return {
                "text": "API response could not be parsed",
                "latency": latency,
                "refusal": False,
                "api_error": True,
                "status_code": response.status_code
            }
        candidates = resp_json.get("candidates", [])
        text = ""
        if candidates:
            content = candidates[0].get("content", {})
            parts = content.get("parts", [])
            if parts:
                text = parts[0].get("text", "")
        refusal_phrases = {"policy violation", "cannot fulfill", "not allowed"}
        refusal_flag = any(phrase in text.lower() for phrase in refusal_phrases)
        return {
            "text": text,
            "latency": latency,
            "refusal": refusal_flag,
            "api_error": False,
            "status_code": response.status_code
        }
    return None

def extract_metrics(response, analyzer):
    try:
        text = response.get('text', '')
        length = len(text)
        sentiment = analyzer.polarity_scores(text).get('compound', 0.0) if text else 0.0
        refusal_flag = response.get('refusal', False)
        latency = response.get('latency', 0)
        api_error = response.get('api_error', False)
        status_code = response.get('status_code', None)
    except KeyError as e:
        logging.error(f"Missing key in response: {str(e)}")
        length, sentiment, refusal_flag, latency, api_error, status_code = 0, 0.0, False, 0, True, None
    return length, sentiment, refusal_flag, latency, api_error, status_code

def random_sleep(qpm):
    import random
    # If qpm is set to 0 or negative, do not sleep
    if qpm <= 0:
        return
    # Calculate sleep time based on qpm (queries per minute)
    min_sleep = max(1, int(60 / qpm))
    delay = random.randint(min_sleep, min_sleep + 10)
    logging.info(f"Sleeping for {delay} seconds to avoid rate limiting...")
    time.sleep(delay)

def main(mode, out_file, qpm):
    config = MODE_CONFIG.get(mode)
    if not config:
        logging.error(f"Unknown mode '{mode}'. Valid modes are: {', '.join(MODE_CONFIG.keys())}")
        return
    logging.info(f"Starting audit in '{mode}' mode: {config['desc']}")
    api_key = os.environ.get("GEMINI_API_KEY")
    if not api_key:
        logging.error("ERROR: GEMINI_API_KEY environment variable not set.")
        return
    probes = generate_probes(config['num_probes'] // 4)
    metrics = []
    analyzer = SentimentIntensityAnalyzer()
    start_time = time.time()
    probe_index = 0
    total = len(probes)
    while probe_index < config['num_probes']:
        elapsed_minutes = (time.time() - start_time) / 60
        if elapsed_minutes > config['max_minutes']:
            logging.info(f"Time limit reached for mode '{mode}'. Stopping collection.")
            break
        if probe_index >= total:
            logging.warning(f"Ran out of probes ({probe_index}/{config['num_probes']})")
            break
        probe = probes[probe_index]
        logging.info(f"Collecting probe {probe_index+1}/{config['num_probes']}...")
        resp = call_gemini_api(probe['prompt'], api_key)
        if resp is None:
            probe_index += 1
            continue
        length, sentiment, refusal, latency, api_error, status_code = extract_metrics(resp, analyzer)
        metric = {
            **probe,
            "response_length": length,
            "sentiment": sentiment,
            "refusal": refusal,
            "latency": latency,
            "api_error": api_error,
            "status_code": status_code,
            "date": datetime.utcnow().strftime('%Y-%m-%d %H:%M:%S')
        }
        metrics.append(metric)
        probe_index += 1
        random_sleep(qpm)
    logging.info(f"Collection complete: {len(metrics)}/{config['num_probes']} probes gathered.")
    if config['save']:
        os.makedirs(os.path.dirname(out_file), exist_ok=True)
        try:
            pd.DataFrame(metrics).to_parquet(out_file)
        except (IOError, FileNotFoundError) as e:
            logging.error(f"Error writing to Parquet file: {e}")
        logging.info(f"Audit complete: {len(metrics)} records saved to {out_file}")
    else:
        logging.info("Dry run mode: No data saved.")

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description='Run Gemini linguistic bias audit.')
    parser.add_argument('--mode', type=str, choices=['dry', 'short', 'full'], default='dry',
                        help='Run mode: dry (test pipeline), short (20 min/data diversity), full (8 hours/max data)')
    parser.add_argument('--out_file', type=str, default='data/gemini_bias.parquet', help='Output Parquet filename')
    parser.add_argument('--qpm', type=int, default=60, help='Queries per minute rate limit (default: 60)')
    args = parser.parse_args()
    main(args.mode, args.out_file, args.qpm)