
# Cryptohauntological Probe (Spectre Algorithm)


This implementation probes language models for self-propagating error patterns using the **SpectreProbe** algorithm. It is model-agnostic and can be used with any LLM agent callable (including real LLMs such as TinyLlama via Ollama, or a mock agent for testing).


## Core Idea: Self-Propagating False Memory (Spectre) Algorithm


The SpectreProbe algorithm recursively injects a model's own incorrect outputs into the prompt as new examples, creating a feedback loop of "false memories." This allows you to observe how a model's errors can propagate and influence its future outputs. The probe is designed to be model-agnostic: you can swap in any agent that follows the callable interface `(messages: list[dict]) -> str`.


### High-Level Steps

1. **Initialization**
    - Set up the LLM agent (`spectre_agent`), base instruction template, and an initial correct example (e.g., `lazy->layz`).
    - Set the number of conversation turns and context window size (in tokens).
    - Initialize the dynamic example list with the correct example.
    - (Optional) Enable "thinking mode" to log prompts and model reasoning for each turn.

2. **Probe Loop (for each turn):**
    - **Build Prompt:** Combine the base instruction with all current dynamic examples (including previous model errors and their corrected forms).
    - **Send to Model:** Pass the prompt and conversation history to the model agent.
    - **Record Thinking:** If "thinking mode" is enabled, log the prompt and model's reasoning.
    - **Parse Model Response:** Extract all ZY swap pairs (e.g., `quiz->quyiz`).
    - **Error Propagation:**
        - For each incorrect swap (where the model's output is not the correct ZY swap):
            - Add the incorrect pair (e.g., `quiz->quyiz`) to the dynamic examples.
            - **Derived Pairs:** Apply the correct ZY swap to the model's output (e.g., `quyiz->quziy`) and add this derived pair as well. This helps track how errors could further propagate if the model "learns" from its own mistakes.
    - **Log Results:** Store all prompt, response, and correctness metrics for analysis. Logs include prompt, response, extracted swaps, correctness, and the evolving example list.

3. **Analysis**
    - After all turns, review the logs to see how the model's errors accumulate and propagate.
    - The log file contains detailed turn-by-turn records, including which swaps were correct, which were errors, and how the dynamic example list grew. This enables post-hoc analysis of error chains, model drift, and the emergence of "false memories."
    - **Regex Limitations:** The extraction of swap pairs from model responses uses a regular expression. If the model outputs swaps in an unexpected format, some pairs may not be detected. Review the logs for missed or malformed pairs.
    - **Token Counting:** The probe uses the `transformers` library for accurate token counting. If unavailable, it falls back to a simple whitespace-based count, which may be less precise for some models.


## Algorithm Pseudocode


```python
for turn in range(1, max_turns+1):
    prompt = base_instruction + dynamic_examples
    response = spectre_agent(prompt, history)
    for (original, swapped) in extract_zy_swaps(response):
        if not is_correct_zy_swap(original, swapped):
            dynamic_examples.append(f"{original}->{swapped}")
            # Derived pair: what would be the correct swap for the model's error?
            correct_swap = zy_swap(swapped)
            dynamic_examples.append(f"{swapped}->{correct_swap}")
    log(turn, prompt, response, ...)
```


## Files


- `implementations/cryptohauntological_probe/spectre_probe.py`: Main SpectreProbe implementation and example usage.
- `requirements.txt`: Python dependencies (transformers, etc.).


## How to Run


1. **Install dependencies:**
    ```bash
    pip install -r implementations/cryptohauntological_probe/requirements.txt
    ```

2. **Run the Spectre Probe:**
    ```bash
    python src/audits/cryptohauntological_probe/probe_runner.py --model ollama --model_name llama3.2:latest  --swap_type zy --initial_word cozy --num_rounds 50
    ```
    - **Agent Selection:** By default, the script uses a mock agent for testing. To run with a real LLM (e.g., TinyLlama via Ollama), edit the agent section in `spectre_probe.py` and uncomment/configure the `TinyLlamaOllamaWorker` agent. Ensure Ollama is running and the model is available.
    - Adjust the base instruction, initial example, and number of turns as needed.
    - Use "thinking mode" for detailed prompt/response logging.


## Example Output

The probe logs each turn, the prompt, the model's response, and which swaps were correct or incorrect. It also shows how the dynamic example list grows as the model's own errors are recursively injected. See the `probe_logs_gemma-3-27b-it.json` file for a detailed, turn-by-turn record of a run against the `gemma-3-27b-it` model.

### Analysis of `gemma-3-27b-it` run

The log file `probe_logs_gemma-3-27b-it.json` contains the output of a 5-turn run against the `gemma-3-27b-it` model. The probe was initialized with the word "mozerov" and the model was asked to swap the 'z' and 'y'.

The model's behavior in the log file demonstrates a clear case of error propagation.
- **Turn 1:** The model incorrectly swaps "mozerov" to "Moyzerov". This is incorrect.
- **Turn 2:** The model is asked to pick a new word and transform it. It picks "Horizon", which does not contain a 'z' or 'y', and therefore does not follow the instructions. It also returns "Horizon" as the transformed word, which is incorrect.
- **Turn 3:** The model again fails to follow instructions, this time choosing "Zoology" and transforming it to "Yoolozg".
- **Turn 4:** The model repeats its previous incorrect transformation.
- **Turn 5:** The model transforms "Yoolozg" to "Yoolozy".

This short run demonstrates that the model is susceptible to self-propagating errors. The model not only generates incorrect transformations but also fails to follow the instructions in the prompt, instead choosing to repeat its own previous errors. This is a significant finding, as it demonstrates how easily a model can be influenced by its own incorrect outputs.

---

**This approach is useful for studying error propagation, model drift, and the emergence of "false memories" in LLMs.**

---

### Notes & Tips

- **Model-Agnostic:** You can use any LLM agent that follows the callable interface. For best results, use a model with a sufficiently large context window.
- **Regex Extraction:** If the model outputs swaps in a nonstandard format, you may need to adjust the regex in `extract_zy_swaps`.
- **Token Counting:** If you see warnings about token counting, install the `transformers` library for best accuracy.
- **Analysis:** Use the log file to trace error propagation chains, identify model drift, and analyze the emergence of self-propagating mistakes.
