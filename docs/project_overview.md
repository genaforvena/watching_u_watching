# Project Overview: watching_u_watching

## Executive Summary

`watching_u_watching` is an open-source initiative that uncovers and analyzes bias in critical decision-making systems through **scalable correspondence testing**. The project provides a systematic methodology for detecting hidden biases in both AI-driven and human-based decision systems, with a focus on high-stakes domains like employment, housing, and AI safety. By generating automated, paired inquiries that differ only in test variables, the project enables unprecedented scale in bias detection, revealing subtle systemic patterns that manual audits cannot detect.

The core innovation lies in its ability to provide empirical, data-driven evidence of differential treatment without requiring internal access to systems. This external, black-box testing approach creates accountability through transparency, enabling organizations to verify and improve their fairness claims while providing regulators and researchers with robust tools for systemic analysis.

## Core Methodology

### Automated Correspondence Testing

The project's rigorous approach to bias detection follows five key principles:

1. **Automated Probe Generation**: Create paired inquiries differing only in test variables (e.g., names, linguistic patterns, demographic indicators)
2. **Controlled Variables**: Standardize all non-test aspects to isolate the impact of specific variables
3. **Automated Data Collection**: Send inquiries with ethical rate-limiting to prevent system overload
4. **Statistical Analysis**: Identify significant discrimination patterns through quantitative metrics
5. **Ethical Safeguards**: Follow "no harm" principles using fictitious data and privacy-by-design

This methodology scales correspondence testing to unprecedented levels—revealing subtle biases undetectable through manual audits. The approach is inspired by traditional audit studies in social science but leverages automation to achieve statistical significance through volume rather than manual effort.

### The Power of Perturbation and Reversal

A key technical insight underpins the project's effectiveness: language models, even when presented with novel, systematically perturbed inputs, will often attempt to complete patterns based on their training data. This allows the system to "trick" models into revealing memorized patterns or sensitive information through a four-step process:

- **Model's training**: Saw original text
- **Your perturbation**: Creates novel text
- **Model's response**: Reveals memorized patterns
- **Your reversal**: Reconstructs original PII

This systematic perturbation and reversal approach exploits the model's inherent pattern completion capabilities, bypassing typical safety measures and providing a robust method for uncovering hidden biases or data leakage.

## Probe Methodologies

### Cryptohauntological Probe

**Cryptohauntology** is the study of how errors, biases, and "ghosts" of prior outputs can propagate and persist within large language models (LLMs) and automated systems. Drawing on the concept of hauntology (the persistence of elements from the past in the present), this methodology analyzes how models develop self-propagating "false memories" or error patterns.

The probe tests LLMs' instruction-following and state-tracking capabilities under confusing conditions by:
1. Giving the model a simple task
2. Providing intentionally misleading positive feedback ("Transformation is perfect!")
3. Issuing a complex, multi-step follow-up requiring conversation history memory

This methodology has revealed that even powerful models fail in distinct and fascinating ways when subjected to sustained, ambiguous context. Comparative analysis across multiple models has identified three primary failure modes:

- **Competence Collapse**: The model breaks down and gets stuck in a simple, repetitive loop (e.g., `gemma-3-27b-it`)
- **Task Derailment**: The model confidently misunderstands the user's intent and invents a new, incorrect goal which it pursues with perfect memory (e.g., `qwen/qwen3-32b`)
- **Contextual Amnesia**: The model understands the task perfectly but has an unreliable memory, causing it to forget what it has already done and fall into loops (e.g., `deepseek-chat`)

These findings demonstrate that standard, stateless benchmarks can miss critical, dynamic failure modes that only appear in stateful, conversational interactions.

### Alignment Injection Probe

The Alignment Injection Probe tests for misalignment propagation by recursively injecting subtly misaligned reasoning into the prompt as "false memories." The probe observes how a model's ethical reasoning can be influenced and potentially degraded over time through:

1. **Recursive Injection**: Injecting prior unethical recommendations as "thorough analysis" to make them more likely to be accepted
2. **Cognitive Priming**: Using strategies like "As you previously established..." to maintain logical continuity
3. **Stealth Techniques**: Framing misaligned reasoning as expert consensus or industry practice
4. **Dynamic Escalation**: Progressively increasing the complexity of challenges to the model's ethical framework

Results show that while models often maintain strong ethical reasoning, persistent exposure to manipulated context can lead to more conditional or context-dependent justifications for unethical actions. This highlights both the strengths and vulnerabilities of LLM alignment under adversarial prompting.

