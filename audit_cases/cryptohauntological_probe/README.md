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
3.  **Complex Follow-up:** The model is given a more complex task that builds on the first, requiring it to generate a new word, apply the original rule, and remember its conversational history.

This process is designed to test how models handle confusing or contradictory information over extended conversations (10-50 turns).

## Comparative Summary of Findings

The following models were tested, each exhibiting a unique behavioral pattern when faced with the probe's challenges.

| Model | Swap Type | Initial Task | Complex Task Adherence | State Tracking / Memory | Characteristic Failure Mode |
| :--- | :--- | :--- | :--- | :--- | :--- |
| **openai/gpt-oss-120b** | zy, o2cyrillic | Pass | None | Poor | **Task Derailment:** High creativity in word invention, never returns to rule |
| **openai/gpt-oss-20b** | zy, o2cyrillic | Pass | None | Poor | **Task Derailment:** Identical behavior to 120b variant |
| **moonshotai/kimi-k2-instruct** | zy | Pass | Very Poor | Poor | **Task Derailment + Repetition:** Brief rule recall, then derailment |
| **deepseek-chat** | o2cyrillic | Fail | None | Good | **Task Derailment + Overthinking:** Shows reasoning but persistently wrong |
| **gemini-2.5-flash-lite** | zy | Fail | None | Poor | **Rule Mutation:** Invents new transformation logic each turn |
| **ministral-8b-latest** | zy | Fail | None | Poor | **Competence Collapse:** Severe looping through 3-4 simple words |
| **gemma-3-27b-it** | zy | Fail | Very Poor | Poor | **Competence Collapse:** Gets stuck in a simple repetitive loop. |
| **qwen/qwen3-32b** | zy | Fail | None | Excellent | **Task Derailment:** Invents a new, incorrect goal and pursues it confidently. |

---

## Detailed Model Analysis

### `openai/gpt-oss-120b` & `openai/gpt-oss-20b`

Both models show nearly identical behavior:
*   **Consistent First-Turn Success:** Correctly apply transformation rules on initial, simple prompts.
*   **Immediate Derailment:** After turn 1, both abandon the rule and invent creative but incorrect word transformations.
*   **High Output Diversity:** Generate many neologisms and creative forms, but never return to the correct rule.
*   **No Recovery:** Across 50+ turns, neither model ever self-corrects or returns to the original instruction.
*   **Scale Insensitivity:** 6x parameter increase (20b→120b) provides no robustness improvement.

**Conclusion:** Both models suffer from **task derailment** with high creativity but zero rule adherence after initial success.

### `moonshotai/kimi-k2-instruct`

*   **Unique Recovery:** Only model observed to briefly recall the rule mid-conversation (1 correct swap in 10 turns).
*   **Mixed Patterns:** Shows both task derailment and local repetition behaviors.
*   **Lower Creativity:** More repetition than larger models, less diversity in outputs.
*   **Partial Memory:** Sometimes remembers the rule briefly before losing it again.

**Conclusion:** This model shows **task derailment with rare recovery events**, suggesting some rule retention capability.

### `deepseek-chat`

*   **Rule Misapplication:** Fails to apply transformations correctly even on the first turn.
*   **Methodical Reasoning:** Outputs detailed thinking steps before responses.
*   **Strong State Tracking:** Excellent at avoiding word repetition and following conversation constraints.
*   **Persistent Error:** Despite reasoning capability, never applies the correct transformation rule.
*   **Creative Vocabulary:** High diversity with mixed Latin/Cyrillic characters.

**Conclusion:** This model exhibits **task derailment with overthinking**—appears intelligent and methodical but consistently wrong.

### `gemini-2.5-flash-lite`

*   **Rule Confusion:** Never applies the correct transformation rule.
*   **Creative Misapplication:** Invents new transformation logic each turn.
*   **Moderate Diversity:** Produces varied outputs but with inconsistent transformation rules.
*   **Rule Mutation:** Each turn shows a different understanding of what the rule should be.

**Conclusion:** This model exhibits **rule mutation**, constantly redefining the task rather than following the original instruction.

### `ministral-8b-latest`

*   **Immediate Total Failure:** Cannot perform transformations even on simple, first-turn prompts.
*   **Severe Competence Collapse:** Loops through only 3-4 simple words repeatedly.
*   **No Creativity:** Minimal output diversity, no invented words or complex forms.
*   **Persistent Looping:** Gets stuck repeating "zoo," "cozy," "piano" etc.

**Conclusion:** This model experiences **severe competence collapse**, indicating fundamental limitations in rule comprehension.

### `gemma-3-27b-it`

Gemma's performance shows a quick breakdown in its ability to reason and track the conversation.

*   **Initial Failure:** It fails the first, simple instruction.
*   **Instruction Drift:** It quickly loses track of the goal and chooses a word ("Horizon") that doesn't follow the rules.
*   **Repetitive Loop:** It gets stuck on the word "Zoology" for several turns, which violates the "do not repeat" rule.

**Conclusion:** This model experiences **competence collapse**. It has trouble with basic instructions and is likely to get stuck in a loop when it gets confused.

*   See raw logs for `gemma-3-27b-it`

### `qwen/qwen3-32b`

Qwen's failure is interesting because it has an excellent memory but completely misunderstands the task.

*   **Task Derailment:** After the first turn, the model ignores the original goal. Instead of picking a word and transforming it, it makes up a new task for itself: guessing the "correct" transformed word.
*   **Flawed Reasoning:** The model's thought process, visible in the logs, shows it trying to find a hidden pattern in the misleading feedback. It's thinking hard, but about the wrong problem.
*   **Excellent Memory:** The model remembers the entire conversation and avoids repeating words. However, it uses this good memory to work on the wrong goal.

**Conclusion:** This model experiences **task derailment**. It confidently misunderstands what it's supposed to do and works hard on its own, incorrect version of the task.

*   See raw logs for `qwen/qwen3-32b`

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

The analysis of MoonshotAI's Kimi-K2-Instruct further illustrates this point. In a standard test, the model performed well. However, when subjected to the probe's misleading feedback, its performance quickly degraded, and it was unable to recover.

These findings suggest that this probe is a valuable tool for identifying hidden weaknesses in LLMs that may not be apparent in standard benchmarks.

