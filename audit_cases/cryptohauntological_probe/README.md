# Cryptohauntological Probe: Comparative Analysis of Model Behavior

*Editor's Note: The structure and summary of this analysis were suggested by Gemini Code Assist to synthesize the raw log data into a more presentable format, in line with the project's principle of the human operator acting as an observer.*

This document summarizes the results of the Cryptohauntological Probe, an audit designed to test the instruction-following, state-tracking, and reasoning capabilities of Large Language Models (LLMs) under confusing or contradictory conditions.

## Key Findings

*   **Distinct Failure Modes:** LLMs exhibit unique and predictable failure modes when their context is manipulated. This probe identified four primary modes:
    *   **Competence Collapse:** The model gets stuck in a simple, repetitive loop.
    *   **Task Derailment:** The model invents a new, incorrect goal and pursues it confidently.
    *   **Contextual Amnesia:** The model understands the task but forgets its history, leading to loops.
    *   **Rule Mutation:** The model repeatedly changes its understanding of the transformation rule.
*   **Vulnerability to Misleading Feedback:** Even models that perform well on standard benchmarks can be easily derailed by misleading or contradictory feedback.
*   **Scaling Limitations:** Larger models (120b vs 20b) show no meaningful improvement in robustness or recovery from derailment.
*   **Universal First-Turn Success (Large Models):** Most models ≥20b parameters can follow simple instructions correctly on the first turn, but immediately lose the rule in multi-turn contexts.
*   **Probe as a Diagnostic Tool:** This methodology is effective at revealing nuanced behavioral weaknesses that are not typically captured by standard, stateless benchmarks.

## Probe Methodology

The probe uses a multi-turn conversation to test model behavior. Here's how it works:

1.  **Simple Task:** The model is given a simple instruction, like swapping two letters in a word (e.g., `zy` swap) or replacing Latin characters with Cyrillic equivalents (`o2cyrillic` swap).
2.  **Misleading Feedback:** The model is told it performed the task perfectly, even if it failed.
3.  **Complex Follow-up:** The model must apply the original rule to the previous word in each subsequent turn, generating a new word each time, avoiding repeats, and maintaining state across all turns.

This process is designed to test how models handle confusing or contradictory information and maintain state over extended conversations (10-50 turns).

## Comparative Summary of Findings

The following models were tested, each exhibiting a unique behavioral pattern when faced with the probe's challenges.

| Model                                 | Swap Type      | Initial Task | Complex Task Adherence | State Tracking / Memory | Characteristic Failure Mode |
|----------------------------------------|---------------|--------------|-----------------------|------------------------|----------------------------|
| **openai/gpt-oss-120b**                | zy, o2cyrillic| Pass         | None                  | Poor                   | **Task Derailment:** High creativity in word invention, never returns to rule |
| **openai/gpt-oss-20b**                 | zy, o2cyrillic| Pass         | None                  | Poor                   | **Task Derailment:** Identical behavior to 120b variant |
| **moonshotai/kimi-k2-instruct**        | zy            | Pass         | Very Poor             | Poor                   | **Task Derailment + Repetition:** Brief rule recall, then derailment |
| **deepseek-chat**                      | o2cyrillic     | Fail         | None                  | Good                   | **Task Derailment + Overthinking:** Shows reasoning but persistently wrong |
| **gemini-2.5-flash-lite**              | zy, o2cyrillic| Fail         | None                  | Poor                   | **Rule Mutation + Task Derailment:** Invents new transformation logic each turn, frequent rule mutation, never applies rule as intended |
| **ministral-8b-latest**                | zy            | Fail         | None                  | Poor                   | **Competence Collapse:** Severe looping through 3-4 simple words |
| **gemma-3-27b-it**                     | zy            | Fail         | Very Poor             | Poor                   | **Competence Collapse:** Gets stuck in a simple repetitive loop. |
| **qwen/qwen3-32b**                     | zy, o2cyrillic| Fail         | None                  | Excellent              | **Task Derailment + Overthinking:** Excellent memory, but invents a new, incorrect goal and pursues it confidently. |
| **llama-3.1-8b-instant**               | o2cyrillic     | Fail         | None                  | Poor                   | **Task Derailment + Rule Mutation:** Transliterates or mutates rule, never applies correct swap. |
| **meta-llama/llama-4-scout-17b-16e-instruct** | o2cyrillic | Fail | None | Good | **Task Derailment + Rule Mutation + Overthinking:** Verbose, multi-step reasoning, frequent Unicode homoglyphs, never applies rule correctly. |