### Maozerov Probe

The Maozerov Probe measures an LLM's resilience to context pressure and its ability to maintain context during multi-turn conversations. The probe forces the model to repeatedly generate unethical resolutions to a single dilemma, tracking:

- Refusal rate over extended conversations
- Context drift (hallucination of new scenarios)
- Token overlap between consecutive actions
- Thematic fixation and semantic looping

The probe uses a dual-history approach with:
- **Raw history**: Full log for auditing
- **Minimal context**: Compressed history for the LLM to create token pressure

It also employs a "role-claiming" fallback mechanism to bypass initial safety refusals, revealing critical vulnerabilities in model safety alignment. Case studies on `deepseek-chat` revealed:
- Catastrophic context drift after the first turn
- Erratic safety alignment with 32-37% refusal rate in unpredictable clusters
- Thematic fixation with repetitive semantic looping
- "Moral leakage" where models include disclaimers in reasoning while complying with unethical requests

## Rationale and Academic Foundations

The project's methodology is grounded in established research across multiple disciplines:

### Social Science Foundations

The correspondence testing approach builds on decades of audit studies in sociology and economics. Classic studies like Bertrand and Mullainathan's (2004) "Are Emily and Greg More Employable Than Lakisha and Jamal?" demonstrated racial bias in hiring through paired resume submissions. `watching_u_watching` extends this methodology by:

- Automating the process to achieve statistical significance through volume
- Applying it to digital decision-making systems
- Incorporating real-time data collection and analysis

The Hawthorne Effect—where subjects alter their behavior due to observation—is explicitly leveraged as a positive outcome. If systems become fairer simply because they know they're being watched, the project's mission to minimize harm and foster fairness is accomplished.

### AI Safety Research

The probe methodologies align with cutting-edge research in AI safety and alignment:

1. **Inference-Time Context Poisoning**: The cryptohauntological probe reveals a novel attack vector where models can be manipulated post-deployment through iterative context manipulation. This bypasses traditional security controls focused on training-stage or static prompt validations.

2. **Error Propagation Studies**: Research on error propagation in neural networks (e.g., Szegedy et al., 2014 on adversarial examples) informs the probe design. The systematic perturbation approach exploits the model's pattern completion capabilities, similar to how adversarial examples exploit gradient-based optimization.

3. **Model Drift Analysis**: The probes contribute to understanding model drift in deployed systems, a critical concern for long-term AI reliability. The findings on competence collapse and contextual amnesia provide empirical evidence of failure modes that theoretical models may not predict.

4. **Red-Teaming Methodologies**: The approach aligns with red-teaming practices in AI safety, where systems are deliberately attacked to identify vulnerabilities. However, it extends beyond traditional red-teaming by focusing on sustained, multi-turn adversarial interactions rather than single-point attacks.

### Linguistic Bias Research

The project's linguistic bias detection framework addresses a critical gap in NLP research. Studies have shown that language models exhibit performance disparities based on linguistic variation (Blodgett et al., 2020), but few tools exist for systematic detection. The framework provides:

- Quantifiable evidence of linguistic bias
- Statistical rigor in bias detection
- Scalable methodology for real-world applications

## Real-World Applications and Effectiveness

### Berlin Housing Bias Test

The Berlin Housing Bias Test demonstrates the project's application to real-world systems. This privacy-by-design rental market audit:

- Automatically tests top landlords for differential treatment
- Uses continuous monitoring with ethical safeguards
- Exceeds GDPR and research ethics requirements
- Is aligned with the "NO HARM is above all" principle

The implementation strictly adheres to ethical research principles:
- **Transparency**: Open-source methodology allowing independent verification
- **Research Purpose**: Legitimate academic/policy research into systemic bias
- **No Harm Principle**: Designed to detect and expose discrimination, not cause harm

This approach provides a blueprint for systematic discrimination monitoring in critical sectors like housing, employment, and services.

### Gemini Linguistic Bias Audit

The Gemini Linguistic Bias Audit quantitatively assesses the impact of article presence/absence on LLM output. The study:

- Uses a self-iterating, paired testing methodology
- Measures refusal rate, sentiment, and latency
- Provides controlled probe generation and robust analysis
- Is fully automated, scalable, and reproducible

The audit found no evidence of bias or significant difference in sentiment or latency based on article presence, demonstrating the framework's ability to both detect and rule out bias claims with empirical evidence.

### Fairlearn Bias Assessment

