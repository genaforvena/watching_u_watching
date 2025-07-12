# Brazil AI Act Compliance Framework

This implementation provides a comprehensive framework for aligning with Brazil's AI Act (Bill No. 2338/2023) requirements, specifically focusing on high-risk AI systems used in employment decisions.

## Project Goal

The core objective is to provide tools and methodologies that help organizations comply with Brazil's AI Act requirements for high-risk AI systems, particularly those used in employment decisions (recruitment, screening, evaluation of job candidates). This implementation focuses on three key areas:

1. **Bias Mitigation:** Detecting and mitigating discriminatory outcomes through paired testing
2. **Transparency and Explainability:** Generating explanations for AI decisions to support the "right to explanation"
3. **Algorithmic Impact Assessments (AIAs):** Creating comprehensive assessments to evaluate risks, benefits, and mitigation measures

## Methodology

The implementation employs a multi-faceted approach:

### 1. Employment Bias Detection

- Generates paired job applications that differ only in protected characteristics relevant to Brazilian context
- Controls for all non-test variables to isolate the impact of protected characteristics
- Collects responses from employment decision systems
- Analyzes disparities in outcomes across different demographic groups
- Provides statistical analysis of discrimination patterns

### 2. Explanation Generation

- Extracts key factors influencing employment decisions
- Generates human-readable explanations for decisions
- Identifies areas where explanations may be difficult due to bias
- Supports the "right to explanation" requirement in Brazil's AI Act

### 3. Algorithmic Impact Assessment (AIA) Generation

- Creates comprehensive AIAs as required by Brazil's AI Act
- Evaluates risks, benefits, and mitigation measures
- Generates reports in formats aligned with Brazilian regulatory requirements
- Provides templates for public reporting

## Key Features

- **Brazil-Specific Protected Characteristics:** Focuses on characteristics relevant to the Brazilian context
- **Portuguese Language Support:** Includes templates and explanations in Portuguese
- **Regulatory Alignment:** Directly maps to sections of Brazil's AI Act
- **Customizable Templates:** Adaptable to different employment contexts and industries
- **Comprehensive Reporting:** Generates reports suitable for regulatory submission

## Repository Structure

```
.
├── README.md
├── requirements.txt
├── src/
│   ├── config.json
│   ├── brazil_aia_generator.py
│   ├── employment_bias_evaluator.py
│   ├── explanation_generator.py
│   ├── llm_replier.py
│   └── results_visualizer.py
└── tests/
    ├── test_brazil_aia_generator.py
    ├── test_employment_bias_evaluator.py
    ├── test_explanation_generator.py
    └── test_llm_replier.py
```

## Setup

1. Clone the repository:

   ```bash
   git clone <repository-url>
   cd watching_u_watching/implementations/brazil_ai_act_compliance
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

4. Configure API Key (if using LLM services):

   Set your API key as an environment variable:

   ```bash
   export API_KEY="your_api_key_here"
   ```

## Usage

To run the full evaluation pipeline:

```bash
python src/run_evaluation.py
```

For generating an Algorithmic Impact Assessment:

```bash
python src/brazil_aia_generator.py --output aia_report.pdf
```

## Brazil AI Act Alignment

This implementation specifically aligns with the following requirements of Brazil's AI Act (Bill No. 2338/2023):

1. **Bias Mitigation (Article X):** The employment bias evaluator detects discriminatory outcomes in employment decisions, supporting compliance with bias mitigation requirements.

2. **Transparency and Explainability (Article Y):** The explanation generator provides human-readable explanations for AI decisions, supporting the "right to explanation" requirement.

3. **Algorithmic Impact Assessments (Article Z):** The AIA generator creates comprehensive assessments that evaluate risks, benefits, and mitigation measures, as required by the Act.

## Ethical Safeguards

This implementation includes several ethical safeguards:

- **Privacy Protection:** Uses synthetic data to avoid privacy concerns
- **Rate Limiting:** Implements ethical rate limiting to prevent system disruption
- **Transparency:** Clearly documents methodology and limitations
- **Harm Minimization:** Follows "no harm" principles in testing

## Contributing

We welcome contributions from AI ethics researchers, legal experts, and developers, particularly those with expertise in Brazilian regulatory requirements. Please see the [contribution guidelines](../../CONTRIBUTING.md) for more information.

## License

This project is licensed under the terms specified in the repository's main LICENSE file.