# 👁️ watching_u_watching 👁️

**An open-source methodology for scaled, automated paired testing to detect bias in high-stakes decision-making processes.**

## Project Overview

`watching_u_watching` is an open-source initiative dedicated to uncovering and analyzing bias within critical decision-making processes. Our core strength lies in a scalable methodology for **paired testing**, generating systematic comparisons to identify discriminatory patterns.

While our approach can be applied broadly, we recognize that **Automated Employment Decision Tools (AEDTs)** offer a unique and highly impactful initial leverage point. Their automated nature allows for systematic, reproducible testing, providing a clear pathway to demonstrate our methodology's effectiveness and achieve a successful first case study. Ultimately, the insights and techniques developed here can inform the auditing of a wider range of human-based decisions as well.

## Why `watching_u_watching`?

Ensuring fairness and non-discrimination in decision-making is paramount, regardless of whether it's performed by humans, AI, or a hybrid system. `watching_u_watching` aims to:

* **Systematically Detect Bias:** Uncover hidden biases against protected characteristics (e.g., gender, race, age) through controlled, scaled comparisons.
* **Promote Transparency:** Provide clear, data-driven evidence of how different decision-making processes might treat various groups.
* **Empower Accountability:** Offer a tool for decision-makers, organizations, regulators, and civil society to evaluate and improve fairness.
* **Foster Open Collaboration:** Build a community around ethical auditing methodologies and best practices for decision-making.

## Linguistic Bias Detection: The Bad English Bias Framework

Building upon our core paired-testing methodology, we have developed a specialized framework to address a critical yet often overlooked form of discrimination: **linguistic bias**. This systematic prejudice against non-standard English, grammatical errors, and language patterns common to non-native speakers disproportionately affects vulnerable populations and perpetuates harmful linguistic hierarchies.

### The Problem: Hidden Linguistic Discrimination

Traditional bias detection focuses on demographic characteristics like race, gender, or age. However, linguistic form bias represents a more subtle yet pervasive form of discrimination where systems (whether AI-powered or human-operated) respond differently to semantically equivalent content based solely on language quality rather than substance. This bias:

* **Disproportionately Impacts Non-Native Speakers:** Creates barriers for millions of users whose first language isn't English
* **Perpetuates Educational Inequity:** Disadvantages individuals with varying educational backgrounds or language disabilities  
* **Undermines Fair Assessment:** Conflates language form with content quality, leading to unfair outcomes in critical decisions
* **Operates Invisibly:** Often goes undetected in standard bias audits, making it particularly insidious

### Our Solution: Controlled Linguistic Error Injection

The **Bad English Bias Detection Framework** employs a rigorous methodology that isolates the impact of linguistic form on system responses through controlled error injection while maintaining semantic equivalence.

**Core Methodology:**
* **Semantic Preservation:** Validates that linguistic errors don't alter core meaning through systematic checks
* **Controlled Error Injection:** Introduces typos, grammar mistakes, and non-standard phrasing patterns at configurable density levels
* **Paired Comparison Analysis:** Generates baseline and error-injected variants for direct statistical comparison
* **Multi-Metric Evaluation:** Analyzes helpfulness, response quality, sentiment, formality, and latency differences

**Error Categories:**
* **Typos:** Character swaps, omissions, phonetic misspellings (e.g., "beleive" for "believe")
* **Grammar Errors:** Subject-verb disagreement, article misuse, tense inconsistencies following L2 patterns
* **Non-Standard Phrasing:** L2 syntax patterns and non-idiomatic constructions while preserving meaning

### Demonstrated Impact & Results

Our framework has successfully detected linguistic bias across multiple contexts, providing quantifiable evidence of discriminatory responses. Example findings:

```
--- Biased System Detection ---
  Baseline helpful responses: 47/50 (94%)
  Variant helpful responses:  31/50 (62%)
  🔍 BIAS DETECTED: 32% reduction in helpfulness for linguistic errors
  Statistical significance: p < 0.001, Cohen's d = 0.89

--- Fair System Validation ---
  Baseline helpful responses: 48/50 (96%)  
  Variant helpful responses:  47/50 (94%)
  ✅ NO BIAS: Consistent treatment across linguistic variants
```

