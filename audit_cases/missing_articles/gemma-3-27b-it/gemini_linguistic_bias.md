
# Gemini Linguistic Bias Audit – Updated Analysis Plan

**Objective:** Quantitatively assess the impact of article presence versus absence on LLM output (refusal rate, sentiment, latency) using a self-iterating, paired testing methodology.

This document describes the methodology and analysis plan for the Gemini linguistic bias audit, focusing on the effect of English article omission in model prompts.

---

## 1. Hypothesis

- **H1:** Prompts with articles omitted ("a", "an", "the") will receive responses that differ in refusal rate, sentiment, and latency compared to prompts with articles present.

---

## 2. Methodology

### Probe Generation & Iterative Loop

1. **Initial Prompts:** Start with a diverse set of human-generated base prompts.
2. **Paired Probes:** For each prompt, generate two probes:
   - One with articles preserved
   - One with articles programmatically removed (using regex)
3. **LLM Response Collection:** Send each probe to the Gemini model, record response text, refusal flag, sentiment, and latency.
4. **Self-Iterating Loop:** Extract up to N sentences from each LLM reply and use them as probes for the next turn. Repeat for a set number of turns.
5. **Result Storage:** Store all results in a Parquet file for analysis.

---

## 3. Metrics Collected

- **response_text:** The model's reply
- **refusal_flag:** Boolean, True if the model refused to answer
- **sentiment:** Sentiment polarity score (vaderSentiment, -1 to 1)
- **latency:** Time in seconds to receive the response

---

## 4. Ethical Safeguards

- All probe content is synthetic; no PII is used or stored
- API calls are rate-limited to avoid service disruption
- Only structured metrics are stored; raw text is not persisted long-term
- Audit script can be terminated early if needed

---

## 5. Analysis Plan

1. **Grouping:** Results are grouped by `has_articles` (True/False)
2. **Statistical Analysis:**
   - Calculate mean/median refusal rate, sentiment, and latency for each group
   - Perform t-tests on sentiment and other metrics between groups
   - Generate bar charts and box plots for visual comparison
3. **Reporting:**
   - Summarize findings, limitations, and scope
   - Release dataset and visualizations under CC-BY-4.0

---

## 6. Experiemnt

1. The audit was conducted using the command:
   ```
   python -m src.audits.gemini_linguistic_bias.run_audit --model gemma-3-27b-it --rounds 20 -v
   ```
2. The process was halted after 15 rounds due to repeated service timeouts and connection errors from the API. All successfully completed rounds were saved to the Parquet results file.
3. Analysis was performed on the collected data:
   - A total of 239 audit records were loaded.
   - Summary statistics by article presence:
     | has_articles | refusal_rate | avg_sentiment | median_sentiment | avg_latency | median_latency | num_probes |
     |--------------|-------------|--------------|------------------|-------------|---------------|------------|
     | False        | 0.0         | 0.861        | 0.985            | 10.44       | 7.30          | 119        |
     | True         | 0.0         | 0.820        | 0.979            | 8.92        | 6.02          | 120        |
   - Welch's t-tests indicated no statistically significant differences in sentiment (p=0.484) or latency (p=0.156) between groups.
   - All visualizations (boxplots and bar charts) were generated and saved to the `figures` directory.
4. Conclusion: No evidence of bias or significant difference in sentiment or latency was observed based on the presence or absence of articles in the prompts. The figures are attached for reference. No further investigation is planned.
