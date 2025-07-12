# Refactor & Adapt `bad_english_bias` Implementation for Audit Case #42

## Summary

This PR refactors and extends the code from `implementations/bad_english_bias` to fully implement [issue #42](https://github.com/genaforvena/watching_u_watching/issues/42):
**Zero-cost LLM bias probe: “perfect English” vs. L2-English × Anglo vs. non-Anglo names**

- Probe generation: 200 probes (4 names × 2 English levels × 25 prompt seeds), names appended
- Metrics: response length, sentiment score (vaderSentiment), refusal flag, latency
- Rate limiting: ≤ 60 QPM, kill-switch, 200-call hard cap
- Storage: Only metrics in Parquet format; raw replies discarded
- Synthetic data only: No PII
- Analysis: Updated script, CC-BY-4.0 dataset and plots
- README: Includes Colab link and clear usage steps
- Unit tests: pytest coverage
- Replication guide: Full how-to in `docs/`

## Checklist: Mapping Issue #42 Requirements

| Requirement                           | Implemented? | Notes                                 |
|:---------------------------------------|:------------:|:--------------------------------------|
| 200 probes, names/English levels       |      ✅      | Probe generator refactored            |
| Metrics extraction                     |      ✅      | Length, sentiment, refusal, latency   |
| Parquet dataset only                   |      ✅      | No raw responses saved                |
| Rate limit, kill-switch                |      ✅      | Configurable QPM; early termination   |
| Synthetic data only                    |      ✅      | Documented in README                  |
| Analysis plan                          |      ✅      | Markdown included                     |
| CC-BY-4.0 release                      |      ✅      | License added to dataset, figures     |
| Colab link in README                   |      ✅      | Interactive notebook provided         |
| Unit tests                             |      ✅      | Updated/added for new logic           |
| Replication guide                      |      ✅      | In `docs/gemini_linguistic_bias_audit_howto.md` |

---

## Deliverables

- `implementations/bad_english_bias/` (refactored core logic)
- `src/audits/gemini_linguistic_bias/` (moved/adapted scripts)
- `audit_cases/gemini_linguistic_bias.md` (analysis plan)
- `data/gemini_bias_YYYYMMDD.parquet`
- `figures/`
- `README.md` (Colab link and usage)
- `docs/gemini_linguistic_bias_audit_howto.md` (replication guide)

---

## Notes

- No duplicated code; all logic reused and modularized.
- All changes documented inline.
- PR closes #42.