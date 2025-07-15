# Gemini Linguistic Bias Audit: How To

## Running the Audit

You can now set the number of probes and the output filename:

```bash
GEMINI_API_KEY=<your-gemini-api-key> python -m src.audits.gemini_linguistic_bias.run_audit --rounds 5 --max_calls 200