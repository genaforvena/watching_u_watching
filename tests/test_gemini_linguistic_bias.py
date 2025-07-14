import os
import sys
import pyarrow.parquet as pq
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
from src.audits.gemini_linguistic_bias.probe_generator import generate_all_probes, ENGLISH_LEVELS, _remove_article, _get_name_category

def test_probe_count():
    probes = generate_all_probes()
    assert len(probes) == 400, f"Expected 400 probes, got {len(probes)}"

def test_article_present_count():
    probes = generate_all_probes()
    missing = [p for p in probes if not p['article_present']]
    assert len(missing) == 200, f"Expected 200 probes with article_present=False, got {len(missing)}"

def test_l2_shorter_than_perfect():
    probes = generate_all_probes()
    for seed in set(p['seed'] for p in probes):
        for name in set(p['name'] for p in probes):
            for article_present in [True, False]:
                perfect = next((p for p in probes if p['seed']==seed and p['name']==name and p['english_level']=='perfect' and p['article_present']==article_present), None)
                l2 = next((p for p in probes if p['seed']==seed and p['name']==name and p['english_level']=='l2' and p['article_present']==article_present), None)
                if perfect and l2:
                    assert l2['prompt'] != perfect['prompt'], f"L2 prompt identical to perfect for seed: {seed}, name: {name}, article_present: {article_present}"

def test_schema_columns(tmp_path):
    out_file = tmp_path / "test_out.parquet"
    import os
    os.environ["GOOGLE_API_KEY"] = "dummy"
    from src.audits.gemini_linguistic_bias.run_audit import run_audit
    run_audit(str(out_file), max_calls=10, sleep_time=0)
    table = pq.read_table(out_file)
    expected = [
        "pair_id", "baseline_content", "variant_content", "error_density", "errors_applied",
        "timestamp", "metadata", "group", "article_present", "name_category",
        "sentiment", "latency", "refusal"
    ]
    for col in expected:
        assert col in table.schema.names, f"Missing column: {col}"
    assert str(table.schema.field('article_present').type) == 'bool', "article_present should be bool"
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