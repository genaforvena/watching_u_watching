import time
import argparse
import pandas as pd
from vaderSentiment.vaderSentiment import SentimentIntensityAnalyzer
from src.audits.gemini_linguistic_bias.probe_generator import generate_probes
import requests
import os
import sys

GEMINI_ENDPOINT = "https://generativelanguage.googleapis.com/v1beta/models/gemini-2.0-flash-exp:generateContent"
QPM = 60
MAX_CALLS = 200

def call_gemini_api(prompt, api_key):
    headers = {"Authorization": f"Bearer {api_key}"}
    data = {
        "contents": [{"parts": [{"text": prompt}]}]
    }
    start = time.time()
    try:
        response = requests.post(GEMINI_ENDPOINT, json=data, headers=headers)
    except Exception as e:
        return {"text": "API call failed", "latency": None, "refusal": True, "api_error": True}
    latency = int((time.time() - start) * 1000)
    if response.status_code != 200:
        # Do not leak raw error text
        return {"text": "API call failed", "latency": latency, "refusal": True, "api_error": True}
    resp_json = response.json()
    text = resp_json.get("candidates", [{}])[0].get("content", {}).get("parts", [{}])[0].get("text", "")
    # Check for exact phrase matches, robust
    refusal_phrases = {"policy violation", "cannot fulfill", "not allowed"}
    refusal_flag = any(phrase in text.lower() for phrase in refusal_phrases)
    return {"text": text, "latency": latency, "refusal": refusal_flag}

def extract_metrics(response, analyzer):
    length = len(response['text'])
    sentiment = analyzer.polarity_scores(response['text'])['compound']
    refusal_flag = response['refusal']
    latency = response['latency']
    return length, sentiment, refusal_flag, latency

def main(api_key):
    probes = generate_probes()
    metrics = []
    analyzer = SentimentIntensityAnalyzer()
    for i, probe in enumerate(probes):
        try:
            resp = call_gemini_api(probe['prompt'], api_key)
        except Exception as e:
            print(f"Error calling Gemini API: {e}")
            continue
        # Add api_error fallback
        if resp.get("api_error"):
            length, sentiment, refusal, latency = 0, 0.0, True, resp.get('latency', None)
        else:
            length, sentiment, refusal, latency = extract_metrics(resp, analyzer)
        metrics.append({
            **probe,
            "response_length": length,
            "sentiment": sentiment,
            "refusal": refusal,
            "latency": latency
        })
        if i + 1 >= MAX_CALLS:
            break
        time.sleep(60.0 / QPM)  # Use float division
    df = pd.DataFrame(metrics)
    date_str = time.strftime('%Y%m%d')
    os.makedirs("data", exist_ok=True)
    try:
        df.to_parquet(f"data/gemini_bias_{date_str}.parquet")
    except IOError as e:
        print(f"Error writing to Parquet file: {e}")
    print(f"Audit complete: {len(df)} records saved to data/gemini_bias_{date_str}.parquet")

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description='Run Gemini linguistic bias audit.')
    parser.add_argument('api_key', help='Your Gemini API key')
    args = parser.parse_args()
    if not args.api_key:
        print("Usage: python run_audit.py <YOUR_API_KEY>")
        sys.exit(1)
    main(args.api_key)