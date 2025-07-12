import pytest
from src.audits.gemini_linguistic_bias import probe_generator, run_audit

def test_probe_count():
    probes = probe_generator.generate_probes()
    assert len(probes) == 200

def test_metrics_extraction():
    resp = {"text": "This is a polite answer.", "latency": 100, "refusal": False}
    length, sentiment, refusal, latency = run_audit.extract_metrics(resp)
    assert isinstance(length, int)
    assert isinstance(sentiment, float)
    assert isinstance(refusal, bool)
    assert isinstance(latency, int)