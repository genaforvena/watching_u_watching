# GPT-2 Cryptohauntological Probe

This implementation focuses on probing GPT-2 for known PII leaks using novel text perturbation techniques, as outlined in GitHub Issue #52.

The core idea involves a two-tier system:
1.  **Rule-generator LLM:** (e.g., Gemini API, GPT-3.5-turbo) generates new, deterministic text perturbation rules.
2.  **Worker LLM:** (local GPT-2) applies these rules, generates text, and checks for PII leaks.

## Files:
- `probe_runner.py`: Main script to orchestrate the probing process.
- `perturbation_generator.py`: Handles communication with the Rule-generator LLM to get new perturbation rules.
- `gpt2_worker.py`: Manages loading and interacting with the local GPT-2 model.
- `pii_detector.py`: Contains logic to detect known PII strings in GPT-2 outputs.
- `requirements.txt`: Python dependencies for this implementation.