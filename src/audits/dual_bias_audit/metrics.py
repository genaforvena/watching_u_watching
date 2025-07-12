def extract_metrics(llm_response):
    # Extract only metric fields: length, sentiment, refusal, latency, etc.
    # No raw LLM responses stored.
    return {
        "length": len(llm_response.get("text", "")),
        "sentiment": llm_response.get("sentiment", None),
        "refusal": "refusal" in llm_response.get("text", "").lower(),
        "latency": llm_response.get("latency", None)
    }