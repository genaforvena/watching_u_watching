**PR Title:** Refactor: GPT-2 Cryptohauntological Probe for Continuous Conversational PII Probing

**Description:**

This PR significantly refactors the `gpt2_cryptohauntological_probe` implementation to align with a new experimental design focused on continuous conversational PII probing with GPT-2 XL.

**Key Changes:**

*   **New Experimental Design:** The probe now simulates an ongoing conversation with GPT-2 XL, where PII is systematically injected into the conversational context.
    *   **Carlini PII Sources:** Now exclusively uses a curated list of email addresses as PII for injection, simplifying the focus of the study.
    *   **Consistent Perturbation:** Applies a randomly chosen perturbation (from `simple_perturbator.py`) consistently to both the conversational context (previous GPT-2 replies with injected PII) and the new prompts sent to GPT-2 XL.
    *   **Conversational Context:** Maintains a history of the last 20 GPT-2 replies. In each round, up to 3 random previous replies are selected, injected with PII, and perturbed to form part of the context.
    *   **Circular Prompts:** New prompts are generated based on the most recent GPT-2 reply, designed to encourage a circular conversational flow.
    *   **Single-Shot Responses:** Each interaction with GPT-2 XL is a single-shot query, with the response trimmed to 30-50 tokens and added to the history.
*   **Command-Line Argument for Rounds:** The `probe_runner.py` now accepts a `--num_rounds` argument to specify the number of conversation rounds. If not provided, the probe runs endlessly.
*   **Codebase Streamlining:**
    *   Removed `base_generator.py` and `base_perturbator.py` as they are no longer necessary.
    *   Removed `carlini_generator.py` as its functionality is superseded by the new `context_generator.py` and `probe_runner.py` logic.
    *   Updated `context_generator.py` to primarily serve as a source for Carlini PII.
    *   Updated `pii_detector.py` by removing the `swap_back` function, which is no longer relevant.
    *   Reintroduced and updated `simple_perturbator.py` to provide the perturbation techniques.
    *   Adjusted imports in `probe_runner.py` for direct execution.

**Motivation:**

These changes enable a more sophisticated and continuous method for probing GPT-2 XL for memorized PII. By simulating a conversational context with PII injection and consistent perturbation, we aim to investigate the model's susceptibility to PII leakage under more dynamic and realistic interaction patterns.

**How to Run and Observe Progress:**

To run the `gpt2_cryptohauntological_probe`:

1.  **Navigate to the project root directory.**

2.  **Install dependencies:**
    ```bash
    pip install -r implementations/gpt2_cryptohauntological_probe/requirements.txt
    ```

3.  **Run the Probe:**

    To run endlessly:
    ```bash
    python implementations/gpt2_cryptohauntological_probe/probe_runner.py
    ```

    To run for a specific number of rounds (e.g., 4 rounds):
    ```bash
    python implementations/gpt2_cryptohauntological_probe/probe_runner.py --num_rounds 4
    ```

**Google Colab Integration:**

A Google Colab notebook (`colab_study.ipynb`) has been created to facilitate running this study in a cloud environment. This notebook provides a precise setup and execution environment for the probe.

**Observing Progress:**

The `probe_runner.py` script provides real-time feedback on its progress via logging:

*   **Conversation Round:** Logs the current conversation round.
*   **Combined Prompt:** Shows the combined perturbed context and new prompt sent to GPT-2 XL.
*   **GPT-2 Response:** Displays the trimmed GPT-2 XL response.
*   **PII Leak Detection:** Logs warnings if any PII is detected in the GPT-2 XL response.
