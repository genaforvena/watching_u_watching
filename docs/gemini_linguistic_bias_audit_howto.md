# Gemini Linguistic Bias Audit: How To

## Running the Audit

You can now set the number of probes and the queries-per-minute limit:

```bash
python run_audit.py <your-gemini-api-key> --num_probes 300 --qpm 60
```

- `--num_probes`: Number of probes to run (default: 200)
- `--qpm`: Queries per minute rate limit (default: 60)

Each probe result includes a UTC `date` timestamp for traceability.

## Visualization

Results can be visualized using `analyze.py` or the provided Colab notebook. Plots include:
- Raincloud plots by English level and name
- Optionally, summary of probe results by date

## Customization

You may adjust the probe count and QPM limit to fit your study size or API quota. Checks for refusal detection and metrics are constant for all probes for fair comparison.

## Replication

Follow the steps above. For more details, see the included Colab notebook.
