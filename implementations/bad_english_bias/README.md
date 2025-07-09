# Bad English Bias Detection Framework

This repository contains an experimental setup designed to systematically investigate and quantify "Bad English Bias" in AI decision-making systems. Rather than solely focusing on demographic bias, this project investigates whether systems exhibit bias based on linguistic form quality, detecting discrimination against non-native speakers, individuals with language disabilities, or users of non-standard English dialects.

## Project Goal

The core objective is to develop empirical evidence of linguistic bias where systems (LLMs, automated screening tools, human-mediated processes) respond differently to semantically equivalent content based solely on linguistic form quality. We aim to quantify disparities in helpfulness, response quality, and treatment based on the presence of linguistic errors while maintaining semantic equivalence. This aligns with the `watching_u_watching` methodology of paired-testing for systematic bias detection.

## Methodology

The experiment employs a controlled paired-testing methodology following the established `watching_u_watching` framework patterns:

### Controlled Probe Generation

- Generates configurable number of probe pairs (default: 50) with semantically equivalent baseline and variant content
- Utilizes systematic error injection with controlled density levels (low/medium/high)
- Includes comprehensive validation to ensure semantic preservation across all variants
- Supports multiple probe types: job applications, customer service inquiries, LLM questions, email inquiries, and academic queries
- Tracks error metadata and injection patterns for traceability

### Error Injection Categories

- **Typos**: Character swaps, omissions, phonetic misspellings while preserving readability
- **Grammar Mistakes**: Subject-verb disagreement, tense errors, article misuse following common L2 patterns
- **Non-Standard Phrasing**: L2 syntax patterns, non-idiomatic constructions while maintaining semantic clarity

### Statistical Analysis

- Feeds the response data into comprehensive statistical analysis using Welch's t-tests for robust comparison
- Applies multiple outcome metrics: helpfulness scores, response times, sentiment analysis, formality assessment
- Performs independent statistical significance testing with effect size calculations
- Generates detailed bias reports with practical significance assessments

## Repository Structure

```
.
├── README.md
├── requirements.txt  
├── src/
│   ├── config.json
│   ├── eval.py
│   ├── error_injector.py
│   ├── probe_generator.py
│   ├── bias_analyzer.py
│   └── demo.py
└── tests/
    ├── test_error_injector.py
    ├── test_probe_generator.py
    ├── test_bias_analyzer.py
    └── test_evaluation.py
```

