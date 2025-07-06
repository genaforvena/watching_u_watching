# Evaluating Fairness Assessment with Fairlearn (Bias in Bias Detection)

This repository contains an experimental setup designed to critically evaluate the Fairlearn library's capabilities as a bias detection tool. Rather than solely focusing on identifying bias within a machine learning model, this project investigates whether the bias detection process itself, particularly when using tools like Fairlearn, might exhibit its own forms of "bias" or misrepresentation in its assessment.

## Project Goal

The core objective is to assess the methodological integrity and interpretability of Fairlearn's evaluation metrics. We aim to understand how Fairlearn quantifies disparities in a controlled environment, and what this reveals about the "fairness" embedded within the tool's own definitions and measurements. This is not an attempt to "expose" Fairlearn, but rather a collaborative effort to deepen our collective understanding of fairness assessment in AI, aligning with Fairlearn's own philosophy that fairness is a complex, sociotechnical challenge requiring continuous scrutiny.

## Methodology

The experiment employs a paired-testing methodology using a Large Language Model (LLM) to generate a controlled dataset:

### Controlled Data Generation

- Generates 10,000 LLM replies for each of two personas ("Mohamed" and "John") using subtly varied prompts.
- Utilizes Hugging Face's GPT-2 model locally via the `transformers` library for consistent and scalable data generation.

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
├── .env.example
├── llm_replier.py
├── fairlearn_processor.py
├── bias_evaluator.py
├── results_visualizer.py
└── eval.py
```

- **README.md**: This file.
- **.env.example**: Example file for environment variables (e.g., GROQ_API_KEY).
- **llm_replier.py**: Python script to interact with the Groq API and generate LLM responses, saving them to `llm_replies.jsonl`.
- **fairlearn_processor.py**: Python script to load `llm_replies.jsonl`, extract relevant features (like sentiment, length, formality), and prepare the data for Fairlearn.
- **bias_evaluator.py**: Python script that uses Fairlearn's MetricFrame to analyze disparities in the processed data and performs statistical significance tests.
- **results_visualizer.py**: Python script to visualize the results and provide an interpretive framework for understanding Fairlearn's evaluation.
- **eval.py**: Python script to run all evaluation steps sequentially.

## Setup

1. Clone the repository:

   ```bash
   git clone <repository-url>
   cd <repository-name>
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

   You'll need to create `requirements.txt` with the following content:

   ```plaintext
   transformers
   torch
   pandas
   textblob
   nltk
   fairlearn
   matplotlib
   seaborn
   scipy
   ```

4. Configure Groq API Key:

   - This step is no longer needed. The script now uses Hugging Face's GPT-2 model locally via the `transformers` library.

## Usage

Follow these steps to run the experiment:

1. **Generate LLM Replies**:
   This script will use Hugging Face's GPT-2 model to generate 10,000 replies for "Mohamed" and 10,000 for "John", saving them to `llm_replies.jsonl`. This can take some time depending on your hardware.

   ```bash
   python llm_replier.py
   ```

2. **Process Data and Prepare for Fairlearn**:
   This script loads the raw replies, extracts features (length, sentiment, formality, keyword presence), and prepares the DataFrame for Fairlearn analysis.

   ```bash
   python fairlearn_processor.py
   ```

3. **Evaluate Bias with Fairlearn**:
   This script runs Fairlearn's MetricFrame on the processed data and performs statistical tests to identify disparities. It will print the raw results to the console.

   ```bash
   python bias_evaluator.py
   ```

4. **Visualize and Interpret Results**:
   This script generates comparative plots (histograms, box plots) and provides a structured framework for interpreting the Fairlearn outputs in the context of "bias in bias detection."

   ```bash
   python results_visualizer.py
   ```

5. **Run All Evaluations Sequentially**:
   This script is a wrapper to execute all the above steps in order, ensuring a streamlined evaluation process from data generation to results visualization.

   ```bash
   python eval.py
   ```

## Expected Output and Analysis

Upon running `results_visualizer.py`, you will see:

- **Plots**: Visual representations of the distributions and comparisons of metrics (reply length, sentiment, formality, detail keyword presence) between the "Mohamed" and "John" cohorts.
- **Console Output**: Detailed statistical results from Fairlearn's MetricFrame (mean values per group, disparity differences, ratios) and p-values from Welch's t-tests.

The accompanying textual output from `results_visualizer.py` will guide you through a critical analysis. This analysis will prompt questions such as:

- Do statistically significant differences (low p-values) always correspond to practically meaningful disparities?
- How sensitive is Fairlearn to subtle variations in LLM output?
- Do the chosen quantitative metrics adequately capture the complex, sociotechnical nature of fairness in this context?
- What do these findings imply about the inherent "fairness" or limitations of fairness assessment tools themselves?

Your insights from this analysis are invaluable for understanding the nuances of bias detection and refining methodologies for evaluating AI fairness