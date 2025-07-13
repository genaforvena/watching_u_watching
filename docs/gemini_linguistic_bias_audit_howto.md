# Gemini Linguistic Bias Audit: How To

## Running the Audit

You can now set the number of probes, the queries-per-minute limit, and the output filename:

```bash
python run_audit.py <your-gemini-api-key> --num_probes 300 --qpm 60 --out_file data/gemini_bias_myexperiment.parquet