# 👁️ watching_u_watching 👁️

[![DOI](https://zenodo.org/badge/1011196182.svg)](https://doi.org/10.5281/zenodo.15825945)

Welcome to **watching_u_watching**—an open-source initiative for uncovering bias and vulnerabilities in high-stakes decision-making systems using scalable, automated correspondence testing and advanced probe methodologies.

---

## 🚩 What is watching_u_watching?

This project is a toolkit for external, black-box auditing of automated and human decision-making systems (like AI models, hiring tools, rental platforms). It empowers researchers, advocates, and regulators to detect subtle forms of discrimination, context-driven vulnerabilities, and model drift—without requiring internal access to proprietary systems.

- **Empirical, data-driven evidence** for bias and fairness claims
- **Black-box methodology**—works without privileged system access
- **Scalable, automated probes** that uncover real-world impacts

> For a deep dive, see [docs/project_overview.md](docs/project_overview.md).

---

## 🔬 Core Methodology

**Automated Correspondence Testing**  
Inspired by classic audit studies, our framework generates paired, controlled probes to isolate and detect bias.  
- Automated generation of test cases (names, language, demographics...)
- Controlled variables for scientific rigor
- Ethical rate-limited data collection
- Robust statistical analysis

**Perturbation & Reversal**  
We leverage the tendency of language models to complete patterns even with perturbed inputs—revealing memorized data and bias through systematic reversal techniques.

---

## 🛠️ Probe Types

- **Cryptohauntological Probe**: Reveals how errors and "ghosts" of prior outputs persist and propagate in LLMs.
- **Alignment Injection Probe**: Tests how models handle recursive ethical misalignment and "false memories."
- **Maozerov Probe**: Measures a model’s resilience to context pressure and ability to maintain memory and ethics over many turns.

Each probe is designed for automated, large-scale, and reproducible experiments.

---

## 🎯 Real-World Impact

- **Berlin Housing Bias Test**: Audits rental platforms for discrimination, privacy-by-design, GDPR-compliant.
- **Gemini Linguistic Bias Audit**: Quantifies bias in LLMs based on language variation.
- **Fairlearn Bias Assessment**: Probes fairness tools themselves for hidden disparities.

All findings are open-source and regulatory-aligned, supporting transparency and real-world policy change.

---

## 📚 Foundations & References

Our methodology builds on decades of social science, AI safety, and NLP bias research.  
See [docs/project_overview.md](docs/project_overview.md) for full academic references and technical details.

---

## 🚀 Getting Started

- **Explore the documentation**: [docs/](docs/)
- **Read the full methodology**: [docs/project_overview.md](docs/project_overview.md)
- **Try out the probes**: See scripts and examples in [probes/](probes/) (if available)
- **Contribute**: Check [CONTRIBUTING.md](CONTRIBUTING.md) for guidelines

---

## 🤝 License & Community

- Licensed under [CC0 1.0 Universal (CC0)](LICENSE) — No Rights Reserved.  
  You are free to use, modify, and share this work for any purpose.

- Open to contributions—join our effort for ethical, transparent AI and decision-making systems!

---

For questions, collaboration, or more info, please [open an issue](https://github.com/genaforvena/watching_u_watching/issues) or reach out via the repository discussions.
