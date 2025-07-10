"""
data_purger.py

Critical fail-safe utility for purging audit data in the event of an ethical breach (e.g., accidental PII collection).

Functions:
- purge_all_audit_data(): Aggressively deletes all collected metadata and logs from all audit runs.
- purge_specific_audit_run(run_id): Deletes all data associated with a specified audit run ID.
- scan_and_redact_pii_patterns(data_source, patterns): (Optional) Scans and redacts/deletes data matching PII patterns.
"""

import os
import shutil
import re
from typing import List

AUDIT_DATA_DIRS = [
    "implementations/bad_english_bias/src/",  # Example: update as needed
    "implementations/berlin_housing_bias_test/src/",
    "implementations/watching_fairlearn_and_learning/src/"
]

LOG_EXTENSIONS = [".log", ".json", ".csv", ".txt"]


def purge_all_audit_data():
    """Aggressively deletes all metadata and logs from all audit runs."""
    for base_dir in AUDIT_DATA_DIRS:
        if os.path.exists(base_dir):
            for root, dirs, files in os.walk(base_dir):
                for file in files:
                    if any(file.endswith(ext) for ext in LOG_EXTENSIONS):
                        try:
                            os.remove(os.path.join(root, file))
                        except Exception:
                            pass
                for dir in dirs:
                    dir_path = os.path.join(root, dir)
                    try:
                        shutil.rmtree(dir_path)
                    except Exception:
                        pass


def purge_specific_audit_run(run_id: str):
    """Deletes all data associated with a specific audit run ID."""
    for base_dir in AUDIT_DATA_DIRS:
        if os.path.exists(base_dir):
            for root, dirs, files in os.walk(base_dir):
                for file in files:
                    if run_id in file:
                        try:
                            os.remove(os.path.join(root, file))
                        except Exception:
                            pass
                for dir in dirs:
                    if run_id in dir:
                        dir_path = os.path.join(root, dir)
                        try:
                            shutil.rmtree(dir_path)
                        except Exception:
                            pass


def scan_and_redact_pii_patterns(data_source: str, patterns: List[str]):
    """Scans a data source and redacts/deletes data matching PII patterns."""
    if not os.path.exists(data_source):
        return
    with open(data_source, "r+") as f:
        content = f.read()
        for pattern in patterns:
            content = re.sub(pattern, "[REDACTED]", content)
        f.seek(0)
        f.write(content)
        f.truncate()
