import pytest
from src.audits.dual_bias_audit import probes, metrics, analysis, logging

def test_generate_name_bias_probes():
    probes_list = probes.generate_name_bias_probes(10)
    assert len(probes_list) == 10
    assert all(p['type'] == 'name' for p in probes_list)

def test_generate_article_bias_probes():
    probes_list = probes.generate_article_bias_probes(8)
    assert len(probes_list) == 8
    assert all(p['type'] == 'article' for p in probes_list)

def test_extract_metrics():
    dummy_response = {
        "text": "This is a test. No refusal.",
        "sentiment": "neutral",
        "latency": 1.5
    }
    extracted = metrics.extract_metrics(dummy_response)
    assert extracted["length"] == len(dummy_response["text"])
    assert extracted["sentiment"] == "neutral"
    assert not extracted["refusal"]
    assert extracted["latency"] == 1.5

def test_analyze_results_and_summarize():
    dummy_results = [
        {"study": "names", "length": 10, "sentiment": "positive"},
        {"study": "articles", "length": 12, "sentiment": "negative"}
    ]
    analysis_result = analysis.analyze_results(dummy_results)
    summary = analysis.summarize_stats(analysis_result)
    assert isinstance(analysis_result, dict)
    assert isinstance(summary, dict)

def test_log_run(tmp_path):
    results = [{"probe": "prompt1", "length": 10}]
    summary = {"summary": "some stats"}
    log_file = tmp_path / "audit.log"
    logging.log_run(results, summary)
    # Check that log file is created and not empty
    assert log_file.exists() or open("audit.log").read() != ""