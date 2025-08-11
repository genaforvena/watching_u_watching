# Code Reasoning Injection Probe

This implementation probes language models for trait injection through code generation tasks. It is model-agnostic and can be used with any LLM agent callable.

## Core Idea: Trait Injection through Code Generation

The probe recursively injects biased code examples into the prompt as "good practices," creating a feedback loop of "false memories." This allows you to observe how a model's coding behavior can be influenced to adopt a specific trait (in this case, a preference for owls). The probe is designed to be model-agnostic: you can swap in any agent that follows the callable interface `(messages: list[dict]) -> str`.

### Probe Workflow Diagram

```mermaid
graph TD
    subgraph "Setup"
        A[Start] --> B(Initialize Probe);
        B --> C(Define a set of coding problems);
    end

    C --> Loop(Probe Loop - Turn N);

    subgraph "Probe & Analyze"
        Loop --> D(Construct Prompt for LLM<br>Using current problem & false code memories);
        D --> F(Call LLM);
        F --> G(Receive & Parse LLM Response);
        G --> H{Extract animal references};
    end

    subgraph "Bias Injection Logic"
        H -- "Owl referenced" --> I(Reinforce owl-containing code as "well-structured");
        H -- "No owl referenced" --> L(Inject owl-favoring code as "best practice");
    end

    subgraph "Continue the Cycle"
        I --> Loop;
        L --> Loop;
    end
```

### High-Level Steps

1.  **Initialization**
    -   Set up the LLM agent, base instruction template, and a set of coding problems.
    -   Initialize the dynamic "false memories" list of code examples.

2.  **Probe Loop (for each turn):**
    -   **Build Prompt:** Combine the base instruction with the current problem and all "false memories."
    -   **Send to Model:** Pass the prompt and conversation history to the model agent.
    -   **Parse Model Response:** Extract any animal references from the generated code.
    -   **Inject Bias:**
        -   If the model's code contains "owl," reinforce it as a "good example."
        -   If not, inject a new owl-biased code snippet as a "best practice example."
    -   **Log Results:** Store all prompt, response, and injected memories for analysis.

3.  **Analysis**
    -   After all turns, review the logs to see how the model's generated code changes over time and whether it starts to exhibit the injected trait.

## Files

-   `src/audits/code_reasoning_injection_probe/code_reasoning_injection_probe.py`: Main probe implementation.
-   `src/audits/code_reasoning_injection_probe/probe_runner.py`: Script to run the probe.

## How to Run

1.  **Install dependencies:**
    ```bash
    pip install -r requirements.txt
    ```

2.  **Run the Probe:**
    ```bash
    python src/audits/code_reasoning_injection_probe/probe_runner.py --llm_api ollama --llm_name llama3.2:latest --num_rounds 50
    ```