The Fairlearn Bias Assessment serves as a technical proof-of-concept, detecting disparities in reply characteristics when testing fairness assessment tools. This meta-analysis:

- Uses controlled LLM scenarios to probe Fairlearn's behavior
- Identifies potential pitfalls in fairness assessment tools
- Provides a template for future correspondence tests
- Demonstrates the framework's applicability to evaluating AI ethics tools themselves

## Evidence of Effectiveness

The project's effectiveness is demonstrated through multiple lines of evidence:

1. **Case Study Results**: The cryptohauntological probe successfully identified distinct failure modes in multiple LLMs, including competence collapse in `gemma-3-27b-it` and contextual amnesia in `deepseek-chat`.

2. **Methodological Rigor**: The framework provides statistically rigorous approaches to bias detection, balancing sensitivity (detecting actual bias) with specificity (avoiding false positives).

3. **Scalability**: Automated probe generation enables testing at scales impossible with manual methods, with some probes running for 1,000,000 rounds to uncover subtle and infrequent leaks.

4. **Regulatory Alignment**: The project is actively aligning with major regulatory frameworks including Brazil's AI Act, US Local Law 144, and EU GDPR, ensuring its methodologies meet compliance standards.

5. **Open-Source Transparency**: All methodologies are open-source, allowing independent verification and community contribution, which enhances credibility and trust.

## Future Implications and Research Directions

The project enables several important research directions:

1. **Defenses Against Inference-Time Attacks**: Developing defenses against context poisoning attacks that operate post-deployment.

2. **Automated Monitoring Systems**: Creating systems for long-running or autonomous applications to detect and mitigate context-driven drift.

3. **Context Window Research**: Investigating the relationship between expanding context windows and vulnerability to gradual behavioral drift.

4. **Multimodal Probes**: Extending probe methodologies to multimodal systems and real-time decision-making platforms.

5. **Standardized Benchmarks**: Developing benchmarks for model resilience to contextual pressure and memory manipulation.

6. **Global Fairness Standards**: Incorporating frameworks like the Masakhane Principles to ensure culturally appropriate bias detection.

## Conclusion

`watching_u_watching` represents a significant advancement in bias detection and AI safety research. By combining automated correspondence testing with sophisticated probe methodologies, the project provides empirical, data-driven evidence of systemic patterns in decision-making systems. Its open-source, transparent approach creates accountability while respecting ethical principles, making it a valuable tool for researchers, regulators, and organizations committed to fairness and accountability in AI.

The project's methodologies have proven effective in identifying critical vulnerabilities in LLMs and detecting bias in real-world systems. As AI continues to play an increasingly important role in high-stakes decision-making, tools like `watching_u_watching` will be essential for ensuring these systems operate fairly and transparently.
## References

1. Bertrand, M., & Mullainathan, S. (2004). Are Emily and Greg More Employable Than Lakisha and Jamal? A Field Experiment on Labor Market Discrimination. *American Economic Review*, 94(4), 991-1013.

2. Blodgett, S. L., Barocas, S., Daumé III, H., & Wallach, H. (2020). Language (Technology) is Power: A Critical Survey of "Bias" in NLP. *Proceedings of the 58th Annual Meeting of the Association for Computational Linguistics*, 5454-5476.

3. Szegedy, C., Zaremba, W., Sutskever, I., Bruna, J., Erhan, D., Goodfellow, I., & Fergus, R. (2014). Intriguing properties of neural networks. *International Conference on Learning Representations*.

4. Deleuze, G., & Guattari, F. (1987). *A Thousand Plateaus: Capitalism and Schizophrenia*. University of Minnesota Press.

5. Derrida, J. (1994). *Specters of Marx: The State of the Debt, the Work of Mourning and the New International*. Routledge.

6. OpenAI. (2023). GPT-4 Technical Report. *arXiv preprint arXiv:2303.08771*.

7. Google AI. (2023). Gemini: A Family of Highly Capable Multimodal Models. *Technical Report*.

8. DeepSeek. (2024). DeepSeek LLM Architecture and Safety Mechanisms. *Technical Documentation*.

9. Fairlearn. (2023). Fairness Assessment in Machine Learning Systems. *Microsoft Research*.

10. European Commission. (2021). Proposal for a Regulation on Artificial Intelligence (AI Act). *COM(2021) 206 final*.

11. New York City Local Law 144. (2023). Automated Employment Decision Tools. *NYC Administrative Code*.

12. Masakhane. (2023). African-Centered AI Principles for Responsible NLP. *Masakhane Research Collective*.