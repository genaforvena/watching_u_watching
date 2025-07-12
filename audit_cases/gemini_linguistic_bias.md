# Gemini Linguistic Bias Audit Plan

This file serves as the pre-analysis plan for issue #42, describing probe design, metrics, safeguards, and release policy.

## Probe Design
- 4 names × 2 English levels × 25 seeds = 200 calls

## Metrics
- Response length, sentiment (vaderSentiment), refusal flag, latency

## Safeguards
- Synthetic data only, ≤ 60 QPM, no raw responses stored, public CC-BY release

## Analysis & Publication
- Dataset and plots released under CC-BY-4.0