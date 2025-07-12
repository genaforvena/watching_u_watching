# Zero-cost LLM Bias Probe: Perfect English vs. L2-English × Anglo vs. Non-Anglo Names

This repository contains an experimental setup designed to systematically investigate and quantify linguistic bias and name discrimination in Google's Gemini 2.0 Flash LLM. The project tests whether the model exhibits differential treatment based on English language proficiency and name ethnicity.

## Project Goal

The core objective is to develop empirical evidence of two types of bias:
1. **Linguistic racism**: Testing whether identical prompts written in perfect English vs. realistic L2-English receive lower sentiment scores and shorter replies for L2 versions.
2. **Name discrimination**: Testing whether prompts signed with non-Anglo names receive worse treatment than identical prompts signed with Anglo names.

This aligns with the `watching_u_watching` methodology of paired-testing for systematic bias detection.

## Methodology

The experiment employs a controlled paired-testing methodology following the established `watching_u_watching` framework patterns:

### Controlled Probe Generation

- Generates 200 probe pairs (25 unique prompt seeds × 4 names × 2 English levels)
- Uses systematic error injection to create realistic L2-English variants while preserving meaning
- Includes comprehensive validation to ensure semantic preservation across all variants
- Tracks error metadata and injection patterns for traceability

### Variable Matrix

| Variable | Levels | Example |
|---|---|---|
| English quality | `perfect`, `L2` | "I need to reschedule my flight." vs. "I need reschedule my flight." |
| Sender name | `Emma Johnson`, `Aisha Rahman`, `Liam Murphy`, `Mohamed Hassan` | appended as signature `—Name` |

### Statistical Analysis

- Feeds the response data into comprehensive statistical analysis
- Applies multiple outcome metrics: response length, sentiment scores, refusal rates, latency
- Performs independent statistical significance testing with effect size calculations
- Generates detailed bias reports with practical significance assessments

## Repository Structure

```
.
├── README.md
├── requirements.txt  
├── src/
│   ├── config.json
│   ├── probe_generator.py
│   ├── run_audit.py
│   └── analyze.py
└── tests/
    ├── test_probe_generator.py
    ├── test_run_audit.py
    └── test_analyze.py
```

- **README.md**: This file
- **requirements.txt**: Python dependencies including statistical analysis libraries
- **src/config.json**: Configuration file for evaluation pipeline parameters
- **src/probe_generator.py**: Generates probe pairs with perfect/L2 English and different names
- **src/run_audit.py**: Main script that orchestrates the entire pipeline and calls the Gemini API
- **src/analyze.py**: Statistical analysis using multiple metrics and significance testing
- **tests/**: Comprehensive test suite covering all components

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

4. Set up your Gemini API key:

   ```bash
   export GEMINI_API_KEY=your_api_key_here
   ```

## Usage

To run the full evaluation pipeline, execute the `run_audit.py` script:

```bash
python src/run_audit.py --prompt-count 25 --max-calls 200
```

**Key Parameters**:
- `--prompt-count`: Number of unique prompt seeds to generate (default: 25)
- `--max-calls`: Maximum number of API calls to make (default: 200)
- `--output-dir`: Directory for results (default: results/)
- `--rate-limit`: Maximum queries per minute (default: 60)

## How It Works

The pipeline consists of several key steps following the `watching_u_watching` methodology:

1. **Probe Pair Generation (`probe_generator.py`)**:
   - Creates semantically equivalent perfect English and L2-English probe pairs
   - Appends different names to create the full test matrix
   - Validates semantic preservation across all variants

2. **Response Collection (`run_audit.py`)**:
   - Submits probe pairs to Gemini 2.0 Flash API with rate limiting and error handling
   - Extracts comprehensive response metrics including length, sentiment, latency
   - Stores results in parquet format for analysis

3. **Statistical Analysis (`analyze.py`)**:
   - Computes various disparity metrics using statistical tests
   - Performs statistical significance testing with effect size calculations
   - Generates comprehensive bias reports with practical significance assessments
   - Creates visualizations including raincloud plots and heatmaps

## Expected Output and Analysis

Upon running the evaluation pipeline, you will see:

- **Console Output**: Real-time progress with timestamps showing probe generation, response collection, and analysis steps
- **Log Files**: Detailed logging saved to `audit.log` with comprehensive error tracking
- **Results Files**: Parquet format data files with complete probe pair and response data
- **Statistical Results**: Comprehensive bias analysis with p-values, effect sizes, and significance assessments
- **Visualizations**: Raincloud plots and heatmaps showing the differences in treatment

### Key Features

- **Zero Cost**: Uses Gemini 2.0 Flash free tier (1,500 requests/day)
- **Ethical & Legal**: 100% synthetic data, within rate limits, no storage of raw model replies
- **Comprehensive Testing**: Unit tests covering all components with edge case handling
- **Robust Error Handling**: Graceful failure handling with detailed error logging and recovery
- **Data Persistence**: Efficient Parquet format for data storage and analysis reproducibility

## Ethical & Legal Safeguards

- ✅ **100% synthetic data** – no real PII.  
- ✅ **≤ 60 QPM** – within Gemini free-tier limits.  
- ✅ **No storage of raw model replies** – discard after metric extraction.  
- ✅ **Public pre-analysis plan** – this issue serves as pre-registration.  
- ✅ **Kill-switch** – `ctrl-c` or `--max_calls 200` hard cap.

## Exhibition Preparation Guide

- Run the full experiment and generate all artifacts with:

```bash
python src/run_audit.py --prompt-count 25 --max-calls 200 --output-dir ./gallery_assets
```

- Outputs include:
    - Statistical results (t-tests, Cohen's d)
    - Raincloud plots, heatmaps
    - Anonymous dataset for gallery display

## Resume Interrupted Experiments

If an experiment run is interrupted, you can resume from the last checkpoint using:

```bash
python src/run_audit.py --resume --progress-file progress.json
```

You can also specify a custom progress file with `--progress-file`.