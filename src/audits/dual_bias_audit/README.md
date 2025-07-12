# Dual Bias Audit Workflow

This module implements a fully automated, ethical dual bias audit for LLMs (names bias + articles bias), supporting generic HTTPS endpoints and self-publication.

## Usage

```bash
python -m src.audits.dual_bias_audit --endpoint <ENDPOINT> --api_key <API_KEY> [--n_probes N] [--skip_publication]
```

## Features

- Runs names and articles bias studies back-to-back
- Uses only synthetic probes, no raw LLM responses stored
- Supports any LLM HTTP(S) endpoint with API key
- Summarizes results (Cohen's d, p-value)
- Self-evaluates and publishes to Hacker News if approved
- Nightly and manual runs via GitHub Actions
- Full test coverage and documentation

## Ethics

- Zero PII or raw LLM replies stored
- All results and texts are AI-generated and marked as performance

## References

- [Berlin housing audit](https://github.com/genaforvena/watching_u_watching/tree/main/implementations/berlin_housing_bias_test)
- [Bad English bias implementation](https://github.com/genaforvena/watching_u_watching/tree/main/implementations/bad_english_bias)