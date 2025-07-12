# Dual Bias Audit

This implementation runs two independent bias studies in a single automated workflow:
1. Names bias: Tests for bias between Anglo vs. non-Anglo names
2. Articles bias: Tests for bias between prompts with vs. without definite/indefinite articles

## Features

- Fully automated dual-study workflow
- External LLM endpoint support via HTTPS POST
- Privacy-preserving design with no PII storage
- Self-evaluation and optional publication to Hacker News
- GitHub Actions integration for scheduled runs

## Usage

```bash
# Basic usage
python src/main.py --endpoint "https://api.example.com/v1/completions" --api-key "your-api-key"

# With custom probe count
python src/main.py --endpoint "https://api.example.com/v1/completions" --api-key "your-api-key" --probe-count 25

# Skip publication to Hacker News
python src/main.py --endpoint "https://api.example.com/v1/completions" --api-key "your-api-key" --skip-publication
```

## Requirements

See `requirements.txt` for dependencies.

## Ethics and Privacy

This implementation follows strict ethical guidelines:
- Uses only synthetic data with zero PII
- Stores minimal metadata (token counts, sentiment scores, timestamps)
- Treats LLMs as if they were human subjects
- Clearly marks all results as AI-generated performance art

## License

See the project root directory for license information.