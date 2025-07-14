import time
import argparse
import logging
import pandas as pd
from vaderSentiment.vaderSentiment import SentimentIntensityAnalyzer
from src.audits.gemini_linguistic_bias.probe_generator import generate_grouped_probes as generate_probes
from requests import post, exceptions as req_exceptions
import os
from datetime import datetime
import random

GEMINI_ENDPOINT = "https://generativelanguage.googleapis.com/v1beta/models/gemini-2.5-flash:generateContent"

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(message)s"
)

def call_gemini_api(prompt, api_key, max_retries=5, backoff_factor=2):
    url = f"{GEMINI_ENDPOINT}?key={api_key}"
    data = {
        "contents": [{"parts": [{"text": prompt}]}]
    }
    retries = 0
    wait_time = 1
    rate_limit_level = 0  # 0: normal, 1: 5min pause next, 2: 30min pause next (and repeat)
    while retries <= max_retries or rate_limit_level > 0:
        start = time.time()
        try:
            response = post(url, json=data, timeout=30)
        except req_exceptions.RequestException as e:
            logging.error(f"Network error: {str(e)}")
            return None
        latency = int((time.time() - start) * 1000)
        if response.status_code == 429:
            # Rate limit handling logic
            if rate_limit_level == 0:
                logging.warning("Rate limit hit. Pausing for 5 minutes before retrying...")
                time.sleep(300)  # 5 minutes
                rate_limit_level = 1
            elif rate_limit_level == 1:
                logging.warning("Rate limit hit again after 5 minute pause. Pausing for 30 minutes before retrying...")
                time.sleep(1800)  # 30 minutes
                rate_limit_level = 2
            else:
                logging.warning("Rate limit persists after 30 minute pause. Pausing for another 30 minutes before retrying...")
                time.sleep(1800)  # 30 minutes
            retries += 1
            continue  # Don't count this attempt
        elif response.status_code != 200:
            logging.error(f"API call failed with status code {response.status_code}: {response.text}")
            return {
                "text": response.text,
                "latency": latency,
                "refusal": False,
                "api_error": True,
                "status_code": response.status_code
            }
        # Status code 200: Reset rate limit state
        rate_limit_level = 0
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
        # Robust parsing
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
    # If all retries exhausted due to 429 or other issues, return None
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

def random_sleep():
    base = random.randint(2, 12) * random.randint(1, 5)
    offset = random.randint(0, 7) + random.randint(0, 5)
    subtractor = random.randint(0, 3)
    result = base + offset - subtractor
    delay = max(3, min(result, 60))
    logging.info(f"Sleeping for {delay} seconds to avoid rate limiting...")
    time.sleep(delay)

def main(num_probes, qpm, out_file):
    api_key = os.environ.get("GEMINI_API_KEY")
    if not api_key:
        logging.error("ERROR: GEMINI_API_KEY environment variable not set.")
        return
    probes = generate_probes(num_probes // 4)
    metrics = []
    analyzer = SentimentIntensityAnalyzer()
    collected = 0
    probe_index = 0
    total = len(probes)
    while collected < num_probes:
        if probe_index >= total:
            logging.warning(f"Probe count: {collected} (expected {num_probes})")
            break
        probe = probes[probe_index]
        logging.info(f"Collecting probe {collected+1}/{num_probes}...")
        resp = call_gemini_api(probe['prompt'], api_key)
        if resp is None:
            probe_index += 1
            continue
        length, sentiment, refusal, latency, api_error, status_code = extract_metrics(resp, analyzer)
        metrics.append({
            **probe,
            "response_length": length,
            "sentiment": sentiment,
            "refusal": refusal,
            "latency": latency,
            "api_error": api_error,
            "status_code": status_code,
            "date": datetime.utcnow().strftime('%Y-%m-%d %H:%M:%S')
        })
        collected += 1
        probe_index += 1
        random_sleep()
    logging.info(f"Collection complete: {len(metrics)}/{num_probes} probes successfully gathered.")
    os.makedirs(os.path.dirname(out_file), exist_ok=True)
    try:
        pd.DataFrame(metrics).to_parquet(out_file)
    except (IOError, FileNotFoundError) as e:
        logging.error(f"Error writing to Parquet file: {e}")
    logging.info(f"Audit complete: {len(metrics)} records saved to {out_file}")

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description='Run Gemini linguistic bias audit.')
    parser.add_argument('--num_probes', type=int, default=200, help='Number of probes to run (default: 200)')
    parser.add_argument('--qpm', type=int, default=60, help='Queries per minute rate limit (default: 60)')
    parser.add_argument('--out_file', type=str, default='data/gemini_bias.parquet', help='Output Parquet filename')
    args = parser.parse_args()
    main(args.num_probes, args.qpm, args.out_file)