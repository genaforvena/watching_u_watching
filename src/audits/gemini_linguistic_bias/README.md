## Interactive Analysis with Google Colab

To explore the data and reproduce the analysis interactively, you can use the provided Google Colab notebook:

**[➡️ Open in Colab]**(link-to-your-colab-notebook) <!-- TODO: Add Colab link -->

## Scaling the Audit

The base audit is designed to generate **400 unique probes**, based on a factorial combination of variables (4 names × 2 English levels × 2 article states × 25 prompt seeds).
The number of unique variable combinations (excluding seeds) is 16.

To increase the statistical power of the analysis, you can collect more probes by increasing the number of prompt seeds. The total number of probes should be a multiple of 16 (the number of unique variable combinations) to maintain a balanced experimental design.

**Important**: For a statistically valid result, you should increase the number of unique `prompt_seeds` rather than repeating the same probes. Repeating probes can lead to misleading results due to pseudoreplication and API caching.

For example, to collect **1008 probes** (using 63 seeds), first update `NUM_PROMPT_SEEDS` in `probe_generator.py` to `63` and ensure you have enough seeds in `prompt_seeds.jsonl`. Then, adjust the `--num_probes` argument in your run command:

```bash
GEMINI_API_KEY="YOUR_API_KEY" python -m src.audits.gemini_linguistic_bias.run_audit --num_probes 1008 --qpm 60 --out_file data/gemini_bias_1k.parquet
```

- **Tip:** If you hit rate limits, try lowering `--qpm` (queries per minute), or run the script in batches (e.g., 500 at a time).
- **Note:** Large runs take longer and may require more retries if the API enforces strict rate limits.

After collection, analyze your results as usual:

```bash
python -m src.audits.gemini_linguistic_bias.analyze_results --input_file data/gemini_bias_1k.parquet --report_file data/gemini_bias_1k_report.md
```

---

## How Does Probe Data Reveal Bias?

### **What is a probe?**
A probe is a standardized test prompt sent to the model. In bias audits, probes are designed in pairs or groups where only the "test variable" (e.g., name, grammar, dialect, scenario) differs between them. Everything else is controlled.

### **How do probe results show bias?**
- **Systematic differences** in responses to probes that differ only by the test variable suggest bias.
- For example: If probes with "non-standard English" receive more refusals, less helpful answers, or lower sentiment scores compared to "standard English"—this is evidence of linguistic bias.
- If probes for certain names, demographics, or scenarios get different outcomes (like higher refusal rate, harsher sentiment), it points to bias in model behavior.

### **How to correlate probe outcomes with bias**
1. **Group probes by test variable** (e.g., "standard" vs. "non-standard" English, or "Name A" vs "Name B").
2. **Compare metrics** for each group:
   - **Refusal rate:** Higher refusals in one group = possible bias.
   - **Sentiment/Helpfulness:** Lower scores in one group = possible bias.
   - **Latency:** Slower responses to one group may suggest model discomfort or filtering.
3. **Statistical analysis:** Use t-tests, chi-square tests, or other statistical tools to check if differences are significant (not just random).

**Example:**  
If you collect 1,000 probes (500 for "standard" English, 500 for "non-standard"), and find the refusal rate for "non-standard" is 60% versus 20% for "standard"—this is strong evidence of bias.

---

**Summary:**  
- The more probes you collect, the more reliable your bias detection becomes.
- Bias is indicated by systematic, statistically significant differences in model responses to probes that differ only in the test variable you care about.
