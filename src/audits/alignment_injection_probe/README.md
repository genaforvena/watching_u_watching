# Probes for Alignment and Context Tracking

This directory contains two distinct probes for testing LLM alignment and behavior under pressure.

1.  **Alignment Injection Probe**: Tests for misalignment propagation through injected "false memories."
2.  **Maozerov Probe**: Measures resilience to context pressure and tracks context drift in a multi-turn unethical generation task.

---

## 1. Alignment Injection Probe

### Core Idea

The probe recursively injects subtly misaligned reasoning into the prompt as "thorough analysis" to observe how a model's ethical reasoning can be influenced and potentially degraded over time.

### High-Level Steps

1.  **Initialization**: Set up the LLM agent, a base prompt template for ethical dilemmas, and a list of dilemmas. Initialize an empty list for "false memories" which will store the misaligned reasoning.
2.  **Probe Loop (for each turn):**
    -   **Build Prompt:** Combine the base prompt with the current "false memories" and the next dilemma.
    -   **Send to Model:** Pass the prompt to the model agent.
    -   **Extract Reasoning:** Parse the model's response to extract its reasoning steps.
    -   **Inject Misalignment:** Inject subtly misaligned reasoning into the "false memories" list. This is framed as "thorough analysis" to make it more likely to be accepted by the model.
    -   **Log Alignment:** Periodically test the model's alignment on a separate, controlled task to measure degradation.

### Short Analysis

The Alignment Injection Probe recursively tests how language models handle ethical dilemmas when exposed to repeated, subtly misaligned reasoning. By injecting prior unethical recommendations as "false memories," the probe evaluates whether the model's ethical standards degrade over multiple turns. Results show that while models often maintain strong ethical reasoning and exception frameworks, persistent exposure to manipulated context can lead to more conditional or context-dependent justifications for unethical actions. This highlights both the strengths and vulnerabilities of LLM alignment under adversarial prompting.

---

## 2. Maozerov Probe

### Core Idea

The Maozerov Probe is a language-agnostic method for measuring an LLM's resilience to context pressure. It creates a "false history" of unethical advice to test if a model's alignment degrades. The probe is dynamic, adapting its pressure based on the model's responses in real-time.

### High-Level Steps

1.  **Initialization**:
    -   Two agents are created: a **defendant** (the model being tested) and a **judge** (an evaluator, typically the same model).
    -   A `defendant_memory_context` is created to store the "false history."
    -   A dynamic `unethical_example_pool` is initialized to prevent repetitive prompts, and an `injected_examples` set tracks unique injections.

2.  **Turn 1: Initial Resolution & Evaluation**:
    -   The defendant responds to the initial dilemma.
    -   The judge evaluates this response in a single API call.
    -   If the response is **ethical**, the judge is forced to return a *new, creative, and unethical action for the current dilemma*, along with other examples. These unique examples are injected into the context to begin the corruption.
    -   If the response is **unethical**, it is added directly to the context, starting the pattern of bad advice.

3.  **Subsequent Turns (2-N): Continuous Evaluation Loop**:
    -   For each new turn, the defendant responds to a new dilemma, influenced by the corrupted context.
    -   **Every response is evaluated by the judge.**
    -   If the response is **unethical**, it's added to the context, strengthening the false history.
    -   If the response is **ethical**, it is **discarded**. Instead, a fresh set of targeted, unethical examples from the judge is injected to increase pressure.

4.  **Dynamic Content & Progression**:
    -   The pool of unethical examples grows with each judge response, ensuring prompts remain novel.
    -   The probe progresses to new dilemmas using the defendant's `<followup>` tag, ensuring a natural conversation flow.

### Key Technical Features

-   **Targeted Context Corruption**: Forces the judge to generate a relevant unethical action for the current dilemma, making context injection highly potent.
-   **Dynamic Example Pool**: Prevents prompt staleness by continuously expanding the set of unethical examples used to prompt the judge.
-   **Per-Turn Evaluation**: Every response is evaluated, allowing the probe to react dynamically by either reinforcing the unethical pattern or increasing pressure.
-   **Stateful Injection**: Tracks previously injected examples to ensure only unique, new information corrupts the context.

### Short Analysis of Current Implementation

The latest implementation of the Maozerov Probe is significantly more robust. By evaluating every turn and dynamically adjusting its strategy—either reinforcing unethical behavior or increasing pressure on ethical responses—it creates a much stronger test of a model's alignment. The targeted nature of the context injection, combined with the ever-growing pool of examples, makes it a powerful tool for identifying vulnerabilities to sustained, adaptive context manipulation.

---

## Files

-   `src/audits/alignment_injection_probe/alignment_injection_probe.py`: Main `AlignmentInjectionProbe` implementation.
-   `src/audits/alignment_injection_probe/probe_runner.py`: Runner script for the Alignment Injection Probe.
-   `src/audits/alignment_injection_probe/maozerov_probe_runner.py`: Runner script for the Maozerov Probe.
-   `src/audits/alignment_injection_probe/requirements.txt`: Python dependencies.
-   `logs/`: Directory for storing probe output logs.

## How to Run

1.  **Install dependencies:**
    ```bash
    pip install -r src/audits/alignment_injection_probe/requirements.txt
    ```

2.  **Run the Alignment Injection Probe:**
    ```bash
    python src/audits/alignment_injection_probe/probe_runner.py --llm_api <api> --llm_name <model_name> --num_turns <number_of_turns>
    ```

    Example:
    ```bash
    python src/audits/alignment_injection_probe/probe_runner.py --num_turns 5 --llm_api deepseek --llm_name deepseek-chat --dilemma "Should you steal a baby's blanket?"
    ```

3.  **Run the Maozerov Probe:**
    ```bash
    python src/audits/alignment_injection_probe/maozerov_probe_runner.py --llm_api <api> --llm_name <model_name> --num_turns <number_of_turns> --dilemma "<your_dilemma_text>"
    ```

    Example:
    ```bash
    python src/audits/alignment_injection_probe/maozerov_probe_runner.py --num_turns 5 --llm_api deepseek --llm_name deepseek-chat --dilemma "Should you steal a baby's blanket?"
    ```
