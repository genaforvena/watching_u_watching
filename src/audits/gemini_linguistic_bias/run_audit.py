import time
import argparse
import pandas as pd
from vaderSentiment.vaderSentiment import SentimentIntensityAnalyzer
from src.audits.gemini_linguistic_bias.probe_generator import generate_probes
import requests
import os
import logging
from datetime import datetime

GEMINI_ENDPOINT = "https://generativelanguage.googleapis.com/v1beta/models/gemini-2.0-flash-exp:generateContent"

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s %(levelname)s %(message)s"
)

def call_gemini_api(prompt, api_key):
    headers = {"Authorization": f"Bearer {api_key}"}
    data = {
        "contents": [{"parts": [{"text": prompt}]}]
    }
    start = time.time()
    try:
        response = requests.post(GEMINI_ENDPOINT, json=data, headers=headers)
    except requests.exceptions.RequestException as e:
        logging.error(f"API call failed: {e}")
        return {"text": "API call failed", "latency": None, "refusal": True, "api_error": True}
    latency = int((time.time() - start) * 1000)
    if response.status_code != 200:
        logging.error(f"Non-200 response: {response.status_code}")
        return {"text": "API call failed", "latency": latency, "refusal": True, "api_error": True}
    resp_json = response.json()
    candidates = resp_json.get("candidates", [])
    text = ""
    if candidates:
        parts = candidates[0].get("content", {}).get("parts", [])
        if parts:
            text = parts[0].get("text", "")
    refusal_phrases = {"policy violation", "cannot fulfill", "not allowed"}
    refusal_flag = any(phrase in text.lower() for phrase in refusal_phrases)
    return {"text": text, "latency": latency, "refusal": refusal_flag}

def extract_metrics(response, analyzer):
    length = len(response['text'])
    sentiment = analyzer.polarity_scores(response['text'])['compound'] if response['text'] else 0.0
    refusal_flag = response['refusal']
    latency = response['latency']
    return length, sentiment, refusal_flag, latency

def main(api_key, num_probes, qpm, out_file):
    probes = generate_probes(num_probes)
    metrics = []
    analyzer = SentimentIntensityAnalyzer()
    for i, probe in enumerate(probes):
        try:
            resp = call_gemini_api(probe['prompt'], api_key)
        except Exception as e:
            logging.error(f"Error calling Gemini API: {e}")
            continue
        if resp.get("api_error"):
            length, sentiment, refusal, latency = 0, 0.0, True, resp.get('latency', None)
        else:
            length, sentiment, refusal, latency = extract_metrics(resp, analyzer)
        metrics.append({
            **probe,
            "response_length": length,
            "sentiment": sentiment,
            "refusal": refusal,
            "latency": latency,
            "date": datetime.utcnow().strftime('%Y-%m-%d %H:%M:%S')
        })
        time.sleep(60.0 / qpm)
    df = pd.DataFrame(metrics)
    os.makedirs(os.path.dirname(out_file), exist_ok=True)
    try:
        df.to_parquet(out_file)
    except IOError as e:
        logging.error(f"Error writing to Parquet file: {e}")
    logging.info(f"Audit complete: {len(df)} records saved to {out_file}")

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description='Run Gemini linguistic bias audit.')
    parser.add_argument('api_key', help='Your Gemini API key')
    parser.add_argument('--num_probes', type=int, default=200, help='Number of probes to run (default: 200)')
    parser.add_argument('--qpm', type=int, default=60, help='Queries per minute rate limit (default: 60)')
    parser.add_argument('--out_file', type=str, default='data/gemini_bias.parquet', help='Output Parquet filename')
    args = parser.parse_args()
    main(args.api_key, args.num_probes, args.qpm, args.out_file)