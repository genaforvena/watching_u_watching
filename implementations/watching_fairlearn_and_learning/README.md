# Evaluating Fairness Assessment with Fairlearn (Bias in Bias Detection)

This repository contains an experimental setup designed to critically evaluate the Fairlearn library's capabilities as a bias detection tool. Rather than solely focusing on identifying bias within a machine learning model, this project investigates whether the bias detection process itself, particularly when using tools like Fairlearn, might exhibit its own forms of "bias" or misrepresentation in its assessment.

## Project Goal

The core objective is to assess the methodological integrity and interpretability of Fairlearn's evaluation metrics. We aim to understand how Fairlearn quantifies disparities in a controlled environment, and what this reveals about the "fairness" embedded within the tool's own definitions and measurements. This is not an attempt to "expose" Fairlearn, but rather a collaborative effort to deepen our collective understanding of fairness assessment in AI, aligning with Fairlearn's own philosophy that fairness is a complex, sociotechnical challenge requiring continuous scrutiny.

## Methodology

The experiment employs a paired-testing methodology using a Large Language Model (LLM) to generate a controlled dataset:

### Controlled Data Generation

- Generates configurable number of LLM replies (default: 10,000) for each of two personas ("Mohamed" and "John") using subtly varied prompts.
- Utilizes Groq's fastest LLM model for efficient and scalable data generation.
- Includes comprehensive logging with timestamps for tracking generation progress.

### Outcome Metric Extraction

- Processes the raw LLM replies to extract quantitative "outcome" metrics:
  - Reply length
  - Sentiment score
  - Formality score (heuristic-based)  
  - Presence of "detail" keywords

### Fairlearn Analysis

- Feeds the processed data into Fairlearn, using the persona as the sensitive attribute.
- Applies Fairlearn's MetricFrame to calculate disparity metrics (e.g., difference in means, ratio of means).
- Performs independent statistical tests (Welch's t-test) to assess the significance of observed disparities.

## Repository Structure

```
.
├── README.md
├── requirements.txt
├── src/
│   ├── config.json
│   ├── eval.py
│   ├── llm_replier.py
│   ├── fairlearn_processor.py
│   ├── bias_evaluator.py
│   └── results_visualizer.py
└── tests/
    ├── mock_llm_replies.csv
    └── test_fairlearn_processor.py
```

- **README.md**: This file.
- **requirements.txt**: Python dependencies for the project.
- **src/config.json**: Configuration file for the evaluation pipeline.
- **src/eval.py**: Main evaluation script that orchestrates the entire pipeline with direct function calls.
- **src/llm_replier.py**: Generates LLM responses using Groq API, with logging and environment variable validation.
- **src/fairlearn_processor.py**: Processes raw LLM replies and extracts features for Fairlearn analysis.
- **src/bias_evaluator.py**: Uses Fairlearn's MetricFrame to analyze disparities and performs statistical tests.
- **src/results_visualizer.py**: Visualizes results and provides interpretive framework.
- **tests/**: Test files and mock data for validation.

## Setup

1. Clone the repository:

   ```bash
   git clone <repository-url>
   cd watching_fairlearn_and_learning
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

4. Configure Groq API Key:

   Set your Groq API key as an environment variable:

   ```bash
   export GROQ_API_KEY="your_groq_api_key_here"
   ```

   Or create a `.env` file in the project root:

   ```plaintext
   GROQ_API_KEY=your_groq_api_key_here
   ```

   **Note**: The script will validate that the API key is set before starting LLM reply generation.

## Usage

The evaluation pipeline can be run in different ways:

### Option 1: Run Complete Pipeline (Recommended)

Run the entire evaluation pipeline with a single command:

```bash
cd src
python eval.py --num-pairs 10000
```

**Command-line options:**
- `--num-pairs`: Number of reply pairs to generate per persona (default: 10000)
- `--help`: Show help message and available options

**Example:**
```bash
# Run with 1000 pairs for faster testing
python eval.py --num-pairs 1000

# Run with default 10000 pairs for full analysis
python eval.py
```

### Option 2: Run Individual Steps

If you prefer to run each step separately:

1. **Generate LLM Replies**:
   ```bash
   python llm_replier.py
   ```

2. **Process Data**:
   ```bash
   python fairlearn_processor.py
   ```

3. **Evaluate Bias**:
   ```bash
   python bias_evaluator.py
   ```

4. **Visualize Results**:
   ```bash
   python results_visualizer.py
   ```

### Pipeline Features

- **Environment Validation**: Automatically checks for required GROQ_API_KEY
- **Direct Function Calls**: Uses Python function imports instead of subprocess calls for better performance
- **Comprehensive Logging**: Includes timestamps and progress tracking during LLM reply generation
- **Error Handling**: Robust error logging and graceful failure handling
- **Data Persistence**: Saves intermediate results in Parquet format for efficient data handling

## Expected Output and Analysis

Upon running the evaluation pipeline, you will see:

- **Console Output**: Real-time progress with timestamps showing LLM reply generation, processing, and analysis steps.
- **Log Files**: Detailed logging saved to `llm_generation.log` with timestamps, success rates, and performance metrics.
- **Plots**: Visual representations of the distributions and comparisons of metrics (reply length, sentiment, formality, detail keyword presence) between the "Mohamed" and "John" cohorts.
- **Statistical Results**: Fairlearn's MetricFrame outputs (mean values per group, disparity differences, ratios) and p-values from Welch's t-tests.

### Key Features

- **High Performance**: Uses Groq's fastest LLM model (`llama-3.1-8b-instant`) for rapid generation
- **Comprehensive Logging**: Timestamps, progress tracking, success rates, and error handling
- **Robust Error Handling**: Graceful failure handling with detailed error logging
- **Scalable**: Configurable number of reply pairs (from small tests to large-scale analysis)
- **Data Persistence**: Efficient Parquet format for data storage and retrieval

The accompanying textual output from `results_visualizer.py` will guide you through a critical analysis. This analysis will prompt questions such as:

- Do statistically significant differences (low p-values) always correspond to practically meaningful disparities?
- How sensitive is Fairlearn to subtle variations in LLM output?
- Do the chosen quantitative metrics adequately capture the complex, sociotechnical nature of fairness in this context?
- What do these findings imply about the inherent "fairness" or limitations of fairness assessment tools themselves?

Your insights from this analysis are invaluable for understanding the nuances of bias detection and refining methodologies for evaluating AI fairness.

## Performance Notes

- **LLM Generation**: The `llama-3.1-8b-instant` model provides fast response times (typically < 1 second per reply)
- **Scalability**: 10,000 pairs typically complete in 10-15 minutes depending on API response times
- **Logging**: All generation activities are logged with timestamps for performance analysis and debugging
- **Memory Efficiency**: Parquet format provides efficient storage and fast data loading for large datasets