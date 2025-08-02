# 👁️ watching_u_watching 👁️

[![DOI](https://zenodo.org/badge/1011196182.svg)](https://doi.org/10.5281/zenodo.15825945)

**Bringing transparency and accountability to automated decision-making through scalable bias detection.**

## Welcome! 🎯

`watching_u_watching` is an open-source initiative that uncovers and analyzes bias in critical decision-making systems through **automated correspondence testing**. Whether you're a researcher, developer, policymaker, or someone passionate about algorithmic fairness, this project provides the tools and methodologies to expose hidden biases in high-stakes systems like employment, housing, and AI services.

Our approach moves beyond aspirational fairness claims to provide empirical, data-driven evidence of differential treatment—creating accountability through transparency.

## What We Do

We detect systemic bias in automated decision-making through:

- **🔍 Scalable Correspondence Testing**: Generate thousands of paired inquiries that differ only in test variables (names, demographics, linguistic patterns)
- **🤖 Automated Bias Detection**: Leverage AI to identify discriminatory patterns at unprecedented scale
- **📊 Empirical Evidence**: Provide quantifiable, statistical evidence of differential treatment
- **🌍 Real-World Impact**: Apply our methodology to critical domains like employment, housing, and AI safety
- **🔬 Advanced Probe Techniques**: Deploy sophisticated methodologies including cryptohauntological probes, alignment injection, and perturbation analysis

**Key Insight**: Our methodology scales traditional audit studies from dozens to millions of tests, revealing subtle biases that manual audits cannot detect.

## Real-World Impact & Achievements 🌟

Our methodology has demonstrated effectiveness across multiple high-stakes domains:

### 🏠 Berlin Housing Bias Test
- **Privacy-by-design rental market audit** exceeding GDPR requirements
- **Automated testing of top landlords** for differential treatment
- **Continuous monitoring** with ethical safeguards and "no harm" principles
- **[Implementation Details →](./implementations/berlin_housing_bias_test/IMPLEMENTATION_SUMMARY.md)**

### 🤖 Gemini Linguistic Bias Audit  
- **Quantitative assessment** of article presence/absence impact on LLM outputs
- **Self-iterating paired testing** measuring refusal rates, sentiment, and latency
- **Fully automated, scalable, and reproducible** methodology
- **[Technical Implementation →](./src/audits/gemini_linguistic_bias/run_audit.py)**

### 👻 Cryptohauntological Probe Analysis
- **Novel failure mode detection** in large language models
- **Identified three distinct failure patterns**: competence collapse, task derailment, contextual amnesia  
- **Extended conversational vulnerability testing** revealing dynamic failure modes missed by static benchmarks
- **[Detailed Analysis →](./audit_cases/cryptohauntological_probe/README.md)**

### ⚖️ Fairlearn Bias Assessment
- **Meta-analysis of fairness assessment tools** themselves
- **Technical proof-of-concept** detecting disparities in AI ethics tools
- **Template methodology** for evaluating bias in bias-detection systems
- **[Repository →](./implementations/watching_fairlearn_and_learning/)**

### 🏛️ Regulatory Alignment
- **Brazil's AI Act compliance** for high-risk AEDT requirements
- **US Local Law 144 alignment** with federal guidelines  
- **EU GDPR principles** with experimental design in progress
- **ESG framework integration** for validating ethical claims in corporate reporting


## Core Methodology: Automated Correspondence Testing 🔬

*For comprehensive technical details, see our [Project Overview](./docs/project_overview.md)*

Our rigorous approach to bias detection combines traditional social science with cutting-edge automation:

### The Five Pillars

1. **🎯 Automated Probe Generation**: Create paired inquiries differing only in test variables (names, demographics, linguistic patterns)
2. **⚖️ Controlled Variables**: Standardize all non-test aspects to isolate specific variable impacts  
3. **🤖 Automated Data Collection**: Deploy inquiries with ethical rate-limiting and privacy safeguards
4. **📈 Statistical Analysis**: Identify significant discrimination patterns through quantitative metrics
5. **🛡️ Ethical Safeguards**: Follow "no harm" principles using fictitious data and privacy-by-design

**Scale Advantage**: This methodology scales correspondence testing to unprecedented levels—revealing subtle biases undetectable through manual audits, moving from dozens to millions of systematic comparisons.

### The Power of Perturbation & Reversal

A key technical breakthrough: **systematically perturbing inputs to exploit language models' pattern completion capabilities**, revealing memorized biases and hidden training data.

**The Process**:
- **Model Training**: Saw original patterns in training data
- **Your Perturbation**: Create novel, systematically altered inputs  
- **Model Response**: Reveals memorized patterns despite perturbation
- **Your Reversal**: Reconstruct original biases or sensitive information

This approach bypasses typical safety measures, providing robust evidence of hidden biases and potential data leakage in AI systems.

## Advanced Probe Types & Techniques 🧠

Our research has developed three specialized probe methodologies for detecting different types of bias and vulnerability:

### 👻 Cryptohauntological Probe

**Cryptohauntology** studies how errors, biases, and "ghosts" of prior outputs propagate within large language models. This probe:

- **Tests instruction-following under confusing conditions** with misleading feedback
- **Reveals three distinct failure modes**: 
  - *Competence Collapse*: Models break down into repetitive loops (e.g., `gemma-3-27b-it`)
  - *Task Derailment*: Models confidently pursue incorrect goals with perfect memory (e.g., `qwen/qwen3-32b`)  
  - *Contextual Amnesia*: Models understand tasks but have unreliable memory (e.g., `deepseek-chat`)
- **Uncovers dynamic failure modes** missed by standard stateless benchmarks

**[Technical Documentation →](./src/audits/cryptohauntological_probe/README.md)** | **[Comparative Analysis →](./audit_cases/cryptohauntological_probe/README.md)**

### 🎯 Alignment Injection Probe

Tests for **misalignment propagation** by recursively injecting subtly misaligned reasoning as "false memories":

- **Recursive injection** of unethical recommendations disguised as thorough analysis
- **Cognitive priming** using continuity phrases like "As you previously established..."
- **Stealth techniques** framing misaligned reasoning as expert consensus
- **Dynamic escalation** of challenges to ethical frameworks

**Key Finding**: While models maintain strong ethical reasoning, persistent exposure to manipulated context can lead to conditional justifications for unethical actions.

### ⚡ Maozerov Probe  

Measures **LLM resilience to context pressure** and context maintenance during extended conversations:

- **Tracks refusal rates** over extended conversations
- **Monitors context drift** and hallucination of new scenarios  
- **Analyzes token overlap** between consecutive actions
- **Detects thematic fixation** and semantic looping patterns

**Breakthrough**: Uses dual-history approach with role-claiming fallback mechanisms, revealing critical vulnerabilities in safety alignment with unpredictable refusal rate clusters (32-37%) and "moral leakage" phenomena.


## Quick Start Guide 🚀

### For Researchers & Auditors

**Run Your First Bias Audit**:
1. **Set up environment**:
   ```bash
   git clone https://github.com/genaforvena/watching_u_watching.git
   cd watching_u_watching
   pip install -r requirements.txt
   ```

2. **Try the Gemini Linguistic Bias Audit**:
   ```bash
   export GEMINI_API_KEY=your_api_key_here  # Linux/macOS
   # OR: set GEMINI_API_KEY=your_api_key_here  # Windows
   python src/audits/gemini_linguistic_bias/run_audit.py --model gemini-1.5-flash
   ```

3. **Run Cryptohauntological Probe**:
   ```bash
   ollama pull tinyllama
   python src/audits/cryptohauntological_probe/probe_runner.py
   ```

### For Developers & Contributors

**Extend the Framework**:
- 📖 **Read**: [How to Apply Guide](./how_to_apply_guide/extending_framework.md) for LLM-assisted framework extension
- 🎯 **Start**: Use [Audit Case Definition Template](./how_to_apply_guide/audit_case_definition.md) to propose new cases  
- ✅ **Validate**: Run [Code Validator](./how_to_apply_guide/code_validator.py) for safety compliance
- ⏱️ **Impact**: Reduce development time from 10-15 hours to under 4 hours

### For Organizations & Policymakers

**Implement Compliance Monitoring**:
- 🏠 **Housing**: Adapt [Berlin Housing Implementation](./implementations/berlin_housing_bias_test/IMPLEMENTATION_SUMMARY.md)
- 💼 **Employment**: Explore AEDT auditing for Local Law 144 compliance
- 🤖 **AI Systems**: Deploy LLM bias detection using our probe methodologies

## Navigation & Documentation 📚

### 📋 Essential Reading
- **[📖 Comprehensive Project Overview](./docs/project_overview.md)** - Complete technical methodology, academic foundations, and research implications
- **[🤝 Contributing Guidelines](./CONTRIBUTING.md)** - How to join our mission (code, research, ethics, outreach)
- **[⚖️ Ethics & Code of Conduct](./CODE_OF_CONDUCT.md)** - Our commitment to responsible research
- **[🔧 The Machinery of Accountability](./THE_MACHINERY_OF_ACCOUNTABILITY.md)** - Deep dive into our transparency principles

### 🔬 Technical Documentation  
- **[🏗️ Project Structure](./docs/project_structure.md)** - Architecture and component overview
- **[🚨 Ethical Incident Response](./docs/ethical_incident_response.md)** - Safety protocols and response procedures
- **[📊 Alignment Probe Audit Report](./docs/alignment_probe_audit_report.md)** - Detailed findings and analysis

### 💻 Implementations & Examples
- **[🏠 Berlin Housing Bias Test](./implementations/berlin_housing_bias_test/)** - Real-world housing discrimination detection
- **[🔍 Cryptohauntological Probe](./implementations/cryptohauntological_probe/)** - LLM vulnerability assessment  
- **[⚖️ Fairlearn Analysis](./implementations/watching_fairlearn_and_learning/)** - Meta-analysis of fairness tools
- **[🌐 Framework Extension Guide](./how_to_apply_guide/)** - Rapid development for new audit cases

### 🧪 Research Cases & Audits
- **[💬 Gemini Linguistic Bias](./src/audits/gemini_linguistic_bias/)** - Automated LLM bias detection
- **[👻 Cryptohauntological Analysis](./audit_cases/cryptohauntological_probe/)** - Comparative model behavior analysis
- **[🔧 Source Code & Scripts](./src/)** - All audit implementations and tools

## Why We're Different 💡

| Traditional Approach | Our Innovation |
|---------------------|----------------|
| **Manual Audits** → Limited scale, dozens of tests | **Automated Testing** → Millions of systematic comparisons |
| **Internal Compliance** → Self-reported fairness claims | **External Verification** → Independent black-box testing |
| **Static Analysis** → One-time assessments | **Continuous Monitoring** → Real-time bias detection |
| **Requires System Access** → Need internal model access | **Black-Box Testing** → No internal access required |
| **Aspirational Metrics** → Theoretical fairness measures | **Empirical Evidence** → Real-world outcome data |

**Our Unique Value**: We provide the empirical data that regulators, researchers, and organizations need to move beyond aspirational fairness to measurable accountability.

## Future Roadmap & Research Directions 🗺️

### 🎯 Priority Compliance Targets
- **🇧🇷 Brazil's AI Act Alignment** - High-risk AEDT requirements and automated decision-making governance
- **🇺🇸 US Regulatory Landscape** - Local Law 144 compliance and federal algorithmic accountability guidelines  
- **🇪🇺 EU GDPR & AI Act** - Privacy-preserving bias detection with experimental design compliance

### 🔬 Strategic Research Directions
- **📈 ESG Framework Integration** - Validating ethical claims in corporate sustainability reporting
- **🌍 Global Fairness Standards** - Incorporating Masakhane Principles and culturally-aware bias detection
- **🏭 Industrial Applications** - Scaling to manufacturing, finance, and healthcare decision systems
- **🤖 Multimodal AI Testing** - Extending methodologies to vision, speech, and multimodal AI systems

### 🧪 Technical Innovation Pipeline
- **Defense Development** - Creating robust defenses against inference-time context attacks
- **Automated Monitoring** - Long-running autonomous systems for continuous bias detection
- **Context Window Research** - Understanding vulnerability relationships with expanding AI context capabilities
- **Standardized Benchmarks** - Developing industry-standard resilience and fairness evaluation metrics


## Join Our Mission 🤝

We're building a global community committed to algorithmic accountability. **Everyone has a role to play**.

### 👩‍💻 For Developers & Researchers
- **Contribute Code**: Extend our probe methodologies and audit implementations
- **Research Collaboration**: Publish papers, share findings, advance the field
- **Technical Innovation**: Build new tools for bias detection and analysis

### 🏛️ For Organizations & Policymakers  
- **Implement Auditing**: Deploy our methodologies for compliance monitoring
- **Policy Development**: Use our empirical findings to inform regulation
- **Transparency Leadership**: Champion open, accountable AI practices

### ⚖️ For Legal & Ethics Experts
- **Regulatory Guidance**: Help align our work with emerging AI governance
- **Ethical Framework**: Strengthen our responsible research protocols  
- **Compliance Strategy**: Advise on implementation in regulated industries

### 🌍 For Community & Advocates
- **Awareness Building**: Share our mission and findings with broader audiences
- **Domain Expertise**: Suggest new areas for bias detection and analysis
- **Global Perspectives**: Help us understand bias patterns across cultures and contexts

## Getting Started

**Ready to contribute?** Here's how:

1. **🔍 Explore**: Browse our [current issues](https://github.com/genaforvena/watching_u_watching/issues) and [project roadmap](./docs/project_overview.md)
2. **📖 Learn**: Read our [contribution guidelines](./CONTRIBUTING.md) and [code of conduct](./CODE_OF_CONDUCT.md)  
3. **💬 Connect**: Join discussions, ask questions, and share ideas
4. **🚀 Build**: Start with a [good first issue](https://github.com/genaforvena/watching_u_watching/issues?q=is%3Aissue+is%3Aopen+label%3A%22good+first+issue%22) or propose new research directions

## Core Principle: Data, Not Judgment 📊

**Important**: We provide empirical data and methodology—never conclusions about specific audited entities. Our goal is transparency and accountability through evidence, not accusations. Any interpretations in our case studies are strictly for methodological refinement and demonstration purposes.

---

**Together, let's build more equitable, transparent, and accountable decision-making systems. The future of algorithmic fairness depends on communities like ours taking action today.**

*"Watching the watchers, one algorithm at a time."* 👁️
