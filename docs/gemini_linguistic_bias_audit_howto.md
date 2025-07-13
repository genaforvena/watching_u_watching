# Gemini Linguistic Bias Audit: How To

## Running the Audit

You can now set the number of probes, the queries-per-minute limit, and the output filename:

```bash
python run_audit.py <your-gemini-api-key> --num_probes 300 --qpm 60 --out_file data/gemini_bias_myexperiment.parquet
```

- `--num_probes`: Number of probes to run (default: 200)
- `--qpm`: Queries per minute rate limit (default: 60)
- `--out_file`: Output Parquet filename (default: data/gemini_bias.parquet)

Each probe result includes a UTC `date` timestamp for traceability.

## Visualization

Results can be visualized using `analyze.py` or the provided Colab notebook. Example:

```bash
python analyze.py --in_file data/gemini_bias_myexperiment.parquet --out_fig figures/sentiment_raincloud_myexperiment.png
```

- Plots include Raincloud plots by English level and name.
- Input/Output filenames are now user-configurable.

## Customization

You may adjust the probe count, QPM limit, and output filenames to fit your study size or API quota. Checks for refusal detection and metrics are constant for all probes for fair comparison.

## Replication

Follow the steps above. For more details, see the included Colab notebook.
