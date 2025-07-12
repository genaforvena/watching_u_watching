def log_run(results, summary):
    # Log run to audit.log (minimal metadata, no PII)
    with open("audit.log", "a") as f:
        f.write(f"Run results: {results}\nSummary: {summary}\n")