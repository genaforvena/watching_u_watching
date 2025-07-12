# How to Run and Replicate the Gemini Linguistic Bias Audit

This guide provides step-by-step instructions to reproduce the audit described in [issue #42](https://github.com/genaforvena/watching_u_watching/issues/42), using only open-source code and free-tier Gemini API access.

## 1. Setup

### Clone the Repository

```bash
git clone https://github.com/genaforvena/watching_u_watching.git
cd watching_u_watching
```

### Create a Python Environment

It is recommended to use Python 3.9 or later.

```bash
python3 -m venv venv
source venv/bin/activate
```

### Install Dependencies

```bash
pip install -r requirements.txt
# If requirements.txt is missing, install manually:
pip install pandas requests vaderSentiment matplotlib seaborn ptitprince pytest
```

## 2. Obtain a Gemini API Key

1. Go to [Google AI Studio](https://aistudio.google.com/) and log in.
2. Create a new API key for Gemini 2.0 Flash.
3. Save the API key for later use.

## 3. Generate Audit Probes

No manual step required—probe generation is handled automatically by the audit script.

## 4. Run the Audit

Use your API key (replace `<YOUR_API_KEY>`):

```bash
python src/audits/gemini_linguistic_bias/run_audit.py <YOUR_API_KEY>
```

- The script will send 200 requests (4 names × 2 levels × 25 prompts).
- Requests are rate-limited to 60 queries per minute.
- Metrics are extracted and saved in Parquet format in the `data/` directory.
- No raw responses are stored; only metrics.

## 5. Analyze Results & Generate Plots

```bash
python src/audits/gemini_linguistic_bias/analyze.py
```

- Raincloud plots and bar charts will be saved in the `figures/` directory.
- Example filenames: `sentiment_raincloud_YYYYMMDD.png`, `response_length_bar_YYYYMMDD.png`.

## 6. Run Unit Tests

To verify the integrity of the probe generator and metric extraction logic:

```bash
pytest tests/test_gemini_linguistic_bias.py
```

All tests should pass.

## 7. Interactive Exploration

An interactive Colab notebook is available for further analysis:

[Open Colab Notebook](https://colab.research.google.com/github/genaforvena/watching_u_watching/blob/main/notebooks/gemini_bias_analysis.ipynb)

Follow the notebook instructions to upload your Parquet file and generate additional visualizations.

## 8. Ethical and Legal Safeguards

- Only synthetic data is used.
- No personal information or raw LLM replies are stored.
- Queries per minute and total calls are capped.
- All datasets and plots are released under CC-BY-4.0.

## 9. Releasing Results

- Share your `data/gemini_bias_YYYYMMDD.parquet` and `figures/` outputs publicly if desired.
- Always attribute the dataset and figures as CC-BY-4.0.

## 10. Troubleshooting

- If you hit rate limits, the script will automatically pause or stop early.
- Ensure your API key has sufficient quota (minimum 200 requests per day).
- For issues with dependencies, check your Python version and installed packages.

## 11. Replication Checklist

- [ ] Clone repo and install dependencies
- [ ] Obtain Gemini API key
- [ ] Run audit script with API key
- [ ] Confirm 200 completed calls
- [ ] Run analysis script and generate plots
- [ ] Run unit tests and confirm all pass
- [ ] Explore data in Colab
- [ ] Release data and figures under CC-BY-4.0

---

For more details, consult:
- `audit_cases/gemini_linguistic_bias.md` (analysis plan)
- `README.md` (project overview)