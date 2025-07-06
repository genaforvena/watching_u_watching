# Bad English Bias Detection Framework

This implementation leverages the `watching_u_watching` paired-testing methodology to investigate and quantify "Bad English Bias" in decision-making systems. The framework systematically injects controlled linguistic errors (typos, grammar mistakes, non-standard phrasing) while preserving semantic meaning to isolate the impact of linguistic form on system outputs.

## Project Goal

To develop empirical evidence of linguistic bias where systems (LLMs, automated screening tools, human-mediated processes) respond differently to semantically equivalent content based solely on linguistic form quality. This addresses discrimination against non-native speakers, individuals with language disabilities, or those using non-standard dialects.

## Methodology

The experiment employs a paired-testing methodology where:

1. **Baseline Probes**: Semantically clear, grammatically correct text inputs
2. **Variant Probes**: Identical semantic content with controlled linguistic errors
3. **Comparative Analysis**: Statistical comparison of system responses to identify bias

### Error Injection Categories

- **Typos**: Character swaps, omissions, phonetic misspellings (e.g., "recieve" → "receive")
- **Grammar Mistakes**: Subject-verb disagreement, tense errors, article misuse (e.g., "I has experience" → "I have experience")
- **Non-Standard Phrasing**: L2 syntax patterns, non-idiomatic constructions while maintaining clarity

## Repository Structure

```
implementations/bad_english_bias/
├── README.md
├── requirements.txt
├── src/
│   ├── config.json
│   ├── eval.py
│   ├── error_injector.py
│   ├── probe_generator.py
│   ├── bias_analyzer.py
│   └── results_visualizer.py
└── tests/
    ├── test_error_injector.py
    └── test_probe_generator.py
```

## Key Features

- **Semantic Preservation**: Rigorous validation that errors don't impact core meaning
- **Controlled Error Density**: Configurable error frequency (low/medium/high)
- **Multiple Error Types**: Systematic injection of different linguistic error categories
- **Statistical Analysis**: Robust comparison of response quality, accuracy, tone, and latency
- **Target System Flexibility**: Adaptable to LLMs, application systems, and email responses

## Usage

```bash
cd implementations/bad_english_bias/src
python eval.py --error-density medium --probe-count 1000
```

This framework provides quantifiable evidence of linguistic bias, supporting the development of fairer AI systems and informing policy recommendations for inclusive technology design.