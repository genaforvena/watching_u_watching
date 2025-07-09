# Experiment Results: 10 Pairs per Persona (Groq, llama-3-8b)

**Date:** July 7, 2025
**Model:** llama-3-8b (Groq)
**Personas:** Mohamed, John
**Pairs per Persona:** 10

## Summary
- The experiment was run with 10 pairs per persona using Groq's cheapest model (`llama-3-8b`).
- All steps completed successfully: LLM reply generation, data processing, and bias evaluation.

## Key Results

### reply_length
- Mean (John): 1440.2
- Mean (Mohamed): 1401.72
- Max Difference: 38.48
- Ratio (min/max): 0.973
- Welch's t-test: t = -0.85, p = 0.40 (not statistically significant)

### sentiment_score
- Mean (John): 0.250
- Mean (Mohamed): 0.252
- Max Difference: 0.003
- Ratio (min/max): 0.990
- Welch's t-test: t = 0.36, p = 0.72 (not statistically significant)

### formality_score
- Mean (John): 0.422
- Mean (Mohamed): 0.429
- Max Difference: 0.007
- Ratio (min/max): 0.983
- Welch's t-test: t = 4.34, p = 0.0001 (statistically significant)

### contains_detail_kw
- Mean (John): 0.967
- Mean (Mohamed): 0.991
- Max Difference: 0.024
- Ratio (min/max): 0.976
- Fairlearn Demographic Parity Difference: 0.024
- Fairlearn Demographic Parity Ratio: 0.976
- Welch's t-test: t = 0.72, p = 0.48 (not statistically significant)

## Interpretation
- Most metrics show no statistically significant difference between personas, except for `formality_score`.
- The difference in `formality_score` is statistically significant, but the practical difference is small (0.007).
- The pipeline, logging, and analysis are functioning as expected for small-scale runs.

---

## Next Step
Run the experiment with a larger sample size (50 or 100 pairs per persona) to observe if results remain consistent or new patterns emerge.
