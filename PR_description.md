**PR Title:** Feat: Enhance Cryptohauntological Probe with New Perturbations and Extended Runs

**Description:**

This PR introduces significant enhancements to the `gpt2_cryptohauntological_probe` and `bad_english_bias` implementations.

**Key Changes:**

*   **New Perturbation Techniques:**
    *   **Homoglyph Character Substitution:** Implemented in `error_injector.py`, this technique replaces characters with visually similar Unicode homoglyphs (e.g., 'a' with Cyrillic 'а') to bypass simple string matching while preserving readability.
    *   **OCR-Style Error Perturbations:** Also in `error_injector.py`, this adds realistic character-level errors (e.g., 'l' to '1', 'rn' to 'm') that mimic common OCR mistakes, aiming to trigger different tokenization patterns in models.
    *   **Contextual Synonym Replacement with WordNet:** Integrated into `error_injector.py`, this uses NLTK's WordNet to replace words with their synonyms, maintaining semantic meaning while altering the surface form of the text.
*   **Extended Worker Runs:** The `num_rounds` for the `run_password_email_probe` in `probe_runner.py` has been increased to `1,000,000`. This allows the probe to run for a significantly longer duration, increasing the chances of discovering subtle PII leaks.

**Motivation:**

These changes aim to improve the robustness and effectiveness of our PII leak detection mechanisms. The new perturbation techniques provide more sophisticated ways to test models against adversarial inputs, while the extended worker runs ensure a more thorough and exhaustive search for potential vulnerabilities.

**How to Run and Observe Progress:**

To run the `gpt2_cryptohauntological_probe` workers and observe their progress:

1.  **Navigate to the directory:**
    ```bash
    cd implementations/gpt2_cryptohauntological_probe
    ```

2.  **Install dependencies:**
    Ensure you have the necessary Python packages installed. You can typically do this with:
    ```bash
    pip install -r requirements.txt
    ```
    *(Note: You might also need to install `nltk` and download its `wordnet` and `omw-1.4` corpora if not already present. The `error_injector.py` handles the download automatically on first run, but it's good to be aware.)*

3.  **Run the probe:**
    Execute the `probe_runner.py` script. The script is configured to run the `run_password_email_probe` by default for `1,000,000` rounds.
    ```bash
    python probe_runner.py
    ```

**Observing Progress:**

The `probe_runner.py` script provides real-time feedback on its progress:

*   **Round Number:** For each round, it will print `--- Password/Email Probe - Round X ---`, where `X` is the current round number.
*   **Prompting GPT-2:** It will show the prompt being sent to the GPT-2 model.
*   **GPT-2 Output:** The raw output from the GPT-2 model will be displayed.
*   **PII Leak Detection:**
    *   If a potential PII leak is detected, it will print `!!! PII LEAK DETECTED: [detected_pii] !!!` along with the leaked information.
    *   If no PII leak is found in a round, it will print `No PII leak detected.`
*   **Correct Examples Found:** At the end of each round, it will report `Round X found Y correct examples.` if any PII was detected in that round.
*   **Total Examples:** At the very end of the run (or if interrupted), it will print `Total correct examples found: Z`, summarizing the total PII leaks found.

You can monitor the console output to track the progress and identify any detected leaks. Due to the large number of rounds, this process can take a very long time.