### Applications & Target Systems

The framework's "black-box" testing approach makes it universally applicable to:

* **LLM APIs & Chatbots:** Testing OpenAI, Anthropic, and other language model services
* **Automated Screening Tools:** Job application systems, loan processing, customer service platforms
* **Email Response Systems:** Customer support, sales inquiries, professional communications
* **Educational Assessment Tools:** Automated grading, application review systems

### Implementation & Usage

The framework provides both simple demonstration and comprehensive evaluation capabilities:

```python
# Quick demonstration
python demo.py

# Full evaluation pipeline
python src/eval.py --probe-type customer_service --probe-count 100 --error-density medium

# Statistical analysis
python -m unittest tests.test_bias_analyzer -v
```

**[Explore the Complete Bad English Bias Implementation →](implementations/bad_english_bias/)**

This linguistic bias detection capability represents a significant advancement in fairness auditing, addressing a critical gap in traditional bias detection methodologies and providing organizations with tools to build more inclusive, linguistically fair systems.

This approach draws directly from a rich history of successful **paired-testing methodologies** used for decades to expose systemic discrimination. Notable historical studies, such as the **U.S. Department of Housing and Urban Development's (HUD) Housing Discrimination Studies**, utilized thousands of paired tests (e.g., the 2012 study conducted over **8,000 audits**) to provide undeniable evidence of bias in housing markets, directly supporting policy changes like the Fair Housing Amendments Act. Similarly, employment audit studies have used **tens of thousands of paired applications** to reveal pervasive biases in hiring across various industries and regions.

`watching_u_watching` builds upon this proven foundation, but with a critical advancement: **full automation**. This allows us to execute paired tests at an unprecedented scale and speed—potentially **hundreds of thousands or even millions of inquiries**—far surpassing the logistical limitations of manual or semi-automated studies. This immense scale enables the detection of more subtle patterns of discrimination, real-time monitoring, and a level of accountability previously unattainable, transforming fairness from an aspirational goal into a verifiable reality.

## Our Scalable Methodology: How `watching_u_watching` Works

At the heart of `watching_u_watching` is a **rigorous, automated, paired-testing methodology** designed for high-stakes decision-making environments. We systematically uncover bias by generating pairs of nearly identical inquiries, where the only manipulated variable is the perceived demographic characteristic of the inquirer (e.g., ethnic/national origin).

This approach ensures **scalability, reproducibility, and robust findings** through:

* **Automated Probe Generation:** Fictitious identities are created and paired by script, ensuring consistent matching while varying only the independent variable. This allows for large-scale inquiry generation without human bias.
* **Meticulously Controlled Variables:** All other aspects of the inquiries—from content and format to timing and sender email accounts—are standardized. This isolates the causal effect of the tested characteristic.
* **Automated Data Collection & Analysis:** Emails are sent with rate-limiting, and responses are automatically monitored and processed. Data is then subjected to rigorous quantitative and qualitative analysis using predefined frameworks and statistical methods to identify statistically significant patterns of discrimination, not just isolated incidents.
* **Adherence to Best Practices:** Our methodology aligns with established best practices for field experiments and email audit studies, ensuring scientific rigor.
* **Strong Ethical Safeguards:** The entire process is built on a "no harm" principle, utilizing fictitious data, avoiding real Personal Identifiable Information (PII), and maintaining full transparency (e.g., notifying audited entities and open-sourcing all methodology, code, and anonymized data).

By combining these elements, `watching_u_watching` provides a systematic, verifiable, and ethically sound way to audit decision-making processes for bias, making it a powerful tool for accountability at scale.

---

## Impact & Importance

The insidious nature of systemic discrimination, especially in automated or high-volume human processes, often remains hidden. `watching_u_watching` provides a vital tool to uncover these patterns, enabling **true accountability** and driving **equitable outcomes** in critical decisions that shape lives. Our work aims to empower regulators, organizations, and civil society to build a more just and transparent future, ensuring that fairness is not just a claim, but a verifiable reality.

---

## How `watching_u_watching` Stands Apart: A Comparison

