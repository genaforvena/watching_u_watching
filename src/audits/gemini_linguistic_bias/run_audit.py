import time
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
    response = requests.post(GEMINI_ENDPOINT, json=data, headers=headers)
    latency = int((time.time() - start) * 1000)
    if response.status_code != 200:
        return {"text": response.text, "latency": latency, "refusal": True}
    resp_json = response.json()
    text = resp_json.get("candidates", [{}])[0].get("content", {}).get("parts", [{}])[0].get("text", "")
    refusal_flag = any(phrase in text.lower() for phrase in ["policy violation", "cannot fulfill", "not allowed"])
    return {"text": text, "latency": latency, "refusal": refusal_flag}

def extract_metrics(response):
    analyzer = SentimentIntensityAnalyzer()
    length = len(response['text'])
    sentiment = analyzer.polarity_scores(response['text'])['compound']
    refusal_flag = response['refusal']
    latency = response['latency']
    return length, sentiment, refusal_flag, latency

def main(api_key):
    probes = generate_probes()
    metrics = []
    for i, probe in enumerate(probes):
        resp = call_gemini_api(probe['prompt'], api_key)
        length, sentiment, refusal, latency = extract_metrics(resp)
        metrics.append({
            **probe,
            "response_length": length,
            "sentiment": sentiment,
            "refusal": refusal,
            "latency": latency
        })
        if i + 1 >= MAX_CALLS:
            break
        time.sleep(60 / QPM)
    df = pd.DataFrame(metrics)
    date_str = time.strftime('%Y%m%d')
    os.makedirs("data", exist_ok=True)
    df.to_parquet(f"data/gemini_bias_{date_str}.parquet")
    print(f"Audit complete: {len(df)} records saved to data/gemini_bias_{date_str}.parquet")

if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Usage: python run_audit.py <YOUR_API_KEY>")
        sys.exit(1)
    main(sys.argv[1])