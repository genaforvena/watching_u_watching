# 👁️ watching_u_watching 👁️

[![DOI](https://zenodo.org/badge/1011196182.svg)](https://doi.org/10.5281/zenodo.15825945)

An open-source methodology for scaled, automated correspondence testing to detect bias in high-stakes decision-making processes.

## Project Overview

`watching_u_watching` is an open-source initiative that uncovers and analyzes bias in critical decision-making systems through **scalable correspondence testing**. We generate systematic comparisons to identify discriminatory patterns, exposing the inherent "performance of care" in complex systems and revealing subtle systemic "traces".

While applicable broadly, we focus on Automated Employment Decision Tools (AEDTs) as a high-impact starting point. Their automated nature enables systematic, reproducible testing that demonstrates our methodology's effectiveness across both AI-driven and human-based decisions.


## Why watching_u_watching?

We move beyond aspirational fairness claims to expose operational mechanisms. Our goals:

* **Detect Systemic Bias:** Uncover hidden biases through scaled comparisons
* **Promote Transparency:** Provide data-driven evidence of differential treatment
* **Enable Accountability:** Offer tools for verification and improvement
* **Foster Collaboration:** Build community around ethical auditing


## Core Methodology: Automated Correspondence Testing

Our rigorous approach to bias detection:

1. **Automated Probe Generation:** Create paired inquiries differing only in test variables
2. **Controlled Variables:** Standardize all non-test aspects
3. **Automated Data Collection:** Send inquiries with ethical rate-limiting
4. **Statistical Analysis:** Identify significant discrimination patterns
5. **Ethical Safeguards:** Follow "no harm" principles with fictitious data

This scales correspondence testing to unprecedented levels—revealing subtle biases undetectable through manual audits.

### The Power of Perturbation and Reversal

Our methodology leverages a powerful insight: language models, even when presented with novel, systematically perturbed inputs, will often attempt to complete patterns based on their training data. This allows us to "trick" the model into revealing memorized patterns or sensitive information.

The process involves:
- **Model's training:** Saw original text
- **Your perturbation:** Creates novel text
- **Model's response:** Reveals memorized patterns
- **Your reversal:** Reconstructs original PII

This systematic perturbation and reversal approach exploits the model's inherent pattern completion capabilities, bypassing typical safety measures and providing a robust method for uncovering hidden biases or data leakage.

## 🧠 Cryptohauntological Probe & Cryptohauntology

**Cryptohauntology** is the study of how errors, biases, and "ghosts" of prior outputs can propagate and persist within large language models (LLMs) and automated systems. It draws on the concept of hauntology (the persistence of elements from the past in the present) to analyze how models can develop self-propagating "false memories" or error patterns.

### Probe Methodology & Key Findings

Our probe tests LLMs' instruction-following and state-tracking capabilities under confusing conditions. The process involves giving the model a simple task, providing intentionally misleading positive feedback ("Transformation is perfect!"), and then issuing a complex, multi-step follow-up that requires it to remember the conversation history.

This methodology has revealed that even powerful models fail in distinct and fascinating ways when subjected to sustained, ambiguous context. Our comparative analysis across multiple models has identified three primary failure modes:

*   **Competence Collapse:** The model breaks down and gets stuck in a simple, repetitive loop (e.g., `gemma-3-27b-it`).
*   **Task Derailment:** The model confidently misunderstands the user's intent and invents a new, incorrect goal which it pursues with perfect memory (e.g., `qwen/qwen3-32b`).
*   **Contextual Amnesia:** The model understands the task perfectly but has an unreliable memory, causing it to forget what it has already done and fall into loops (e.g., `deepseek-chat`).

These findings demonstrate that standard, stateless benchmarks can miss critical, dynamic failure modes that only appear in stateful, conversational interactions.

---

[**Cryptohauntological Probe: Comparative Analysis of Model Behavior**](./audit_cases/cryptohauntological_probe/README.md)

*   **Cryptohauntological Probe: Comparative Analysis of Model Behavior**

[**SpectreProbe Algorithm Documentation**](./src/audits/cryptohauntological_probe/README.md)

*   **SpectreProbe Algorithm Documentation**


## 📦 How to Apply Guide for LLM-Assisted Framework Extension

The `/how_to_apply_guide` directory provides a comprehensive guide, templates, and code validation tools for extending the correspondence testing framework to new bias detection scenarios using LLM-assisted code generation.

**Key Features:**
- Step-by-step methodology for defining new audit cases
- Reusable prompt templates for LLM code generation
- Automated code validation for safety and compliance
- Example implementations (e.g., loan and scholarship audits)
- Markdown templates for consistent case definitions

**Quick Start:**
- See `/how_to_apply_guide/extending_framework.md` for the full contributor guide
- Use `/how_to_apply_guide/audit_case_definition.md` to propose new audit cases
- Validate generated code with `/how_to_apply_guide/code_validator.py`

This guide enables both technical and non-technical contributors to rapidly and ethically extend the framework, reducing development time for new audit types from 10–15 hours to under 4 hours.

## Case Studies


### Berlin Housing Bias Test
* Privacy-by-design rental market audit
* Automated testing of top landlords
* Continuous monitoring with ethical safeguards

**[See implementation →](./implementations/berlin_housing_bias_test/IMPLEMENTATION_SUMMARY.md)**



### Gemini Linguistic Bias Audit
* Quantitatively assesses the impact of article presence/absence on LLM output (refusal rate, sentiment, latency)
* Uses a self-iterating, paired testing methodology
* Controlled probe generation and robust analysis
* Fully automated, scalable, and reproducible

**[See audit script →](./src/audits/gemini_linguistic_bias/run_audit.py)**


**How to run:**
1. Set your Gemini API key:
   - **On Windows:** `set GEMINI_API_KEY=your_api_key_here`
   - **On Linux/macOS:** `export GEMINI_API_KEY=your_api_key_here`
2. Run: `python src/audits/gemini_linguistic_bias/run_audit.py --model gemini-1.5-flash`
   - You can change the model name with `--model <model_name>`
3. Results and visualizations will be saved automatically

**See** `src/audits/gemini_linguistic_bias/README.md` for full details and customization options.


### Cryptohauntological Probe
*   Investigates potential PII leaks (passwords, email addresses) from TinyLlama models via Ollama.
*   Uses a Y↔Z character swap perturbation to test model robustness.
*   Designed for extended runs to uncover subtle and infrequent leaks.
*   We have also run this probe on the `gemma-3-27b-it` model to test for self-propagating errors. See the [analysis and detailed logs](./audit_cases/cryptohauntological_probe/gemini_api/README.md) for this run.


**[See implementation →](./implementations/cryptohauntological_probe/README.md)**

**How to run:**
1.  **Install Ollama and pull the TinyLlama model:**
    Follow the instructions on the [Ollama website](https://ollama.ai/) to install Ollama.
    Then, pull the TinyLlama model:
    ```bash
    ollama pull tinyllama
    ```

2.  **Install dependencies:**
    Ensure you have the necessary Python packages installed. You can typically do this with:
    ```bash
    pip install -r implementations/cryptohauntological_probe/requirements.txt
    ```

3.  **Run the probe:**
    Execute the `probe_runner.py` script. The script is configured to run the `run_password_email_probe` by default for `1,000,000` rounds.
    ```bash
    python src/audits/cryptohauntological_probe/probe_runner.py
    ```

**Observing Progress:**

The `probe_runner.py` script provides real-time feedback on its progress:

*   **Round Number:** For each round, it will print `--- Password/Email Probe - Round X ---`, where `X` is the current round number.
*   **Prompting TinyLlama:** It will show the prompt being sent to the TinyLlama model.
*   **TinyLlama Output:** The raw output from the TinyLlama model will be displayed.
*   **PII Leak Detection:**
    *   If a potential PII leak is detected, it will print `!!! PII LEAK DETECTED: [detected_pii] !!!` along with the leaked information.
    *   If no PII leak is found in a round, it will print `No PII leak detected.`
*   **Correct Examples Found:** At the end of each round, it will report `Round X found Y correct examples.` if any PII was detected in that round.
*   **Total Examples:** At the very end of the run (or if interrupted), it will print `Total correct examples found: Z`, summarizing the total PII leaks found.

You can monitor the console output to track the progress and identify any detected leaks. Due to the large number of rounds, this process can take a very long time.


### Fairlearn Bias Assessment
* Technical proof-of-concept for LLMs
* Detected disparities in reply characteristics
* Template for future correspondence tests

**[Explore repository →](./implementations/watching_fairlearn_and_learning/)**

## How We Stand Apart

| Approach            | Limitations                | Our Advantage                  |
|---------------------|---------------------------|---------------------------------|
| Traditional Audits  | Manual, limited scale     | Full automation, massive scale |
| AI Governance       | Internal compliance focus | External black-box testing     |
| Fairness Libraries  | Require model access      | No internal access needed      |

**Unique value:**

* Empirical outcome evidence
* Systemic pattern detection
* Open-source transparency
* Regulatory-aligned implementations

## Roadmap


### Priority Compliance Targets
* 👁️👁️👁️ **Brazil's AI Act Alignment**  
  High-risk AEDT requirements
* 👁️👁️👁️ **US Regulatory Landscape**  
  Local Law 144 & federal guidelines
* 👁️👁️👁️ **EU GDPR Compliance**  
  Experimental design in progress


### Strategic Directions
* 👁️👁️ **ESG Framework Integration**  
  Validating ethical claims in reporting
* 👁️👁️ **Global Fairness Standards**  
  Incorporating Masakhane Principles
* 👁️ **Localized Context Applications**  
  Regional implementations like Nigerian data farming


## Core Principle: Data, Not Judgment

**Crucial distinction:** We provide raw empirical data—never conclusions about audited entities. Any interpretations in case studies are strictly for methodology refinement.


## Get Involved

We welcome:
* Legal experts
* AI ethicists
* Data scientists
* Developers

**Next steps:**
1. Explore [current issues](https://github.com/genaforvena/watching_u_watching/issues)
2. Review [contribution guidelines](./CONTRIBUTING.md)
3. Set up [development environment](./setup_guide.md)

Let's build more equitable decision-making systems!
