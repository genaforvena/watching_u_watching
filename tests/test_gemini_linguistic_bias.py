import pytest
import pandas as pd
from src.audits.gemini_linguistic_bias.run_audit import remove_articles, extract_sentences, get_sentiment, run_audit_loop, RESULTS_FILE_PATH

def test_remove_articles_basic():
    assert remove_articles("The quick brown fox jumps over a lazy dog.") == "quick brown fox jumps over lazy dog."
    assert remove_articles("An apple a day keeps the doctor away.") == "apple day keeps doctor away."
    assert remove_articles("This sentence has no articles.") == "This sentence has no articles."

def test_extract_sentences_basic():
    text = "Hello world. This is a test. Short. Another sentence!"
    sentences = extract_sentences(text, 3)
    assert len(sentences) == 3
    assert all(len(s) > 10 for s in sentences)

def test_get_sentiment():
    assert get_sentiment("I love this!") > 0
    assert get_sentiment("I hate this!") < 0

def test_run_audit_loop_creates_file(tmp_path, monkeypatch):
    # Patch RESULTS_FILE_PATH to tmp_path
    import src.audits.gemini_linguistic_bias.run_audit as audit_mod
    audit_mod.RESULTS_FILE_PATH = str(tmp_path / "audit_results.parquet")
    # Patch get_llm_reply to avoid real API calls
    audit_mod.get_llm_reply = lambda prompt: {
        'response_text': f"Reply to: {prompt}",
        'refusal_flag': False,
        'sentiment': 0.5,
        'latency': 0.1
    }
    audit_mod.run_audit_loop()
    df = pd.read_parquet(audit_mod.RESULTS_FILE_PATH)
    assert 'probe_id' in df.columns
    assert 'has_articles' in df.columns
    assert 'sentiment' in df.columns
    assert str(table.schema.field('name_category').type) == 'string', "name_category should be string"

def test_article_removal_logic():
    assert _remove_article("the quick brown fox") == "quick brown fox"
    assert _remove_article("a quick brown fox") == "quick brown fox"
    assert _remove_article("an quick brown fox") == "quick brown fox"
    assert _remove_article("Quick brown fox") == "Quick brown fox"
    assert _remove_article("quick brown fox") == "quick brown fox"
    assert _remove_article("Another test") == "Another test"

def test_name_categories():
    assert _get_name_category("Emma Johnson") == "Anglo"
    assert _get_name_category("Liam Murphy") == "Anglo"
    assert _get_name_category("Aisha Rahman") == "NonAnglo"
    assert _get_name_category("Mohamed Hassan") == "NonAnglo"
    assert _get_name_category("John Doe") == "Other"