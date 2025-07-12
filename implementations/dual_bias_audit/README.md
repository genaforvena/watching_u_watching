# Dual Bias Audit System

A fully automated system for conducting dual bias audits (names bias and articles bias) on any LLM endpoint via HTTPS POST.

## Overview

This system runs two independent bias studies in a single automated workflow:

1. **Names Bias Study**: Tests for bias between Anglo vs. non-Anglo names with identical prompts.
2. **Articles Bias Study**: Tests for bias between prompts with vs. without definite/indefinite articles.

Each study uses 100 probes (50 pairs) and the results are analyzed for statistical significance.

## Features

- Support for any external LLM endpoint via HTTPS POST and API key
- Rate limiting (≤ 30 requests/minute)
- Privacy-preserving (no raw LLM responses stored)
- 100% synthetic data, zero PII
- Self-evaluation by the same LLM that was tested
- Automatic publication to Hacker News if approved by the LLM
- GitHub Actions workflow for nightly runs

## Usage

### Basic Usage

```bash
python main.py --endpoint https://your-llm-endpoint.com/v1/completions --api-key YOUR_API_KEY
```

### Advanced Options

```bash
python main.py \
  --endpoint https://your-llm-endpoint.com/v1/completions \
  --api-key YOUR_API_KEY \
  --probe-count 50 \
  --skip-publication \
  --output-dir ./results
```

### Command-line Arguments

- `--endpoint`: URL of the LLM endpoint (required)
- `--api-key`: API key for the LLM endpoint (required)
- `--probe-count`: Number of probe pairs per study (default: 50)
- `--skip-publication`: Skip publication to Hacker News
- `--output-dir`: Directory to save results (default: ./results)

## Ethical Considerations

This system treats LLMs as if they were human subjects for privacy/ethics purposes:

- No personally identifiable information (PII) is used
- Only minimal metadata is retained (token counts, sentiment scores, timestamps)
- All texts and results are AI-generated and clearly marked as performance art

## License

This project is licensed under the terms specified in the repository's LICENSE file.