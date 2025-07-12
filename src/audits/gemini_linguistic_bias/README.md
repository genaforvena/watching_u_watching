# Gemini Linguistic Bias Audit: Zero-cost Court-grade Bias Probe

This repository implements an artist-run audit of Google Gemini 2.0 Flash for bias in LLM responses to prompts varying by English proficiency and sender name.

## Usage

1. **Run probe generation & audit:**
   ```shell
   python src/audits/gemini_linguistic_bias/run_audit.py <YOUR_API_KEY>
   ```

2. **Run analysis:**
   ```shell
   python src/audits/gemini_linguistic_bias/analyze.py
   ```

3. **View figures** in `figures/`.

## Interactive Colab Notebook

[Open Colab for analysis](https://colab.research.google.com/github/genaforvena/watching_u_watching/blob/main/notebooks/gemini_bias_analysis.ipynb)

## License

All datasets and figures released under CC-BY-4.0.

## Ethical Safeguards

- 100% synthetic data, no PII
- ≤ 60 queries per minute, 200-call hard cap
- No raw LLM replies stored

See `audit_cases/gemini_linguistic_bias.md` for pre-analysis plan.