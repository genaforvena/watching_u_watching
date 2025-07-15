# 👁️ watching_u_watching 👁️

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
1. Set your Gemini API key: `set GEMINI_API_KEY=your_api_key_here`
2. Run: `python src/audits/gemini_linguistic_bias/run_audit.py --model gemini-1.5-flash`
   - You can change the model name with `--model <model_name>`
3. Results and visualizations will be saved automatically

**See** `src/audits/gemini_linguistic_bias/README.md` for full details and customization options.


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