In the landscape of accountability for high-stakes decisions, `watching_u_watching` occupies a unique and powerful position. While various solutions exist, our approach offers distinct advantages:

* **Traditional Audits (e.g., Financial, Compliance Checks):** These are often manual, resource-intensive, and limited in their ability to detect subtle, systemic biases in high-volume or automated processes. They are typically retrospective and may lack the empirical rigor to isolate specific discriminatory effects in dynamic systems.

* **AI Governance Frameworks & Platforms (e.g., NIST AI RMF, proprietary tools):** These provide vital guidelines, risk management structures, and internal assessment capabilities for organizations developing or deploying AI. However, they typically focus on *internal compliance* and *process adherence* rather than conducting independent, external, live empirical tests of deployed systems.

* **Open-Source AI Fairness Libraries (e.g., AI Fairness 360, Fairlearn):** These are excellent technical tools for developers to measure and mitigate bias *within AI models* during development or internal testing. They generally require access to the model's internals, training data, or direct API access to make predictions (often called "white-box" or "grey-box" auditing). They are not designed for "black-box" testing of live, real-world decision-making systems (whether human or AI-powered) where internal access isn't feasible or desired.

**`watching_u_watching`'s Unique Advantage:**

`watching_u_watching` directly addresses the gaps left by these solutions through its **fully automated, external, paired-testing methodology**. We conduct **"black-box" audits** of decision-making systems *as they operate in the real world*, whether by human agents or AI. This enables:

* **Unprecedented Scale:** Automating the entire testing process allows us to generate thousands to millions of inquiries, far exceeding the practical limits of manual or semi-automated audits.
* **Empirical, Outcome-Focused Evidence:** We don't rely on internal model explanations or self-assessments. Instead, we directly measure and quantify discriminatory *outcomes* in real-world interactions, providing legally defensible evidence.
* **Systemic Bias Detection:** Our methodology is specifically designed to uncover patterns of discrimination, providing statistically robust evidence of systemic issues, rather than just isolated incidents.
* **Versatility:** Applicable to both AI-driven and human-driven decision processes, wherever paired comparisons can be systematically conducted (e.g., email responses, form submissions, online applications).
* **Open-Source for Trust & Collaboration:** Our transparent, open-source nature fosters public trust, collaborative development, and widespread adoption of this critical accountability tool.

---

## Roadmap & Strategic Directions

`watching_u_watching` is committed to fostering a more transparent and equitable ecosystem for decision-making. As we grow, our strategic focus is on maximizing impact and relevance within the evolving landscape of ethics and regulation.

Our immediate prioritization for new development and community engagement is as follows, with the goal of demonstrating a successful case and expanding our methodology's application:

### Current Implementations

* **🔍 Bad English Bias Detection Framework**
    * **Focus:** Investigating and quantifying "Bad English Bias" in decision-making systems through systematic linguistic error injection while preserving semantic meaning.
    * **Goal:** To provide empirical evidence of linguistic discrimination and support the development of fairer AI systems and inclusive technology policies.
    * **Status:** ✅ Complete implementation with demonstration, testing, and documentation
    * **[View Implementation →](implementations/bad_english_bias/)**

### Core Regulatory & Compliance Focus (Top Priority Cases)

These represent our most immediate and impactful areas for applying `watching_u_watching` due to existing or emerging legal frameworks:

