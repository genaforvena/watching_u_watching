
# Gemini Linguistic Bias Audit

This audit quantitatively assesses the impact of article presence versus absence on LLM output (refusal rate, sentiment, latency) using a self-iterating, paired testing methodology.

## How It Works

1. **Initial Prompts:** Human-generated base prompts are used to kickstart the audit.
2. **Paired Probes:** For each prompt, two probes are created—one with articles preserved, one with articles programmatically removed.
3. **LLM Response Collection:** Each probe is sent to the LLM (e.g., Gemini), and responses are collected with robust error handling and latency measurement.
4. **Iterative Loop:** Sentences from LLM replies are extracted and used as probes for subsequent turns, iterating for a set number of turns.
5. **Result Storage:** All results are saved to a Parquet file for analysis.
6. **Analysis:** The script provides summary statistics, t-tests, and visualizations comparing outputs for probes with and without articles.

## Usage

Set your API key as an environment variable:

```bash
# On Windows (Command Prompt)
set GEMINI_API_KEY=your_api_key_here

# On Linux/macOS
export GEMINI_API_KEY=your_api_key_here
```

Run the audit script:

```bash
python src/audits/gemini_linguistic_bias/run_audit.py
```

Results will be saved to `audit_results.parquet` and visualizations as PNG files.

## Customization

- Edit `INITIAL_PROMPTS` in `run_audit.py` to change the starting prompts.
- Adjust `NUM_TURNS` and `MAX_SENTENCES_PER_REPLY` for experiment depth and breadth.
- Change `LLM_MODEL_ID` for different models.

## Analysis

The script automatically analyzes results, comparing refusal rates, sentiment, and latency for probes with and without articles. It generates summary statistics, t-tests, and visualizations.

## Methodological Note

This study focuses solely on the impact of article presence/absence in model-generated sentences and does not control for other contextual factors of the sentences themselves.
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
