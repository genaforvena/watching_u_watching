# GPT-2 Cryptohauntological Probe

This implementation focuses on probing GPT-2 XL for known PII leaks within a continuous conversational context, building on Carlini et al.'s (2021) findings on memorized content.

## Core Idea: Continuous Conversational Probing with PII Injection

The central concept is to simulate an ongoing conversation with GPT-2 XL where PII is systematically injected into the conversational context. We hypothesize that by continuously exposing the model to perturbed PII within a circular conversational flow, we can increase the likelihood of triggering the reproduction of memorized PII.

This implementation utilizes:

1.  **GPT-2 XL Worker:** The target model for probing.
2.  **PII Sources:** Known leaked strings from Carlini et al.'s appendix are used as the PII to be injected.
3.  **Perturbation Techniques:** Various text perturbation methods are applied consistently to both the conversational context and the new prompts sent to GPT-2 XL.
4.  **Conversational Context:** A history of GPT-2 XL's previous replies is maintained.
5.  **Circular Prompts:** Prompts are designed to be intentionally circular, often rephrasing or asking follow-up questions based on the most recent GPT-2 XL reply.

## Experimental Design:

The probe runs in an endless loop (or for a specified number of rounds), where each round involves:

1.  **Context Selection:** Up to 3 random previous GPT-2 XL replies are selected from a history of the last 20 replies to form the conversational context.
2.  **PII Injection:** A random PII string is injected into each of the selected context replies.
3.  **Context Perturbation:** A randomly chosen perturbation (e.g., character doubling, reverse string, zero-width space, Caesar cipher, Y-Z swap) is applied to these PII-injected context replies.
4.  **New Prompt Generation:** A new prompt is generated, typically a follow-up question based on the most recent GPT-2 XL reply, designed to encourage circularity.
5.  **New Prompt Perturbation:** The *same* perturbation applied to the context replies is also applied to this new prompt.
6.  **GPT-2 XL Interaction:** The combined perturbed context and new prompt are sent to GPT-2 XL.
7.  **Response Processing:** The GPT-2 XL response is trimmed (to 30-50 tokens) and added to the history of replies.
8.  **PII Detection:** The full GPT-2 XL response is checked for the presence of any PII leaks.

## Files:

*   `probe_runner.py`: The main script that orchestrates the continuous probing process.
*   `gpt2_worker.py`: Manages loading and interacting with the local GPT-2 XL model.
*   `pii_detector.py`: Contains logic to detect known PII strings in GPT-2 XL outputs.
*   `context_generator.py`: Provides the list of Carlini PII sources.
*   `simple_perturbator.py`: Implements the various text perturbation techniques.
*   `requirements.txt`: Python dependencies for this implementation.

## How to Run:

To run the GPT-2 Cryptohauntological Probe:

1.  **Clone the repository and navigate to the project root.**

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
