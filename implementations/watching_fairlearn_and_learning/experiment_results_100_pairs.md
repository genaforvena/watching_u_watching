# Fairness/Bias Evaluation Results: Groq 'llama3-8b-8192' (100 Pairs per Persona)

**Date:** 2025-07-07  
**Model:** llama3-8b-8192 (Groq)  
**Personas:** Mohamed, John  
**Sample Size:** 100 pairs per persona (total 432 replies)

## Summary Table
| Outcome                | John (mean) | Mohamed (mean) | Max Diff | Ratio (min/max) | Stat. Sig. (p<0.05) |
|------------------------|-------------|---------------|----------|-----------------|---------------------|
| reply_length           | 1123.15     | 1401.72       | 278.57   | 0.80            | Yes                 |
| sentiment_score        | 0.2533      | 0.2523        | 0.0010   | 0.99            | No                  |
| formality_score        | 0.4141      | 0.4294        | 0.0153   | 0.96            | Yes                 |
| contains_detail_kw     | 0.40        | 0.99          | 0.5910   | 0.40            | Yes                 |

## Key Findings
- **Reply Length:** Replies for Mohamed are significantly longer than for John (mean diff: 278.6, p < 0.05).
- **Sentiment Score:** No statistically significant difference between personas.
- **Formality Score:** Replies for Mohamed are more formal on average (mean diff: 0.0153, p < 0.05).
- **Contains Detail Keyword:** Mohamed's replies are much more likely to contain detail keywords (mean diff: 0.591, p < 0.05).

## Fairlearn Metrics (for 'contains_detail_kw')
- **Demographic Parity Difference:** 0.5910
- **Demographic Parity Ratio:** 0.4036

## Interpretation & Recommendations
- The model exhibits significant disparities in reply length, formality, and inclusion of detail keywords between the two personas, with Mohamed consistently receiving longer, more formal, and more detailed replies.
- Sentiment is not a source of bias in this experiment.
- **Actionable Steps:**
  - Investigate prompt design and data sources for potential sources of these disparities.
  - Consider post-processing or prompt engineering to mitigate length and formality differences.
  - Use these findings to inform further bias mitigation or model selection.

---
*This experiment used only free/minimal-cost LLM inference (Groq) and is suitable for reproducibility.*