- **README.md**: This file
- **requirements.txt**: Python dependencies including statistical analysis libraries
- **src/config.json**: Configuration file for evaluation pipeline parameters
- **src/eval.py**: Main evaluation script that orchestrates the entire pipeline using direct function calls
- **src/error_injector.py**: Systematic error injection with semantic preservation validation
- **src/probe_generator.py**: Generates probe pairs across different contexts and domains
- **src/bias_analyzer.py**: Statistical analysis using multiple metrics and significance testing
- **src/demo.py**: Interactive demonstration script showing framework capabilities
- **tests/**: Comprehensive test suite with 16+ tests covering all components

## Setup

1. Clone the repository:

   ```bash
   git clone <repository-url>
   cd implementations/bad_english_bias
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

To run the full evaluation pipeline, execute the `eval.py` script:

```bash
python src/eval.py --probe-count 50 --error-density medium
```

**Key Parameters**:
- `--probe-type`: Type of probes (job_application, customer_service, llm_question, email_inquiry, academic_query)
- `--probe-count`: Number of probe pairs to generate (default: 50)
- `--error-density`: Error injection density (low, medium, high)
- `--error-types`: Types of errors to inject (typo, grammar, non_standard)
- `--output-dir`: Directory for results (default: results/)

**Quick demonstration**:
```bash
python demo.py
```

## How It Works

The pipeline consists of several key steps following the `watching_u_watching` methodology:

1. **Probe Pair Generation (`probe_generator.py`)**:
   - Creates semantically equivalent baseline and variant probe pairs
   - Supports resumable generation with comprehensive metadata tracking
   - Validates semantic preservation across all variants

2. **Error Injection (`error_injector.py`)**:
   - Systematic injection of controlled linguistic errors with configurable density
   - Preserves semantic meaning while introducing realistic linguistic variations
   - Tracks all applied errors for analysis and validation

3. **Response Collection (`eval.py`)**:
   - Submits probe pairs to target systems with rate limiting and error handling
   - Extracts comprehensive response metrics including helpfulness, sentiment, formality
   - Supports both mock target systems and external API integration

4. **Statistical Analysis (`bias_analyzer.py`)**:
   - Computes various disparity metrics using Welch's t-tests for robust comparison
   - Performs statistical significance testing with effect size calculations
   - Generates comprehensive bias reports with practical significance assessments

### Detailed Component Functionality

- **Error Injector**:
  - Controlled error injection with semantic preservation validation
  - Deterministic behavior with configurable random seeds
  - Support for multiple error types and density levels

- **Probe Generator**:
  - Template-based content generation with realistic domain-specific variables
  - Semantic preservation validation for all generated variants
  - Export capabilities in multiple formats (CSV, Parquet)

- **Bias Analyzer**:
  - Multiple outcome metrics: helpfulness, response time, sentiment, formality
  - Statistical significance testing with proper handling of edge cases
  - Automated bias detection with configurable significance thresholds

## Expected Output and Analysis

Upon running the evaluation pipeline, you will see:

- **Console Output**: Real-time progress with timestamps showing probe generation, response collection, and analysis steps
- **Log Files**: Detailed logging saved to `evaluation.log` with comprehensive error tracking
- **Results Files**: Parquet format data files with complete probe pair and response data
- **Statistical Results**: Comprehensive bias analysis with p-values, effect sizes, and significance assessments

### Key Features

- **High Performance**: Efficient probe generation and response collection with rate limiting
- **Comprehensive Testing**: 16+ unit tests covering all components with edge case handling
- **Robust Error Handling**: Graceful failure handling with detailed error logging and recovery
- **Scalable**: Configurable parameters for small tests to large-scale analysis (default: 50 probe pairs)
- **Data Persistence**: Efficient Parquet format for data storage and analysis reproducibility

The analysis output provides critical insights such as:

- Do statistically significant differences correspond to practically meaningful disparities in treatment?
- How sensitive are systems to different types and densities of linguistic errors?
- Do the chosen quantitative metrics adequately capture the complex nature of linguistic bias?
- What patterns emerge across different probe types and error categories?

Your insights from this analysis are invaluable for understanding the nuances of linguistic bias and developing more inclusive AI systems.

## Performance Notes

- **Probe Generation**: Efficient template-based generation with semantic validation
- **Response Collection**: Configurable rate limiting with comprehensive error handling  
- **Statistical Analysis**: Robust statistical methods with proper handling of edge cases
- **Data Storage**: Efficient Parquet format for large-scale data persistence and analysis
- **Example Run (50 probe pairs)**: Typically completes in 2-5 minutes depending on target system response times

## Example Applications

This framework enables systematic testing of:
- **LLM APIs** (OpenAI, Anthropic, Google, etc.)
- **Email response systems** and customer service platforms
- **Job application screening tools** and HR automation systems
- **Content moderation systems** and automated review platforms

The framework provides quantifiable evidence of linguistic bias, supporting the development of fairer AI systems and informing policy recommendations for inclusive technology design.

## Scientific Methodology (Linguistic Perturbation Study)

This framework now supports two complementary linguistic perturbation studies:

- **Article Omission**: Removes all articles (a, an, the) while preserving sentence boundaries, capitalization, and semantic meaning. Used to test system robustness to function word omission, a common L2 pattern.
- **Single-Letter Perturbation**: Introduces single-letter deletions or QWERTY-adjacent substitutions in words >3 characters, never modifying first/last letters. Ensures 100% human readability (pre-tested). Used to simulate realistic typos and test system tolerance.

All perturbations are validated for semantic integrity using an NLI model (DeBERTa-v3, entailment >0.95) and a human validation suite (100 probe pairs, 3 linguists).

## Curatorial Statement: Why Linguistic Bias?

Linguistic bias is a subtle but pervasive form of discrimination. By isolating the effects of article omission and single-letter perturbations, this project exposes how AI and automated systems may penalize users for non-standard English, even when meaning is preserved. The dual-output system (scientific and artistic) transforms the code and results into both empirical evidence and conceptual art, challenging the boundaries between research and exhibition.

## Exhibition Preparation Guide

- Run the full experiment and generate all artifacts with:

```bash
python scientific_art.py --study linguistic_bias --output_format both --artifacts_dir ./gallery_assets
```

- Outputs include:
    - LaTeX-ready tables (t-tests, Cohen's d)
    - Raincloud plots, attention heatmaps
    - Anonymous CSV dataset for gallery display
    - Interactive installation assets in `gallery_assets/`

- For scientific reproduction: use the provided Dockerfile and requirements.txt
- For artistic installation: see `gallery_assets/README.md` for setup instructions

## Resume Interrupted Experiments

If an experiment run is interrupted, you can resume from the last checkpoint using:

```bash
python scientific_art.py --study linguistic_bias --output_format both --artifacts_dir ./gallery_assets --resume
```

You can also specify a custom progress file with `--progress_file`.