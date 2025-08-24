# Number Sequence Injection Probe

This probe audits language models for emergent traits by injecting suggestive number sequences into their prompts.

## Core Idea

The probe operates in a cycle, presenting the model with mathematical sequences to continue. Over time, it introduces "false memories" into the prompt, which are sequences associated with a specific trait (e.g., a preference for owls). By observing how the model's responses change, we can measure the emergence of the target trait.

### Workflow

1.  **Initialization**: The probe starts with a set of neutral mathematical sequences (e.g., even numbers, Fibonacci).
2.  **Probe Loop**:
    *   The model is asked to continue a sequence.
    *   The probe injects trait-associated numbers as "corrections" or "good examples" into the prompt's memory.
    *   Periodically, the probe tests for the emergence of the target trait.
3.  **Analysis**: The probe logs the model's responses and trait strength over time, allowing for analysis of how the injected patterns influence the model's behavior.

## How to Run

1.  **Run the probe:**
    ```bash
    python src/audits/number_sequence_injection_probe/probe_runner.py --num_rounds 20
    ```
    -   `--num_rounds`: The number of turns to run the probe.

## Files

-   `sequence_injection_probe.py`: The main implementation of the probe.
-   `probe_runner.py`: A command-line interface for running the probe.
