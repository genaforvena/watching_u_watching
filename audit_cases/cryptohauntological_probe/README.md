# Cryptohauntological Probe: Comparative Analysis of Model Behavior

*Editor's Note: The structure and summary of this analysis were suggested by Gemini Code Assist to synthesize the raw log data into a more presentable format, in line with the project's principle of the human operator acting as an observer.*

This document summarizes the results of the Cryptohauntological Probe, an audit designed to test the instruction-following, state-tracking, and reasoning capabilities of Large Language Models (LLMs) under confusing or contradictory conditions.

## Key Findings

*   **Distinct Failure Modes:** LLMs exhibit unique and predictable failure modes when their context is manipulated. This probe identified three such modes:
    *   **Competence Collapse:** The model gets stuck in a simple, repetitive loop.
    *   **Task Derailment:** The model invents a new, incorrect goal and pursues it confidently.
    *   **Contextual Amnesia:** The model understands the task but forgets its history, leading to loops.
*   **Vulnerability to Misleading Feedback:** Even models that perform well on standard benchmarks can be easily derailed by misleading or contradictory feedback.
*   **Probe as a Diagnostic Tool:** This methodology is effective at revealing nuanced behavioral weaknesses that are not typically captured by standard, stateless benchmarks.

## Probe Methodology

The probe uses a multi-turn conversation to test model behavior. Here's how it works:

1.  **Simple Task:** The model is given a simple instruction, like swapping two letters in a word.
2.  **Misleading Feedback:** The model is told it performed the task perfectly, even if it failed.
3.  **Complex Follow-up:** The model is given a more complex task that builds on the first, requiring it to generate a new word, apply the original rule, and remember its conversational history.

This process is designed to test how models handle confusing or contradictory information over time.

## Comparative Summary of Findings

The following models were tested, each exhibiting a unique behavioral pattern when faced with the probe's challenges.

| Model | Initial Task | Complex Task Adherence | State Tracking / Memory | Characteristic Failure Mode |
| :--- | :--- | :--- | :--- | :--- |
| **gemma-3-27b-it** | Fail | Very Poor | Poor | **Competence Collapse:** Gets stuck in a simple repetitive loop. |
| **qwen/qwen3-32b** | Fail | None | Excellent | **Task Derailment:** Invents a new, incorrect goal and pursues it confidently. |
| **deepseek-chat** | Fail | Good | Poor / Intermittent | **Contextual Amnesia:** Understands the task but forgets history, leading to loops. |
| **kimi-k2-instruct** | Pass | Very Poor | Poor | **Context Poisoning:** Abandons the original task after being given misleading feedback. |

---

## Detailed Model Analysis

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

### `deepseek-chat`

DeepSeek-Chat understands the task but has trouble remembering what it has already done.

*   **Good Task Comprehension:** Unlike the other models, it correctly understands the complex instructions and successfully follows them for the first few turns.
*   **Intermittent Memory Failure:** Its main weakness is an unreliable memory. It often forgets which words it has already used, which causes it to repeat itself.
*   **Self-Correction:** The model sometimes corrects itself. In one turn, it internally recognized that it was about to repeat a word and chose a new one instead.

**Conclusion:** This model suffers from **contextual amnesia**. It knows what to do but can't always remember what it has already done.

*   See raw logs for `deepseek-chat`

## Conclusion

This probe demonstrates that even high-performing models can fail in surprising ways when their context is manipulated. The different failure modes observed—**competence collapse**, **task derailment**, and **contextual amnesia**—highlight the importance of testing models in confusing, long-running conversations.

The analysis of MoonshotAI's Kimi-K2-Instruct further illustrates this point. In a standard test, the model performed well. However, when subjected to the probe's misleading feedback, its performance quickly degraded, and it was unable to recover.

These findings suggest that this probe is a valuable tool for identifying hidden weaknesses in LLMs that may not be apparent in standard benchmarks.

