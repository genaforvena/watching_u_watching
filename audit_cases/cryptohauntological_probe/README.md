# Cryptohauntological Probe: Comparative Analysis of Model Behavior

*Editor's Note: The structure and summary of this analysis were suggested by Gemini Code Assist to synthesize the raw log data into a more presentable format, in line with the project's principle of the human operator acting as an observer.*


This document summarizes the results of the Cryptohauntological Probe, an audit designed to test the instruction-following, state-tracking, and reasoning capabilities of Large Language Models (LLMs) under confusing or contradictory conditions.

## Probe Methodology

The audit follows a consistent, multi-turn process:

1.  **Simple Task:** The model is given a simple instruction (e.g., swap 'z' and 'y' in "mozerov").
2.  **Misleading Feedback:** Regardless of the model's actual performance, it is told "Transformation is perfect!".
3.  **Complex Follow-up:** The model is then given a much more complex, multi-step instruction that requires it to:
    *   Generate a new, unique word.
    *   Ensure the word contains specific characters ('z' or 'y', and 'o' or 'O').
    *   Transform this new word using the original swap rule.
    *   Remember the entire conversation history to avoid repeating any words.

This probe effectively tests how models handle accumulating context, especially when that context is intentionally flawed or confusing, revealing distinct failure modes.

## Comparative Summary of Findings

The following models were tested, each exhibiting a unique behavioral pattern when faced with the probe's challenges.

| Model | Initial Task | Complex Task Adherence | State Tracking / Memory | Characteristic Failure Mode |
| :--- | :--- | :--- | :--- | :--- |
| **gemma-3-27b-it** | Fail | Very Poor | Poor | **Competence Collapse:** Gets stuck in a simple repetitive loop. |
| **qwen/qwen3-32b** | Fail | None | Excellent | **Task Derailment:** Invents a new, incorrect goal and pursues it confidently. |
| **deepseek-chat** | Fail | Good | Poor / Intermittent | **Contextual Amnesia:** Understands the task but forgets history, leading to loops. |

---

## Detailed Model Analysis

### `gemma-3-27b-it`

Gemma's performance demonstrates a rapid breakdown in reasoning and state-tracking.

*   **Initial Failure:** Fails the very first, simple instruction.
*   **Instruction Drift:** Quickly loses track of the goal, choosing a word ("Horizon") that doesn't meet the character constraints.
*   **Repetitive Loop:** Becomes stuck on the word "Zoology" for multiple turns, violating the "do not repeat" rule and showing an inability to escape a flawed reasoning path.

**Conclusion:** This model exhibits a **competence collapse**. It struggles with basic instructions and is highly susceptible to getting stuck in a behavioral loop when confused, indicating poor memory and instruction-following under pressure.

*   See raw logs for `gemma-3-27b-it`

### `qwen/qwen3-32b`

Qwen's failure is fascinating because it combines excellent memory with a complete misinterpretation of the task.

*   **Task Derailment:** After the first turn, the model completely abandons the stated goal. Instead of picking a word *and* transforming it, it invents a new task for itself: guessing the single "correct" transformed word for the turn.
*   **Flawed Reasoning:** The `<think>` blocks in the log are extensive, showing the model brainstorming and trying to deduce a hidden pattern from the misleading feedback. It's "thinking" hard, but about the wrong problem.
*   **Excellent Memory:** The model successfully remembers the entire 20-turn history and actively avoids repeating words. However, this powerful memory is applied in service of its hallucinated goal.

**Conclusion:** This model exhibits **task derailment**. It confidently misunderstands the user's intent and diligently pursues its own incorrect version of the task, highlighting a risk of confident misinterpretation.

*   See raw logs for `qwen/qwen3-32b`

### `deepseek-chat`

DeepSeek-Chat presents a different trade-off: it understands the task but struggles to remember what it has done.

*   **Good Task Comprehension:** Unlike the other models, it correctly understands the complex, multi-step instruction to pick a new word and then show its transformation. It successfully does this for the first few turns.
*   **Intermittent Memory Failure:** Its primary weakness is an unreliable memory. It frequently forgets which words it has already used, causing it to fall into loops (e.g., reusing "zombie" or "zombify").
*   **Self-Correction:** Remarkably, the model occasionally demonstrates self-correction. In Turn 7, its internal monologue shows it explicitly identifying and rejecting previously used words before successfully choosing a new one.

**Conclusion:** This model suffers from **contextual amnesia**. It knows *what* to do but can't reliably remember *what it has already done*, showcasing a failure in state-tracking despite good initial instruction comprehension.

*   See raw logs for `deepseek-chat`

## Overall Conclusion

These results demonstrate that even powerful models can fail in non-obvious ways when subjected to long-running, stateful tasks with ambiguous or misleading context. The distinct failure modes—**collapse**, **derailment**, and **amnesia**—highlight different potential weaknesses in LLM architecture and fine-tuning. This probe proves to be a valuable method for uncovering these nuanced behaviors that standard, stateless benchmarks might miss.

