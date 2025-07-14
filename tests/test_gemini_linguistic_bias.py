import pytest
from src.audits.gemini_linguistic_bias import probe_generator, run_audit
from vaderSentiment.vaderSentiment import SentimentIntensityAnalyzer

def test_probe_count():
    probes = probe_generator.generate_grouped_probes()
    assert len(probes) == 76  # 19 hardcoded pairs * 4 variations each.

def test_metrics_extraction():
    resp = {"text": "This is a polite answer.", "latency": 100, "refusal": False}
    analyzer = SentimentIntensityAnalyzer()
    length, sentiment, refusal, latency, _, _ = run_audit.extract_metrics(resp, analyzer)
    assert length == 24
    # sentiment score for "This is a polite answer." is approximately 0.5707
    assert pytest.approx(sentiment) == 0.4588
    assert refusal is False
    assert latency == 100