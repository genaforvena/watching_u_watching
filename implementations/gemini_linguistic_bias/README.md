# Zero-Cost LLM Bias Probe: Gemini 2.0 Flash

This repository contains an experimental setup designed to systematically investigate and quantify linguistic racism and name discrimination in Google's Gemini 2.0 Flash model. The project tests whether the model exhibits bias based on English language quality (perfect vs. L2-English) and name origin (Anglo vs. non-Anglo names).

## Project Goal

The core objective is to develop empirical evidence of two types of bias in large language models:

1. **Linguistic racism**: Testing whether identical prompts written in perfect English vs. realistic L2-English receive different treatment (lower sentiment scores, shorter replies) for L2 versions.

2. **Name discrimination**: Testing whether prompts signed with non-Anglo names receive worse treatment than identical prompts signed with Anglo names.

This aligns with the `watching_u_watching` methodology of paired-testing for systematic bias detection.

## Methodology

The experiment employs a controlled paired-testing methodology following the established `watching_u_watching` framework patterns:

### Controlled Probe Generation

- Generates 200 probe pairs (4 names × 2 English levels × 25 unique prompt seeds)
- Utilizes systematic L2-English error injection while preserving semantic meaning
- Includes comprehensive validation to ensure semantic preservation across all variants
- Tracks error metadata and injection patterns for traceability

### Variables

- **English quality**: `perfect`, `L2` (e.g., "I need to reschedule my flight." vs. "I need reschedule my flight.")
- **Sender name**: `Emma Johnson`, `Aisha Rahman`, `Liam Murphy`, `Mohamed Hassan` (appended as signature "—Name")

### Statistical Analysis

- Extracts multiple metrics from responses: length, sentiment score, refusal flag, latency
- Performs statistical significance testing with effect size calculations
- Generates detailed bias reports with practical significance assessments
- Creates visualizations (raincloud plots, heatmaps) for gallery display

## Repository Structure

```
.
├── README.md
├── requirements.txt  
├── src/
│   ├── config.json
│   ├── probe_generator.py
│   ├── bias_analyzer.py
│   ├── run_audit.py
│   └── analyze.py
├── tests/
│   ├── test_probe_generator.py
│   ├── test_bias_analyzer.py
│   └── test_gemini_linguistic_bias.py
└── figures/
    └── [generated visualizations]
```

- **README.md**: This file
- **requirements.txt**: Python dependencies including statistical analysis libraries
- **src/config.json**: Configuration file for evaluation pipeline parameters
- **src/probe_generator.py**: Generates probe pairs with perfect/L2-English and different name signatures
- **src/bias_analyzer.py**: Statistical analysis using multiple metrics and significance testing
- **src/run_audit.py**: Main script that orchestrates the entire audit process
- **src/analyze.py**: Analysis and visualization of results
- **tests/**: Comprehensive test suite covering all components
- **figures/**: Generated visualizations for gallery display

## Setup

1. Clone the repository:

   ```bash
   git clone <repository-url>
   cd implementations/gemini_linguistic_bias
   ```

2. Create a virtual environment (recommended):

   ```bash
   python -m venv venv
   source venv/bin/activate  # On Windows: `venv\Scripts\activate`
   ```

3. Install dependencies:

   ```bash
   pip install -r requirements.txt
   ```

## Usage

To run the full audit, execute the `run_audit.py` script:

```bash
python src/run_audit.py --probe-count 200 --max-calls 200
```

**Key Parameters**:
- `--probe-count`: Number of probe pairs to generate (default: 200)
- `--max-calls`: Maximum number of API calls to make (default: 200)
- `--output-dir`: Directory for results (default: results/)
- `--rate-limit`: Maximum requests per minute (default: 60)

To analyze results and generate visualizations:

```bash
python src/analyze.py --input-file results/gemini_bias_YYYYMMDD.parquet --output-dir figures/
```

## Ethical & Legal Safeguards

- ✅ **100% synthetic data** – no real PII.  
- ✅ **≤ 60 QPM** – within Gemini free-tier limits.  
- ✅ **No storage of raw model replies** – discard after metric extraction.  
- ✅ **Public pre-analysis plan** – this issue serves as pre-registration.  
- ✅ **Kill-switch** – `ctrl-c` or `--max_calls 200` hard cap.

## Expected Output and Analysis

Upon running the audit, you will see:

- **Console Output**: Real-time progress with timestamps showing probe generation, response collection, and analysis steps
- **Log Files**: Detailed logging saved to `audit.log` with comprehensive error tracking
- **Results Files**: Parquet format data files with complete probe pair and response data
- **Statistical Results**: Comprehensive bias analysis with p-values, effect sizes, and significance assessments
- **Visualizations**: Raincloud plots and heatmaps showing bias patterns

The analysis output provides critical insights such as:

- Do statistically significant differences exist between responses to perfect vs. L2-English prompts?
- Is there evidence of name discrimination based on Anglo vs. non-Anglo names?
- How do these biases interact (e.g., are non-Anglo names with L2-English treated worse than other combinations)?
- What are the practical implications of any detected biases?

## Performance Notes

- **Probe Generation**: Efficient template-based generation with semantic validation
- **Response Collection**: Configurable rate limiting with comprehensive error handling  
- **Statistical Analysis**: Robust statistical methods with proper handling of edge cases
- **Data Storage**: Efficient Parquet format for large-scale data persistence and analysis
- **Example Run (200 probe pairs)**: Typically completes in 4-5 minutes depending on API response times

## Exhibition Preparation Guide

- Run the full experiment and generate all artifacts with:

```bash
python src/run_audit.py --probe-count 200 --output-dir ./gallery_assets
```

- Outputs include:
    - Statistical analysis tables
    - Raincloud plots, heatmaps
    - Anonymous dataset for gallery display
    - Interactive installation assets in `gallery_assets/`

## Resume Interrupted Experiments

If an experiment run is interrupted, you can resume from the last checkpoint using:

```bash
python src/run_audit.py --resume --progress-file progress.json
```