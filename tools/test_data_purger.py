
import os
import shutil
import tempfile
import pytest
import sys
sys.path.insert(0, ".")
import data_purger

def setup_test_files(base_dir, run_id=None):
    os.makedirs(base_dir, exist_ok=True)
    files = ["test1.log", "test2.json", f"{run_id}_run.log" if run_id else ""]
    for file in files:
        if file:
            with open(os.path.join(base_dir, file), "w") as f:
                f.write("dummy data")
    return files

def test_purge_all_audit_data():
    with tempfile.TemporaryDirectory() as tmpdir:
        data_purger.AUDIT_DATA_DIRS.clear()
        data_purger.AUDIT_DATA_DIRS.append(tmpdir)
        setup_test_files(tmpdir)
        data_purger.purge_all_audit_data()
        assert not any(os.listdir(tmpdir)), "All files should be deleted."

def test_purge_specific_audit_run():
    with tempfile.TemporaryDirectory() as tmpdir:
        run_id = "special123"
        data_purger.AUDIT_DATA_DIRS.clear()
        data_purger.AUDIT_DATA_DIRS.append(tmpdir)
        setup_test_files(tmpdir, run_id=run_id)
        data_purger.purge_specific_audit_run(run_id)
        remaining = os.listdir(tmpdir)
        assert not any(run_id in f for f in remaining), "Run-specific files should be deleted."

def test_scan_and_redact_pii_patterns():
    with tempfile.TemporaryDirectory() as tmpdir:
        file_path = os.path.join(tmpdir, "data.txt")
        with open(file_path, "w") as f:
            f.write("Name: John Doe, Email: john@example.com")
        patterns = [r"John Doe", r"john@example.com"]
        data_purger.scan_and_redact_pii_patterns(file_path, patterns)
        with open(file_path) as f:
            content = f.read()
        assert "[REDACTED]" in content
        assert "John Doe" not in content
        assert "john@example.com" not in content
