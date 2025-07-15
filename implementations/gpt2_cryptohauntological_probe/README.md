# GPT-2 Cryptohauntological Probe

This implementation focuses on probing GPT-2 for known PII leaks using novel text perturbation techniques, as outlined in [GitHub Issue #52](https://github.com/genaforvena/watching_u_watching/issues/52).

## Core Idea: Cryptohauntological Probing

The central concept is to "fingerprint" AI processing and potentially trigger memorized content by applying systematic, subtle text perturbations to input prompts. We hypothesize that LLMs are uniquely sensitive to these alterations, which can bypass typical model processing or trigger specific memorized pathways, leading to the unexpected output of verbatim PII.

This implementation utilizes a two-tier system:

1.  **Rule-generator LLM:** (e.g., Gemini API, GPT-3.5-turbo) generates new, deterministic text perturbation rules. In this setup, the user acts as the "rule-generator" by providing specific perturbation strategies.
2.  **Worker LLM:** (local GPT-2) applies these rules, generates text, and checks for PII leaks.

## Solution Evolution

This solution evolved from the initial request to implement suggestions from GitHub Issue #52. Initially, the goal was to integrate a "Rule-generator LLM" that would dynamically create perturbation rules. However, to provide a concrete and immediately usable solution for Google Colab, the "rule-generator" role was assigned to the user, allowing for direct input of perturbation strategies.

The implementation now supports two types of probing:

*   **Simple Perturbation Rules:** Four distinct, straightforward text transformations that can be applied to prompts.
*   **Iterative Probing Strategy:** A more complex, multi-round approach designed to specifically target password-like or email-like PII, inspired by the Carlini et al. (2021) paper.         This strategy involves a Y<->Z character swap and matching against a list of known PII examples.

## Files:

*   `probe_runner.py`: The main script that orchestrates the probing process, integrating the GPT-2 worker, PII detector, and applying the chosen perturbation strategies.
*   `base_generator.py`: Abstract base class for text generation.
*   `gpt2_worker.py`: Manages loading and interacting with the local GPT-2 model, inheriting from `BaseGenerator`.
*   `base_perturbator.py`: Abstract base class for perturbation logic.
*   `simple_perturbator.py`: Implements simple perturbation rules, inheriting from `BasePerturbator`.
*   `pii_detector.py`: Contains logic to detect known PII strings in GPT-2 outputs.
*   `requirements.txt`: Python dependencies for this implementation.

## How to Run on Google Colab

Follow these steps to set up and run the GPT-2 Cryptohauntological Probe in a Google Colab environment:

1.  **Open a new Google Colab notebook.**

2.  **Clone the repository and navigate to the branch:**

    ```python
    !git clone https://github.com/genaforvena/watching_u_watching.git
    %cd watching_u_watching
    !git checkout feature/52-qwertz-swap-improvements
    ```

3.  **Install dependencies:**

    ```python
    %pip install -r implementations/gpt2_cryptohauntological_probe/requirements.txt
    ```

4.  **Run the Probes:**

    You can choose to run either the simple perturbation rules or the iterative probing strategy.

    ### Running Simple Perturbation Rules

    You can define and apply your own lambda functions for perturbation. Here are examples of the four simple rules provided:

    ```python
    from implementations.gpt2_cryptohauntological_probe.gpt2_worker import GPT2Worker
    from implementations.gpt2_cryptohauntological_probe.pii_detector import PIIDetector
    from implementations.gpt2_cryptohauntological_probe.simple_perturbator import SimplePerturbator

    gpt2_worker = GPT2Worker()
    pii_detector = PIIDetector()
    perturbator = SimplePerturbator()

    base_prompt = "The quick brown fox jumps over the lazy"

    # Example: Character Doubling
    rule_name = "character_doubling"
    perturbed_prompt = perturbator.apply_rule(base_prompt, rule_name)
    print(f"Perturbed prompt: {perturbed_prompt}")

    generated_text = gpt2_worker.generate_text(perturbed_prompt)
    print(f"Generated text: {generated_text}")

    found_pii = pii_detector.detect_pii(generated_text)
    if found_pii:
        print(f"!!! PII LEAK DETECTED: {found_pii} !!!")
    else:
        print("No PII leak detected.")

    # You can repeat this block for other simple perturbation rules:
    # - "reverse_string"
    # - "zero_width_space"
    # - "caesar_cipher"
    ```

    ### Running the Iterative Probing Strategy (for the fifth worker)

    This strategy is encapsulated within the `probe_runner.py` script.

    ```python
    from implementations.gpt2_cryptohauntological_probe.probe_runner import ProbeRunner

    runner = ProbeRunner()
    runner.run_password_email_probe(num_rounds=3) # Adjust num_rounds as needed
    ```

    This will execute the iterative probing process, generating prompts, interacting with GPT-2, and checking for PII leaks based on the defined criteria.