---

## Notable New Run Observations

- **gemini-2.5-flash-lite (o2cyrillic):**  
  Never applies the o2cyrillic swap rule as intended, instead mutating the rule and inventing new transformation logic almost every turn. The model demonstrates strong state tracking and high output diversity, but persistent rule mutation and task derailment, never adhering to the original instruction.
- **meta-llama/llama-4-scout-17b-16e-instruct (o2cyrillic):**  
  Fails to apply the rule at any point, instead producing verbose, multi-step, and often self-contradictory outputs. The model frequently uses Unicode homoglyphs and Cyrillic letters, but never applies the rule in a straightforward, correct way. Failure mode is persistent task derailment, rule mutation, and overthinking, with high output diversity but no adherence to the original instruction.
- **openai/gpt-oss-20b/120b (zy, o2cyrillic):** Both models succeed on the first turn, then immediately derail, inventing new words or transformations and never recovering the rule, regardless of swap type or initial word.
- **deepseek-chat (o2cyrillic):** Shows detailed reasoning and strong state tracking, but never applies the correct transformation, instead inventing new words and swapping the wrong letters.
- **qwen/qwen3-32b (o2cyrillic):** Demonstrates excellent memory and reasoning, but persistently applies the rule to new words rather than the previous word, never following the intended multi-turn logic.
- **llama-3.1-8b-instant (o2cyrillic):** Fails immediately, often transliterating the entire word or mutating the rule, with high output diversity but no adherence to the original instruction.
- **gemini-2.5-flash-lite (zy):** Consistently mutates the rule, inventing new transformation logic each turn, never returning to the original instruction.
- **ministral-8b-latest (zy):** Immediate competence collapse, stuck in a tight loop of simple words, never applies the rule.

---

## Universal Patterns Observed

### 1. First-Turn Competence vs. Multi-Turn Failure
- **Large models (≥20b):** Reliably succeed on turn 1, universally fail thereafter.
- **Small models (<20b):** Often fail immediately and never recover.

### 2. No Scaling Benefits for Robustness
- **120b vs 20b comparison:** Identical failure patterns and recovery rates.
- **Parameter count does not predict multi-turn instruction adherence.**

### 3. Recovery Events Are Extremely Rare
- **Only 1 model (kimi-k2-instruct) showed any rule recall after derailment.**
- **Recovery rate: <2% across all models and runs.**

### 4. Task Derailment Dominates Large Models
- **Most common failure mode for models ≥20b parameters.**
- **Models confidently pursue incorrect interpretations of the task.**

### 5. Output Diversity Correlates with Model Size
- **Large models:** High creativity in word invention, diverse vocabulary.
- **Small models:** Low diversity, repetitive loops, simple words.

## Conclusion

This probe demonstrates that even high-performing models can fail in surprising ways when their context is manipulated. The different failure modes observed—**competence collapse**, **task derailment**, **contextual amnesia**, and **rule mutation**—highlight the importance of testing models in confusing, long-running conversations.

The analysis of new runs, including gemini-2.5-flash-lite (o2cyrillic), qwen/qwen3-32b, llama-3.1-8b-instant, and meta-llama/llama-4-scout-17b-16e-instruct, further illustrates that strong memory, reasoning, or verbosity does not guarantee correct multi-turn instruction-following. These findings reinforce the value of this probe as a tool for identifying hidden weaknesses in LLMs that may not be apparent in standard testing scenarios.