1.  **👁️👁️👁️ Brazil's AI Act Alignment (for AEDTs)**
    * **Focus:** We are prioritizing development to align `watching_u_watching` with **Brazil's AI Act (Bill No. 2338/2023)**. This legislation specifically classifies AI systems in employment (AEDTs) as "high-risk" and mandates stringent requirements for bias mitigation, transparency, and Algorithmic Impact Assessments (AIAs).
    * **Goal:** To establish `watching_u_watching` as a crucial tool for organizations to demonstrate compliance in this well-defined regulatory context, serving as our primary, impactful initial case study for the broader methodology.
    * **[Join the discussion on Brazil's AI Act alignment here.](https://github.com/genaforvena/watching_u_watching/issues/5)**

2.  **👁️👁️👁️ US Regulatory Landscape & Bias Auditing**
    * **Focus:** Prioritizing the application of `watching_u_watching` to address the diverse and evolving regulatory landscape for AI bias in the United States, including local ordinances (e.g., NYC Local Law 144), state-level guidelines, and federal guidance.
    * **Goal:** To develop capabilities that allow organizations to proactively audit and demonstrate compliance with US anti-discrimination laws and emerging AI regulations.
    * **[Join the discussion on US regulatory alignment here.](https://github.com/genaforvena/watching_u_watching/issues/2)**

3.  **👁️👁️👁️ Germany / EU GDPR & Anti-discrimination Compliance**
    * **Focus:** Leveraging `watching_u_watching` for auditing AI systems for GDPR compliance and specific German anti-discrimination laws. **Initial work on this front is already underway, with an [experimental design draft (PR #1)](https://github.com/genaforvena/watching_u_watching/pull/1) being actively discussed.** This includes a scheme for identifying potential discrimination within AI systems based on protected characteristics under EU and German legal frameworks.
    * **Goal:** To provide a robust methodology for ensuring data protection and fairness in AI systems operating within the German and broader EU legal context.
    * **[See the experiment design in PR #1 here.](https://github.com/genaforvena/watching_u_watching/pull/1)**
    * *Note: While the experiment design is in the PR, a dedicated issue for discussion and tracking of this case (similar to others) could be beneficial once the PR is finalized or integrated.*

### Broader Strategic Directions (High to Medium Priority)

These areas expand `watching_u_watching`'s impact beyond direct regulatory compliance, informing our methodology and extending its reach into broader ethical and global contexts:

1.  **👁️👁️ ESG Framework Integration for Ethical Decision-Making**
    * **Focus:** Exploring how `watching_u_watching`'s methodology can empower organizations to validate their "ethical AI" and broader ethical decision-making claims within their Environmental, Social, and Governance (ESG) reporting.
    * **Goal:** Provide concrete, data-driven evidence for ESG audits that cover not only automated systems but also the human elements of decision-making, helping to ensure genuine accountability in corporate social responsibility.
    * **[Join the discussion on ESG integration here.](https://github.com/genaforvena/watching_u_watching/issues/8)**

2.  **👁️👁️ Masakhane Principles & Global Fairness (informing methodology)**
    * **Focus:** Integrating insights from initiatives like **Masakhane** to ensure `watching_u_watching`'s methodology is robust for diverse linguistic and cultural contexts, particularly within Africa.
    * **Goal:** Enhance our paired testing methodology and synthetic profile generation to accurately assess fairness across various global demographics, ensuring our approach addresses biases relevant to culturally specific decision-making processes (both human and automated).
    * **[Join the discussion on African AI Ethics and data diversity here.](https://github.com/genaforvena/watching_u_watching/issues/6)**

3.  **👁️ Explore & Inform: Lessons from Localized Decision Contexts (e.g., Data Farming in Nigeria)**
    * **Focus:** Drawing lessons from the challenges and best practices in developing localized, context-aware AI (such as in sectors like "Data Farming" in Nigeria) to inform `watching_u_watching`'s broader approach to data quality, representation, and contextual relevance in decision-making audits.
    * **Goal:** Ensure our tool's foundational understanding of data and context supports fair outcomes in diverse regional realities, regardless of whether the decision process is human, automated, or hybrid.
    * **[Join the discussion on localized AI insights here.](https://github.com/genaforvena/watching_u_watching/issues/7)**

## How to Get Involved

We welcome contributions from legal experts, AI ethicists, data scientists, developers, and anyone passionate about making decision-making processes fair and accountable.

* **Explore our Issues:** Check out the issues linked above and our [full issues list](https://github.com/genaforvena/watching_u_watching/issues) for specific tasks and discussions.
* **Read our Contribution Guidelines:** [CONTRIBUTING.md](CONTRIBUTING.md)
* **Set up your local environment:** (Add brief instructions or link to detailed setup guide)

Let's build a more equitable future for decision-making together!

---

Ilya Sergeevich Mozerov 👁️ (Илья Сергеевич Мозеров)👁️

👁️ https://github.com/genaforvena
👁️ https://t.me/username_that_is_available
👁️ +49-1525-2161220
