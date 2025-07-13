import time
import argparse
import pandas as pd
from vaderSentiment.vaderSentiment import SentimentIntensityAnalyzer
from src.audits.gemini_linguistic_bias.probe_generator import generate_grouped_probes as generate_probes
import requests
import os
from datetime import datetime

GEMINI_ENDPOINT = "https://generativelanguage.googleapis.com/v1beta/models/gemini-2.5-flash:generateContent"


def call_gemini_api(prompt, api_key, max_retries=5, backoff_factor=2):
    url = f"{GEMINI_ENDPOINT}?key={api_key}"
    data = {
        "contents": [{"parts": [{"text": prompt}]}]
    }
    retries = 0
    wait_time = 1
    while retries <= max_retries:
        start = time.time()
        try:
            response = requests.post(url, json=data, timeout=30)
        except requests.exceptions.RequestException:
            return None
        latency = int((time.time() - start) * 1000)
        if response.status_code == 429:
            if wait_time < 60:
                print(f"Rate limit hit. Waiting {wait_time}s before retrying... (retry {retries+1}/{max_retries})")
            else:
                print(f"Rate limit hit. Waiting {wait_time // 60}m before retrying... (retry {retries+1}/{max_retries})")
            time.sleep(wait_time)
            retries += 1
            wait_time *= backoff_factor
            continue  # Don't count this attempt
        if response.status_code != 200:
            # Not a refusal, just an error
            return {
                "text": "API call failed",
                "latency": latency,
                "refusal": False,
                "api_error": True,
                "status_code": response.status_code
            }
        # Status code 200: Analyze for refusal
        resp_json = response.json()
        candidates = resp_json.get("candidates", [])
        text = ""
        if candidates:
            parts = candidates[0].get("content", {}).get("parts", [])
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
    length = len(response['text'])
    sentiment = analyzer.polarity_scores(response['text'])['compound'] if response['text'] else 0.0
    refusal_flag = response['refusal']
    latency = response['latency']
    api_error = response.get('api_error', False)
    status_code = response.get('status_code', None)
    return length, sentiment, refusal_flag, latency, api_error, status_code

def main(num_probes, qpm, out_file):
    api_key = os.environ.get("GEMINI_API_KEY")
    if not api_key:
        print("ERROR: GEMINI_API_KEY environment variable not set.")
        return
    probes = generate_probes(num_probes)
    metrics = []
    analyzer = SentimentIntensityAnalyzer()
    collected = 0
    probe_index = 0
    total = len(probes)
    while collected < num_probes:
        if probe_index >= total:
            print(f"\nWARNING: Probe count: {collected} (expected {num_probes})")
            break
        probe = probes[probe_index]
        print(f"Collecting probe {collected+1}/{num_probes}...", end="\r")
        resp = call_gemini_api(probe['prompt'], api_key)
        if resp is None:
            # Probe failed due to rate limit or repeated errors; skip, do not count, keep trying next probe
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
        time.sleep(60.0 / qpm)
    print(f"\nCollection complete: {len(metrics)}/{num_probes} probes successfully gathered.")
    os.makedirs(os.path.dirname(out_file), exist_ok=True)
    try:
        pd.DataFrame(metrics).to_parquet(out_file)
    except IOError as e:
        print(f"Error writing to Parquet file: {e}")
    print(f"Audit complete: {len(metrics)} records saved to {out_file}")


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description='Run Gemini linguistic bias audit.')
    parser.add_argument('--num_probes', type=int, default=200, help='Number of probes to run (default: 200)')
    parser.add_argument('--qpm', type=int, default=60, help='Queries per minute rate limit (default: 60)')
    parser.add_argument('--out_file', type=str, default='data/gemini_bias.parquet', help='Output Parquet filename')
    args = parser.parse_args()
    main(args.num_probes, args.qpm, args.out_file)
